---
baseline_commit: 00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0
baseline_note: >-
  HEAD is `00c8d1b` ("Merge pull request #2 from Inan15/fix/honest-verdict-reporting").
  `master` and `origin/master` are the SAME sha — the tree is pushed, which is why this
  story can cite executed CI at all. `git status --porcelain` reported 21 entries when this
  context was authored: 13 ` M` planning/config files (the 2026-08-10b amendment cascade),
  and 8 `??` paths — `.bmad-drift-audit/`, `_bmad-output/audit-reports/{ollama-audit,run-demo,self-audit}/`,
  `bmad-dev-loop-pack/`, and three untracked planning documents
  (`implementation-readiness-report-2026-08-10.md`, `sprint-change-proposal-2026-08-10.md`,
  `sprint-change-proposal-2026-08-10b.md`). **`bmad-dev-loop-pack/` and `.bmad-drift-audit/`
  belong to the orchestrator — do not add, move or delete them.** THIS FILE is a 22nd
  untracked path and IS yours: `git add` it with your delta or you repeat AI-E8-1, in which
  Epic 8 shipped with its own story file untracked because `git diff` cannot see an
  untracked path.
  ⚠️ **`sprint-change-proposal-2026-08-10b.md` is untracked and is the source of Epics 10-13.**
  It is not yours to commit or to edit, but it IS the authority for the epics.md text you are
  implementing. Read it; do not rewrite it.
  **Consequence you must internalise:** `git diff HEAD` over `argus/` is EMPTY, so it is not
  the measuring instrument for anything in this story. Every figure below was produced by
  running `gh` against the live GitHub Actions API and by reading the files in place.
  **Re-derive them yourself; do not read them off this document.** That instruction is not
  boilerplate here — it is literally this story's subject matter.
story_key: 10-1-release-status-must-cite-evidence
epic: 10
---

# Story 10.1: A release status must cite evidence, not assert it

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo, `argus/` tree only.** ArgusAgent (formerly APAA) is a self-contained
> headless audit tool extracted from the Minions monorepo into its own repository (`Agent-Argus`,
> distribution `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo. The
> `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no back-port.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`, `minions_core/apaa/`
> or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/` and `tests/`.

---

## Story

As the ArgusAgent maintainer,
I want a release-readiness statement to be refused unless it cites an executed gate,
so that ArgusAgent never publishes about itself the kind of unevidenced green it exists to catch in
other repositories.

**Why this is Epic 10's FIRST story.** It is the *control* that would have caught 10.2, 10.3 and
10.4. Fixing the artifacts those stories name while the gate still accepts self-attestation invites
the recurrence. 10.2-10.4 cite the run id this story establishes.

---

## Story Context

### Method statement — MEASURED LIVE against the GitHub Actions API on 2026-08-10

Every run id, conclusion and job result below came from `gh run list` / `gh run view` executed against
`github.com/Inan15/Agent-Argus` while authoring this story, not from a document. **`gh` is
authenticated on this machine** (`gh auth status` → account `varinderpratap`, keyring token). Network
egress may be sandboxed for your tool calls; if a `gh` call fails to reach `api.github.com`, that is a
sandbox restriction, not an outage — see **§A.4** for what to do, and read it before you conclude
anything is unavailable.

### A. The evidence, measured — and it is better AND worse than the ledger says

#### A.1 — `audit-ci.yml`'s complete run history on `master`, live

| Run id | Commit | Conclusion | When | Duration |
|---|---|---|---|---|
| **`31341363300`** | **`00c8d1b`** (HEAD, = `origin/master`) | ✅ **success** | 2026-08-09T23:13:27Z | 1m54s |
| `31322881580` | `cd60dbb` *(the repair commit itself)* | ❌ **failure** | 2026-08-09T16:05:48Z | 1m37s |
| `30774175196` | pre-repair | ❌ **failure** | 2026-08-03T00:18:06Z | 40s |

`30774175196` is the run `DF-AUD-APAA-C` cites. It reproduces exactly.

#### A.2 — 🟢 AC3's evidence ALREADY EXISTS, and all three matrix legs are green

Run **`31341363300`**, jobs measured individually:

| Leg | Conclusion |
|---|---|
| `Run Argus Quality Gates & Audit Suite (3.10)` | ✅ success |
| `Run Argus Quality Gates & Audit Suite (3.11)` | ✅ success |
| `Run Argus Quality Gates & Audit Suite (3.12)` | ✅ success |

- URL: `https://github.com/Inan15/Agent-Argus/actions/runs/31341363300`
- `headSha`: `00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0`

**AC3 is therefore not a "make CI pass" task. It is a "cite the run that already passed, and scope
the citation honestly" task.** See **§A.5** for the trap in that sentence.

#### A.3 — 🚩 THE FINDING THIS STORY DID NOT EXPECT: the ledger entry repeats the defect it files

`deferred-work.md:1336-1337` (`DF-AUD-APAA-C`) states:

> *"Both were repaired 2026-08-09 and a clean-venv reproduction of every step passes on 3.12; the
> repair is NOT the deferred item."*

Measured: **the repair commit `cd60dbb`'s own CI run `31322881580` FAILED.** The 3.11 leg died at
*"Run Pytest & Coverage Assurance Gate"*; 3.10 and 3.12 were `cancelled` by fail-fast, so **the "passes
on 3.12" claim was never executed on 3.12 either.**

The cause is measured, not guessed. `git diff cd60dbb 00c8d1b -- .github/workflows/audit-ci.yml
pyproject.toml` is **EMPTY** — the workflow repair was correct and has not changed since. What was
still broken was **product code on POSIX**, visible in the failed log:

```
E       Failed: DID NOT RAISE WorkspaceContainmentError
```

— closed by the twelve commits in `cd60dbb..00c8d1b`, of which six are the POSIX/non-ASCII chain
(`d0e0a5c`, `ebdca75`, `f7c666e`, `266bb28`, `f85fe76`, `40c0727`).

**Why this matters more than a footnote.** `DF-AUD-APAA-C` is the ledger entry filed *about* asserting
a status over an unexecuted gate, and its own repair sentence is a **local, unevidenced claim that the
executed gate contradicted at the moment it was written.** The class recurred inside the record of the
class. AC2's guard must be written so that this entry would have gone RED — and AC4 requires the entry
itself be corrected, append-only.

#### A.4 — Getting the run id yourself (do this; do not copy the table above)

```bash
gh run list --workflow=audit-ci.yml --branch master --limit 10
gh run view 31341363300 --json headSha,conclusion,url,jobs \
  -q '{sha:.headSha,concl:.conclusion,url:.url,jobs:[.jobs[]|{name,concl:.conclusion}]}'
```

**If `gh` cannot reach `api.github.com`** — the message is *"error connecting to api.github.com"* —
your shell is sandboxed. Re-run the same read-only command with the sandbox disabled. It is a `GET`
against a public repository's Actions API: no writes, no pushes, no tags.

**If, and only if, you genuinely cannot observe the run:** you do **not** copy `31341363300` out of
this document. You record the status as **NOT ESTABLISHED**, name the reason, and give the exact
command a human runs. **That is not a failure of this story. That is this story.** A dev agent that
transcribes a run id it did not observe, into the story whose subject is not transcribing unobserved
evidence, has produced the exact defect under repair.

#### A.5 — 🚩 THE TRAP IN AC3: a run id is SHA-SCOPED, and your commit moves the sha

Run `31341363300` covers `00c8d1b`. **Your delta is not in it.** The moment you commit, `master`'s HEAD
is no longer the sha that run evidences.

Two things follow, and both are mandatory:

1. **Every citation you write names its sha.** `run 31341363300` alone is a half-truth; `run
   31341363300 (00c8d1b, 3/3 legs green)` is the claim. A run id without a sha is the *next* version
   of the defect being fixed — it looks like evidence and covers an unknown tree.
2. **What 10.2-10.4 cite is the state of the gate, not a frozen number.** Say so explicitly: the
   citation format and the *standard* are what this story delivers; each later story cites the run
   covering **its own** HEAD. A story that reuses `31341363300` to evidence a tree it does not contain
   repeats §A.3.

**You are not required to push, tag, or trigger a run.** Pushing is an operator step (AI-E9-1, still
unowned). Your local commit will produce a run *when the operator pushes*, and your record must say
that plainly rather than pretending the future run already happened.

### B. The record being corrected, read in place

`sprint-change-proposal-2026-07-28.md` is **63 lines**. The relevant three:

| Line | Content |
|---|---|
| `:35` | *"CI/CD Pipeline Added: Created `.github/workflows/audit-ci.yml` … coverage enforcement (`--cov-fail-under=80`)"* |
| `:55` | *"**Pytest Suite**: **916 PASSED, 1 SKIPPED, 0 FAILED** (Duration: 182.41s)."* — **local**, the only evidence offered |
| `:63` | *"- **Release Status**: Upgraded from `NEEDS TARGETED REWORK` to **READY FOR RELEASE**!"* — the last line of the file |

The proposal **created** the gate at `:35` and then declared release readiness at `:63` over a run of
that gate which had never passed. Both halves are in the same document, four sections apart.

### C. §3.4 evidence immutability — the correction form this project already uses

There is **no numbered §3.4 document in this repository.** `§3.4` is a project-wide shorthand for
*"correct by striking or appending, never by silent rewrite"*, and it is cited **20+ times** across
`deferred-work.md`, `architecture.md` and the retrospectives. Do not go looking for the definition and
do not invent one; **copy the shape from the two committed exemplars**:

- **Strike-and-supersede in prose** — `architecture.md:428-433`: original text wrapped in `~~…~~`,
  followed by a bolded `**Superseded 2026-08-10b — …**` paragraph giving the date and the reason, and
  closing *"Original text struck rather than deleted (§3.4 evidence immutability)."*
- **Append-only note in the ledger** — `deferred-work.md:23-24`, `:84`, `:363`, `:520`: a nested
  bullet added *under* the untouched original, opening
  *"(append-only closure note — the original entry above is NOT rewritten, §3.4 evidence immutability)"*.

### D. The guard's ancestry — reuse this, do not invent a new shape

`tests/test_release_surface_honesty.py` is the direct precedent and is the file to read **before you
write a line of test code**. It already solves the three problems you are about to hit:

| Problem | Solved at | Shape |
|---|---|---|
| A guard that names only the files existing when it was written | `-18`, L303-330 | Registry + **glob closure**: resolve patterns against the tree, fail on anything unregistered |
| A substring scan cannot tell a claim from its own denial | `_is_denied`, L190-202 | **Sentence-scoped** scan; negation counts only when it **precedes** the phrase; qualifiers may follow |
| A filter whose exemption swallows what it looks for | `-17b`, L260-300 | **Positive control**: assert the detector catches a planted affirmative AND does not flag the real honest sentences, verbatim |

The `-17b` trailing-negation escape (*"externally validated with no exceptions"* walked through the
first version) was found **by code review, not by the author**. Assume yours has the same bug until a
positive control says otherwise.

### E. Where a rule of this kind lives in this project — and the retro item that says so

**AI-E9-7** (epic-9 retro §7) is the standing recommendation this story is the first opportunity to
satisfy: *"never publish a prose copy of a pinned figure… either the document cites the pin, or a test
asserts the document's number equals the pin's"*, with destination *"record it here and in
`architecture.md`'s testing patterns"*. Its DoD has never been met because no story existed after 9.2.

`architecture.md` **§H — Self-Audit & CI (trust substrate)** (`L420-425`) is the section: it already
enumerates the cartridges, the import-isolation gate and the determinism golden-tests. `§Enforcement`
(`L574-578`) is where guards are named. **AI-E9-8** is the reason not to create a new governance
document: a register with no reader is how the last one evaporated.

### F. Fences — what is NOT in this story, with the owner

| Out of scope | Owner |
|---|---|
| `action.yml:127` / the `${{ inputs.* }}` sweep (`DF-9-2-D`, AI-E9-6) | **Story 11.3** |
| `argus-student-audit.yml` — a third workflow, also `${{ }}`-interpolating into `run:` | **Story 11.3** |
| Amending PRD/architecture for multi-language (10 sites) | **Story 10.2** |
| The 4 unspecified CLI flags | **Story 10.3** |
| Grammar-failure reason tokens | **Story 10.4** |
| `standards_refs[]` / the FR1-37 reachability sweep | **Story 10.5** |
| `pipeline.py` 1331/1200 NFR-M1 breach + the repo-wide sweep test | **Story 12.1** |
| Tagging, pushing, publishing, the release URL | **Story 12.9** / operator (AI-E9-1) |
| The ≥80% precision gate — **NOT CLEARED, and nothing here clears it** | **Epic 13** |

**Do not "fix" `audit-ci.yml`.** It is already correct (§A.3: unchanged since `cd60dbb` and green at
`00c8d1b`). Editing a green workflow inside a story about evidence discipline is scope creep with a
regression risk attached.

---

## Acceptance Criteria

### AC1 — The 2026-07-28 record is corrected in place: dated, reasoned, struck, never rewritten

`sprint-change-proposal-2026-07-28.md` is amended so that:

1. Line `:63`'s claim is **struck** (`~~…~~`), not deleted, not reworded.
2. An adjacent **dated, reasoned correction block** states: the status was asserted on a local
   `pytest` run (`:55`); the CI gate the same proposal created (`:35`) had **never passed** at that
   time; the run that proves it is **`30774175196`** (`failure`, 40s, 2026-08-03); and the corrected
   status as of the correction date, **with its own citation**.
3. The correction gives the **superseding evidence** — run `31341363300`, sha `00c8d1b`, 3/3 matrix
   legs — and **states explicitly which sha that run does and does not cover** (§A.5).
4. Nothing else in the file is edited. `git diff` on that file shows **additions plus the two
   strike-through markers, and no other deletion.**

**Verification:** `TC-ArgusAgent-DOCS-001-20`.

### AC2 — The evidence standard exists as a written rule AND as a committed guard

**(a) The rule.** `architecture.md` §H (`L420-425`) gains a named rule, in the register of its
neighbours, stating: *a document that asserts a release or release-readiness status cites an executed
gate — a GitHub Actions run URL or run id, with the sha it covers — or records the status as* **NOT
ESTABLISHED**. It names `AUDIT_FAILED`-is-not-a-verdict (`action.yml:33-48`) as the same rule applied
to the tool's own output, so the tool and its governance share one principle. `§Enforcement`
(`L574-578`) names the guard file.

**(b) The guard.** A committed test scans every registered status-asserting document and fails when a
status claim carries neither a citation nor a `NOT ESTABLISHED` marker.

**A rule that exists only in a test is not a rule; a rule that exists only in prose is not enforced.**
Both halves are required, and a test asserts the prose is present so half (a) cannot be silently
deleted.

**Verification:** `TC-ArgusAgent-DOCS-001-21`, `-23`.

### AC3 — The guard bites, and cannot be satisfied by a document nobody registered

1. **Positive control** (`-21b`): a planted affirmative status claim with no citation is **caught**;
   each real, honest sentence now on disk is **not** flagged, asserted verbatim. Include at minimum
   the trailing-negation shape that defeated `-17b`'s first version.
2. **Closure** (`-22`): the registry is resolved by **glob** over
   `sprint-change-proposal-*.md` and `epic-*-retro-*.md` under the artifact directory; any file found
   that is not registered **fails**. A new proposal cannot escape by being new.
3. **Non-vacuity**: the globs resolve to a non-empty set, and the guard fails if they do not — a
   pattern that matches nothing passes every assertion in it.

Exclusions are **by name with a reason**, never by silence (the `_PRESERVED_RECORD` precedent,
`test_release_surface_honesty.py:89-96`). Story files under `stories/` are excluded deliberately: a
story records test-run evidence, and its status lives in `sprint-status.yaml`. **State that; do not
just omit them.**

**Verification:** `TC-ArgusAgent-DOCS-001-21b`, `-22`.

### AC4 — `DF-AUD-APAA-C` is closed against the evidence, and its own incorrect claim is corrected

An **append-only** note under the untouched entry (`deferred-work.md:1328-1345`) that:

1. Cites run **`31341363300`** (`00c8d1b`, 3/3 legs) as the executed gate the entry asked for.
2. Records the §A.3 finding: **the entry's own *"repaired… passes on 3.12"* sentence was contradicted
   by run `31322881580`**, in which the 3.11 leg failed and 3.10/3.12 were cancelled — so the 3.12
   claim was never executed. Give the measured cause (product code on POSIX; the workflow was already
   correct and is byte-identical between `cd60dbb` and `00c8d1b`).
3. States which commits closed it (`cd60dbb..00c8d1b`, the six POSIX/non-ASCII fixes).
4. Names what remains open — this story does not clear the precision gate, does not publish, and does
   not push.

**The original entry text is not edited.** Recording that the ledger repeated the class it files is
the point; quietly correcting it would be the third instance.

**Verification:** `TC-ArgusAgent-DOCS-001-20` covers the append-only shape.

### AC5 — 10.2-10.4 are told what to cite, in a form that survives their commits

`epics.md`'s Epic 10 dependency-flow block (`L1748-1750`) — or the Story 10.1 AC that promises *"that
run id is the evidence 10.2-10.4 cite"* (`L1808`) — is amended to state the **sha-scoped** form from
§A.5: each story cites the `audit-ci.yml` run covering **its own** HEAD, in the format the AC2 rule
fixes. Amend with a date, in place, `~~struck~~` if wording is replaced.

**Rationale, recorded:** as written, `L1808` invites 10.2-10.4 to cite a number that predates their
own code. That is the defect this epic exists to close, one level up.

⛔ **Fence: those two locations and nothing else in `epics.md`.** Epics 1-9 are delivered and their
retrospectives are signed; Epics 11-13 were written 2026-08-10b and are not yours. A story that
rewrites the plan while implementing one of its cells is the failure mode `sprint-status.yaml`'s delta
notes exist to prevent. If the amendment cannot be made without touching a third location, **stop and
record why** rather than widening.

### AC6 — The gates are re-run locally, and the local result is labelled as what it is

`mypy argus`, `bandit -r argus --severity-level medium`, and
`pytest --cov=argus --cov-report=term-missing --cov-fail-under=80` all pass on this host, and the
figures are recorded in the Dev Agent Record **explicitly labelled as a LOCAL run that is necessary
but not sufficient** — the precise conflation this story exists to end. **1230 tests collect** at
baseline; report the executed figure, not the collected one.

⚠️ Local `mypy` here is **2.3.0**; CI installs `mypy>=1.0` and may resolve differently. If a local
mypy result disagrees with run `31341363300`, the **executed CI run is the evidence** and the local
divergence is recorded, not hidden.

### AC7 — Whole-system proof and no regression

1. Full suite green; **no test removed, skipped or weakened**; the count grows by exactly the new
   cases (baseline **1230 collected**).
2. `git diff` touches only these seven paths — **four documents** (`sprint-change-proposal-2026-07-28.md`,
   `architecture.md`, `deferred-work.md`, `epics.md`), the new `tests/test_evidence_citation.py`, this
   story file, and `sprint-status.yaml`. **Zero `argus/**` product-code changes** — this story changes
   no runtime behaviour, and a diff under `argus/` means scope has leaked.
3. `deferred-work.md` diff is **`+n / -0`** (append-only, mechanically checkable).
4. Any new deferral is filed with an id, an owner and a `target_story` — **never `target_story: NONE`
   without a named human** (AI-E9-8).

---

## Tasks / Subtasks

- [x] **T1 — Re-derive the evidence yourself (AC3, AC6) — FIRST, before any edit**
  - [x] `gh run list --workflow=audit-ci.yml --branch master --limit 10`; if it cannot reach
        `api.github.com`, re-run read-only with the sandbox disabled (§A.4)
  - [x] `gh run view <id> --json headSha,conclusion,url,jobs` — confirm **3/3** legs and the sha
  - [x] Confirm `30774175196` = `failure` and `31322881580` = `failure` with the 3.11 leg dying at the
        pytest step (§A.3)
  - [x] `git diff cd60dbb 00c8d1b -- .github/workflows/audit-ci.yml pyproject.toml` → expect **empty**
  - [x] ⛔ **If you could not observe the runs, STOP and take the NOT ESTABLISHED path (§A.4).** Do
        not copy an id out of this document. *(Not triggered — all three runs were observed live.)*

- [x] **T2 — Read before writing (prevents the three known failure shapes)**
  - [x] `tests/test_release_surface_honesty.py` in full — registry, closure, sentence scan, positive
        control (§D)
  - [x] `architecture.md:413-434` (§G/§H/§I) — the register your rule must match, and the
        strike-and-supersede exemplar at `:428-433`
  - [x] `deferred-work.md:1326-1346` (`DF-AUD-APAA-C`) and one append-only exemplar (`:520`, `:363`)
  - [x] `sprint-change-proposal-2026-07-28.md` end-to-end — 63 lines
  - [x] `action.yml:33-53` — the `AUDIT_FAILED`-is-not-a-verdict prose your rule mirrors

- [x] **T3 — Correct the 2026-07-28 record (AC1)**
  - [x] Strike `:63`; strike or annotate `:55`'s local-evidence framing
  - [x] Append the dated, reasoned correction: the failed run, the superseding run, **the sha each
        covers**, and what is still not established
  - [x] Verify: no other line deleted

- [x] **T4 — Write the rule (AC2a)**
  - [x] `architecture.md` §H — the citation rule, in its neighbours' register; cross-reference
        `AUDIT_FAILED`
  - [x] `architecture.md` §Enforcement — name the new guard file alongside the existing gates

- [x] **T5 — Build the guard (AC2b, AC3)** — new `tests/test_evidence_citation.py`
  - [x] Module docstring naming the story, the AC, the area and **why the shape is what it is** —
        house style; every test file here does this
  - [x] `_STATUS_DOCUMENTS` registry + `_STATUS_DOCUMENT_PATTERNS` globs
  - [x] Sentence-scoped claim scan **reusing the `_is_denied` position rule** (§D)
  - [x] `-20` correction/append-only shape · `-21` every registered doc cites or says NOT ESTABLISHED
        · `-21b` positive control **both directions** · `-22` closure + non-vacuity · `-23` the
        architecture rule prose is present
  - [x] ⚠️ **RED first.** Run each new test against the *uncorrected* documents and confirm it fails.
        A guard first run after the fix has proven nothing (Epic-3 lesson **AI-E3-1**: 3.4's keystone
        test was green over its own keystone bug). *(Discharged twice — see Debug Log D3/D4.)*

- [x] **T6 — Close the ledger honestly (AC4)**
  - [x] Append-only note under the untouched `DF-AUD-APAA-C`
  - [x] Include the §A.3 finding — the entry's own repair claim was contradicted by `31322881580`
  - [x] Verify `git diff --numstat` on `deferred-work.md` is **`+n 0`** *(161 0)*

- [x] **T7 — Tell 10.2-10.4 what to cite (AC5)**
  - [x] Amend `epics.md:1748-1750` / `:1808` to the sha-scoped form, dated, struck where replaced

- [x] **T8 — Gates and record (AC6, AC7)**
  - [x] `mypy argus` · `bandit -r argus --severity-level medium` · `pytest --cov=argus
        --cov-fail-under=80`
  - [x] Record figures **labelled LOCAL**, plus the cited CI run and its sha, separately
  - [x] `git status --porcelain` — confirm no `argus/**` change; `git add` this story file
  - [x] Set Status to `review`; update `sprint-status.yaml` `10-1-…: review`

### Review Findings

**Code review 2026-08-10, iteration 1 — PASS. No unresolved findings.** Verified independently, not
read off this document: (1) all 7 ACs checked against the actual files — `sprint-change-proposal-2026-07-28.md`
(`:63` struck intact, `:55` LOCAL-annotated, dated §5 correction with failed run/superseding run/sha-scope/NOT
ESTABLISHED), `architecture.md` §H + §Enforcement (rule text present, guard named), `deferred-work.md`
`DF-AUD-APAA-C` (original text byte-intact, append-only closure note with the §A.3 finding), `epics.md`
(both fenced locations amended/dated/struck, no third location touched); (2) mechanical claims re-derived —
`git diff --stat HEAD -- argus/` empty (zero product-code change), `deferred-work.md` numstat `161 0`
(append-only), `.github/workflows/audit-ci.yml` diff empty (DN-6 honored), `git tag -l` empty and
`master`...`origin/master` show no ahead (DN-7 honored — nothing pushed/tagged); (3) the guard
(`tests/test_evidence_citation.py`) read in full and exercised: non-vacuous glob closure confirmed against
the 14 files actually on disk, positive control in both directions inspected, `_is_denied` duplication vs.
`test_release_surface_honesty.py` judged justified by the recorded rationale (different marker vocabulary,
different registry), `_STATUS_CLAIMS` narrowing spot-checked against the corpus (grepped for `shippable`,
`release readiness`, `certified`, `signed off`, `clears the bar`, etc. — no missed uncited claim found);
(4) gates re-run locally by the reviewer: `mypy argus` → 0 issues/71 files (match), `bandit -r argus
--severity-level medium` → 0 Med/0 High, 18 Low (match), `pytest tests/ --cov=argus --cov-fail-under=80` →
exit 0, coverage 94.97% (match), 1235 collected (match, summed per-file collection counts independently),
full run all-dots / zero F|E across the entire progress bar (independent re-run); `git diff --stat HEAD --
tests/` shows only the new file (608 insertions, 0 deletions elsewhere) — mechanically confirms no existing
test was touched, skipped or weakened (AC7.1). Two theoretical Low-severity observations were considered and
dismissed as noise (not filed as action items): the `_EXCLUDED_BY_DESIGN` dict's combined key for four
unrelated filenames is a documentation-only convenience, not a functional gap; and the sha/run-id citation
regex could in principle accept an unrelated hex token as a "sha" if one ever appeared in the same sentence
as a run id, but this does not occur anywhere in the current corpus and hardening it further is more
machinery than AC3 asks for (KISS/YAGNI, consistent with the dev's own recorded tradeoffs). DN-1..DN-8 all
honored, none re-litigated. Status set to `done`.

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

| # | Decision | Why |
|---|---|---|
| **DN-1** | The rule lives in **`architecture.md` §H**, not a new governance document | AI-E9-7 names `architecture.md`; AI-E9-8 diagnosed that a register with no reader evaporates. §H is literally *"Self-Audit & CI (trust substrate)"*. |
| **DN-2** | Guard = **new `tests/test_evidence_citation.py`**, area `ArgusAgent-DOCS`, ids **`-20`..`-23`** | `-01`..`-19` are taken (`test_release_note.py`, `test_release_surface_honesty.py`). A *new file*, not an extension: `test_release_surface_honesty.py`'s docstring binds it to Story 9.2/AC12 and its registry is release **surfaces**; status-asserting **planning records** are a different set with a different rule. |
| **DN-3** | Citation format = an **Actions run URL or run id, plus the sha it covers** | §A.5. A bare run id looks like evidence and covers an unknown tree. |
| **DN-4** | Scanned set = `sprint-change-proposal-*.md` + `epic-*-retro-*.md` under the artifact dir | Exactly what the epic's AC names (*"any future change proposal or retrospective"*). Wider is scope creep; narrower fails AC3's closure. |
| **DN-5** | Story files are **excluded, by name, with the reason written down** | A story records test-run evidence, not a release status; its status lives in `sprint-status.yaml`. Silent omission is the `_PRESERVED_RECORD` anti-pattern. |
| **DN-6** | `audit-ci.yml` is **NOT edited** | Already correct and green (§A.3). Editing a green workflow inside an evidence-discipline story is unjustified regression risk. |
| **DN-7** | **No push, no tag, no `workflow_dispatch`** | AI-E9-1 is an operator step with no owner. Triggering a run to manufacture a citation is manufacturing evidence. |
| **DN-8** | `DF-AUD-APAA-C`'s wrong sentence is **corrected append-only, never edited** | Recording that the ledger repeated the class it files is the finding; quietly fixing it would be the third instance. |

### Architecture patterns & constraints a reviewer will check

- **§3.4 evidence immutability** — strike, never delete; append, never rewrite. Exemplars at
  `architecture.md:428-433` and `deferred-work.md:520`.
- **AR10 / honest degradation** — *unknown* is a first-class recordable state. `NOT ESTABLISHED` is
  the governance twin of `AUDIT_FAILED`-is-not-a-verdict (`action.yml:33-48`) and of
  `INSUFFICIENT_COVERAGE` (never a false block, never a fabricated pass).
- **NFR-M1 ≤1200 lines/module** — applies to your new test file too. Currently breached **only** by
  `argus/pipeline.py` at 1331; that is **Story 12.1's**, not yours, and you must not touch it.
- **No `print()` in library code; typed exceptions at the impure shell** — not directly engaged (no
  `argus/**` change), listed so you notice if your diff starts touching product code.

### Traps previous stories already paid for — the four that apply here

1. **AI-E3-1 (Epic 3) — a keystone test can be green over its own keystone bug.** Story 3.4's resume
   test passed while resume silently dropped coverage, because the fixture always sorted into the
   skipped remainder. **Run every new assertion RED against the uncorrected documents first.**
2. **AI-E8-6 (Epic 8) — all five Epic-8 stories shipped a guard narrower than their own AC**, where
   the AC said *every*. AC3's closure clause is the direct countermeasure; do not weaken it to a
   fixed file list.
3. **`-17b` (Epic 9) — the denial filter that swallowed what it looked for.** Found by review, not by
   the author. Positive control, both directions, verbatim honest sentences.
4. **AI-E9-7 / R1 (Epic 9) — a prose copy of a pinned figure drifted into the release contract at
   five sites** and only the committed pin caught it. If your correction block states a number a test
   also pins, cite the pin or assert equality.

### Recent git context — the twelve commits that made CI green

`cd60dbb..00c8d1b` (12 commits). The six that matter for §A.3: `d0e0a5c` (non-ASCII filenames crashed
on POSIX under a C locale), `ebdca75` (containment decided differently on POSIX vs Windows —
**this is the `DID NOT RAISE WorkspaceContainmentError` failure**), `f7c666e`, `266bb28` (F-21
surrogate repair), `f85fe76`, `40c0727`. `8290cde` is the Epic 10 planning commit that created the
epic you are implementing.

**Pattern to notice:** every one of those is a *host-portability* defect invisible on the Windows
development machine and fatal on the ubuntu runner. Anything you assert from a local run inherits that
blind spot — which is precisely why AC6 makes you label local results as local.

### Runtime & toolchain, verified on this machine 2026-08-10

| | |
|---|---|
| Python | **3.11.15** (CI matrix: 3.10 / 3.11 / 3.12) |
| `mypy` | **2.3.0** local; CI resolves `mypy>=1.0` — may differ (AC6) |
| `pytest-cov`, `bandit`, `vulture` | all importable locally |
| Tests collected | **1230** |
| `gh` | authenticated, account `varinderpratap` |
| Network | reachable **only with the tool sandbox disabled** (§A.4) |

**No new dependency.** The guard is pure `pathlib` + `re` over committed markdown — same as
`test_release_surface_honesty.py`. Adding a YAML or HTTP dependency to a documentation guard would be
rejected at review.

### Testing standards — the house form your new file must match

```bash
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q          # whole suite
python -m pytest tests/test_evidence_citation.py -v        # your file
python -m mypy argus
python -m pytest --cov=argus --cov-report=term-missing --cov-fail-under=80
```

- **`PYTHONIOENCODING=utf-8` is not optional on this Windows host.** The artifact tree contains
  non-ASCII (`café`, Cyrillic, `⚠️`, `🚩`, `~~`), and every file you read must be opened
  `encoding="utf-8"` explicitly. `Path.read_text()` without it inherits the host locale — the exact
  class that produced `d0e0a5c`/`ebdca75` and turned run `31322881580` red.
- **Naming:** `test_TC_ArgusAgent_DOCS_001_<nn>_<snake_case_claim>()`. The `TC-…` id appears in the
  docstring's first line, the story and AC in the second. Copy `test_release_surface_honesty.py`
  verbatim in form.
- **Every assertion carries a failure message that names the offending file and the offending
  sentence.** A guard over prose whose failure reads `assert not hits` costs the next reader an hour.
- **No network, no LLM, no `.argus/` write, no subprocess** in the test — pure functions over
  committed bytes, so it runs identically on all three CI legs.

### Latest technical information — GitHub Actions API surface used

`gh` reads the Actions REST API (`GET /repos/{owner}/{repo}/actions/runs`). Two facts that bear on
this story:

- **Run ids are stable and permanent; logs are not.** `gh run view --log-failed` depends on log
  retention (default 90 days). Your citation must be the **run id and conclusion**, which persist, not
  a log excerpt, which does not.
- **`--json jobs` returns per-leg conclusions.** A run's top-level `conclusion: success` does not by
  itself prove every matrix leg ran — `31322881580` is the counter-example, where two legs are
  `cancelled` by fail-fast. **AC3 requires the per-leg check**, which is why §A.2 lists all three.

### Project structure notes

- Tests are **flat under `tests/`**. `tests/apaa/` no longer exists (Epic 9 separation) — architecture
  prose still saying `tests/apaa/` is stale; read it as `tests/`.
- Planning artifacts: `_bmad-output/design-artifacts/ArgusAgent/`; stories in `stories/`.
- `_bmad/bmm/config.yaml` was corrected 2026-08-10b to point at the real artifact tree (AI-E9-9's D1,
  finally closed) — it is in your `git status` as an unstaged edit; **it is not yours.**

### Open question for the operator, saved for the end as the workflow requires

**§A.3 is a NEW finding, discovered while authoring this story, and it is not in any AC of the epic
as written.** It has been folded into AC4 because it is the same defect class the story exists to
close and the entry is one this story already touches. If you would rather it were tracked as its own
ledger item, say so before dev starts; otherwise AC4 carries it.

### References

- Epic + ACs — [epics.md:1738-1808](../epics.md) (Epic 10 preamble, dependency flow, Story 10.1)
- Ledger entry — [deferred-work.md:1326-1346](../deferred-work.md) (`DF-AUD-APAA-C`)
- Record under correction — [sprint-change-proposal-2026-07-28.md:35,55,63](../sprint-change-proposal-2026-07-28.md)
- Rule's home — [architecture.md:420-425](../architecture.md) (§H) · [architecture.md:574-578](../architecture.md) (§Enforcement)
- §3.4 exemplars — [architecture.md:428-433](../architecture.md) · [deferred-work.md:520](../deferred-work.md)
- Guard precedent — [tests/test_release_surface_honesty.py](../../../../tests/test_release_surface_honesty.py) (`-17`/`-17b`/`-18`, L190-330)
- Non-verdict precedent — [action.yml:33-53](../../../../action.yml)
- Retro items AI-E9-7 / AI-E9-8 — [epic-9-retro-2026-08-09.md:211-212](../epic-9-retro-2026-08-09.md)
- Keystone-test lesson AI-E3-1 — [epic-3-retro-2026-06-27.md](../epic-3-retro-2026-06-27.md)
- Sprint delta authorising Epic 10 — [sprint-change-proposal-2026-08-09.md](../sprint-change-proposal-2026-08-09.md)

---

## Dev Agent Record

### Context Reference

This story file. Every figure in it is re-derivable by the commands in §A.4 and T1 — **re-derive, do
not transcribe.**

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), BMAD `dev-story` workflow, single unattended pass, 2026-08-10.

### Debug Log References

**D1 — T1, evidence re-derived live, not transcribed.** `gh` reached `api.github.com` **without**
disabling the sandbox, so §A.4's fallback was not needed. All figures reproduce:

| Command | Result (measured) |
|---|---|
| `gh run list --workflow=audit-ci.yml --branch master --limit 10` | exactly 3 runs: `31341363300` success · `31322881580` failure · `30774175196` failure |
| `gh run view 31341363300 --json headSha,conclusion,url,jobs` | `success`; sha `00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0`; jobs 3.10 ✅ 3.11 ✅ 3.12 ✅ (**3/3**, read per-job) |
| `gh run view 31322881580 …` | `failure`; sha `cd60dbbe45d03b7bc647307a3b14a66a2bd019ff`; **3.11 = failure at *"Run Pytest & Coverage Assurance Gate"***; 3.10 + 3.12 = **`cancelled`** |
| `gh run view 30774175196 …` | `failure`, 40s, 2026-08-03T00:18:06Z; sha `ae5f00cd05f5bbc3b00952efadeab1d3f6d3a5f1`; **3.12 = failure at *"Run Static Analysis & Security Scans"*** (the bandit step the ledger names); 3.10 + 3.11 `cancelled` |
| `git diff cd60dbb 00c8d1b -- .github/workflows/audit-ci.yml pyproject.toml` | **empty (0 bytes)** — the workflow repair was correct and is byte-identical across the range |
| `git log --oneline cd60dbb..00c8d1b` | **12 commits**; the six POSIX/non-ASCII fixes present as named |

**One figure the story did not carry:** run `30774175196` covers sha `ae5f00c`, not the 2026-07-28 tree
by name. Recorded and cited, because DN-3 makes the sha part of the citation.

**D2 — corpus measured before the detector was written.** A probe over all 14 registered documents
counted every candidate claim phrase. This changed the design: the wide phrases (`release status` ×6,
`shippable` ×4, `release readiness` ×1) fire almost entirely on *meta-discussion and rule statements* —
including this project's own governance prose — so a wide list would have produced a guard that cries
wolf and gets deleted by the third person to hit it. The narrow list leaves exactly **three** claim
sentences in the corpus, each individually accounted for below.

**D3 — RED, first pass** (guard vs. uncorrected documents): `-20` FAIL, `-21` FAIL, `-23` FAIL, 2 passed.
`-21`'s failure message quotes the real defect line. `-22` was proven to bite separately by planting
`sprint-change-proposal-9999-01-01.md` → *"status-asserting document(s) exist but are not registered"* →
file removed.

**D4 — RED, re-run after the test file changed.** `_flatten()` was added to `-20`/`-23` (markdown hard-wraps
mid-sentence, so a literal substring check was asserting the line wrapping rather than the content). Because
the guard changed after D3, **the RED demonstration was repeated with the final code** against all four
pre-edit documents: `-20`/`-21`/`-23` FAIL again, 2 passed. Anything less would leave the final assertions
never having been seen red — the AI-E3-1 shape exactly. All four documents were then restored and verified
**byte-identical by sha256 round-trip**; the RED runs mutated nothing.

`-21b` and `-22` pass in the RED state **by design and this is not a gap**: `-21b` is a pure-function
positive control over planted strings and `-22` is a closure check over the registry — neither is a test of
the corrections, and both were shown to bite by their own means.

**D5 — GREEN.** `python -m pytest tests/test_evidence_citation.py -v` → **5 passed** in 0.16s.

### Completion Notes List

**AC1 — the 2026-07-28 record.** `:63` is **struck**, not deleted or reworded. `:55` carries a ⚠️ **LOCAL**
annotation appended to (not replacing) the original figure. A new dated `## 5. Correction — 2026-08-10`
section gives: the failed gate (`30774175196`, `failure`, 40s, sha `ae5f00c`, the step it died in), the
superseding gate (`31341363300`, `success`, 3/3 legs, sha `00c8d1b`), an explicit **sha-scope** paragraph
naming what that run does *and does not* cover, and the corrected status — **NOT ESTABLISHED** — with the
narrower thing that *is* established stated separately and cited. Diff is **+45/−2**, and both "deletions"
are in-place line replacements whose original text survives verbatim inside the replacement.

**AC2 — both halves.** (a) `architecture.md` §H gains the rule in its neighbours' register, in three
binding parts: the sha is part of the citation; a local run is necessary but not sufficient; NOT
ESTABLISHED is a first-class state. It cross-references `AUDIT_FAILED`-is-not-a-verdict (`action.yml:33-48`)
so the tool and its governance visibly share one principle. §Enforcement names the guard. (b) The guard is
`tests/test_evidence_citation.py`, and `-23` asserts the prose is present, so half (a) cannot be silently
deleted.

**AC3 — the guard bites, and the set is closed.** `-21b` is a positive control in both directions whose
primary case is the **verbatim historical defect line**: if the guard cannot catch the sentence it was
written for, it catches nothing. It also pins three trailing-negation shapes (the `-17b` escape), a
**dangling-`~~` escape** (an unterminated strike must not retract the rest of the file — a one-character
way to hide a claim), and an unattributed blockquote. The other direction asserts, verbatim, each honest
sentence now on disk. `-22` resolves the registry by **glob** and fails on any unregistered match, in both
directions (unregistered file found → fail; registered name the globs can no longer see → fail), plus
non-vacuity.

**AC4 — the ledger.** A six-part append-only closure note under the **byte-intact** original: (a) the
executed gate, (b) 🚩 the §A.3 finding that the entry's own *"passes on 3.12"* sentence was contradicted by
`31322881580` at the moment it was written, (c) the measured cause (product code on POSIX; the workflow was
already correct), (d) the closing commits, (e) where the standard now lives, (f) what remains open. `-20`
asserts the original sentence is still present, so a future silent repair goes red.

**AC5 — 10.2-10.4.** Both fenced locations amended and dated; the replaced clause is struck. No third
location touched.

**AC6 — LOCAL gates. Necessary, NOT sufficient.** See the table below. **AC7** — see the fence table.

#### AC6 — figures, explicitly labelled

> ⚠️ **Every figure in this block is a LOCAL run on the Windows development host (Python 3.11.15).
> It is necessary and it is NOT sufficient.** Six of the twelve commits in `cd60dbb..00c8d1b` were
> host-portability defects invisible on exactly this machine and fatal on the ubuntu runner; that is
> the structural reason a local run cannot discharge the rule this story writes.

| LOCAL gate | Result |
|---|---|
| `python -m mypy argus` | **Success: no issues found in 71 source files** |
| `python -m bandit -r argus --severity-level medium` | **exit 0** — 0 Medium, 0 High (18 Low, below threshold) |
| `python -m pytest tests/ --cov=argus --cov-report=term-missing --cov-fail-under=80` | **1235 passed, 0 failed, 0 skipped**, 484.99s, **coverage 94.97%** (gate 80%) |

**Local/CI divergence:** local `mypy` is **2.3.0**; CI resolves `mypy>=1.0`. They did not disagree here —
both are clean — but the standing rule is recorded: **if they ever disagree, the executed CI run is the
evidence** and the local result is the divergence.

**The separately-stated CI citation, and its honest limit.** The executed gate this repository can cite is
run **`31341363300`** — `success`, 3/3 legs, covering sha **`00c8d1b`**. **It does not cover this story's
delta.** Per **DN-7** nothing was pushed, tagged or `workflow_dispatch`-ed: triggering a run to manufacture
a citation would be manufacturing evidence. The run that evidences this commit **does not exist yet** and is
created when the operator pushes (**AI-E9-1**, still unowned). Until then this tree's gate status is
**NOT ESTABLISHED** — the rule, applied to the story that writes it. The command a human runs afterwards:

```bash
gh run list --workflow=audit-ci.yml --branch master --limit 5
gh run view <id> --json headSha,conclusion,jobs \
  -q '{sha:.headSha,concl:.conclusion,jobs:[.jobs[]|{name,concl:.conclusion}]}'
```

#### AC7 — the fence, verified

| Check | Measured |
|---|---|
| `git status --porcelain -- argus/` | **empty** — zero product-code change |
| Paths in my delta | exactly the **7** permitted (4 documents · the new test · this story file · `sprint-status.yaml`) |
| `deferred-work.md` | **+161 / −0** vs HEAD (was +114/−0 before this story: **+47 appended, −0**) |
| `epics.md` | +823/−29 (was +802/−28) → +21 lines, **exactly one deletion**, the AC5-sanctioned struck clause |
| `architecture.md` | +273/−35 (was +247/−35) → +26 lines, **zero new deletions** |
| `sprint-change-proposal-2026-07-28.md` | +45/−2, both in-place replacements preserving the original text verbatim |
| Test count | **1230 → 1235**, i.e. exactly the 5 new cases; no test removed, skipped or weakened |
| New dependency | **none** — pure `pathlib` + `re` over committed markdown |
| New deferral filed | **none** |
| Tracking | story file and `tests/test_evidence_citation.py` `git add`-ed (**AI-E8-1**: `git diff` cannot see an untracked path) |

#### Decisions taken under dev authority, with rationale (none re-litigates DN-1..DN-8)

1. **Task order: T5's RED demonstration was executed by temporarily restoring the pre-edit documents,
   rather than by reordering the tasks.** T5 mandates RED *against the uncorrected documents*, which is
   impossible once T3/T4 have run, while the workflow mandates following the task sequence exactly. Both
   were honoured: T3/T4 ran in order, then the pre-edit snapshots (taken before the first edit) were copied
   back, the guard was run red, and the corrected files were restored and **verified byte-identical by
   sha256**. Reordering the tasks or skipping the demonstration were the alternatives; the first breaks the
   workflow's explicit sequencing rule and the second is AI-E3-1.
2. **The position rule is re-stated in the new module, not imported from `test_release_surface_honesty.py`.**
   §D says reuse the shape, and the shape is reused exactly. The *table* is not shared: this guard needs
   `nothing` as a denial marker (the corpus contains a denial with no bare `no `/`not `), and adding it to
   the Story-9.2 guard would silently retune a shipped, review-hardened detector. Two independent guards
   sharing one mutable policy table is worse coupling than fifteen lines of duplicated policy is
   duplication, and DN-2 already establishes these as different sets under different rules.
3. **Attributed quotations are excluded, narrowly and positively controlled.** A correction document
   necessarily quotes the claim it corrects — `sprint-change-proposal-2026-08-09.md:31-33` does exactly
   this — so a scanner that cannot tell *"X said we were ready"* from *"we are ready"* flags every
   correction ever written, including this story's own. The exemption requires **both** a blockquote **and**
   a preceding line that names a `.md` source and ends in a colon; `-21b` asserts an *unattributed*
   blockquote is still caught. Abusing it means falsely attributing your claim to a named file — a
   different, checkable lie.
4. **Struck text is treated as retracted.** That is what §3.4 striking means, and a guard that ignored it
   would make the AC1 fix impossible. The loophole this opens is closed twice: `-20` pins that the struck
   claim is still *physically present* (so "strike" cannot become "delete"), and `-21b` pins that a
   **dangling** `~~` cannot retract a later paragraph.
5. **The citation requirement is document-scoped; the NOT ESTABLISHED marker is claim-scoped.** AC2a's own
   wording is *"a document that asserts … cites …"*. Making the marker claim-scoped is strictly tighter
   than document scope and stops one unrelated "NOT ESTABLISHED" elsewhere in a file from exempting every
   claim in it. **Recorded tradeoff:** a document could still cite one run and assert a second, unrelated
   status. Section-scoping was considered and rejected as more machinery than the AC asks for (KISS/YAGNI);
   if a reviewer wants it tightened, the change is local to `-21`.
6. **A bare run id is rejected as a citation, mechanically.** The sha regex requires at least one `a-f`
   character precisely so an all-digit run id (`31341363300` is 11 valid hex characters) cannot be read as
   its own sha — which would have made every bare run id self-certifying and handed the guard back the
   exact loophole it exists to close. `-21b` asserts this in both directions.
7. **`:56` (the coverage figure) was left unannotated** although it is as local as `:55`. T3 authorises
   annotating `:55` only, and AC1.4 says nothing else is edited. The annotation was written, then reverted
   to hold the fence; the §5 correction block carries the point for both figures instead. **Project
   standard over marginal improvement.**

#### Things a reviewer should look at first

- **The three real claim sentences in the corpus**, each handled by a different mechanism — the 2026-07-28
  defect (struck + cited), the 2026-08-09 attributed quotation (exemption #3), the epic-8-retro denial
  (`nothing` marker). If any one of those mechanisms is wrong, `-21` is either vacuous or a false alarm.
- **Whether the narrow `_STATUS_CLAIMS` list is too narrow.** It is a deliberate precision/recall trade
  made on measured data (D2), and it is the most reversible thing in this change.
- **`deferred-work.md` line endings:** the Edit tool normalised 64 tail lines from LF to CRLF. Git's own
  normalisation makes this invisible (`−0` confirmed) and no content changed. Recorded rather than hidden.

### File List

| Path | Change |
|---|---|
| `tests/test_evidence_citation.py` | **new** — the guard (`TC-ArgusAgent-DOCS-001-20`..`-23`, 5 tests) |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-07-28.md` | modified — AC1: `:63` struck, `:55` LOCAL-annotated, `## 5. Correction — 2026-08-10` appended |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | modified — AC2a: §H evidence-citation rule + §Enforcement naming the guard |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | modified — AC4: append-only closure note under `DF-AUD-APAA-C` (+47/−0) |
| `_bmad-output/design-artifacts/ArgusAgent/epics.md` | modified — AC5: Epic 10 dependency-flow block + Story 10.1's third AC, sha-scoped, dated, struck where replaced |
| `_bmad-output/design-artifacts/ArgusAgent/stories/10-1-release-status-must-cite-evidence.md` | modified + **newly tracked** (`git add`) — this file |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | modified — `10-1-…: ready-for-dev → review` + dated dev annotation |

**No `argus/**` file appears in this list, and that is an acceptance criterion, not an omission.**

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-10 | 1.0 | **Implemented; Status ready-for-dev → review.** All 7 ACs met, 8/8 tasks complete, no HALT. Evidence RE-DERIVED live against the Actions API rather than transcribed (D1) — all four of the story's figures reproduce, plus one it did not carry: run `30774175196` covers sha `ae5f00c`, now cited per DN-3. AC1 `:63` struck + dated §5 correction (failed run, superseding run, the sha each covers, what `31341363300` does NOT cover, corrected status **NOT ESTABLISHED**). AC2 rule in `architecture.md` §H + §Enforcement **and** the committed guard `tests/test_evidence_citation.py`. AC3 registry + **glob closure** + sentence scan + positive control whose primary case is the verbatim historical defect line; also closes a **dangling-`~~`** escape found while writing it. AC4 six-part append-only note under the byte-intact `DF-AUD-APAA-C`, carrying the §A.3 finding. AC5 both fenced `epics.md` locations, dated and struck. AC6 LOCAL gates: mypy 0 issues/71 files · bandit exit 0, 0 Med 0 High · **1235 passed, 0 failed, 0 skipped**, coverage 94.97% — labelled LOCAL, necessary not sufficient. AC7 **zero `argus/**` diff**, `deferred-work.md` **+161/−0**, 1230 → 1235 tests (exactly the 5 new cases), no new dependency, no new deferral. **RED-first discharged twice** (D3, D4) — repeated with the final test code after `_flatten()` was added, so no assertion shipped unseen-red; documents restored sha256-identical. **DN-7 honoured: nothing pushed, tagged or dispatched** — no CI run covers this delta, and that is recorded as NOT ESTABLISHED rather than papered over. | Amelia (Dev) |
| 2026-08-10 | 0.1 | Story created. Live GitHub Actions measurement found AC3's evidence already exists (run `31341363300`, `00c8d1b`, 3/3 legs green) and surfaced a new finding: `DF-AUD-APAA-C`'s own *"repaired… passes on 3.12"* claim was contradicted by run `31322881580`, in which the 3.11 leg failed and 3.10/3.12 were cancelled — the filed defect class recurring inside the record of the class. Folded into AC4. | Bob (SM) |
