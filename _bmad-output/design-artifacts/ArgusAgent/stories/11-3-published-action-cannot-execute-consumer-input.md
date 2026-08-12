---
baseline_commit: 93adc94d0203eaaf4d1cb1d8bc7113e9b885beed
baseline_note: >-
  `HEAD` = `93adc94` on `master`, **6 commits unpushed**, `git tag -l` **empty**. Epic 10 is 5/5
  `done`; Stories 11.1 and 11.2 are `done` and **both deltas are in the tree, uncommitted**. **No CI
  run has ever seen a line of Epic 10 or Epic 11.** Every baseline figure in this story is **LOCAL,
  Windows / CPython 3.11.15**, under the dated risk acceptance recorded in Story 11.1 §0.1
  (AI-E10-1, 2026-08-11, XAgent007). See §0.1 — carried forward, not re-taken.
  ⚠️ **The tree is NOT clean and you did not dirty it.** `git status --porcelain -- argus/` shows
  exactly **four ` M` lines** — `argus/cli.py`, `argus/detectors/vacuous_test.py`,
  `argus/reports/generator.py`, `argus/verdict/negative_assurance.py` — which are Stories 11.1's and
  11.2's reviewed and `done` deltas. `action.yml` itself is ` M` for **11.1's one-line FR34
  description change** (verified: `git diff -- action.yml` is a single replaced line, line 2, which
  moved **no** line number). `CHANGELOG.md`, `README.md`, `pyproject.toml`,
  `tests/test_release_surface_honesty.py` are inherited-dirty from 10.5/11.1/11.2. `_bmad/**` churn
  is AI-E10-9's. `bmad-dev-loop-pack/`, `.bmad-drift-audit/` and `_bmad-output/audit-reports/*`
  belong to the orchestrator/host. **Do not commit, revert, restage or "tidy" any of it.** THIS FILE
  is untracked and IS yours: `git add` it with your delta or you repeat AI-E8-1.
  ⚠️ **ONE TEST IS ALREADY RED AND IT IS NOT YOURS.** See §0.4 (`DF-11-1-A`), carved out **by node
  id**. Any second red is yours, whatever its file.
  **Every figure, coordinate, count, hit-set and classification result below was produced by
  EXECUTING code on THIS tree on 2026-08-12.** Locate every site by its **anchor text**; treat every
  line number as a hint you must re-verify — with the exception explicitly measured in §A.1, where
  the coordinates were re-verified against **both** the working tree and `HEAD` and are exact.
story_key: 11-3-published-action-cannot-execute-consumer-input
epic: 11
---

# Story 11.3: The published action cannot execute a consumer's input

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo. The
> `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no back-port.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`,
> `minions_core/apaa/` or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/`
> and `tests/`.
>
> ⚠️ **This is the one story in Epic 11 whose entire write set is OUTSIDE `argus/`.** Read §0.2
> before you assume the epic's fences bind the way they did for 11.1 and 11.2 — **they were both
> measured, and neither binds here.** That is a finding, not a licence: §0.2 states what still does.

---

## Story

As a developer running the Argus action in my own repository,
I want my workflow inputs to be data, never shell source,
so that using Argus cannot execute code in my CI job.

**Why this is one story, and what it is not.** Epic 11's charter is *"nothing unsafe or untrue can be
published."* This story closes exactly one defect class: **a GitHub Actions expression expanded into
the text of a shell script before `bash` parses it.** It converts every such site in the published
composite action into an `env:`-bound, double-quoted shell variable, and it closes the class with a
guard over the **whole committed workflow corpus** that fails on the next one anybody writes. It ships
**no new capability**, changes **no input name, default, description or output**, changes **no
verdict, threshold or exit code**, and moves **not one byte under `argus/`**.

**Why it is release-blocking despite the ledger's 🟢.** `DF-9-2-D` was filed 🟢 because the defect is
*latent*: `action.yml` today is executed only by this repository's own maintainer. **Publishing
inverts that.** The moment the action is listed on the Marketplace, every consuming repository
executes this file, and the vulnerable value is one that the *consumer's* workflow author supplies —
which in practice is frequently `${{ github.event.* }}`, GitHub's documented untrusted-input surface.
A latent finding in one repository becomes a live finding in every repository that adopts the tool.
**PRD §Product Scope V1.5 already states the consequence as a binding gate:** *"GitHub Marketplace —
the composite action | **In scope, gated** on the `action.yml` input-interpolation fix."* This story
is that fix.

**The bitter irony, stated because this project does not let itself off:** the file is a *security
gate* that a student repository installs to be told whether its code is safe, and the gate itself is
the injection surface. And it is CI-executed code that **no CI run has ever executed** (§0.1).

⚠️ **Read §0 before anything else.** Six items gate this story. Two of them were expected to constrain
your design and **do not** — measured, not assumed. One is a red test you must not touch. Two are
ledger items you must **not** absorb.

---

## Story Context

### Method statement — everything in §0–§F was MEASURED on this tree on 2026-08-12

Every count, coordinate, hit-set, hash and parse result below was produced by running `git`, `wc`,
`pytest`, by importing and calling `tests.test_invocation_contract`'s own extractor and run-block
resolver over the real corpus, by calling
`argus.dogfood.partition_plan.build_full_repo_plan('.')` in this working tree, and by rendering the
`action.yml` script template with an adversarial value and **executing it through a real `bash`**
(§A.2 — a demonstrated exploit, not an asserted one). **§A.4 and §A.8 additionally record a
REVERSIBLE EXPERIMENT**: the candidate resolver change was applied **in memory only** (a monkeypatch
of the module attribute inside one Python process — **no file on disk was modified**, which is why no
`sha256` round-trip is quoted for it), the real corpus was re-extracted through it, and the resulting
invocation set was compared element-by-element against the unmodified one. **Three figures are
ATTRIBUTED, not re-measured here**: `bandit` 0 High / 0 Medium (19 Low), coverage 95.82%, and
`argus audit .`'s field values, all from Story 11.2's run at this tree. **Re-derive everything;
transcribe nothing.**

---

### §0. The six gates on this story — read these first

#### 0.1 — 🔴 DATED RISK ACCEPTANCE, CARRIED FORWARD (AI-E10-1)

**Recorded by: XAgent007 (operator), 2026-08-11. Carried forward to this story, not re-taken.**

> **No CI run covers any Epic 10 or Epic 11 sha.** Re-verified this session: `HEAD` = `93adc94`, **6
> commits ahead of `origin/master`**, `git tag -l` **empty**. Every gate figure this story cites —
> 1362 collected tests, `mypy` clean on 72 files, the dogfood partition ids — is a **LOCAL run on a
> Windows host at CPython 3.11.15**. CI is ubuntu × 3.10/3.11/3.12, and this project has measured
> evidence that the difference matters (six of the twelve commits in `cd60dbb..00c8d1b` were
> host-portability defects invisible on exactly this machine).

**🚩 This gate lands harder on THIS story than on any before it, and the story must say so out loud.**
The artifact you are hardening — `action.yml` — **only ever executes inside GitHub Actions**, and
`.github/workflows/audit-ci.yml` has never run on a commit containing any of it. You are fixing
CI-executed code that no CI run has exercised, using a local Windows shell, and you cannot close that
gap from inside this story (see §0.5 — nothing may be pushed or dispatched). **Therefore:**

1. Apply Story 10.1's evidence-citation rule (`architecture.md` §H + §Enforcement, enforced by
   `tests/test_evidence_citation.py`) to **your own** gate run: label every figure **LOCAL**, and
   either cite an `audit-ci.yml` run id **plus the sha it covers** for your own HEAD, or record
   **`NOT ESTABLISHED`** and name the command a human runs.
2. ⛔ **Do not push, tag or `workflow_dispatch` to manufacture a citation** (10.1's DN-7).
3. ⛔ **Your committed guard must not need `bash`, a runner, `PyYAML`, or any network.** See DN-5:
   `PyYAML` is **NOT a declared dependency** of this project (measured — it is absent from
   `pyproject.toml`'s `dependencies` *and* its `[dev]` extra, and is present in this venv only
   transitively via `bandit`/`markdown-it-py`). A guard that `import yaml` passes here and is a
   coin-toss in CI. And a guard that shells out to `bash` cannot run on a Windows developer's box —
   `pytest.skip` is **not** an acceptable answer in this project, because `audit-ci.yml` sets
   `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` precisely to make a skip a hard failure. **Pure text
   analysis, stdlib only.** §A.2 explains how to prove the security property without a shell.

#### 0.2 — ⛔ THE `DF-10-4-D` FENCE AND THE LOC BUDGET (AI-E10-2) — BOTH MEASURED, NEITHER BINDS. HERE IS WHY THAT IS NOT A LICENCE

**The operator ruling stands for ALL of Epic 11: NO Epic 11 story may create or stage a new
`argus/**` source file.** The mechanism, re-verified this session:
`argus/dogfood/partition_plan.py::enumerate_minions_source_files` enumerates via **`git ls-files
argus`**, and `git ls-files` reports the **INDEX**, not `HEAD` — so the dogfood-audited population
moves the instant a new `argus/**` module is **staged**, before any commit, at the exact moment
`AI-E8-1` *requires* the `git add`. In Story 10.4 that turned five committed-artifact staleness tests
red mid-implementation and halted the story.

**Measured this session by executing `build_full_repo_plan('.')`:**

| Quantity | Measured 2026-08-12 | Meaning for this story |
|---|---|---|
| `git ls-files -- argus` | **72** | must still read **72** after you stage |
| `git status --porcelain -- argus/` | exactly **four ` M`** lines, **no ` A`** line | 11.1's three + 11.2's one. Add none. |
| dogfood `scope_prefix` | **`argus/`** | 🚩 the audited population is `argus/` **ONLY** |
| dogfood `source_file_count` / `total_loc` | **72** / **20034** | unit 1 = 1330, **unit 2 = 14900**, unit 3 = 3804 |
| unit 2 `partition_id` | `82a3d605e61e…` (soft cap **15000**) | **100 physical lines of headroom** |
| all three `partition_id`s | `477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…` | must be **byte-unchanged** after you stage |

**🚩 THE CONSEQUENCE, WHICH IS THE POINT OF THIS SUBSECTION.** The dogfood partitioner's scope prefix
is `argus/`. **`action.yml`, `.github/workflows/**` and `tests/**` are not in the audited population
at all.** This story's entire write set therefore consumes **0 of the 100 remaining lines**, and
`git ls-files -- argus` cannot move because no file this story writes is under `argus/`.

**⛔ That makes both fences non-binding by construction, and it makes them cheap to VERIFY rather than
optional to check.** They are AC6.1 and AC6.2 anyway, with a **mandated HALT**:

- If you find yourself needing to add or edit **any** file under `argus/` — **STOP and HALT**. It
  means the fix has grown a runtime component that was not scoped, and the operator ruling has become
  a genuine conflict that a dev agent may not resolve alone.
- If `unit 2`'s LOC moves off **14900**, or any `partition_id` changes — **STOP and HALT**.
- ⛔ **NEVER regenerate a committed dogfood artifact to make a staleness test pass.** That is the
  antipattern this project has refused three times.

**CONFIRMED DELIVERABLE UNDER THE FENCE.** Every line of this story lands in `action.yml`,
`tests/**`, `CHANGELOG.md` and `deferred-work.md`. **No HALT is expected. Verify it; do not assume
it.**

#### 0.3 — 🔴 RE-MEASURED PREMISES (AI-E10-3) — the first Epic 11 story whose central premise SURVIVED

`AI-E10-3` requires every Epic 11 premise to be re-measured at create-story time and the divergence
recorded. For 11.1, two of three premises were stale. For 11.2, the ledger's central premise had
**expired** and its count was wrong for the sixth time. **For 11.3, the epic's headline measurement is
EXACT** — and two adjacent claims are not.

| Premise as the epic / ledger writes it | Measured on this tree, 2026-08-12 | Verdict |
|---|---|---|
| *"**five** action-input sites are interpolated into `run:` bodies (`action.yml:74,78,79,80,126`)"* | **HELD, and every coordinate is exact.** Re-derived by regex over the file and cross-checked against the run-block resolver: exactly five `${{ inputs.* }}` occurrences sit inside a `run:` body, at **74, 78, 79, 80, 126** — identical in the **working tree and at `HEAD`** (11.1's `action.yml` edit replaced line 2 and moved nothing). §A.1. | ✅ **holds — cite it** |
| *"the ledger named only `:127`"* | **TRUE, and the ledger's one coordinate is ALSO WRONG.** `DF-9-2-D` says `action.yml:127`. Line **126** is the `if [ "${{ inputs.strict }}" = "true" ]`; line **127** is the `echo "❌ Argus Release Gate failed…"` beneath it. The ledger named one site out of five **and put it on the wrong line** — the seventh stale coordinate in this project. §A.1. | ⚠️ **corrected → AC5.1** |
| *"all five are bound through `env:` and **compared** as quoted shell variables"* | **PARTLY IMPRECISE.** Only **one** of the five (`strict`, `:126`) is *compared*. The other three inputs at `:74/:78/:79/:80` are **passed as arguments** to `mkdir` and `argus audit`. The operative property is *bound through `env:` and referenced as a **double-quoted shell variable***; "compared" is true of exactly one site. §C.2. | ⚠️ **corrected → AC1.3** |
| *"a guard test fails on **any** action-input interpolation appearing inside a `run:` block"* (epics + `DF-9-2-D` close condition) | **THE OBVIOUS IMPLEMENTATION IS VACUOUS.** This repo already owns a run-block resolver (`tests/test_invocation_contract.py::_executable_line_numbers`) and AR7/§3.3 forbid a second mechanism where one exists — but the existing one **only recognises block scalars** (`run: \|`). Measured: for a synthetic `- run: echo "${{ inputs.evil }}"` it returns an **EMPTY** line set. A guard built on it would be blind to the single-line form, which is the cheapest way to reintroduce this exact defect. §A.4. | ❌ **stale → this is why AC3 is a closure with its own negative control** |
| *"`DF-9-2-D`: `action.yml:127` runs `if [ "${{ inputs.strict }}" …]` … a consumer who sets `strict` to a crafted value executes shell"* | **DEMONSTRATED, not merely asserted.** The rendered script was executed through a real `bash` with a crafted `strict` value; an injected `id -un` **ran and printed the user**. The same value through the `env:`-bound form produced `GATE_OFF`, rc 0, no execution. §A.2. | ✅ **holds — exploit path proven** |

#### 0.4 — ⛔ ONE TEST IS ALREADY RED. IT IS `DF-11-1-A` AND IT IS NOT YOURS

`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
**FAILS on this tree, before you touch anything.** Re-run and confirmed this session:

```
AssertionError: status-asserting document(s) exist but are not registered:
['epic-10-retro-2026-08-11.md']
```

**Attribution is PROVEN, not assumed.** Story 11.1's review adjudicated it by a positive git-stash
isolation experiment (all nine of 11.1's touched files reverted, the identical failure reproduced from
the untracked `epic-10-retro-2026-08-11.md` alone, stash popped content-identical). Story 11.2 carried
it forward unchanged. It is Story 10.1's own citation guard working **as designed** on an Epic-10
artifact that was never registered.

**Ruled for this story: `DF-11-1-A` STAYS DEFERRED. Do not close it here.** The reasoning is recorded
as **DN-8** so it is not re-litigated:

1. It is an **artifact-registration** item about an Epic-10 retrospective document. It shares no line,
   no file and no defect class with shell-injection hardening in a composite action.
2. Closing it means registering the retro in `_STATUS_DOCUMENTS`, which then obliges **the retro
   itself** to satisfy the citation rule — a run id **plus the sha it covers**, or a `NOT ESTABLISHED`
   marker. There is no such run id (§0.1), so closing it from here would mean either editing a signed
   Epic-10 retrospective or minting a citation this story is forbidden to create.
3. Its owner is **XAgent007 (operator)** by the ledger, not Engineering.
4. Precedent: **Story 8.1's AC18 carve-out**, and Story 11.2's DN-7, which ruled identically.

**What this obliges you to do (AC6.3):** your "full suite green" claim must **carve this failure out
BY NODE ID** and assert it is the **only** failure. ⛔ A second red is yours, whatever its file. Do not
add `epic-10-retro-2026-08-11.md` to `_STATUS_DOCUMENTS`, do not `git add` it, do not delete it.

*(Surfaced to the operator again as open question 1 — it is now standing red across three consecutive
stories.)*

#### 0.5 — ⛔ NOTHING IS PUBLISHED BY THIS STORY, AND THAT IS SHARPEST HERE

**No push. No tag. No release. No `workflow_dispatch`.** The publish is **Story 12.9**, by design
(`epics.md` Epic 11 preamble; `sprint-status.yaml` Epic 11 header).

This is pointed for *this* story specifically, and the point must not be lost: **this story hardens
the published action; it does not ship it.** The temptation is structural — the fix is only *observable*
in a real Actions run, and the marketplace listing is the thing the fix unblocks. Resist both. What
this story delivers is the **hard precondition** on the marketplace channel (`epics.md` Story 11.3 AC3;
PRD §Product Scope V1.5). Story 12.9 decides, with evidence, whether to exercise it.

#### 0.6 — ⛔ TWO OPEN LEDGER ITEMS THAT ARE **NOT** THIS STORY'S. Judged, not ignored

`DF-11-2-A` and `DF-11-2-B` were filed by Story 11.2 and are open and unowned-by-a-story in the
orchestrator's reading. **Both were read in full this session and both are ruled OUT of 11.3:**

- **`DF-11-2-A`** (six real test-name conventions unrecognised — `*_test.rb`, `*Tests.java`,
  `*TestCase.java`, `Test*.java`, `*Test.php`, `*_test.c`; every one a false **negative**) and
  **`DF-11-2-B`** (`c` and `php` ground with **no** convention at all) are **file-classification**
  defects living in `argus/detectors/vacuous_test.py`. They share **zero** lines, zero files and zero
  defect class with shell-injection in a YAML file.
- **The ledger already assigns them.** Both carry `target_story: **12.5**` and
  `owner: **Delivery Orchestrator**` — a *recommendation of record* from Story 11.2's operator open
  question 1, because 12.5's disclosure surface (*"a deliberately-excluded language states its absence
  AND reason at the point of downgrade"*) is the same surface that answers them.
- **Absorbing them here would breach §0.2 anyway.** Their fix is `argus/**` code that *widens*
  classification and *moves* verdicts on real repositories — the opposite of this story's
  zero-`argus`-byte, zero-behaviour-change shape, and a widening inside an epic chartered *"nothing
  unsafe or untrue can be published."*

**Ruled: they stay filed against 12.5. Do not touch them, do not fix them, do not re-file them.**
Restated to the operator as open question 2 so the ruling is visible rather than silent.

---

### §A. What was measured, and what it changes

#### A.1 — 🚩 The five sites, exact — and the two coordinates the records got wrong

Derived by regex over the file and cross-checked against the run-block resolver's executable-line set.
`action.yml` is **136 lines**, `sha256` `1b62ac549ed0e01e…` (working tree). Every `${{ … }}`
occurrence in the file, with its context and whether it sits inside a `run:` body:

| Line | Context expression | Inside a `run:` body? | Shell source? | Consumer-controlled? |
|---|---|---|---|---|
| 16 | `github.sha` (an input **default**) | no | no | no |
| 42, 49, 54 | `steps.run_audit.outputs.*` (**outputs** block) | no | no | no |
| **68** | `github.action_path` | **YES** | **YES** | **no** — runner-provided |
| **74** | `inputs.report-dir` | **YES** | **YES** | **YES** |
| **78** | `inputs.repo-path` | **YES** | **YES** | **YES** |
| **79** | `inputs.commit-sha` | **YES** | **YES** | **YES** |
| **80** | `inputs.report-dir` | **YES** | **YES** | **YES** |
| **126** | `inputs.strict` | **YES** | **YES** | **YES** |
| 135 | `inputs.report-dir` (`with: path:` of `upload-artifact`) | no | **no** | YES — but see §C.3 |

**Three findings the records do not contain:**

1. **The epic's five are exact, at exactly `74, 78, 79, 80, 126`**, in the working tree **and** at
   `HEAD` (`git show HEAD:action.yml` re-checked — 11.1's FR34 edit replaced line 2 and moved nothing).
   Cite them; still locate by anchor text.
2. **`DF-9-2-D`'s single coordinate `action.yml:127` is off by one.** Line 126 carries the `if [
   "${{ inputs.strict }}" = "true" ]`; line 127 is `echo "❌ Argus Release Gate failed with exit code
   $EXIT_CODE"`. The ledger named **one of five sites, on the wrong line**. → AC5.1.
3. **🚩 There is a SIXTH interpolation inside a `run:` body that no document names: `:68`,
   `pip install "${{ github.action_path }}"[languages]`.** It is **not** consumer-controlled
   (`github.action_path` is set by the runner to the action's own checkout directory), so it is **not
   part of the vulnerability**. It is nonetheless in scope for the *sweep* — see DN-3 for the ruling
   and its reason.

**All five `inputs.*` sites live in ONE step** (`- name: 🔍 Execute Argus Audit Engine`, `id:
run_audit`). So the fix is **one `env:` block with four entries**, plus one more on the install step.

#### A.2 — 🚩🚩 THE EXPLOIT, DEMONSTRATED — and how to prove it closed WITHOUT a shell

GitHub's own documentation states the mechanism plainly: *"Before the shell script is run, the
expressions inside `${{ }}` are evaluated and then substituted with the resulting values, which can
make it vulnerable to shell command injection."* The value is **not** passed to `bash` as data — it is
**pasted into the script text**.

**Executed this session.** The `action.yml:126` template was rendered with a crafted `strict` value and
handed to a real `bash`, exactly as the runner does:

```
value:    x" = "x" ]; then echo PWNED_ARBITRARY_EXECUTION; id -un; fi; if [ "z

rendered: if [ "x" = "x" ]; then echo PWNED_ARBITRARY_EXECUTION; id -un; fi; if [ "z" = "true" ]; then echo GATE_ON; fi
stdout:   PWNED_ARBITRARY_EXECUTION
          varin                       <- `id -un` EXECUTED
rc:       0
```

**The same value through the `env:`-bound form:**

```
env STRICT=<the same value>;  if [ "$STRICT" = "true" ]; then echo GATE_ON; else echo GATE_OFF; fi
stdout:   GATE_OFF
rc:       0                    <- nothing executed, no error, correct answer
```

The attack needs no exotic input: a consumer whose workflow writes
`with: { strict: "${{ github.event.issue.title }}" }` hands an attacker the job. The runner's token,
`$GITHUB_ENV`, `$GITHUB_OUTPUT` and the checked-out source are all in that job's reach.

**⛔ DO NOT COMMIT THIS DEMONSTRATION AS A TEST.** §0.1/3 forbids a `bash`-dependent guard: it cannot
run on Windows, `pytest.skip` is a false green in this project, and a committed test that spawns a
shell to prove code execution is itself a liability. **The demonstration belongs in this story
document, where it now is.**

**🔑 The portable formulation of the same property — this is what AC2 requires.** The security
property is not *"a shell does not execute the value"*; it is the stronger, purely-textual:

> **The `run:` script text of every step is INVARIANT under the value of every action input.**

`env:`-binding buys exactly that, and it is checkable with `str` operations over the committed file:
render the script for an adversarial corpus of input values, and assert the script bytes never change
— because the value never appears in the script at all. Give it a **positive control** built from the
pre-fix line, held as a literal string inside the test (never read back from a file), so the assertion
is proven to fire. See AC2.

#### A.3 — 🚩 THE MEASUREMENT THAT DECIDES THE GUARD: this repo's existing run-block resolver is BLIND to single-line `run:`

AR7 / architecture §3.3 forbid a second mechanism where one exists, and one exists:
`tests/test_invocation_contract.py::_executable_line_numbers(text, suffix)` already answers *"which
lines sit inside a `run:` body?"* for the corpus `README.md`, `action.yml`, `.github/workflows/*.yml`.
Its YAML branch keys on:

```python
if re.match(r"^-?\s*run:\s*[|>]?[-+]?\s*$", stripped):
```

**`\s*$` requires end-of-line after `run:`.** Measured by execution:

| Input | Existing resolver says |
|---|---|
| `.github/workflows/release.yml:126` `run: python scripts/release_preflight.py --phase pre-build --tag "$TAG"` | **NOT inside a run body** |
| `:132` `run: python -m pip install --upgrade pip build`, `:135` `run: python -m build`, `:140` `run: python scripts/release_preflight.py --phase post-build …` | **NOT inside a run body** |
| synthetic `- run: echo "${{ inputs.evil }}"` | executable line set = **`[]`** — **NOT DETECTED** |

**🚩 A guard built naively on this resolver would be VACUOUS against the single easiest way to
reintroduce `DF-9-2-D`:** a one-line `run:` step. This project has already shipped one guard whose
denial filter swallowed the thing it looked for (the Epic-9 `-17b` case, trap E.3) and refuses to do
it again. → AC3.2 and its negative controls in **both** directions.

#### A.4 — The generalized resolver, PROVEN not to move the guard that already uses it

A generalized YAML branch — block scalars **and** single-line scalars —

```python
m = re.match(r"^-?\s*run:\s*(?:[|>][-+]?\s*)?(.*)$", stripped)
if m:
    if m.group(1).strip():
        inside.add(number)      # single-line `run: cmd …`
    else:
        run_indent = indent     # block scalar `run: |`
```

was applied **in memory only** (module-attribute monkeypatch, one process, **no file on disk
modified**) and the real corpus re-extracted:

```
invocations BEFORE: 5   AFTER: 5   IDENTICAL: True
added: []   removed: []
negative control (single-line run) detected: True
```

The five documented invocations are unchanged element-by-element (`README.md:205/208/211`,
`action.yml:78`, `argus-student-audit.yml:45`). **Reason it does not move:** every single-line `run:`
in the corpus starts with `python`, which is not one of `_CONSOLE_SCRIPTS`. **Verify this yourself
after your edit — it is AC4.1, and it is the assertion that lets you touch a green guard safely.**

Under the generalized resolver, the complete hit-set of expression interpolations inside `run:` bodies
across the whole committed corpus is **eight**:

```
action.yml:68   github.action_path      action.yml:74/78/79/80/126   inputs.*
.github/workflows/argus-student-audit.yml:46   github.sha
.github/workflows/argus-student-audit.yml:66   github.sha   (interpolated into PYTHON source
                                                inside a `python -c "…"` run body)
.github/workflows/release.yml    — ZERO. audit-ci.yml — ZERO.
```

**`release.yml` is the pattern, and it is already written down in this repository.** Its header
comment (lines 39–47) states the rule this story generalises: *"A `${{ }}` expression is expanded by
the runner INTO THE SHELL SOURCE TEXT before bash parses it … (1) every untrusted value is bound
through `env:` and referenced as a quoted shell variable, never interpolated into the script body."*
**Story 9.2 already did this work — on the release workflow only.** Follow that file's shape exactly;
do not invent a second style. → DN-1.

#### A.5 — Compatibility, proven before you write a line: the post-fix invocation still parses

`tests/test_invocation_contract.py::TC-ArgusAgent-DOCS-001-28` extracts `action.yml:78`'s command and
runs it through the **live** argparse parser. After the sweep that line becomes
`argus audit "$REPO_PATH" --commit "$COMMIT_SHA" --report-dir "$REPORT_DIR"`. Executed this session
against the real `parse_failure`:

```
'argus audit "$REPO_PATH" --commit "$COMMIT_SHA" --report-dir "$REPORT_DIR"'        -> None  (parses)
'argus audit "${REPO_PATH}" --commit "${COMMIT_SHA}" --report-dir "${REPORT_DIR}"'  -> None  (parses)
```

Both spellings are absorbed by `_PLACEHOLDER_RE` (`\$[A-Za-z_][A-Za-z0-9_]*` and `\$\{[^}]*\}`). **No
test pins the command TEXT** — the extractor is rule-based and the assertions require only that
`action.yml` still yields an invocation and that it parses. → AC4.

#### A.6 — The three coordinate references that will go stale, and the one that will not

Your `env:` blocks are inserted inside `runs.steps` (which begins at line 58), so **every line from 59
down shifts**. Checked this session:

- `architecture.md:548` and `tests/test_evidence_citation.py:590` both pin the string
  **`action.yml:33-48`** (the `AUDIT_FAILED`-is-not-a-verdict outputs block). Lines 33–48 are **above**
  your edit and **do not move**. `-23` only asserts the *string* is present in `architecture.md` §H; it
  never resolves the coordinate. ✅ **Safe — do not "fix" it.**
- `epics.md`, `sprint-status.yaml` and `deferred-work.md` record `74/78/79/80/126` and `:127`. Those
  are **historical records**; `deferred-work.md` is **append-only** (§3.4), so the corrected
  coordinates go in a **closure note appended at the end**, never by editing the original entry.
  → AC5.1.
- ⛔ `epics.md` and `sprint-status.yaml` **are not yours to edit** (§D).

#### A.7 — Baseline, re-measured this session (LOCAL — see §0.1)

| Figure | Measured 2026-08-12 | How |
|---|---|---|
| Tests collected | **1362** across **85** test files | `pytest --collect-only -q`, summed per-file |
| Failures | **exactly 1** — `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed` | re-run standalone; reproduces identically (§0.4) |
| The three files this story touches or reads | `test_invocation_contract.py` + `test_release_surface_honesty.py` + `test_release_preflight.py` = **33 passed, 0 failed** | run together |
| Python | **3.11.15**, Windows | `python -V` |
| `git ls-files -- argus` | **72** | `git ls-files` |
| dogfood unit 2 | **14900** / 15000 → **100 lines spare** | `build_full_repo_plan('.')` |
| `PyYAML` declared? | **NO** — absent from `dependencies` and `[dev]` | `grep -i yaml pyproject.toml` |
| `mypy` clean on 72 sources; `bandit` 0H/0M/19L; coverage 95.82% | **ATTRIBUTED to Story 11.2's run at this tree**, not re-run here | — |

**File hashes at story time (working tree), so you can prove what you changed:**

```
1b62ac549ed0e01e  136 lines  action.yml
03306b9465c779f6  190 lines  .github/workflows/release.yml
0c4fb15c3973a4c2   86 lines  .github/workflows/argus-student-audit.yml
f159accf72cb5d4f   86 lines  .github/workflows/audit-ci.yml
8e346a5ea326b8f5  640 lines  CHANGELOG.md
f0dad04f9c5f0b84  863 lines  tests/test_invocation_contract.py
673b2c71d54d4b49  399 lines  tests/test_release_surface_honesty.py
```

---

### §B. The shape — proven viable, not mandated

You own the implementation. This is the shape the measurements support; deviate with a recorded reason.

**B.1 — `action.yml`, the install step (`⚡ Install ArgusAgent`):**

```yaml
    - name: ⚡ Install ArgusAgent
      shell: bash
      env:
        ACTION_PATH: ${{ github.action_path }}
      run: |
        python -m pip install --upgrade pip
        pip install "$ACTION_PATH"[languages]
```

**B.2 — `action.yml`, the audit step (`🔍 Execute Argus Audit Engine`), one `env:` block, four entries:**

```yaml
      env:
        REPO_PATH: ${{ inputs.repo-path }}
        COMMIT_SHA: ${{ inputs.commit-sha }}
        REPORT_DIR: ${{ inputs.report-dir }}
        STRICT: ${{ inputs.strict }}
```

…then `mkdir -p "$REPORT_DIR"`, `argus audit "$REPO_PATH" --commit "$COMMIT_SHA" --report-dir
"$REPORT_DIR"`, and `if [ "$STRICT" = "true" ] && [ "$EXIT_CODE" -ne 0 ]; then`. **Every variable
double-quoted, every time.**

**B.3 — the resolver, generalized in place** (`tests/test_invocation_contract.py`) per §A.4, and
**renamed to the public `executable_line_numbers`** so the shared seam is explicit (one internal call
site; the new guard imports it). → DN-2.

**B.4 — the new guard, `tests/test_workflow_input_containment.py`**, stdlib only, corpus resolved by
**glob**, not by a list. See AC2/AC3.

#### B.5 — Regression watchlist: the four things your change passes closest to

| Guard | Why it is close | What proves it |
|---|---|---|
| `test_invocation_contract.py::TC-ArgusAgent-DOCS-001-28` | reads `action.yml:78`'s command through the live parser | §A.5 — both spellings parse. Re-run. |
| `…::TC-ArgusAgent-CLI-001-39` (non-vacuity) | asserts the extractor found something and reached `README.md` **and** `action.yml` | your resolver edit must not empty it |
| `test_release_surface_honesty.py::…-16` | `_NOTE_SECTIONS` closed set **and ORDER**-pinned | your new `###` section must be registered, in the position the file uses |
| `…::-17` over-claim scan | `action.yml` + `CHANGELOG.md` are registered surfaces | your CHANGELOG prose must not affirm external validation |

---

### §C. Design constraints a reviewer will check

**C.1 — The consumer contract is frozen.** Input **names**, **defaults**, **descriptions**; output
**names** and **values**; the exit-code `case` map and its `::error::` strings; `assessed`. All
byte-equivalent in behaviour. Story 9.2 / `DF-8-4-A` wrote that map deliberately and 11.3 has no
mandate over it.

**C.2 — `env:` binds, `"$VAR"` quotes — always both.** GitHub's own guidance: *"the preferred approach
to handling untrusted input is to set the value of the expression to an intermediate environment
variable"*, and *"consider using double quote shell variables to avoid word splitting."* An
`env:`-bound but **unquoted** `$REPORT_DIR` reintroduces word-splitting and glob expansion — a weaker
bug in the same family.

**C.3 — `action.yml:135` (`with: path: ${{ inputs.report-dir }}`) is NOT changed, and that is a
decision.** It is an **action input** to `actions/upload-artifact`, not shell source — the same
distinction `release.yml:84-87` already documents in prose for its `ref:`. A step-level `env:` on the
*audit* step is not in scope for a later step's `with:` anyway. → DN-4.

**C.4 — Do NOT add `set -euo pipefail` to the audit step.** The step deliberately uses `set +e` / `set
-e` around the audit alone so that a non-zero exit is *captured and mapped* rather than aborting.
Adding `-u`/`pipefail` changes the failure semantics of a **shipped consumer contract** for no security
benefit once the values are `env:`-bound.

**C.5 — Stdlib only, no new dependency.** §0.1/3 and DN-5. No `PyYAML`, no `actionlint`, no `zizmor`,
no network. The project is offline-by-default (NFR-S6, no egress) and its guards are pure text/`ast`
walks.

**C.6 — The guard is a CLOSURE, not a list (AI-E10-5).** Where an AC names a set of sites, the test
must **derive** the set and fail on an unenumerated member. `inputs.*` and `github.event.*` are
**forbidden with no exemption possible**; any other context surviving inside a `run:` body must be a
**registered, reason-carrying exemption** — the `_NO_CONVENTION_EXEMPTIONS` shape Story 11.2 just
established. *(Note for the record: `AI-E10-5` asks the Architect to promote this rule into
`architecture.md` §Enforcement; measured this session, **that edit has not landed** — the rule is
applied here as a story-authoring standard, and promoting it is still open.)*

**C.7 — Purity and determinism.** No file writes, no `subprocess`, no clock, no network in the guard.
`mypy` must stay clean; the repo is fully annotated.

---

### §D. ⛔ FENCES — what this story must NOT touch

| Path | Why |
|---|---|
| **`argus/**` — every file** | §0.2. `git ls-files -- argus` must read **72**; exactly four ` M`, no ` A`. |
| `_bmad-output/.../minions-dogfood-*.md` | ⛔ never regenerate a committed artifact to pass a staleness test |
| `_bmad-output/.../epics.md`, `sprint-status.yaml` | records of the plan; the loop writes status, you do not |
| `_bmad-output/.../architecture.md`, `E-PRD/prd.md` | inherited-dirty from 10.5; not yours (`AI-E10-5`'s edit is the Architect's) |
| `tests/test_evidence_citation.py`, `epic-10-retro-2026-08-11.md` | §0.4 — `DF-11-1-A` stays deferred |
| `argus/detectors/vacuous_test.py`, `tests/test_classification_word_boundary.py` | §0.6 — `DF-11-2-A`/`-B` belong to 12.5 |
| `.github/workflows/release.yml`, `audit-ci.yml` | **measured ZERO hits** — they already comply. Do not "tidy" them. |
| `.github/workflows/argus-student-audit.yml` | its two `github.sha` sites are **registered exemptions**, not fixes. DN-6. |
| `README.md`, `pyproject.toml` | measured: README documents **no** `uses:` block for the action; nothing to correct. |
| `_bmad/**`, `bmad-dev-loop-pack/`, `.bmad-drift-audit/`, `_bmad-output/audit-reports/*` | operator / orchestrator / host |
| ⛔ any `git push`, `git tag`, `gh release`, `gh workflow run` | §0.5 |

---

### §E. Traps previous stories already paid for — the five that apply

- **E.1 — RED-FIRST, with the FINAL test code.** Prove each closure fails against the unfixed text
  *before* claiming it passes, and re-demonstrate with the code you actually ship. Where you revert a
  file to demonstrate, **`sha256`-round-trip it** and record both hashes (11.2's §E.1).
- **E.2 — A registry that cannot go red is theatre.** Every exemption entry needs a **negative
  control**: remove it in a synthetic copy and the guard must fail.
- **E.3 — The `-17b` lesson: a filter can swallow what it looks for.** Your run-block resolver *is* a
  filter. §A.3 measured it already swallowing the single-line form. Assert the positive direction with
  a synthetic input, in both YAML shapes.
- **E.4 — `git add` your delta, including this story file** (`AI-E8-1`). Stage; **do not commit** —
  the review gate takes that decision.
- **E.5 — Do not re-baseline a threshold to agree with a corrected count** (11.2's fix iteration). If a
  number disagrees with a guard, re-derive the number by execution; the guard is the last thing you
  change.

---

## Acceptance Criteria

### AC1 — Every action input is data, and no expression survives inside a `run:` body in `action.yml`

1. **All five `${{ inputs.* }}` sites are swept in ONE pass**, located by anchor text and coordinate
   re-verified: `mkdir -p` (`:74`), the `argus audit` positional (`:78`), `--commit` (`:79`),
   `--report-dir` (`:80`), and the `strict` comparison (`:126`).
2. Each is bound through a **step-level `env:`** map on the step that uses it, in the `release.yml`
   shape (DN-1). All five live in one step, so **one `env:` block with four entries**.
3. Each is referenced as a **double-quoted shell variable** — `"$REPO_PATH"`, `"$COMMIT_SHA"`,
   `"$REPORT_DIR"`, `"$STRICT"`. *(Corrected premise, §0.3: only `strict` is **compared**; the other
   three are **passed as arguments**. The binding property is the invariant, not the comparison.)*
4. **The sixth site, `:68` `github.action_path`, is swept too** (DN-3). It is **not** consumer input
   and is **not** the vulnerability; it is converted so the published artifact carries a stronger,
   exemption-free claim.
5. 🔑 **Measured, not asserted:** after the change, the count of `${{ ` occurrences inside any `run:`
   body in `action.yml` is **ZERO**, derived by the AC3 resolver over the committed file.
6. **The consumer contract is unchanged** (§C.1): input names/defaults/descriptions, output
   names/values, the exit-code `case` map, its `::error::` strings, and `assessed` are all
   behaviourally identical. No `set -euo pipefail` (§C.4).

### AC2 — 🔑 The security property is proven as an INVARIANCE, portably, with a positive control

1. A pure **renderer** reproduces the runner's textual substitution — given a `run:` body and a
   `{input-name: value}` map, it replaces every `${{ inputs.<name> }}` (whitespace-tolerant) with the
   value and returns the resulting script text. A test drives it over each `run:` body of the
   **committed** `action.yml` with an **adversarial corpus** — at minimum: the §A.2 shell-breakout
   string, `"; id; #`, `$(id)`, a backtick form, an embedded newline, and the empty string — and
   asserts the rendered text is **byte-identical to the committed text for every value**, because
   after AC1 there is nothing left to substitute. ⚠️ The renderer must be **real** (it must actually
   substitute when a placeholder is present) or the assertion is circular — which is precisely what
   AC2.2 proves.
2. 🔑 **Positive control, mandatory (E.3):** the same assertion is applied to the **pre-fix** line held
   as a **literal string inside the test** (never read back from a file, never from git history) and
   **must FAIL**. A test that cannot demonstrate its own failure mode has not proven anything.
3. ⛔ **Stdlib only. No `bash`, no `subprocess`, no `PyYAML`, no network, no `pytest.skip`** (§0.1/3,
   DN-5). The `bash` demonstration lives in this story document (§A.2), not in the suite.
4. The test carries an id in the existing `TC-ArgusAgent-SECURITY-001-*` namespace, continuing from the
   measured maximum **`-23`** (`tests/test_secret_containment.py`).

### AC3 — 🔑 THE CLOSURE: an interpolation inside a `run:` body fails CI, anywhere in the committed corpus

1. The corpus is resolved by **glob**, never by a hand-written file list, and the glob covers **both
   spellings GitHub accepts**: `action.yml` **and** `action.yaml`, `.github/workflows/*.yml` **and**
   `*.yaml`. *(Measured: the existing `_WORKFLOW_GLOB` is `*.yml` only — a workflow committed as
   `foo.yaml` would escape it silently. Today the corpus is 4 files; a workflow added tomorrow is
   covered the day it is committed.)* A **non-vacuity assertion is mandatory**: the resolved corpus
   must be non-empty **and** must contain `action.yml`, or every assertion below is vacuous.
2. 🔑 **The run-block resolver recognises BOTH shapes**: block scalars (`run: |`, `run: >`) **and
   single-line** (`run: cmd …`). §A.3 measured the existing resolver returning an **empty** set for the
   single-line form; a guard that inherits that blindness is vacuous against the cheapest
   reintroduction path.
3. **ONE mechanism, not two** (AR7 / architecture §3.3): the resolver is the **single** definition in
   `tests/test_invocation_contract.py`, generalized in place, and the new guard **imports** it — the
   same import-from-the-single-declaration shape Story 11.2 used. A test asserts there is exactly one
   definition and that the guard uses it (no local re-implementation).
4. **`inputs.*` and `github.event.*` are FORBIDDEN outright — no exemption is possible.** (GitHub
   documents `github.event.*` as the untrusted-input surface: `…body`, `…title`, `…head_ref`, `…label`,
   `…message`, `…name`, `…ref`, and friends.) The guard therefore protects the **future**, not only
   today's five sites.
5. **Every other surviving context is a registered, reason-carrying exemption** (§C.6). After AC1 the
   registry contains **exactly two** entries, both in `.github/workflows/argus-student-audit.yml`
   (`:46` and `:66`, both `github.sha`), each with a written reason (DN-6). An unregistered survivor
   **fails**; a registered exemption that no longer exists **also fails** — both directions.
6. 🔑 **Negative controls, three shapes:** a synthetic single-line `- run: echo "${{ inputs.evil }}"`,
   a synthetic block-scalar equivalent, and a **line-wrapped** `${{` whose context name sits on the
   *next* line must **each** drive the guard **RED**. A synthetic clean corpus must drive it
   **GREEN**. Real files are never mutated to produce these.
7. **Detection is over the JOINED run-body text, not per-line.** A `${{ … }}` expression may be
   wrapped across lines inside a block scalar, so a naive per-line regex requiring the context name on
   the same line as `${{` is escapable. Attribute each hit to the line carrying its `${{` and
   **report `file:line`** in the failure message, so a future violation is navigable rather than a
   bare boolean.

### AC4 — The two guards that already read this corpus stay green, and are proven still non-vacuous

1. 🔑 **Re-measured, not assumed:** after the resolver edit, `extract_documented_invocations()` returns
   the **same five** invocations, element-by-element (§A.4 proved this in memory; prove it again
   against the file you actually wrote).
2. `tests/test_invocation_contract.py` passes in full, including
   `TC-ArgusAgent-DOCS-001-28` (`action.yml:78`'s rewritten command still parses through the live
   parser — §A.5) and `TC-ArgusAgent-CLI-001-39/-40`'s non-vacuity and positive controls.
3. `tests/test_release_surface_honesty.py` passes in full, including the `_NOTE_SECTIONS` closed-set
   **and ORDER** assertion and the `-17` over-claim scan over `action.yml` and `CHANGELOG.md`.
4. **No existing assertion is weakened, deleted or re-baselined** to accommodate this story (E.5).

### AC5 — The corrected record, the release note, and the registrations

1. **`deferred-work.md` gains an APPEND-ONLY closure note for `DF-9-2-D`** which records, because the
   original entry cannot be edited (§3.4): (a) the real count is **FIVE**, not one; (b) the ledger's
   `action.yml:127` is **off by one** — the site is `:126`; (c) the **sixth** in-`run:` site `:68`
   (`github.action_path`) that no document named, and the ruling on it; (d) `:135` (`with: path:`) is
   **not** a shell site and was deliberately not changed; (e) the exploit was **demonstrated**, and by
   what method. Append-only verified **programmatically** (`after.startswith(before)`, `+n/-0`).
2. `CHANGELOG.md` gains one `### …` section under `## Unreleased`, registered in
   `tests/test_release_surface_honesty.py::_NOTE_SECTIONS` with its **placement decided and its reason
   written** as that registry's own comment demands. **Ruled: register it THIRD**, after 11.1's
   disclosure and 11.2's classification fix — reason in DN-7. Do not move an existing section.
3. The note states the change **honestly and narrowly**: it hardens the composite action; it makes
   **no** claim that the action has been exercised in CI, and **no** assurance claim about Argus. It
   must survive the `-17` over-claim scan.
4. The note names the consumer-visible truth: **no input name, default or output changed**; a workflow
   already using the action needs **no edit**.

### AC6 — Fences, budget, gates, and the one permitted red

1. ⛔ **`git ls-files -- argus` reads exactly `72`** after you stage; `git status --porcelain --
   argus/` shows exactly the **four ` M`** lines listed in the frontmatter and **no ` A`** line.
   Re-measure **after** `git add`, not before. **HALT** if it moves (§0.2).
2. ⛔ **`build_full_repo_plan('.')` re-run after staging:** unit 2 = **14900** (0 of 100 consumed) and
   all three `partition_id`s byte-unchanged (`477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…`).
   **HALT** if any moves. ⛔ **Never regenerate a dogfood artifact** to make a staleness test pass.
3. **Full suite:** `1362` collected + **exactly N new** (state N), `0` skipped, and **exactly ONE**
   failure — `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`,
   carved out **BY NODE ID** as `DF-11-1-A` (§0.4: not closed, not touched). ⛔ **A second red is
   yours.** Report via `--junit-xml`, not by reading the terminal tail.
4. `mypy` clean on **72** source files (the count must not move); `bandit` **0 High / 0 Medium**;
   coverage **≥ 80** and not below the **95.82%** baseline.
5. `argus audit .` re-run and compared **field by field** against the 11.2 baseline —
   `verdict=RELEASE_READY`, `blocking_findings=0`, `assessed_deep_ratio=61/77`, `scope=application`,
   `exit 0`. `deep_ratio`/`held_out` may move by **exactly +1 each** per new test file; any other
   movement must be **arithmetically explained** or it is a defect.
6. **Every figure is labelled LOCAL** (Windows / CPython 3.11.15); CI evidence is cited as an
   `audit-ci.yml` run id **plus the sha it covers**, or recorded **`NOT ESTABLISHED`** with the command
   a human runs (§0.1). ⛔ **Nothing is pushed, tagged, released or dispatched** (§0.5) — state that
   explicitly.
7. **The write set is exactly §F.** Any deviation is **recorded, not hidden** (11.2 recorded one; that
   is the standard).

---

### §F. Write set — exactly this, nothing else

| File | Change | Fence |
|---|---|---|
| `action.yml` | ` M` — two `env:` blocks; six interpolations removed from `run:` bodies | contract frozen (§C.1) |
| `tests/test_invocation_contract.py` | ` M` — resolver generalized + renamed public (DN-2) | invocation set must not move (AC4.1) |
| `tests/test_workflow_input_containment.py` | ` A` **NEW** — the AC2/AC3 guard | `tests/`, **not** `argus/` |
| `CHANGELOG.md` | ` M` — one `### …` section under `## Unreleased` | over-claim scan (AC5.3) |
| `tests/test_release_surface_honesty.py` | ` M` — one `_NOTE_SECTIONS` entry, placed third (DN-7) | order assertion |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | ` M` — **append-only** `DF-9-2-D` closure note | `after.startswith(before)` |
| **this story file** | ` A` — `git add` it (E.4 / `AI-E8-1`) | — |

**Not in the write set, deliberately:** anything under `argus/`; `.github/workflows/**` (measured
compliant or exempt); `README.md`; `pyproject.toml`; `architecture.md`; `epics.md`;
`E-PRD/prd.md`; `tests/test_evidence_citation.py`. `sprint-status.yaml` is written by the loop.

---

## Tasks / Subtasks

- [x] **T1 — Re-measure the premises before writing anything (AC1.1, §0.3)**
  - [x] Re-derive the interpolation hit-set over `action.yml` and confirm `74/78/79/80/126` + `:68`
  - [x] Confirm `git ls-files -- argus` = 72 and unit 2 = 14900 **before** you start
  - [x] Re-run the `DF-11-1-A` node id and confirm it is the only inherited red
- [x] **T2 — RED FIRST: write the AC2/AC3 guard against the UNFIXED tree (AC2, AC3, E.1)**
  - [x] Generalize + rename the resolver; prove the invocation set is unchanged (AC4.1)
  - [x] Assert the guard fails naming **all six** in-`run:` sites in `action.yml`
  - [x] Prove both negative controls (single-line **and** block scalar) and the clean-corpus green
  - [x] Prove AC2's positive control fails on the pre-fix literal
- [x] **T3 — Sweep `action.yml` in one pass (AC1)**
  - [x] Two `env:` blocks; every reference double-quoted; contract byte-frozen (§C.1, §C.4)
  - [x] `:135` deliberately unchanged (§C.3 / DN-4)
- [x] **T4 — Turn the guard green and re-prove non-vacuity with the FINAL test code (E.1)**
  - [x] Registry now holds exactly the two `argus-student-audit.yml` exemptions, both directions tested
- [x] **T5 — Records: `DF-9-2-D` closure note (append-only), CHANGELOG section, `_NOTE_SECTIONS` (AC5)**
- [x] **T6 — Gates and fences (AC6)**
  - [x] `--junit-xml` suite run; carve out `DF-11-1-A` by node id; state N new tests
  - [x] `mypy` / `bandit` / coverage; `argus audit .` field-by-field
  - [x] ⛔ **After `git add`:** re-run `git ls-files -- argus` and `build_full_repo_plan('.')`. HALT on any move.
  - [x] Label everything LOCAL; record CI evidence as `NOT ESTABLISHED`; confirm nothing published
- [x] **T7 — Stage the delta including this story file (E.4). Do NOT commit** — the review gate decides.

### Review Follow-ups (AI) — fix iteration 1, 2026-08-12

- [x] **[AI-Review][High] The run-block resolver is vacuous against a commented block-scalar header**
  (`tests/test_invocation_contract.py:485,531-536`; violates AC3.2 + AC3's closure mandate §C.6)
  - [x] Reproduce the reviewer's exact `action.yml`-shaped synthetic and confirm `interpolations()`
        returns `()` **before** changing anything — and sweep the neighbourhood rather than the one
        shape: **9** header spellings measured vacuous, not 1
  - [x] Fix the resolver **in place** (no fork, AR7/§3.3) by keying on the PRESENCE of the `|`/`>`
        block indicator: handles `|`, `>`, `|-`, `|+`, `>-`, `>+`, digit indentation indicators and
        both indicator orders, with or without a trailing comment; plus bare `run: # …` and a
        single-line scalar continued across lines
  - [x] Prove the new controls **RED against the pre-fix resolver with the FINAL test code**, with a
        `sha256` round-trip on the reverted file (E.1)
  - [x] Add the fourth..seventh negative-control shapes to `-29`, and add `-32` as a closure over the
        GENERATED YAML block-header grammar (108 spellings) rather than a longer list
  - [x] Re-confirm the documented-invocation set is element-identical **5 → 5** and that no existing
        assertion was weakened (AC4.1, AC4.4, E.5)
  - [x] Re-run every gate and fence; append the correction to `deferred-work.md` (append-only)

### Review Findings (code-review, iteration 1, 2026-08-12)

**Independently re-verified and CONFIRMED correct, on disk, this session** (not re-transcribed from
the story): `action.yml`'s staged diff is coherent — a single clean patch, no duplicated or orphaned
fragments from the interrupted/resumed dev session; current `action.yml` is 160 lines,
`sha256=45341dbc3a289f0f5c09ba404af9826be4aaf94c1f4cabbb303e03b99173dd3c`, byte-identical to the
dev's own D4/File-List figure, and `git diff -- action.yml` (working tree vs index) is empty, so
nothing is left half-applied. All six `${{ }}` sites (`:74/:78/:79/:80/:126/:68` pre-fix) are gone
from `run:` bodies; `:135`→now `:159` `with: path: ${{ inputs.report-dir }}` is unchanged and pinned
by `-25`. The `env:` + `"$VAR"`-quoting closure is genuinely closed, not relocated: because bash's
plain `"$VAR"` parameter expansion does not re-scan its own substituted value for further shell syntax
(unlike `eval`), none of `` `id` ``, `$(id)`, `; id; #`, embedded newlines, or the exact §A.2
shell-breakout string can execute through any of the six sites — verified by re-deriving the
adversarial corpus assertions in `-27`/`-28` directly. `executable_line_numbers` is a true rename, not
a fork (`grep` confirms exactly one definition, no `_executable_line_numbers` survives, one caller
updated, the guard imports it) and `extract_documented_invocations()` independently re-run in this
review returns the same 5 invocations element-for-element, with the `action.yml` member correctly
moved to `:102`. `TC-ArgusAgent-DOCS-001-28`, `-39`, `-40` still pass. Full suite independently re-run
with `--junit-xml`: **1370 tests, 1 failure, 0 errors, 0 skipped** — the single failure is exactly
`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
(`DF-11-1-A`), confirmed by parsing the junit XML, not by eye. `mypy argus` → clean, 72 files.
`bandit -r argus` → 0 High / 0 Medium / 19 Low, matching the 11.2 baseline exactly. `argus audit .`
independently re-run: `verdict=RELEASE_READY blocking_findings=0 assessed_deep_ratio=61/77
scope=application deep_ratio=61/167 held_out=90`, exit 0 — matches the dev's D7 table exactly, the
+1/+1 movement arithmetically explained by the one new test file. Fences independently re-measured
after `git add`: `git ls-files -- argus` = 72, `git status --porcelain -- argus/` = exactly the four
` M` lines claimed, `build_full_repo_plan('.')` re-run gives unit 2 = 14900 and all three
`partition_id`s byte-identical to the ones quoted in §0.2/§A.7. `git log origin/master..HEAD` = 6
commits, `git tag -l` empty, `HEAD` = `93adc94` — nothing pushed, tagged or dispatched. `-31`'s
AC1.6-freeze scope addition is judged **legitimate, not scope creep**: it adds no file, is disclosed
in the Completion Notes as a deviation with a stated reason, and is severable. `-16`/`-17`'s
extensions to `_NOTE_SECTIONS`/`_RELEASE_SURFACES` for the Security section are a straightforward,
correctly-ordered registration, not an assertion being bent — the closed-set/order machinery itself is
untouched. `argusdemo/demo.sh`: read in full; it is exactly the SM's stdlib+`subprocess`+`bash` §A.2
demonstration, matches the story's description, is **not** collected by pytest (`testpaths =
["tests"]`), is **not** reached by any corpus glob in `test_workflow_input_containment.py`,
`test_release_surface_honesty.py` or `test_evidence_citation.py` (all scoped to specific dirs/globs,
none of which is the repo root for arbitrary files), and is outside `argus/` so the dogfood
partitioner never sees it. **It does not currently break anything** and is not, by itself, the same
mechanism as `DF-11-1-A` (that guard's glob is scoped to the artifact directory, not the repo root) —
but it is the same *shape* of risk (an untracked root-level artifact nobody has fenced), and it should
be resolved (git-ignored, moved under a story's own write set, or deleted) before Epic 11 closes, not
carried into 12.x by default.

**FINDING — the closure's run-block resolver is genuinely vacuous against a natural YAML variant
neither of the shipped negative controls exercises: a block-scalar `run:` header with a trailing
comment.** [High] `tests/test_invocation_contract.py:485,531-536` (`_RUN_HEADER_RE` /
`executable_line_numbers`) — violates AC3.2 ("the run-block resolver recognises BOTH shapes") and
AC3's own "closure, not list" principle (§C.6, AI-E10-5), and reproduces exactly the class of bug the
story itself calls out as "the `-17b` lesson: a filter can swallow what it looks for" (trap E.3),
this time in a shape the shipped tests (`-29`'s three controls: single-line, block-scalar-no-comment,
line-wrapped) do not cover. **Reproduced independently this session**, action.yml-shaped:

```python
from tests.test_workflow_input_containment import interpolations
doc = ('runs:\n  using: composite\n  steps:\n'
       '    - name: x\n      shell: bash\n'
       '      run: | # scrub inputs before use\n'
       '        echo "${{ inputs.strict }}"\n')
interpolations('action.yml', doc)   # -> ()  EMPTY — the injection is UNDETECTED
```

Root cause: `_RUN_HEADER_RE = re.compile(r"^-?\s*run:\s*(?:[|>][-+]?\s*)?(.*)$")` captures the trailing
comment text into group 1; `executable_line_numbers` then tests `header.group(1).strip()` and, finding
it non-empty (`"# scrub inputs before use"`), classifies the line as **single-line `run: cmd`** and
adds only that one line to `inside` — it never sets `run_indent`, so the indented block-scalar body
that follows (which is where the real script, and the injection, lives) is never scanned at all. This
is not a contrived adversarial trick: appending a comment to a `run: |` header is ordinary, unremarkable
YAML/CI style, so a future contributor could silently reopen `DF-9-2-D` — in `action.yml` or any
workflow in the corpus — and this guard, plus `test_invocation_contract.py`'s own invocation extractor,
would both stay fully green. **This is the exact non-vacuousness failure mode item 3 of this review's
brief asked to be ruled out, and it is not ruled out.** `action.yml` itself does not currently use this
shape, so today's six sites are genuinely closed (see the confirmation above) — but AC3's mandate is to
protect the *next* one, and this shape defeats it.

Suggested fix: before deciding whether `header.group(1)` is "the single-line command" vs "empty (block
scalar)", strip a well-formed trailing YAML comment (an unquoted `#` preceded by whitespace or start-
of-remainder) from it — e.g. split on `(?:^|\s)#` outside of quotes, or simply treat `[|>][-+]?\s*#.*$`
as equivalent to the block-scalar empty case. Add a fourth shape to
`test_TC_ArgusAgent_SECURITY_001_29_negative_controls_in_three_shapes_and_a_clean_corpus` (rename to
reflect four shapes, or add a `-32`) exercising `run: | # comment` with an `inputs.*` interpolation in
the body, asserting it drives the guard RED — mirroring the very discipline (E.2/E.3, "prove the
positive direction with a synthetic input") this story otherwise applies rigorously to the other three
shapes.

**Verdict: FAIL.** The six documented sites are genuinely fixed and the `env:`/quoting closure for
them is real, not relocated — this is not a partial fix in the sense item 1 asked about. But the
committed guard that is supposed to make the class un-reintroducible is demonstrably not a closure: a
plausible, non-adversarial YAML edit defeats it silently. Given this story's own stated charter
("closure over enumeration," AI-E10-5, and the explicit E.3 trap it names), shipping this guard as the
permanent defense is the same mistake the story set out to avoid, just one shape further out. Fix the
resolver, add the fourth negative control, re-run the full ledger (§0.4's carve-out and the fence
re-measurements are cheap re-checks, not new risk) and resubmit.

### Review Findings (code-review, iteration 2, 2026-08-12) — FOCUSED CONFIRMATION

**Scope, stated so nothing already-adjudicated is re-litigated.** This is a narrow confirmation of
fix iteration 1's repair to `_RUN_HEADER_RE` / `executable_line_numbers`, plus a check that it broke
nothing. The six sites, the `env:`+quoting closure, the AR7 no-fork property, the documented-invocation
set, both corpus-glob fences, and the resumed-session diff coherence were all independently verified
correct in iteration 1's review and are **not re-derived here**.

**1. The fix is GENERAL, not a wider enumeration — verified with the reviewer's OWN adversarial
spellings, not the dev's 108.** Constructed independently and run against the live
`executable_line_numbers`: `run: |0`, `run: |9-`, `run: |-9#c` (digit outside the dev's tested
1–3 range), `run: |#nospace`, `run: >-#c` (comment glued to the indicator, no space), CRLF line
endings (`\r\n` throughout a synthetic `action.yml`-shaped document), a header with only a trailing
tab before whitespace (`run: |  \t `), and a **single-line** command whose value contains a literal
`#` **inside a double-quoted string** (`run: echo "value # not-a-comment ${{ inputs.strict }}"` —
confirms the quoted `#` does not get misread as a YAML comment and the interpolation on that same
line is still caught). **Every one classified correctly** — body scanned and the `inputs.*` hit
detected and attributed to the right line for every block-header case; the single-line-with-quoted-
`#` case correctly flagged on its own line. No blind spelling found. The regex's `[0-9+\-]*`
character class is confirmed to be genuinely order- and count-agnostic (not a re-enumeration of the
orders the dev happened to generate), and the classification keys on `block is not None`, never on
the content of `rest` — the property claimed.
**2. RED-first proof, independently reproduced.** Reconstructed the reviewed pre-fix
`_RUN_HEADER_RE`/`executable_line_numbers` **in memory** (module-attribute monkeypatch in both
`tests.test_invocation_contract` and `tests.test_workflow_input_containment`, no file touched) and
ran the FINAL `-29`/`-32` test bodies against it directly: `-29` failed on the first commented-block
shape it hit; `-32` failed with **"THE GUARD IS BLIND TO 102 OF 108 LEGAL `run:` BLOCK HEADERS"** —
the exact count and message claimed. `sha256` of the current (post-fix) `tests/test_invocation_contract.py`
on disk was independently computed: `55b3efa15c18ea09a6c0a89b8ea7eb1260fa533eab448d60171bf6456a0d0974`
— byte-identical to the claimed FIXED/RESTORED hash, confirming the file is genuinely back to the
shipped state and the round-trip demonstration was real (not merely asserted).
**3. No fork, no weakening — confirmed.** `grep` for `def executable_line_numbers(` /
`def _executable_line_numbers(` across `tests/` shows exactly one definition, in
`test_invocation_contract.py`; the guard file contains no re-implementation and imports it. Re-ran
`extract_documented_invocations()` directly: still the same 5 invocations element-for-element,
`action.yml` member at `:102`. `git ls-files -- argus` = 72; `git status --porcelain -- argus/` =
the same four ` M` lines, zero ` A`. `action.yml`, the three workflows and `README.md` re-scanned:
zero executable-line-count movement anywhere in the corpus.
**4. Continuation-absorption behaviour — verified correct, no over-absorption.** Built a synthetic
`- run: echo "${{` folded across a line boundary, followed by a **sibling `env:` key at the SAME
indent as `run:`**: the guard correctly stops absorbing at the line carrying the closing `}}` and
does **not** pull the sibling `env:`/its body into the executable set — confirmed by direct call,
result `{6, 7}` only, line 8 (`env:`) and line 9 (`SAFE: value`) excluded.
**5. Test ledger — independently re-run, not transcribed.** Ran the full suite with
`--junit-xml` this session: **`tests="1371" failures="1" errors="0" skipped="0"`**, the one
`<failure>` element attributed to `tests.test_evidence_citation::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
— exactly `DF-11-1-A`, exactly one, no second red. Independently confirmed 1371 by summing this
repo's own per-file `--collect-only` report across 86 files. `mypy argus` → clean, 72 files.
`bandit -r argus --exit-zero` → 0 High / 0 Medium / 19 Low by severity, matching claim exactly.
`argus audit .` re-run: `verdict=RELEASE_READY blocking_findings=0 assessed_deep_ratio=61/77
deep_ratio=61/167 held_out=90`, exit 0 — field-identical.
**6. Fences re-measured after `git add`.** `git ls-files -- argus` = 72 with zero ` A` (confirmed
above). `build_full_repo_plan('.')` re-run: unit 2 = 14900/15000 (0 of 100 consumed since last
measurement), all three `partition_id`s (`477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…`)
byte-unchanged. `deferred-work.md`'s Story-11.3 paragraph (g) is a pure append: lines 2435–2465
(31 content lines + 1 leading blank = 32) sit after the file's prior end-of-content with no edit to
anything above — `+32/-0`, confirmed by inspection of the diff boundary. `HEAD` = `93adc94d0203aeaf`,
`git tag -l` empty, `git log origin/master..HEAD` = 6 — nothing pushed, tagged, released or
dispatched.
**7. `sprint-status.yaml`** parses clean (re-read directly); the `STATUS DEFINITIONS` block and all
prior comment history are intact and unedited above the `11-3` entry being updated.

**No High or Medium finding survives.** No unresolved `decision-needed` or `patch` item remains.
`argusdemo/demo.sh` is unchanged from iteration 1's assessment (breaks nothing; operator is holding
it for the epic checkpoint) — not re-litigated, not actioned here.

**Verdict: PASS.** The single High finding from iteration 1 is resolved correctly and generally —
independently re-derived adversarial spellings outside the dev's own generated set all classify
correctly, the RED-first proof reproduces exactly, no fork or weakening was introduced, the
continuation-absorption addition does not over-absorb into sibling keys, and every gate/fence figure
re-measures to the claimed value. Status → `done`.

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

- **DN-1 — `release.yml` is the pattern; there is no second style.** Its header (lines 39–47) already
  states the rule and its steps already implement it (`env:` + `"$TAG"`, zero hits measured). AR7 /
  architecture §3.3 forbid a second mechanism where one exists. Matching an in-repo precedent also
  makes the diff reviewable by inspection.
- **DN-2 — The run-block resolver stays in `tests/test_invocation_contract.py`, generalized in place
  and renamed to the public `executable_line_numbers`; the new guard IMPORTS it.** Rejected: a second
  private copy in the new file (AR7 breach, and §A.3's blindness would then exist in two places);
  rejected: moving it to a new `tests/` helper module (churn on a security story, and Story 11.2's
  precedent is explicitly *import from the single declaration*). The rename is one internal call site
  and makes the shared seam explicit rather than reaching through a private name.
- **DN-3 — `:68` `github.action_path` IS swept, though it is not the vulnerability.** It is
  runner-provided and not consumer-settable, so it is not `DF-9-2-D`. It is converted anyway because
  it costs three lines and buys a materially stronger claim on the **published** artifact: *zero*
  interpolations inside any `run:` body in `action.yml`, with **no exemption registry entry on the
  file a consumer executes**. Behaviour is identical — `pip install "$ACTION_PATH"[languages]` and
  `pip install "${{ github.action_path }}"[languages]` differ only in when the text is produced.
- **DN-4 — `:135` `with: path: ${{ inputs.report-dir }}` is NOT changed.** It is an action input to
  `actions/upload-artifact`, not shell source — the identical distinction `release.yml:84-87` already
  documents in prose for its `ref:`. A step-level `env:` cannot reach a later step's `with:` anyway,
  and routing it through a step output would add machinery to fix a non-bug.
- **DN-5 — Stdlib only; `PyYAML` is forbidden.** Measured: `PyYAML` is **absent** from
  `pyproject.toml`'s `dependencies` and `[dev]` extra, and present in this venv only transitively via
  `bandit`/`markdown-it-py`. A guard that `import yaml` passes locally and is a coin-toss in CI. Text
  analysis is also the *right* model here: `${{ }}` substitution is a **textual** operation on the
  script string, and a text scan can report a line number a consumer can navigate to.
- **DN-6 — `argus-student-audit.yml:46` and `:66` are REGISTERED EXEMPTIONS, not fixes.** Both are
  `${{ github.sha }}`: runner-provided, `^[0-9a-f]{40}$`, not attacker-settable. `:66` is the more
  interesting one — it interpolates into **Python** source inside a `python -c "…"` body — and its
  reason must say so. Each entry states *why the context is trusted*, and AC3.4 means that the day
  that file gains a `workflow_dispatch` input or reads `github.event.*`, the guard catches it with no
  registry edit.
- **DN-7 — The CHANGELOG section is registered THIRD, and no existing section moves.** Rejected:
  promoting it above 11.2's on urgency grounds. Reason: the registry's stated principle is *what a
  consumer of THIS release hits first*, and the dominant install path for this release is the
  index/VCS channel — a CLI/library consumer is **unaffected** by the action fix, whereas 11.2's
  classification change can move **any** consumer's verdict. The action fix binds only the marketplace
  channel, which per `epics.md` Story 11.3 AC3 is **hard-gated on this story and ships later** (12.9).
  Reordering an already-reviewed entry would also add avoidable churn to a security story.
- **DN-8 — `DF-11-1-A` stays deferred and is carved out by node id.** Full reasoning in §0.4.
- **DN-9 — `DF-11-2-A` / `DF-11-2-B` are NOT absorbed.** Full reasoning in §0.6; the ledger already
  targets them at **12.5**.
- **DN-10 — This story publishes nothing.** §0.5. It delivers the marketplace **precondition**; 12.9
  decides whether to exercise it.

### Architecture patterns & constraints a reviewer will check

- **AR7 / §3.3 — extend, never duplicate.** Applied at DN-2 (the resolver) and DN-1 (the `env:` shape).
- **Closure over enumeration (`AI-E10-5`).** Applied at AC3. *(Its promotion into `architecture.md`
  §Enforcement is measured **not yet landed** and remains the Architect's open item.)*
- **§H evidence citation (Story 10.1)**, enforced by `tests/test_evidence_citation.py`: every status
  figure cites an executed gate or is `NOT ESTABLISHED`. Applied at AC6.6.
- **NFR-S1/S3 containment.** A workflow log is a publication surface; nothing new is echoed. The fix
  strictly *reduces* what reaches a log, since values now arrive as environment variables rather than
  as script text.
- **NFR-S6 / offline by default.** No network in any guard.
- **Invocation-contract enforcement** (`architecture.md` §Enforcement, Story 10.3): the corpus
  `README.md` + `action.yml` + `.github/workflows/*.yml` must keep parsing through the **live** parser.
  Applied at AC4.

### Testing standards — the house form your new file matches

- One `TC-ArgusAgent-<AREA>-NNN-NN` id per test, in the docstring's first line, with the story/AC it
  serves. Continue **`SECURITY-001`** from the measured maximum `-23`; cross-file continuation of a
  namespace is established house style (`DOCS-001` already spans three files).
- Registries are module-level, `Final`-typed tuples with a **written reason per entry**.
- Every closure carries a **non-vacuity / positive control** (E.2, E.3).
- Fully type-annotated; `mypy` clean. Pure functions; no I/O beyond `read_text`.
- Paths resolved from a module-level repo root, never relative to the CWD.

### Previous story intelligence (11.1, 11.2, 10.3, 10.4, 9.2)

- **9.2** wrote `release.yml`'s injection discipline and **filed `DF-9-2-D` rather than widening** —
  correct scoping then, and the reason this story exists now.
- **10.3** built `tests/test_invocation_contract.py`, including the resolver you are generalizing, and
  established *derive the corpus by rule, never by a fixed list*.
- **10.4** was **halted mid-implementation** by staging a new `argus/**` file — the origin of the
  `DF-10-4-D` fence. It also refused to regenerate an artifact to go green; do the same.
- **11.1** shipped FR34 inside existing files, measured its budget rather than assuming it, and left a
  Low review finding that became the *carve the red out by node id* rule you inherit.
- **11.2** re-measured a count the planning documents got wrong **four times**, fixed it, and then had
  its own completion note corrected in review for asserting a number it never measured (`60` vs `32`).
  **Every number you write must come from an execution you ran in this session.**

### Runtime & toolchain, verified on this machine 2026-08-12

CPython **3.11.15**, Windows. `pytest` 9.1.1 (`--junit-xml` available). `mypy` clean on 72 sources
(attributed, 11.2). `tree-sitter` pinned `>=0.25.0,<0.26` (load-bearing — Story 11.4's subject, not
yours). `PyYAML` present in the venv but **not declared** (DN-5).

### Latest external technical facts (checked 2026-08-12, GitHub Docs)

- **The mechanism, verbatim:** *"Before the shell script is run, the expressions inside `${{ }}` are
  evaluated and then substituted with the resulting values, which can make it vulnerable to shell
  command injection."*
- **The recommended mitigation, verbatim:** *"the preferred approach to handling untrusted input is to
  set the value of the expression to an intermediate environment variable"*, plus *"consider using
  double quote shell variables to avoid word splitting."*
- **`runs.steps[*].env` IS supported in composite actions**, confirmed against the metadata-syntax
  reference: *"Sets a `map` of environment variables for only that step."* (`runs.steps[*].shell` is
  required when `run` is set — it already is, `shell: bash`.) **The fix is deliverable as specified.**
- Untrusted `github` context members documented as attacker-influenced end in `body`, `default_branch`,
  `email`, `head_ref`, `label`, `message`, `name`, `page_name`, `ref`, `title` — the basis for AC3.4's
  outright ban on `github.event.*` inside a `run:` body.

### Project structure notes

The write set spans `action.yml` (repo root), `tests/`, `CHANGELOG.md` and the planning ledger. **No
package layout change, no new module, no new dependency, no `argus/` byte.** The new test file sits
beside its siblings in `tests/` and is picked up by `pyproject.toml`'s `testpaths = ["tests"]`.

### Open questions for the operator — saved for the end, as the workflow requires

1. **`DF-11-1-A` is now standing red across three consecutive stories** (11.1, 11.2, 11.3). It is a
   two-minute operator step (register `epic-10-retro-2026-08-11.md` in `_STATUS_DOCUMENTS` **and** give
   it its §H citation or a `NOT ESTABLISHED` marker). Every additional story it survives degrades the
   loop's ability to attribute a regression. **Owner: XAgent007.**
2. **`DF-11-2-A` / `DF-11-2-B` are confirmed OUT of 11.3** and remain filed against **12.5** with
   `owner: Delivery Orchestrator`. Recorded here so the ruling is visible rather than silent (§0.6).
3. **`AI-E10-5`'s architecture edit has not landed** — the closure-over-enumeration rule is still only a
   story-authoring convention applied by the SM. **Owner: Architect.**
4. **`AI-E10-1` remains the load-bearing gap, and this story is its sharpest instance:** the artifact
   hardened here executes **only** in GitHub Actions, and no CI run has ever executed it. A single push
   plus one `audit-ci.yml` run would convert this whole epic's evidence from LOCAL to cited.
5. **The composite action is documented nowhere a consumer reads** — measured: `README.md` contains **no**
   `uses:` block for it. Before the marketplace channel ships (12.9), a consumer's only documentation is
   `action.yml` itself. Not filed as a defect here; flagged as a 12.8/12.9 input.

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 11.3` — the five sites, the guard, the marketplace precondition]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Epic 11` — charter; *no story in this epic publishes anything*]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md#DF-9-2-D` — original entry, close condition, and the `:127` coordinate corrected in §A.1]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md#DF-11-1-A` / `#DF-11-2-A` / `#DF-11-2-B` — the three items deliberately not absorbed]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#Product Scope V1.5` — *"GitHub Marketplace … In scope, gated on the `action.yml` input-interpolation fix"*]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#NFR-S1` — containment; a workflow log is a publication surface]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#Enforcement` — invocation-contract enforcement, the corpus, and the non-vacuity requirement]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#H. Self-Audit & CI` — the evidence-citation rule and the `action.yml:33-48` anchor that must NOT move]
- [Source: `.github/workflows/release.yml:39-47` — the in-repo statement of the rule this story generalizes]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/11-2-polyglot-repository-is-classified-correctly.md` — §0.2 fence, §0.4 carve-out, closure-over-enumeration and exemption-registry precedent]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml#action_items` — AI-E10-1, AI-E10-2, AI-E10-3, AI-E10-5, AI-E10-7]
- [Source: GitHub Docs — *Script injections* and *Secure use reference* (checked 2026-08-12): expression substitution precedes shell parsing; intermediate environment variable is the preferred mitigation]
- [Source: GitHub Docs — *Metadata syntax* (checked 2026-08-12): `runs.steps[*].env` is supported for composite actions]

---

## Dev Agent Record

### Context Reference

Story file §0–§F, read in full before any edit. No planning artifact was re-opened for authority;
every number below comes from a command executed in THIS session on THIS tree.

### Agent Model Used

`claude-opus-5[1m]` (BMAD `dev-story`, mode `implement`, first round — no prior review findings).

`claude-opus-5[1m]` (BMAD `dev-story`, mode `fix`, **iteration 1** — addressing the single [High]
finding recorded above under "Review Findings". The fix session is stateless: the finding was read
from THIS file on disk, not carried in context, and every figure below comes from a command executed
in the fix session on this tree.)

### Debug Log References

**⚠️ EVERY FIGURE BELOW IS LOCAL — Windows, CPython 3.11.15, `pytest` 9.1.1. CI evidence:
`NOT ESTABLISHED`.** No `audit-ci.yml` run has ever executed any Epic 10 or Epic 11 sha. See
"The irony this story does not get to resolve" below — it is sharpest here of any story so far.

**D1 — T1, premises re-derived before a line was written.** `HEAD` = `93adc94`, `git tag -l`
**empty**, `git status --porcelain -- argus/` = exactly **four ` M`** lines, `git ls-files -- argus`
= **72**. `action.yml` **136 lines**, `sha256` `1b62ac549ed0e01e…` — matching §A.7 exactly. Every
`${{ … }}` occurrence enumerated by regex: `16, 42, 49, 54, 68, 74, 78, 79, 80, 126, 135`. **The
epic's five coordinates held exactly** and the sixth (`:68`) and the non-shell `:135` are where §A.1
measured them. `build_full_repo_plan('.')`: `scope_prefix='argus/'`, `source_file_count=72`,
`total_loc=20034`, units `477ef77d7b65…`/`82a3d605e61e…`/`ed6d08f25ce3…` at `1330`/**`14900`**/`3804`.
Baseline suite via `--junit-xml`: **1362 tests, 1 failure, 0 errors, 0 skipped**; the single failure
is `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
(`DF-11-1-A`, §0.4). **Every §0/§A premise this story rests on was reproduced, not transcribed.**

**D2 — AC4.1, the resolver change ISOLATED from the `action.yml` change.** This is the measurement
that licenses touching a green guard, so it was taken with the resolver edit applied and
`action.yml` still **unfixed** — otherwise the sweep's own effect would have contaminated it:

```
invocations BEFORE: 5   AFTER: 5   IDENTICAL: True   added: []   removed: []
negative control, single-line `- run: echo "${{ inputs.evil }}"` -> detected  {4}   (was: EMPTY SET)
positive control, block scalar `run: |`                          -> still detected {5, 6}
release.yml single-line runs now resolved                        -> 126, 132, 135, 140  (were: missed)
```

After the `action.yml` sweep the set is still **5**, with the `action.yml` member correctly moved
from `:78 argus audit "${{ inputs.repo-path }}" …` to `:102 argus audit "$REPO_PATH" --commit
"$COMMIT_SHA" --report-dir "$REPORT_DIR"` — that movement **is the fix**, it is what §A.5
pre-verified parses, and `TC-ArgusAgent-DOCS-001-28` confirms it against the **live** parser. No
test pins the command text or its line number.

**D3 — RED FIRST, then GREEN, with the FINAL shipped test code (E.1).** The guard was written and
run against the **unfixed** tree before `action.yml` was touched: **4 of its 8 tests failed**
(`-24`, `-25`, `-26`, `-27`), and the closure named **all six** in-`run:` sites:

```
action.yml:68  github.action_path   forbidden=False (would need an exemption)
action.yml:74  inputs.report-dir    forbidden=True
action.yml:78  inputs.repo-path     forbidden=True
action.yml:79  inputs.commit-sha    forbidden=True
action.yml:80  inputs.report-dir    forbidden=True
action.yml:126 inputs.strict        forbidden=True     <- the ledger's ":127", off by one
.github/workflows/argus-student-audit.yml:46, :66  github.sha  (the two registered exemptions)
release.yml, audit-ci.yml -> ZERO
```

**Total 8 — element-for-element what §A.4 measured.** Re-demonstrated afterwards with the final
code by reading the unfixed text from `git show HEAD:action.yml` **straight into memory**:
closure fires (5 forbidden / 6 hits), AC2 invariance violated on 6 body×value pairs; against the
fixed working tree, **0 hits, 0 forbidden, invariance holds**. **No file was mutated to produce any
demonstration** — `action.yml`'s `sha256` was `45341dbc3a289f0f5c09ba404af9826b…` before AND after
the round trip, byte-identical. The negative controls in `-29` are synthetic strings; no real file
is ever written by this suite.

**D4 — post-fix closure measurement (AC1.5).** In-`run:` interpolations across the **whole**
committed corpus: **2**, both `github.sha` in `argus-student-audit.yml`, both registered with a
written reason. **`action.yml` carries ZERO, of any context** — forbidden `[]`, unregistered
survivors `[]`, stale exemptions `[]`. `action.yml` is now **160 lines**, `sha256`
`45341dbc3a289f0f…`.

**D5 — AC5.1 append-only, proven programmatically, not asserted.**
`after.startswith(before)` → **True**; **+90 lines / −0 changed**; the original `DF-9-2-D` entry
(including its wrong `:127`) is byte-unchanged, which is the whole point of §3.4.

**D6 — gates.** Full suite `--junit-xml`: **1370 tests = 1362 baseline + 8 new, 1 failure, 0
errors, 0 skipped**. The single failure is the carved-out node id
`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
(`DF-11-1-A`, DN-8 — not closed, not touched, `epic-10-retro-2026-08-11.md` neither registered nor
staged nor deleted). **No second red. N = 8.** `mypy argus` → *Success: no issues found in **72**
source files* (count unmoved). `bandit -r argus --severity-level medium` → **0 High / 0 Medium**,
19 Low (matches the 11.2 baseline exactly). Coverage `pytest --cov=argus`: **4536/4734 statements
= 95.8175%**, reported as `96%` — **≥ 80 and not below the 95.82% baseline**, which it matches to
the rounded digit. This is the first Epic-11 story to RE-RUN the coverage and bandit figures rather
than attribute them: §A.7 attributed both to Story 11.2's run, and both reproduced.

**D7 — `argus audit .`, compared field by field against 11.2's baseline.**

| Field | 11.2 baseline | This run | |
|---|---|---|---|
| `verdict` | `RELEASE_READY` | `RELEASE_READY` | unmoved |
| `blocking_findings` | `0` | `0` | unmoved |
| `assessed_deep_ratio` | `61/77` | `61/77` | unmoved |
| `scope` | `application` | `application` | unmoved |
| exit code | `0` | `0` | unmoved |
| `deep_ratio` | `61/166` | `61/167` | **+1**, arithmetically explained |
| `held_out` | `89` | `90` | **+1**, arithmetically explained |

The only movement is `deep_ratio`'s denominator and `held_out`, each **+1**, and the arithmetic is
exact: this story adds **one** file to the repository, `tests/test_workflow_input_containment.py`,
which under `scope=application` is held out as a test file. **AC6.5's permitted movement is exactly
+1 each per new test file; one new test file, +1 each.** No other field moved.

**D8 — fences re-measured AFTER `git add`, which is the only measurement that counts (§0.2).**
`git ls-files -- argus` = **72**. `git status --porcelain -- argus/` = the same **four ` M`** lines,
**no ` A` line**. `build_full_repo_plan('.')` re-run: `source_file_count=72`, `total_loc=20034`,
unit 2 = **14900** → **0 of the 100 available lines consumed**, and all three `partition_id`s
**byte-unchanged**. **No dogfood artifact was regenerated.** The mechanism §0.2 warned about could
not fire, and that was verified rather than assumed: every byte this story wrote is outside
`argus/`.

---

#### FIX ITERATION 1 (2026-08-12) — the [High] review finding. All figures LOCAL, Windows / CPython 3.11.15.

**D9 — RED FIRST, and the finding is WIDER than the one shape reported.** Before editing anything I
ran the reviewer's exact `action.yml`-shaped synthetic through the committed guard:
`interpolations('action.yml', "…run: | # scrub inputs before use\n  echo \"${{ inputs.strict }}\"")`
returned **`()`** — confirmed, the guard is fully vacuous there. I then swept the neighbourhood
rather than fixing the reported case, because §E.3's lesson is that a fix aimed at one shape is how
you get here. **Nine ordinary header spellings were measured vacuous, all returning an empty hit
set**, executable-line set `[6]` (the header) instead of `[7]` (the body):

| Shape | Comment involved? |
|---|---|
| `run: \| # …`, `run: > # …`, `run: \|- # …`, `run: \|+ # …` | yes — the reported class |
| **`run: \|2`**, `run: \|2- # …`, **`run: >-2`** | **NO — a digit is not `[-+]`, so an indentation indicator alone defeats it** |
| `run: # …` (bare key, comment, script indented beneath) | yes |
| `run: echo "${{` continued onto the next line (folded plain scalar) | no |

The two bare-indicator rows are the "neighbour left broken" case: a fix that only stripped comments
would have shipped `run: |2` still blind.

**D10 — Root cause and the repair, generalized IN PLACE (AR7/§3.3, no fork).** The first
generalisation asked *"is anything left on the line after the key?"* and called a non-empty remainder
the command; `_RUN_HEADER_RE`'s `(?:[|>][-+]?\s*)?` also failed to consume a digit. The rule now
captures the block header as its own group — `(?P<block>[|>][0-9+\-]*)?` — and **classifies on the
PRESENCE of that indicator, not on what follows it**, because YAML permits only a comment after a
block header, so its remainder is never the command. That makes the recognised set the YAML
`c-b-block-header` grammar rather than an enumeration (§C.6). A bare `run:` and `run: # …` take the
same branch. Additionally, a single-line `run:` whose value carries an **unclosed `${{`** now absorbs
its continuation lines (bounded by the closing `}}` and by the indentation returning) — deliberately
narrow, because a single-line `run:` is normally followed by a sibling `env:` key whose body is more
indented, and absorbing that would report `env:`-bound values, the very shape this project asks
authors to write, as shell source. One definition, one call site, no second mechanism; `-30`'s
one-definition / no-private-spelling / import assertions still pass untouched.

**D11 — RED proven with the FINAL test code, with a `sha256` round-trip (E.1).** The shipped resolver
was reverted to the reviewed pre-fix rule **in the file** and the final tests run against it:

```
FIXED    sha256 55b3efa15c18ea09a6c0a89b8ea7eb1260fa533eab448d60171bf6456a0d0974  tests/test_invocation_contract.py
REVERTED sha256 6025e2d0f8298015000933562d0e46bc090cbbcf3502e878e7c2247d39ee9aa8
  FAILED …-29_negative_controls_in_every_run_shape_and_a_clean_corpus
  FAILED …-32_every_block_header_spelling_reaches_the_body
        AssertionError: THE GUARD IS BLIND TO 102 OF 108 LEGAL `run:` BLOCK HEADERS
RESTORED sha256 55b3efa15c18ea09a6c0a89b8ea7eb1260fa533eab448d60171bf6456a0d0974   round-trip OK
```

Only the 6 uncommented `|`/`>`-with-no-indicator spellings passed pre-fix — i.e. the three shapes
`-29` already covered. Post-fix all 108 pass. **No real file was mutated to produce a control**; the
one file reverted was restored byte-identically and verified by hash.

**D12 — AC4.1 re-proven against the file actually written, and the change is INERT on the real
corpus.** `extract_documented_invocations()` re-run through both resolvers in one process (the
pre-fix rule injected as a module attribute, the real files untouched):

```
invocations BEFORE: 5   AFTER: 5   IDENTICAL: True   added: []   removed: []
  README.md:205 / :208 / :211,  action.yml:102,  argus-student-audit.yml:45
executable-line delta, per file (old resolver vs new):
  action.yml  before=54 after=54 added=[] removed=[]      argus-student-audit.yml 26/26 [] []
  audit-ci.yml 45/45 [] []   release.yml 35/35 [] []      README.md 26/26 [] []
corpus interpolation hits AFTER: 2 — argus-student-audit.yml:46 and :66, both `github.sha`
```

**Zero executable lines added or removed in any corpus file**, and the surviving hit-set is still
exactly the two registered DN-6 exemptions. **No existing assertion was weakened, deleted or
re-baselined** (AC4.4 / E.5): `-29` only gained shapes and gained a commented-block-header step in
its CLEAN corpus (proving the repair does not create a false positive on the shape authors should
write); `-24`..`-28`, `-30`, `-31` are unchanged.

**D13 — Gates and fences, all re-run in the fix session.**

| Gate | Measured | Verdict |
|---|---|---|
| Full suite (`--junit-xml`, parsed as XML) | **1371 tests, 1 failure, 0 errors, 0 skipped** | 1370 + **1 new** (`-32`) |
| The one failure, by node id | `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed` | `DF-11-1-A`, carved out (§0.4). **No second red.** |
| `mypy argus` | clean, **72** source files | count unmoved |
| `bandit -r argus --severity-level medium` | **0 High / 0 Medium**; `--exit-zero`: 19 Low | matches 11.2 baseline |
| coverage | **95.82%** (4536/4734), `--cov-fail-under=80` reached | not below the 95.8175% baseline |
| `argus audit .` | `verdict=RELEASE_READY blocking_findings=0 assessed_deep_ratio=61/77 scope=application deep_ratio=61/167 held_out=90`, exit **0** | field-identical to the reviewed run — **no movement at all**, because this iteration added no file |
| `git ls-files -- argus` (after `git add`) | **72** | unchanged |
| `git status --porcelain -- argus/` | the same **four ` M`**, **zero ` A`** | unchanged |
| dogfood unit 2 / `partition_id`s | **14900** (0 of 100 consumed); `477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…` | byte-unchanged; no artifact regenerated |
| published? | `git log origin/master..HEAD` = **6**, `git tag -l` **empty**, `HEAD` = `93adc94` | nothing pushed, tagged, released or dispatched |

**CI evidence: `NOT ESTABLISHED`** — unchanged and unchangeable from inside this story (§0.1/2). The
command a human runs is `gh workflow run audit-ci.yml --ref master` after a push, then citing the run
id **plus the sha it covers**.

**`argusdemo/demo.sh` was left exactly as it was**, per the reviewer's assessment that it breaks
nothing and the operator's decision to hold it for the epic checkpoint. Not staged, not deleted, not
git-ignored by me.

### Completion Notes List

**What was implemented.** Six `${{ … }}` interpolations were removed from `run:` bodies in
`action.yml` — the five consumer-controlled `inputs.*` sites (`:74`, `:78`, `:79`, `:80`, `:126`)
and the undocumented sixth, `:68`'s `github.action_path` — by binding each through a step-level
`env:` map and referencing it as a **double-quoted** shell variable, in the shape
`.github/workflows/release.yml` already documents (DN-1). Two `env:` blocks: one entry on the
install step, four on the audit step, which is where all five inputs live. A guard,
`tests/test_workflow_input_containment.py` (~~8 tests, `…-24`..`-31`~~ → **9 tests,
`TC-ArgusAgent-SECURITY-001-24`..`-32`**, after fix iteration 1), closes the class over the whole
committed workflow corpus.

**⚠️ FIX ITERATION 1 — what the review found, and the honest reading of it.** Everything in this
section below was verified correct on disk by the reviewer **except the closure itself**, and the
finding is this story's own thesis turned against it: the resolver I generalized was still vacuous
against nine ordinary `run:` header spellings — a trailing YAML comment (`run: | # scrub inputs`) or
a bare indentation indicator (`run: |2`) made the remainder non-empty, so the line was read as the
single-line form and **the indented body was never scanned**. `interpolations()` returned `()` for an
`action.yml`-shaped document containing `echo "${{ inputs.strict }}"`. The six committed sites were
and are genuinely closed, so nothing shipped was unsafe — but AC3's mandate is the **next** one, and
a contributor adding a comment to a `run: |` would have reopened `DF-9-2-D` with the suite green.
**The correction is the lesson, not the patch:** I did not add a fourth shape to a list of three. The
classification now keys on the **presence** of the `|`/`>` indicator — the grammar's own
discriminator, which YAML permits only a comment to follow — and `-32` asserts it over the
**generated** cross product of YAML's `c-b-block-header` grammar (108 spellings; 102 were blind
pre-fix). D9–D13 record the RED-first proof, the `sha256` round-trip, and the corpus-inertness
measurement. This paragraph supersedes the "three negative controls"/"8 tests" figures written
below at first implementation; those sentences are left standing rather than rewritten, because the
record of what was believed is part of the finding.

**The one decision that decided this story: the obvious guard would have been VACUOUS.** §A.3
measured it and I reproduced it: this repo's existing run-block resolver keyed on
`^-?\s*run:\s*[|>]?[-+]?\s*$`, whose `\s*$` requires end-of-line after the key, so it saw **block
scalars only** and returned an **empty** set for `- run: echo "${{ inputs.evil }}"` — the cheapest
way to reintroduce `DF-9-2-D`. A guard inheriting that would have gone green while the vulnerability
stood. AR7 / architecture §3.3 forbid forking it, so it was **generalized in place** and renamed to
the public `executable_line_numbers`; the new guard **imports** it. `-30` asserts there is exactly
one definition, that this file contains no definition of its own, that the import is present, that
`executable_line_numbers.__module__` is still the declaring module, and that **both** `run:` shapes
resolve. The safety of touching a green guard is D2's element-identical invocation set.

**Design decisions and tradeoffs, recorded rather than left implicit:**

1. **The committed property is script-text INVARIANCE, not a live exploit.** `-27` renders every
   `run:` body of the committed `action.yml` against an adversarial corpus (the §A.2 breakout
   string, `"; id; #`, `$(id)`, a backtick form, an embedded newline, the empty string) and asserts
   the text is **byte-identical for every value**. That is portable, stdlib-only, and true on a
   Windows box. The `bash` demonstration stays in §A.2 and in the ledger's closure note, per §0.1/3:
   `PyYAML` is not a declared dependency, and `pytest.skip` is a false green in this project.
2. **`-28` is the mandatory positive control and it is not decorative.** `-27` asserts "rendering
   changes nothing", which is exactly what a renderer that substitutes nothing would also produce.
   So `-28` applies the identical assertion to the **pre-fix line held as a literal in the test
   file** — never read back from `action.yml`, never from git history, because a control sourced
   from the artifact under test stops being a control the moment the artifact is fixed. It requires
   the render to MOVE, the adversarial value to land in the output, and the closure to classify
   `inputs.strict` as forbidden.
3. **Detection is over the JOINED run-body text (AC3.7).** A `${{` can be wrapped so its context
   name sits on the next line; a per-line regex is escapable by pressing Enter. `-29` drives all
   three reintroduction shapes — single-line, block scalar, line-wrapped — RED and asserts each hit
   is attributed to the line carrying its `${{`, and drives a clean `env:`-bound corpus GREEN.
4. **The ban is a closure, not a list.** `inputs.*` and `github.event.*` are forbidden outright with
   **no exemption possible** (`-26` asserts no such exemption can even be registered), so the guard
   protects the future rather than today's five sites. Everything else must be a reason-carrying
   registry entry, failing in **both** directions (E.2).
5. **`:68` swept though it is not the vulnerability (DN-3).** `github.action_path` is
   runner-provided. Sweeping it cost three lines and buys the published artifact a zero-exemption
   claim: `-25` asserts `action.yml` carries no interpolation **and** that no exemption is
   registered against it, so the file a consumer executes needs no registry to be trusted.
6. **`:135` deliberately NOT changed (DN-4), and the non-change is PINNED.** `with: path: ${{
   inputs.report-dir }}` is an action input to `actions/upload-artifact`, not shell source. `-25`
   asserts that line is still present, so a future "tidying" sweep goes red instead of silently
   breaking where a consumer's artifacts come from. Prose alone would not have survived.
7. **Deviation from §F, recorded not hidden (AC6.7): `-31` is an eighth test §F did not name.** §F
   describes the new file as "the AC2/AC3 guard"; `-31` serves **AC1.6** instead, pinning the frozen
   consumer contract — input defaults, output values, every arm of the exit-code map, both
   `::error::` strings, `assessed`, and the deliberate **absence** of `set -euo pipefail` (§C.4)
   together with the presence of the `set +e`/`set -e` bracket. Reason: AC1.6 was otherwise
   verifiable only by reading a diff, no existing guard pins it, and this story's own edit passes
   directly through that surface. It adds no file to the write set. **If a reviewer judges this out
   of scope, it is severable — deleting `-31` weakens nothing else in the file.**
8. **No new dependency, no `argus/` byte, no behaviour change.** Stdlib only (`re`, `pathlib`,
   `dataclasses`, `typing`); no `subprocess`, no network, no clock, no file writes, no `pytest.skip`.

**The irony this story does not get to resolve, stated rather than papered over.** `action.yml`
executes **only** inside GitHub Actions, and **no CI run has ever executed it** — before this change
or after it. Everything above was proven on a local Windows host by text analysis. The property
proven is genuinely strong and genuinely portable — the script text cannot vary with an input value,
so there is no value a consumer can supply that becomes code — but it is **not** the same as a
runner having executed the fixed action. That gap is `AI-E10-1`, it is carried forward under the
dated risk acceptance of 2026-08-11 (XAgent007), and §0.1/2 forbids closing it from inside this
story by pushing or dispatching to manufacture a citation. **CI evidence: `NOT ESTABLISHED.** The
command a human runs is `gh workflow run audit-ci.yml --ref master` after a push, then citing the
run id **plus the sha it covers**.

**⛔ Nothing was published.** No `git push`, no `git tag`, no `gh release`, no `gh workflow run`.
`git tag -l` is still **empty** and `HEAD` is still `93adc94` — the delta is **staged, not
committed**, per E.4/`AI-E8-1`, and the review gate takes the commit decision. Publication of the
action is Story 12.9 (DN-10); this story delivers only its hard precondition.

**Ledger items deliberately NOT absorbed.** `DF-11-1-A` stays deferred and is carved out by node id
(DN-8, §0.4) — `epic-10-retro-2026-08-11.md` was not registered, not staged, not deleted.
`DF-11-2-A` / `DF-11-2-B` stay filed against **12.5** (DN-9, §0.6) — `argus/detectors/vacuous_test.py`
and `tests/test_classification_word_boundary.py` were not touched.

**One untracked artifact at the repo root is NOT mine: `argusdemo/demo.sh`.** It appeared during
this session, and reading it shows it is the **Scrum Master's §A.2 exploit demonstration** — it
renders the pre-fix `strict` template with the identical attacker string recorded in §A.2 and hands
it to a real `bash`, reproducing that section's transcript. It is not part of §F's write set and
§0.1/3 forbids a `bash`-dependent guard in the suite, so I **left it untracked and unstaged rather
than deleting someone else's evidence**. Recommend the operator or the review gate decide whether it
is deleted or preserved as story evidence; if it is kept, it needs a `.gitignore` entry, since an
untracked root directory is exactly the shape that made `DF-11-1-A` a standing red.

### File List

| File | Change |
|---|---|
| `action.yml` | ` M` — two `env:` blocks (1 + 4 entries), six interpolations removed from `run:` bodies, every reference double-quoted; a header comment stating the rule and its enforcement |
| `tests/test_invocation_contract.py` | ` M` — run-block resolver generalized in place (block scalar **and** single-line) and renamed to the public `executable_line_numbers`; one internal call site updated. **Fix iteration 1:** classification re-keyed onto the presence of the `|`/`>` block indicator so **every** YAML block-header spelling (comment, chomping and indentation indicators, both orders) reaches the body, plus continuation of a single-line scalar carrying an unclosed `${{`; `sha256` `55b3efa15c18ea09…` |
| `tests/test_workflow_input_containment.py` | ` A` **NEW** — the guard, ~~8 tests (`…-24`..`-31`)~~ → **9 tests** (`TC-ArgusAgent-SECURITY-001-24`..`-32`). **Fix iteration 1:** `-29` gained four shapes (commented block header, indentation indicator, bare `run:` + comment, continued scalar) and a commented-header step in its CLEAN corpus; `-32` added as the generated-grammar closure; module docstring gained the sixth way-a-guard-lies |
| `CHANGELOG.md` | ` M` — one `### Security …` section under `## Unreleased` |
| `tests/test_release_surface_honesty.py` | ` M` — one `_NOTE_SECTIONS` entry, registered **third** with its reason (DN-7); no existing section moved |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | ` M` — **append-only** `DF-9-2-D` closure note (+90/−0). **Fix iteration 1:** a further append-only paragraph **(g)** recording the guard's own vacuity, the repair and the superseded `-24`..`-31` / 8-test figure (+32/−0, `after.startswith(before)` **True**) |
| `_bmad-output/design-artifacts/ArgusAgent/stories/11-3-published-action-cannot-execute-consumer-input.md` | ` A` — this file, staged per E.4 |

**Not written, deliberately:** anything under `argus/`; `.github/workflows/**` (measured compliant
or exempt); `README.md`; `pyproject.toml`; `architecture.md`; `epics.md`; `E-PRD/prd.md`;
`tests/test_evidence_citation.py`; any dogfood artifact. `sprint-status.yaml` is written by the loop.
`argusdemo/demo.sh` is not mine and was left alone (see above).

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-12 | 1.0 | **Implemented.** Six interpolations removed from `run:` bodies in `action.yml` (the five `inputs.*` at `:74/:78/:79/:80/:126` plus DN-3's undocumented `:68` `github.action_path`), each bound through a step-level `env:` map and referenced as a double-quoted shell variable in `release.yml`'s shape; `:135` (`with: path:`) deliberately unchanged per DN-4 **and pinned** so the non-change cannot be silently "fixed". The existing run-block resolver was **generalized in place and renamed public** (`executable_line_numbers`) rather than forked (AR7/§3.3) — measured blind to single-line `run:`, which would have made the obvious guard **vacuous**; the documented-invocation set was proven element-identical across the change (5→5, 0 added, 0 removed) with `action.yml` still unfixed, isolating the resolver's effect. New guard `tests/test_workflow_input_containment.py`, 8 tests (`TC-ArgusAgent-SECURITY-001-24`..`-31`): the committed security property is **stdlib-only script-text INVARIANCE** over an adversarial corpus, with a mandatory positive control on the pre-fix literal, three negative controls (single-line, block scalar, line-wrapped), a both-directions exemption registry, and a no-second-resolver assertion. Proven **RED first** against the unfixed tree naming all six sites, then GREEN — with **no file mutated** (`action.yml` `sha256` byte-identical across the round trip). `DF-9-2-D` closed by an **append-only** ledger note (`after.startswith(before)` True, +90/−0) recording the corrected count (five, not one), the off-by-one `:127`→`:126`, the sixth site, the `:135` non-change, and the demonstrated exploit. LOCAL gates: **1370 tests = 1362 + 8, exactly ONE failure** (`DF-11-1-A`, carved out by node id), 0 errors, 0 skipped; `mypy` clean on **72** sources; `bandit` 0H/0M/19L; coverage **95.82%**; `argus audit .` field-identical but for `deep_ratio`/`held_out` **+1 each**, explained exactly by the one new test file. Fences re-measured **after** `git add`: `git ls-files -- argus` = **72**, no ` A` line, unit 2 = **14900** (**0 of 100** consumed), all three `partition_id`s byte-unchanged. CI evidence **NOT ESTABLISHED**; nothing pushed, tagged, released or dispatched. Status `ready-for-dev` → `review`. | Dev Agent (bmad-dev-story) |
| 2026-08-12 | 0.1 | Story contexted from `epics.md` Story 11.3 / `DF-9-2-D`. Every premise re-measured on this tree per `AI-E10-3`: the epic's five coordinates **held exactly** (the first Epic 11 premise to survive); the ledger's `:127` is **off by one**; a **sixth** in-`run:` site (`:68`) is undocumented; the epic's *"compared as quoted shell variables"* corrected to *bound and double-quoted*; and the obvious guard implementation was measured **vacuous** against single-line `run:` bodies. Exploit **demonstrated** through a real shell (§A.2) and the portable invariance formulation derived from it. `DF-10-4-D` and the LOC budget both measured **non-binding** (dogfood `scope_prefix` = `argus/`; 0 of 100 lines consumed) and retained as verify-with-HALT ACs. `DF-11-1-A` carved out by node id; `DF-11-2-A`/`-B` ruled out and left at 12.5. Status `backlog` → `ready-for-dev`. | Scrum Master (bmad-create-story) |
| 2026-08-12 | 1.1 | **Code review, iteration 1 — FAIL.** Independently re-verified and confirmed on disk: the `action.yml` diff is coherent (no half-applied/duplicated edits from the interrupted dev session; `sha256` matches the dev's own figure exactly), all six sites are genuinely closed (not relocated — bash `"$VAR"` parameter expansion does not re-scan its own value for shell syntax), `:135` is unchanged and pinned, the resolver rename is a true rename with no fork, the documented-invocation set re-derives identically, and every gate figure (1370/1 failure, mypy, bandit, `argus audit .`, both fences, unpushed/untagged) re-measured to match the dev's claims exactly. **One High finding blocks pass:** the committed guard's run-block resolver (`tests/test_invocation_contract.py::executable_line_numbers`) is genuinely vacuous against a `run: \| # <comment>` block-scalar header — an ordinary, non-adversarial YAML edit that the shipped `-29` (three shapes) does not cover — and a synthetic `action.yml`-shaped reproduction confirms the closure returns **zero** hits for an unambiguous `inputs.*` interpolation inside such a body. This is exactly the "-17b lesson" / E.3 trap the story itself names, one shape further out. `argusdemo/demo.sh` assessed per the operator item: does not currently break anything, but flagged to resolve before Epic 11 closes. Status `review` → `in-progress`. | Reviewer (bmad-code-review) |
| 2026-08-12 | 1.2 | **Fix iteration 1 — the single [High] review finding resolved (1 of 1).** The committed closure's run-block resolver was vacuous against a `run: | # <comment>` block-scalar header, as reported. Reproduced RED first with the reviewer's own synthetic (`interpolations()` -> `()`), then **swept the neighbourhood instead of the reported shape**: **9** ordinary header spellings were measured blind, including `run: |2` and `run: >-2`, where no comment is involved at all (a digit is not `[-+]`) — so a comment-stripping fix would have left a neighbour broken. Repaired **in place** (AR7/§3.3, no fork, one definition, one call site) by capturing the block header as its own group and classifying on the **presence** of the `|`/`>` indicator rather than on whether the remainder is empty — YAML permits only a comment after a block header, so the remainder is never the command, which makes the recognised set the `c-b-block-header` grammar rather than an enumeration (§C.6). A single-line `run:` carrying an unclosed `${{` now also absorbs its continuation lines, bounded by the closing `}}`. `-29` gained four shapes and a commented-header step in its CLEAN corpus (no false positive on the shape authors should write); **`-32` added** as a closure over the GENERATED cross product of the header grammar (108 spellings). **Proven RED-first with the FINAL test code** against the reverted resolver — `-29` and `-32` both failed, `-32` naming **102 of 108** blind spellings — with a `sha256` round-trip on the reverted file (`55b3efa15c18ea09…` -> `6025e2d0f8298015…` -> `55b3efa15c18ea09…`); no real file was mutated to produce a control. **No existing assertion weakened, deleted or re-baselined** (AC4.4/E.5). The change is provably **inert on the real corpus**: zero executable lines added or removed in `action.yml`, the three workflows or `README.md`, `extract_documented_invocations()` still element-identical **5 -> 5** (0 added, 0 removed), surviving hit-set still exactly the two DN-6 exemptions. `deferred-work.md` gained an **append-only** paragraph (g) superseding its `-24`..`-31` / 8-test figure (+32/-0, `after.startswith(before)` True). LOCAL gates re-run: **1371 tests = 1370 + 1 new, exactly ONE failure** (`DF-11-1-A`, carved out by node id; parsed from `--junit-xml`, not read off the terminal), 0 errors, 0 skipped; `mypy` clean on **72** sources; `bandit` 0H/0M/19L; coverage **95.82%**; `argus audit .` **field-identical with no movement at all** (no file added this iteration). Fences after `git add`: `git ls-files -- argus` = **72**, zero ` A`, unit 2 = **14900** (0 of 100 consumed), all three `partition_id`s byte-unchanged. `argusdemo/demo.sh` left untouched per the operator's held decision. CI evidence **NOT ESTABLISHED**; nothing pushed, tagged, released or dispatched (`HEAD` = `93adc94`, 6 unpushed, `git tag -l` empty). Status `in-progress` -> `review`. | Dev Agent (bmad-dev-story, mode fix) |
