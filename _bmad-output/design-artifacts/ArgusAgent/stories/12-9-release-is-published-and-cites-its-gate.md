---
baseline_commit: de05dec77c67a3077c3be6d154b579d024c27901
---

# Story 12.9: The release is published, and its status cites the gate that published it

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`.
>
> 🔴 **This is the NINTH and LAST story of Epic 12, and it is the ONLY story in the entire plan
> that publishes anything.** 12.1–12.8 are all `done`; only the epic retrospective follows.
> `sprint-status.yaml:399` records the operator's standing instruction verbatim: *"NO STORY IN THIS
> EPIC PUBLISHES ANYTHING until 12.9, and the orchestrator halts before it."*
>
> **Four predecessor stories deferred work here BY NAME. Every deferral is collected below and
> answered by an AC:**
>
> | Handed to you by | Where it is written | What it hands over |
> |---|---|---|
> | **Story 12.5** | 12-5 header: *"It publishes nothing until Story 12.9"* | Nothing concrete — a fence acknowledgement |
> | **Story 12.6** | 12-6 §What it is NOT row 2; 12-6 Debug Log | *"Publishing anything — a tag, an index upload, a marketplace listing, a release"* |
> | **Story 12.7** | 12-7 §What it is NOT row 2; 12-7 Task §7 | *"Publishing anything — a tag, an index upload, a marketplace listing, a GitHub Release"* |
> | **Story 12.8** | 12-8 §What it is NOT row 1; 12-8 Debug Log §7; 12-8 Change Log (twice) | ⚠️ **The live one.** `docs/first-run.md:26` publishes `pip install "argus-agent @ git+…@v0.1.0"` — a tag that **does not exist**. 12.8 REJECTED widening its own derivation to cover that line on the stated ground that *"tag `v0.1.0` does not exist, and creating or publishing one is **Story 12.9's fence**"*. The line ships today as a **documented-but-unexercised** command. **Creating the tag makes it true; not creating it leaves a published falsehood in shipped docs — and the guard that would catch the transition does not see that file (§0.1 §B).** |
>
> **Ledger entry this story OWNS:** **`DF-10-3-A`** (`target_story: 12-9-publishing-and-release-surface`,
> owner **Engineering Lead**) — and §0 records that its remedy was **already delivered by Story 12.8**
> without the ledger being told. **Cited, never built, never re-filed:** `DF-3-4-A`, `DF-10-5-C`,
> `DF-12-7-A`, `DF-10-3-B`, `DF-10-3-C`.
>
> ⚠️ **THIS STORY HAS REAL-WORLD BLAST RADIUS ITS PREDECESSORS DID NOT.** Eight of its nine ACs are
> completable **without a single outward-facing act**. **AC9 alone** is outward-facing and it is
> written as a HALT: the dev agent stages, derives, proves and documents the release, and then
> **STOPS and escalates** rather than pushing, tagging, publishing, or changing repository
> visibility without explicit human authorisation. Read AC9 before you read anything else.

---

## Story

As a developer installing Argus,
I want a real published artifact whose release status is evidenced,
So that what I install exists and its claims are backed by an executed gate.

**Why this is one story.** Every clause serves **one capability: what a stranger can actually get,
and what the thing they got is allowed to claim about itself.** The title names the substance —
*published* **and** *cites its gate*. A release with no citation is the defect this project has spent
three epics removing from the tool's own verdicts, committed about itself at the one moment it is
most visible: `sprint-change-proposal-2026-07-28.md:63` declared *"READY FOR RELEASE"* on a local
`pytest` run while the CI gate it had just created had never passed (`DF-AUD-APAA-C`, run
`30774175196` = `failure`). Story 10.1 made that a written rule and a committed guard. **This story
is the first one the rule actually costs something**, and the honest answer today is a measured
`NOT ESTABLISHED`, not a citation (§0 row 2).

### What it is NOT

| Not this story | Whose it is | Authority |
|---|---|---|
| **A PyPI / package-index publish** | **Nobody — DN-1, and it is a LOCKED project decision, not a scoping preference** | `README.md:92-94`, `.github/workflows/release.yml:24-29`, `architecture.md:629` and Story 9.2 / D1-D13 (`sprint-status.yaml:350`) all state the same thing: *a released name+version on an index can never be replaced, it needs a credential this repository cannot prove exists, and it is an operator decision taken with credentials in hand.* `epics.md:2465` permits (*"may ship"*), it does not require |
| **A GitHub Marketplace listing** | **Nobody — DN-2** | `epics.md:2463-2465`'s precondition (Story 11.3) **is MET** — 11.3 is `done`. It is blocked by a **different, measured** fact: the repository is **PRIVATE** (§0 row 4), and Marketplace requires a public repository plus a published release. Recorded, not silently skipped |
| **A version bump** | **Nobody — LOCKED by Story 9.2 / D1** | `sprint-status.yaml:350`: *"release 0.1.0, NOT bumped"* — `epics.md:1669` pins the value, `TC-ArgusAgent-DOCS-001-10` asserts it, and `__version__` is the default envelope `argus_version`, so a bump moves the bytes of **every persisted artifact** for no requirement |
| **A new exit code, verdict, decision-table change, detector, pass or report type** | Nobody — forbidden | `epics.md:2159` (*"this epic adds no new assurance capability"*), `epics.md:2312-2314`, AR3 frozen, NFR-M2 additive-only |
| **A `--resume` CLI entrance** | **Nobody — `DF-3-4-A`, still open, unscheduled** | 12.7 cited it and recorded *"stays open and is NOT re-filed"*; 12.8 cited it again. **Cite it; do not build it** |
| **An `argus evidence-bundle` sub-command (FR29 export)** | **Nobody — `DF-10-5-C`, `target_story: NONE — unscheduled; Governance Owner to schedule`** | Cited by 12.8. Building it is an unscheduled capability addition |
| **Registering further assistant hosts** | **Nobody — `DF-12-7-A`, unscheduled** | 12.7 shipped one verified host by decision (12.7 / DN-2) |
| **Bounding `--ignore-pattern`'s matching semantics; disclosing built-in suppressions** | **Nobody — `DF-10-3-C` / `DF-10-3-B`, both unscheduled** | Cite them. `DF-10-3-B`'s own text names *"the Epic-12 report-quality surface"* as a candidate home and deliberately declines to assert a story id |
| **A second tag-state guard, a second release-note renderer, a second citation vocabulary** | Nobody — forbidden | AR7 / architecture §3.3: **reuse, never fork.** `TC-ArgusAgent-DOCS-001-55` and `tests/test_evidence_citation.py` already exist. A parallel guard beside a shipped one is a defect, not a delivery (12.4's binding words, applied four times since) |
| **Rewriting history, force-pushing, or moving an existing tag** | Nobody — forbidden | `release.yml` refuses a tag move by design (E3); §3.4 evidence immutability |

---

## Acceptance Criteria

> Every AC below is stated against the **measured** tree and the **measured live GitHub state** at
> `de05dec`, not against the epic's prose. §0 records where the epic's premise was found **false** —
> and this time two of the falsehoods are *outside* the repository, which is why §0's method includes
> the GitHub API. **Re-measure before you code (Task 1).**
>
> **AC1–AC8 are completable with ZERO outward-facing acts.** AC9 is the only one that is not, and it
> is a HALT.

### AC1: The artifact is PROVEN by using it — `argus --help`, a fixture audit and an MCP invocation, from an INSTALLED distribution

- **Given** `epics.md:2467-2469` (*"the artifact installs clean in a fresh environment with `argus
  --help`, a fixture audit, and an MCP invocation all succeeding — **proven, not built**"*), and the
  **measured gap** (§0 row 5): `CHANGELOG.md:23-29` **already publishes** the claim — *"the wheel was
  installed into a fresh virtualenv with the repository absent from `sys.path`, and `argus --help`
  and `argus audit <fixture-repo>` both ran to completion there"* — and **no committed guard holds
  it.** It was true by hand on 2026-08-08. Since then the distribution gained `argus-mcp`
  (12.6), three packaged command assets (12.7), nine grammar dependencies (12.5) and a changed
  exit-code contract (12.8). **A published claim with no test is what this repository files as a
  defect** — and this one is the front-door claim of the release.
- **Given** `tests/test_built_distribution.py::TC-ArgusAgent-RELEASE-001-20` proves every shipped
  module **imports** from a freshly built wheel, and Story 11.5's own headline finding is that a
  guard one level away from the claim is vacuous about it.
- **Then** a committed guard **builds** sdist+wheel locally and **installs the wheel into a fresh
  environment**, then exercises the artifact end to end:
  1. **every** console script in `[project.scripts]` resolves and runs — **derived by closure over
     the `[project.scripts]` table, never hand-listed.** ⚠️ `_CONSOLE_SCRIPTS` / `_ENTRY_POINT` is
     the recognizer-that-stopped-recognizing defect class this project has recorded **four** times
     (12.6 twice, 12.7, `-56`'s never-executed branch). Today the table holds **four** aliases —
     `argus`, `argus-agent`, `repo-audit`, `argus-mcp` — and a fifth must be covered with **no edit**;
  2. `argus --help` and `argus audit --help` render;
  3. a **fixture audit** runs to a real verdict against a committed fixture repository and its
     stdout summary line parses;
  4. an **MCP invocation** completes a real JSON-RPC exchange over stdio through the **installed
     `argus-mcp` shim** — 12.6's `tests/test_mcp_server.py` drives the server **in process**, which
     cannot see a broken entry point, a missing asset or a packaging error.
- **Then** the probe **proves its own provenance and REFUSES rather than lying**: it asserts the
  resolved `argus` and the script shim live **inside the fresh environment**, not in the repository
  — reusing `TC-ArgusAgent-RELEASE-001-21`'s established refusal (`PROBE-INVALID`), because this
  repository is installed **editable into its own `.venv`** and any probe that leaves the repo root
  on `sys.path` reports a triumphant pass over the wrong tree. That trap cost Story 11.5 a cycle;
  it is written down so it costs this one nothing.
- **Then** it is **offline** (the test contract: *no network, deterministic*). See **DN-5** for the
  recommended route and its stated alternative. Where the environment cannot be built the guard
  reports `release_preflight.Unevaluable` with a **named reason** and skips — **it never passes
  silently** (AR10 / NFR-R1, the house rule since 9.2).
- **Then** `CHANGELOG.md:23-29`'s hand-made claim is **replaced by one that names the guard now
  holding it** (§3.4 strike-and-correct), and the MCP invocation — absent from the old claim — is
  stated. **Nothing is published, pushed, tagged or uploaded by this AC.**

### AC2: The release status CITES the gate — DERIVED, sha-scoped — or it records NOT ESTABLISHED

- **Given** Story 10.1's evidence standard, binding in **three parts** (`architecture.md:610-627`):
  a status claim cites *a GitHub Actions run URL or id **together with the sha that run covers***,
  or records **NOT ESTABLISHED**; *a local run is necessary, not sufficient*; and *NOT ESTABLISHED
  is a first-class recordable state, not a gap*.
- **Given** the **live measurement** (§0 row 2, taken through the GitHub API on 2026-08-15): the most
  recent `audit-ci.yml` run on `master` is **`31341363300`**, `success`, at sha **`00c8d1b`**, dated
  **2026-08-09** — and **`origin/master` is 34 commits BEHIND local `master`** (`gh repo view` →
  `pushedAt: 2026-08-09T23:13:28Z`). **Every commit Epics 10, 11 and 12 produced is local only.**
  Therefore **no executed gate covers the release commit, and none can exist until `master` is
  pushed** — which is an outward-facing act, fenced into AC9.
- **Then** the release status at story time is **`NOT ESTABLISHED`**, written in exactly that form,
  with (a) the reason — *no `audit-ci.yml` run covers `de05dec` or any Epic-10/11/12 sha* — (b) the
  superseded run stated as what it is (*run `31341363300` covers `00c8d1b`, which is 34 commits
  behind; a run id without its sha is a half-truth, `architecture.md:614-616`*), and (c) the exact
  human step that would establish one.
- **Then ⚠️ citing `31341363300` for this release is FORBIDDEN.** It is the precise defect
  `architecture.md:614-616` names by example, using this exact run id as the example.
- **Then the citation is DERIVED, never transcribed — this is the story's title, mechanised.** One
  named function computes the release-status statement from observed facts (the run id, its sha, its
  conclusion, its leg count, and the sha being released) **or** returns the `NOT ESTABLISHED` state;
  **every** surface that states a release status renders **that** value. A surface that hand-types a
  run id, a sha or a status is the transcription class AI-E9-7 forbids, and it is what made
  `DF-AUD-APAA-C` possible.
- **Then** the guard **extends `-21`'s rule to the surfaces a stranger reads.** Measured: 10.1's
  registry (`tests/test_evidence_citation.py:65-93`) covers **only** `sprint-change-proposal-*.md`
  and `epic-*-retro-*.md` under the artifact directory; `_EXCLUDED_BY_DESIGN` (`:98-111`) does not
  mention `README.md`, `CHANGELOG.md`, `release.yml` **or the GitHub Release notes** — they are not
  excluded with a reason, they are simply **outside the guard**. The release note is the single most
  read status-asserting document this project will ever publish and **nothing checks it.** Extend the
  rule to the registered release surfaces (`_RELEASE_SURFACES`) **without forking the policy tables**
  — 10.1 / `test_evidence_citation.py:7-15` records why the two files hold separate marker
  vocabularies; **decide and record** whether this lands as a widened population in the existing
  guard or a new assertion that imports the existing derivation. **Do not copy the regexes.**
- **Then** the guard is proven **both ways** by positive control (`-21b`'s established shape): a
  planted uncited status claim on a release surface is **caught**; every honest sentence now on disk
  is **not** flagged, asserted verbatim. Non-vacuity: `> 0` surfaces scanned and `> 0` sentences
  classified.
- ⚠️ **Expect real hits the first time you point the rule at `README.md` / `CHANGELOG.md`, and treat
  each one as a finding, not as noise.** These surfaces discuss release readiness constantly. **A hit
  is resolved by CORRECTING the sentence (cite, or mark NOT ESTABLISHED) or by adding an
  `_EXCLUDED_BY_DESIGN` entry with a stated reason — never by trimming `_STATUS_CLAIMS`, widening
  `_DENIAL_MARKERS`, or narrowing the population.** 10.1 built that vocabulary deliberately narrow
  and measured it against the real corpus; loosening it to silence a hit is how this guard stops
  guarding, and `-21b` exists because the first version of the sibling filter was defeated by exactly
  such a "harmless" widening (the trailing-negation escape). Record every disposition.

### AC3: The GitHub Release notes stop being hand-typed prose inside a `run:` block

- **Given** the measurement: `.github/workflows/release.yml:174-190` builds the release-note body as
  a **string literal inside a `run:` script**, and that literal hand-transcribes **three** pinned
  facts that each have a single source elsewhere:
  1. the **exit-code wire contract** — *"0=RELEASE_READY, 2=NOT_READY_FOR_RELEASE,
     3=INSUFFICIENT_COVERAGE, 1=typed audit failure (no verdict produced)"* — whose source is
     `argus/verdict/verdict_gate.py` (`Verdict`, `exit_code_for_verdict`) plus the reserved `1`;
  2. the **install command**, which embeds the tag;
  3. a **paraphrase of the FR34 disclosure** (*"the >=80%-precision externalization gate is
     PROVISIONAL and is not cleared"*) whose source is `argus/verdict/negative_assurance.py`'s
     single-sourced constants.
- **Given the proof that a transcription there cannot track its source:** Story 12.8 changed what
  exit `2` can mean (a usage error now returns the reserved `1`), corrected `action.yml`'s map
  comment and `docs/first-run.md`'s exit table — **and this literal did not move, because nothing
  can see it.** `.github/workflows/release.yml` is in `_RELEASE_SURFACES`, so `-17` scans it for
  *over-claims*; **no guard checks whether what it says is true.**
- **Then** the notes are **generated by one named entry point** and every factual claim in them is
  **derived** — the version from `pyproject.toml`, the exit-code map from the verdict module, the
  disclosure from the disclosure constants in its **canonical single-sourced form** (not a
  paraphrase), the install command from the tag under release, and the release status from **AC2's
  derivation**. The `run:` body invokes the generator; it types no fact.
- **Then** a committed guard **renders the notes and asserts each claim against the live source**,
  in both directions, with a `> 0` floor on claims checked — the shape `TC-ArgusAgent-DOCS-001-63`/
  `-64` already use for `docs/first-run.md`. **Reuse that shape; do not invent a second.**
- **Then** the FR34 disclosure reaching the release channel is registered where FR34 is enforced, so
  `-47`'s *"every registered listing surface carries the disclosure"* and `-50`'s two-sided
  presence/no-over-claim property extend to it. `epics.md:2467-2468` requires **both listings** carry
  it; measured (§0 row 6), `pyproject.toml`'s `[project].description` and `action.yml`'s
  `description:` — the PyPI listing body and the Marketplace listing body — **already do**, held by
  `-47`. The **new** surface this story creates is the release-note body.
- **Then ⚠️ the generator's home is constrained and the constraint is load-bearing:**
  `scripts/release_preflight.py` is **stdlib-only by design** and *"must run on a bare GitHub runner
  before the package (or anything else) is installed"* (its own docstring, `:22-26`). It **may not
  import `argus`**. **DN-4** records the recommended route and requires the alternative be stated.

### AC4: The tag-state and visibility disclosures are mechanised on EVERY surface that publishes them — before any tag exists

> **This AC is the fence 12.8 handed over, and it must land BEFORE AC9. Ordering is load-bearing:
> it is the guard that makes creating the tag self-correcting instead of self-falsifying.**

- **Given** Story 11.5 / AC4.2 built `TC-ArgusAgent-DOCS-001-55` precisely so the caveat *"cannot rot
  in EITHER direction"* — *"the day an operator pushes `v0.1.0` the caveat becomes a NEW falsehood,
  published by the fix that made the old one true."*
- **Given the measured hole** (§0.1 §B): **`-55` reads `_README` and nothing else**
  (`tests/test_built_distribution.py:604`). The tag pin `git+https://…@v0.1.0` appears on **three**
  tracked consumer surfaces — `README.md` (**3** pins), `CHANGELOG.md` (**2**: `:15`, `:625`) and
  `docs/first-run.md` (**1**, `:26`, added by **Story 12.8, after `-55` was written**). Each carries
  a *"does not resolve today"* caveat. **The moment `v0.1.0` exists, `-55` turns RED for README and
  stays silent about the other three pins** — the tag that makes 12.8's line true makes two other
  surfaces false, invisibly. That is 11.5's own stated failure mode, reopened by a file it could not
  have known about.
- **Then** `-55`'s population is **DERIVED by closure** — every registered release surface (or the
  committed corpus) is scanned for the pin pattern, not one hard-coded path — with **both**
  non-vacuity floors: `> 0` surfaces carrying a pin, `> 0` pins found. Both directions are retained
  verbatim (no tag ⇒ caveat required; tag exists ⇒ caveat is the falsehood and must go). **Extend
  `-55`; do not write a second tag-state guard** (AR7).
- **Given the second measured falsehood, which is worse because it is now measurable and MEASURED:**
  `README.md:76-79` and `CHANGELOG.md:627` both say *"This repository's visibility was **NOT
  measured** when this line was written … treat 'public' as the thing to CHECK."* It has now been
  checked: `gh repo view Inan15/Agent-Argus` reports **`visibility: PRIVATE`, `isPrivate: true`**
  (§0 row 4). **Consequence, stated plainly:** the documented install command **cannot resolve for
  any consumer without a credential — tag or no tag** — and a GitHub Release on a private repository
  is not publicly resolvable either.
- **Then** both sentences are **struck-and-corrected in place** (§3.4) to state what was measured, on
  what date, by what command, and **what it costs a consumer**: a read-token-bearing URL, or the
  repository being made public — which is an outward-facing operator act fenced into **AC9**.
  `docs/first-run.md`'s install section, which says **nothing** about authentication today, gains the
  same fact (it is the page a first-time reader meets).
- **Then** the visibility statement is **derived or explicitly marked as a dated measurement with its
  command**, never left as a standing unqualified claim — a repository's visibility can change under
  a document that asserts it.

### AC5: `DF-10-3-A` — the ledger entry that names this story — is resolved against what 12.8 actually shipped

- **Given** `DF-10-3-A` (`deferred-work.md:1750-1770`, severity 🟡, owner **Engineering Lead**,
  `target_story: 12-9-publishing-and-release-surface` — *"the release-surface story that already owns
  `action.yml` and the published consumer contract"*): *"argparse's usage exit code `2` collides with
  the BLOCKED verdict code … a CI step branching on exit `2` reads a typo in its own workflow as
  'Argus found a blocking defect'."* It offered three candidate resolutions, **none chosen**, the
  first being *"map usage errors onto the reserved crash code `1`"*.
- **Given the measurement:** **Story 12.8 / AC8 shipped exactly that first resolution** — the mapping
  lives in `main()` only, `build_parser().parse_args` is byte-identical, `action.yml:110-135` carries
  the corrected map comment, and it is verified live at `de05dec` (a bare `argus` now prints *"the
  command line was rejected by the parser … NO audit ran and NO verdict was produced"*). **The ledger
  was never told**: 12.8 closed `DF-8-4-D` and `DF-10-4-C` and cited three others, and `DF-10-3-A`
  was invisible to it because the entry names **this** story. It stands **OPEN** at `de05dec`,
  describing a defect that no longer exists.
- **Then** it is **CLOSED against the delivered evidence** — naming the commit, the guards and the
  corrected `action.yml` comment — **or** its remaining scope is re-recorded with a reason. Verify by
  **execution** before closing; do not close it on this story's say-so.
- **Then** its `target_story` string is re-recorded: it reads `12-9-publishing-and-release-surface`,
  which **is not this story's key** (`12-9-release-is-published-and-cites-its-gate`). A ledger that
  names a story id the tracker does not have is how a deferral becomes nobody's (AI-E9-8). Correct it
  in the append-only form.
- **Then** `DF-3-4-A`, `DF-10-5-C`, `DF-12-7-A`, `DF-10-3-B` and `DF-10-3-C` are **cited and NOT
  re-filed** (12.7's recorded rule: *"a gap filed twice is a gap that gets closed once and left
  looking open"*). `deferred-work.md`'s diff is **`+n / -0`**, verified programmatically.
- **Then** anything this story defers is filed **with an id, an owner and a `target_story`** — never
  `target_story: NONE` without a named human (AI-E9-8). The outward-facing acts left unperformed
  under AC9 are the obvious candidates: file them **once**, with the named human, and do not also
  leave them implied elsewhere.

### AC6: Every gate and document this story falsifies is CORRECTED, never loosened

**Given** DF-8-5-B's standing rule — *"do not close it by loosening an assertion"* — and the Epic-11
finding that a stale committed guard publishes a false claim (retro §4.4). Handle each and record a
decision for each, **including any you leave unchanged**:

1. **`_bmad-output/design-artifacts/ArgusAgent/architecture.md` §I** — the *"Shipped package,
   measured in place 2026-08-10b"* table (`:637-646`) is **measurably stale in four cells** at
   `de05dec`: *Console scripts* says **three** (`argus`, `argus-agent`, `repo-audit`) and there are
   **four** (`argus-mcp`, 12.6); *Base deps* omits the **nine** grammars 12.5 promoted; *Extras* calls
   `[languages]` a feature when 12.5 made it a **backward-compatibility alias**; *Grounded languages*
   says *"10 — Python (base) + 9 via `[languages]`"*, which is now false in both halves. This is the
   architecture's own statement of **what the release contains** and this is the release story.
   **Strike-and-correct** (§3.4), and prefer a form a guard can hold.
2. **`.github/workflows/release.yml`'s header** (`:3-10`) — *"COMMITTED AND HAS NEVER EXECUTED … no
   tag exists in this repository (`git tag -l` was empty when it was written)"*. TRUE at `de05dec`
   (verified: `git tag -l` empty, `gh release list` empty). It becomes **false the moment AC9 is
   authorised**, and it is a `_RELEASE_SURFACES` member. **Correct it in the same change that
   falsifies it**, and prefer mechanising it the way AC4 mechanises the caveat rather than fixing it
   by hand a second time.
3. **`tests/test_built_distribution.py`** — `-55`'s population (AC4); `-54`'s published module
   figures re-derived against the freshly built artifact; `-56`'s `mechanism_ships` branch
   re-verified as still honest post-12.7. ⚠️ NFR-M1 headroom: **992 / 1200**.
4. **`tests/test_evidence_citation.py`** — AC2's extension. `_EXCLUDED_BY_DESIGN` gains an entry for
   anything deliberately still outside the rule, **with a reason** (`-22` asserts every exclusion
   carries one). **615 / 1200.**
5. **`tests/test_release_surface_honesty.py`** — a `CHANGELOG.md` section registered in
   `_NOTE_SECTIONS` with a **reasoned placement comment** (order pinned by `-16`); any new release
   surface added to **`_RELEASE_SURFACES` and a matching `_RELEASE_SURFACE_PATTERN`, both**, for
   12.7's recorded reason. **794 / 1200.**
6. **`tests/test_release_preflight.py`** — `RELEASE_EDGE_CASE_IDS` closure and `CI_UNREACHABLE`
   (AC7). **698 / 1200.**
7. **`scripts/release_preflight.py`** — AC3's generator and/or AC7's rehearsal phase. **559 / 1200**,
   and it **is** in the NFR-M1 swept population (`git ls-files -z -- '*.py'`).
8. **`README.md` / `CHANGELOG.md` / `docs/first-run.md`** — AC1's guarded claim, AC4's caveats and the
   visibility correction, AC2's status statement. Every removal or restatement is a **§3.4
   strike-not-delete**, matching the form 12.5–12.8 were each reviewed against.
9. **`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`** — AC5. Append-only.
10. **NFR-M1** — every tracked `.py` stays at or under **1200**, swept by
    `tests/test_module_size_ceiling.py` over the re-derived `git ls-files` population. If an addition
    crosses it, apply 12.7/12.8's remedy (a **cohesion split** with a re-export), never shaved lines
    and never a narrowed population.
11. **`tests/test_module_size_ceiling.py::_EXEMPT_BY_DESIGN`** — check the registry is not grown; its
    own rule is that it *"can only shrink"*. `DF-12-1-C`'s exemption was re-recorded by 12.8 with a
    live date and a `NONE — unscheduled` target; `TC-ArgusAgent-MAINT-001-04` requires the ledger and
    the registry strings to agree — **do not desynchronise them while editing the ledger for AC5**.
12. **The dogfood artifact-currency guards (`DF-10-4-D`)** — if this story changes `argus/**`
    composition, follow the bootstrap **in order**: (1) commit the `argus/` delta, (2)
    `python scripts/regenerate_dogfood_artifacts.py`, (3) commit the regenerated artifacts as a
    **separate** commit. The script **refuses by design** if run before (1). **Do not loosen an
    assertion to make them green.** This story is expected to need **no `argus/**` change at all** —
    if you find one, say why in the Dev Agent Record.

### AC7: The release edge cases are re-proven on the channel that ACTUALLY ships, and the index channel's non-shipment is a RECORDED DECISION

- **Given** `epics.md:2471-2473`: *"the release edge cases Story 9.2 pinned (dirty tree, existing
  tag, re-tag, silent overwrite) are **re-proven against the index channel**, which 9.2 could not
  exercise."*
- **Given the measured conflict** (§0 row 7): the index channel **does not ship** — that is not this
  story's choice but a **locked decision restated in four places** (`README.md:92-94`,
  `release.yml:24-29`, `architecture.md:629`, Story 9.2 / D1-D13 at `sprint-status.yaml:350`), and
  `epics.md:2465` is **permissive** (*"the index channel **may** ship independently"*), not
  mandatory. **DN-1** records the decision and its rationale rather than letting the AC quietly go
  unmet.
- **Then** the enumerated space `RELEASE_EDGE_CASE_IDS` (`E1`..`E6`, `scripts/release_preflight.py`)
  is re-proven **against the channel that ships** — the tag + GitHub Release channel — in a
  **rehearsal that publishes nothing**: `--phase validate-tag`, `--phase pre-build` and `--phase
  post-build` driven over a **real local build**, with every refusal and every clearance recorded.
- **Then** the population is **derived from `RELEASE_EDGE_CASE_IDS`**, with a floor asserting the
  rehearsal covered **every** member — a rehearsal that exercised four of six and passed is the
  AI-E8-6 defect (*a guard narrower than its own AC*), which all five Epic-8 stories shipped.
- **Then `E2`'s reachability is re-decided, not inherited.** `CI_UNREACHABLE` records that E2 (*the
  tag already exists*) *"is not reachable from this workflow at all"* because neither trigger creates
  a tag, and calls it a local-tooling guard. **This story is the first that can actually reach it
  locally.** Either exercise it, or re-state `CI_UNREACHABLE`'s note with a date and a reason. Do not
  leave a five-story-old *"unreachable"* claim standing unexamined in the story that publishes.
- **Then `E4` keeps its third outcome.** It needs `GH_TOKEN` to observe the published-release list;
  where it cannot observe it prints **`UNKNOWN`**, never `ok` — *"a guard that cannot observe is not
  a guard"* (`release_preflight.py:30-36`). Do not "fix" an `UNKNOWN` into a clearance.
- **Then** the index channel's non-shipment is written where a reader will meet it: the existing
  **exit condition** at `CHANGELOG.md:629` / `architecture.md:629` is **re-affirmed with a date**, so
  *"interim"* still has a named end rather than becoming permanent by silence.

### AC8: The staged release is COMPLETE, reviewable and reversible — with zero outward-facing acts

- **Then** AC1–AC7 land, the gates are green, and the story records a **RELEASE DOSSIER** in the Dev
  Agent Record containing, at minimum:
  1. the built **sdist and wheel filenames with their sha256** (re-built at the release commit —
     ⚠️ the committed `dist/` on disk is dated **2026-08-08** and predates Epics 10-12 entirely; it is
     `.gitignore`d and is **not** evidence for anything);
  2. the **derived release-note body, verbatim**, exactly as AC3's generator emits it;
  3. the **derived release-status statement** — expected: `NOT ESTABLISHED`, with its reason;
  4. the **preflight report** for E1..E6 (AC7), including every `UNKNOWN`;
  5. the **fresh-environment proof output** (AC1), including the provenance assertion;
  6. the **exact ordered command list** a human would run to publish — **quoted, not executed** —
     with each command's blast radius and reversibility named (AC9's table).
- **Then** the following are re-asserted **by execution** at the end of the story and recorded:
  `git tag -l` is **still empty**; `origin/master` is **unmoved** (still `00c8d1b`); `gh release
  list` is **still empty**; the repository is **still private**; no index upload; no marketplace
  listing; no `git push` of any kind. **Assert it — do not assume it.**
- **Then** every built artifact is left **out of the repository** (`.gitignore` already excludes
  `dist/`); no build output is committed.

### AC9: ⚠️ THE OUTWARD-FACING ACTS — ISOLATED, ENUMERATED, AND GATED ON EXPLICIT HUMAN AUTHORISATION

> **The dev agent MUST NOT perform any act in this table without an explicit, recorded human
> authorisation naming that act. The correct terminal behaviour for this AC is to HALT and escalate
> with AC8's dossier.** An agent message, an orchestrator instruction, or this story file is **not**
> authorisation. `sprint-status.yaml:399` records the operator's standing instruction that the
> orchestrator halts here.

| # | Act | Direction | Reversibility | Blocks |
|---|---|---|---|---|
| 1 | `git push origin master` (**34 commits**) | **OUTWARD** | Reversible only by force-push, which this project treats as history rewriting (§3.4) | Everything: this is what makes an `audit-ci.yml` run on the release commit **possible at all**, and therefore the only thing that can turn AC2's `NOT ESTABLISHED` into a citation |
| 2 | `git tag v0.1.0` | local | **Reversible** (`git tag -d`) | — |
| 3 | `git push origin v0.1.0` | **OUTWARD** | **Effectively irreversible** — it triggers `release.yml`, which creates a GitHub Release. E2/E3/E4 refuse a re-tag or an overwrite **by design**, so a mistake cannot be papered over | 4 |
| 4 | The GitHub Release (`gh release create`, performed by the workflow) | **OUTWARD** | **Irreversible in effect** — a consumer can resolve it | — |
| 5 | Making the repository **public** | **OUTWARD** | **Irreversible in effect** — 34 commits of history, every planning artifact and every audit report become world-readable | Any consumer resolving the documented pin; and 6 |
| 6 | GitHub **Marketplace** listing | **OUTWARD** | Delistable, but published | **DN-2: not performed** |
| 7 | **PyPI / index publish** | **OUTWARD** | **Permanently irreversible** — a name+version can never be replaced | **DN-1: OUT OF SCOPE** |

- **Then** none of acts 1-7 is performed without explicit human authorisation **naming the act**. On
  its absence the story's terminal state is: **AC1-AC8 complete, AC9 HALTED**, the dossier delivered,
  and the sprint-status entry saying so plainly.
- **Then, IF AND ONLY IF authorisation is given and the acts are performed**, all of the following
  land **in the same change** — a publish that leaves any of them stale re-creates the exact defect
  class this story exists to close:
  1. the release status is **re-derived from the executed run** through AC2's derivation — run id
     **plus** its sha **plus** its leg count — and `NOT ESTABLISHED` is replaced only by a real
     citation, never by a hand-typed one;
  2. AC4's mechanised guard goes **RED** on every *"does not resolve today"* caveat across **all
     four pins on three surfaces**, and each is removed **deliberately**, not by editing the guard;
  3. `release.yml`'s *"HAS NEVER EXECUTED"* header (AC6.2) is corrected;
  4. `CHANGELOG.md`'s honesty preamble (`:7-37`) — which states *"Nothing in this file states or
     implies that a release has been published; when one is, **this paragraph gets a URL**"* — gets
     that URL;
  5. the visibility statements (AC4) are re-measured and re-stated;
  6. the full suite, `mypy` and `bandit` are re-run **after** the corrections, and the dogfood
     artifact-currency bootstrap is honoured if `argus/**` composition moved.
- **Then** the *ordering* is binding: **AC4's guard must be committed BEFORE act 2/3.** A tag created
  while only `README.md` is guarded silently converts two other consumer surfaces into published
  falsehoods — which is precisely the failure 11.5 built `-55` to prevent, and precisely what 12.8
  left pointed at this story.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (this project's create-story control, eight-for-eight since Epic 11)

Measured **2026-08-15 on `de05dec`** (HEAD; working tree carries only BMAD artifact edits), by
**execution** — including, for the first time in this epic, **live GitHub API reads through `gh`**,
because two of this story's premises are facts about the world outside the repository. Per the
Epic-11 retro §3.2 refinement, **confirmations are recorded as well as divergences.**

| Premise, as `epics.md:2454-2473` / the tree states it | Re-measured on `de05dec` | Consequence |
|---|---|---|
| *"`release.yml` deliberately abstains from index publish and has **never executed** — `git tag -l` is empty"* | ✅ **HOLDS, all three clauses.** `git tag -l` → empty. `gh release list` → empty. `release.yml:24-29` states the abstention in its own header | **AC6.2 / AC7 / DN-1.** The premise is sound; the *conclusion* the epic draws from it is not (next row) |
| *"the release status cites the **CI run id on the released commit**"* | ❌ **IMPOSSIBLE TODAY.** Latest `audit-ci.yml` run on `master`: **`31341363300`**, `success`, sha **`00c8d1b`**, **2026-08-09**. `origin/master` is **34 commits BEHIND** local `master`; `gh repo view` → `pushedAt: 2026-08-09T23:13:28Z`. **No CI run covers any Epic-10, -11 or -12 sha** | **AC2 — the story's centre of gravity.** The honest output is `NOT ESTABLISHED`; establishing a citation requires an outward-facing push (AC9 act 1). Citing `31341363300` is the exact half-truth `architecture.md:614-616` names, **using this run id as its example** |
| *"Story 11.3 is a hard precondition on the marketplace channel"* | ✅ **PRECONDITION MET** — 11.3 is `done` | **DN-2.** The marketplace channel is blocked by something else entirely (next row) |
| Repository visibility — README/CHANGELOG both say *"was NOT measured … treat 'public' as the thing to CHECK"* | ❌ **MEASURED, AND IT IS THE WORSE CASE.** `gh repo view Inan15/Agent-Argus --json visibility,isPrivate` → **`PRIVATE` / `true`** | **AC4.** The documented pin cannot resolve for **any** consumer without a credential, tag or no tag; Marketplace needs a public repo; a Release on a private repo is not publicly resolvable |
| *"the artifact installs clean in a fresh environment with `argus --help`, a fixture audit and an MCP invocation all succeeding — **proven, not built**"* | ⚠️ **PARTLY CLAIMED, WHOLLY UNGUARDED.** `CHANGELOG.md:23-29` **publishes** the claim for `--help` + a fixture audit (hand-made, 2026-08-08, no MCP). **No committed guard holds it.** `-20` proves imports only. Since then the distribution gained `argus-mcp`, 3 command assets, 9 grammars and a changed exit-code contract | **AC1.** A published claim with no test — this repository's own defect class, on the front-door claim of the release |
| *"**both listings** carry the disclosure"* (FR34) | ✅ **ALREADY HELD.** `pyproject.toml [project].description` (the PyPI listing body) and `action.yml description:` (the Marketplace listing body) both carry it, asserted by `TC-ArgusAgent-DOCS-001-47` over `_DISCLOSURE_SURFACES`, cross-checked against `_RELEASE_SURFACES` | **AC3.** The gap is not the listings — it is the **release-note body**, which is a new surface no guard covers |
| *"the release edge cases … are re-proven **against the index channel**"* | ❌ **CONTRADICTS FOUR LOCKED STATEMENTS.** `README.md:92-94`, `release.yml:24-29`, `architecture.md:629`, `sprint-status.yaml:350` (9.2 / D1-D13) all record that an index publish is irreversible, needs an unprovable credential and is an operator decision. `epics.md:2465` is **permissive**, not mandatory | **AC7 / DN-1.** Re-prove E1-E6 against the channel that ships; record the index decision instead of silently missing the AC |
| `DF-10-3-A` (`target_story: 12-9-…`) — *"argparse's usage exit `2` collides with the BLOCKED verdict code"* | ❌ **ALREADY FIXED, LEDGER NOT TOLD.** Story 12.8 / AC8 shipped the entry's own **first** candidate resolution (map to reserved `1`). Verified live: a bare `argus` prints *"…NO audit ran and NO verdict was produced"*. The entry stands **OPEN**, and its `target_story` names a story key that does not exist | **AC5.** This story owns it: close it against the evidence and correct the id |
| `TC-ArgusAgent-DOCS-001-55` protects the tag caveat *"in both directions"* | ⚠️ **TRUE BUT NARROW — see §0.1 §B.** It reads `README.md` **only** (`test_built_distribution.py:604`). Three surfaces carry the pin | **AC4.** The guard 11.5 built to prevent exactly this transition cannot see two of the three surfaces, one of which **12.8 added** |
| `release.yml`'s release note is checked by something | ❌ **DIVERGES.** `release.yml` is in `_RELEASE_SURFACES`, so `-17` scans it for **over-claims** — nothing checks whether the note's exit-code map, install command or disclosure paraphrase are **true**. 12.8 changed exit-code semantics and this literal did not move | **AC3** |
| 10.1's citation rule covers the consumer-facing surfaces | ❌ **DIVERGES.** `_STATUS_DOCUMENTS` is `sprint-change-proposal-*.md` + `epic-*-retro-*.md` only; `README.md`/`CHANGELOG.md`/`release.yml` are **not excluded with a reason — they are simply outside the guard** | **AC2** |
| architecture §I *"Shipped package"* table is current | ❌ **STALE IN FOUR CELLS** (console scripts 3→4, base deps, extras, grounded languages) | **AC6.1** |
| Test-case id high-water marks | Measured: `DOCS-001-**66**`, `RELEASE-001-**24**`, `MAINT-001-**05**`, `MCP-001-**15**`, `CLI-001-**64**`, `ASSETS-001-**13**`, `SECURITY-001-**32**` | New ids continue from these. **Open no new area** — see §Testing |
| NFR-M1 headroom (files this story touches) | `test_built_distribution.py` **992** · `test_release_note.py` **993** · `test_release_surface_honesty.py` **794** · `test_release_preflight.py` **698** · `test_evidence_citation.py` **615** · `release_preflight.py` **559** · `cli.py` **1139** (61 left) · `test_instrument_disclosure.py` **1179** (21 left) | AC6.10. **`cli.py` and `test_instrument_disclosure.py` are nearly full — 12.8 recorded this deliberately so you would not discover it** |

### §0.1 — THE INVENTORY: what is published about the release, and what actually holds it

**§A — the release channels, measured**

| Channel | Ships today | Guarded by | Decision |
|---|---|---|---|
| **Tag + GitHub Release** (`release.yml`) | ❌ never executed; `git tag -l` empty; `gh release list` empty | E1-E6 in `scripts/release_preflight.py`; `-01`..`-19` | **The only channel this story stages.** AC7 re-proves E1-E6 against it; AC9 acts 2-4 are the outward-facing steps |
| **VCS pin** (`git+…@v0.1.0`) | ⚠️ **documented on 3 surfaces, resolvable by nobody** — the tag does not exist AND the repo is private | `-55`, **README only** | AC4 widens the guard; the credential fact is corrected |
| **PyPI / index** | ❌ never attempted | exit condition recorded at `CHANGELOG.md:629` | **DN-1 — does not ship.** Re-affirm the exit condition with a date |
| **GitHub Marketplace** | ❌ not listed | `action.yml` is in `_RELEASE_SURFACES`; `-47` holds its disclosure | **DN-2 — does not ship** (repo is private). 11.3's precondition is MET; the blocker is elsewhere |

**§B — the tag pin, every tracked occurrence** (`git grep 'git+https://…@v[0-9]'`, excluding story files)

| Surface | Pins | Caveat present | Covered by `-55`? |
|---|---|---|---|
| `README.md` | **3** (`:53`, `:67`, `:103`) | ✅ (`:56-61`, `:71`, `:108-109`) | ✅ **yes — and only this one** |
| `CHANGELOG.md` | **2** (`:15`, `:625`) | ✅ (`:18-21`, inline at `:625`) | ❌ **NO** |
| `docs/first-run.md` | **1** (`:26`) | ✅ (`:32-35`) | ❌ **NO — added by Story 12.8, after `-55` was written** |
| `.github/workflows/release.yml` | 1, **generated at release time** from the tag (`:181`) | n/a — it is the release note | ❌ NO (AC3 derives it) |

**The transition this table describes:** create `v0.1.0` and `-55` turns RED for README's three pins
— correct and intended — while **three further caveats on two other surfaces silently become
published falsehoods.** AC4 closes it, and it must close **before** AC9.

**§C — what a status claim must carry** (`architecture.md:610-627`, Story 10.1 / DN-3)

- a run **URL or id** *and* **the sha it covers**, in the same sentence — a bare id is **not** a
  citation, because it looks like evidence while covering an unknown tree;
- a **local** run is necessary, never sufficient, and is labelled LOCAL;
- **`NOT ESTABLISHED`** is a first-class recordable state — *the governance twin of
  `AUDIT_FAILED`-is-not-a-verdict*. Writing it is compliance, not failure.

### Files to touch

**NEW** — expected to be **tests and release machinery only**. This story is expected to add **no
`argus/**` module and to change no `argus/**` behaviour**; if you find you must, state why in the Dev
Agent Record and honour AC6.12's bootstrap.

| Path (indicative) | Purpose |
|---|---|
| a test module for the fresh-environment artifact proof, **or** additions to `tests/test_built_distribution.py` if that reads better | AC1. Decide by cohesion + NFR-M1 headroom (**992/1200**), and record the choice |

**UPDATE** — read each completely before editing. What it does today and what must be preserved is
stated so the change is a modification, not a rewrite.

| Path | What it does today | What must be preserved |
|---|---|---|
| `.github/workflows/release.yml` (191) | Tag-triggered build + GitHub Release. Header states the abstention and *"HAS NEVER EXECUTED"*. Note body is a **hand-typed string literal** in a `run:` block | ⚠️ **The security design is load-bearing and must not be relaxed:** every untrusted value bound through `env:` and referenced as a quoted shell variable, **never** interpolated into a `run:` body; validated against `_VERSION_TAG` in the **first** step that touches it; third-party actions pinned to **full commit SHAs**. Story 11.3 spent a whole story on this class. `permissions: contents: write` **and nothing else** |
| `scripts/release_preflight.py` (559) | The enumerated E1-E6 space + `CI_UNREACHABLE`; `Refusal` / `Unevaluable` / `None` as three outcomes | **stdlib-only, and it must run on a bare runner BEFORE anything is installed** (`:22-26`). It **may not import `argus`**. `UNKNOWN` is a third outcome and never folds into `ok`. `RELEASE_EDGE_CASE_IDS` is the one named place |
| `tests/test_built_distribution.py` (992) | Builds wheel+sdist locally; `-20` import probe with the `PROBE-INVALID` provenance refusal; `-54` module figures; `-55` tag caveat (**README only**); `-56` documented-vs-shipped commands | `-21`'s provenance refusal shape (**reuse it in AC1**); `-55`'s **both-direction** logic — widen the population, never relax either direction; the `Unevaluable`-not-silent-skip rule |
| `tests/test_evidence_citation.py` (615) | 10.1's rule: `_STATUS_DOCUMENTS` + glob closure + sentence scan + `-21b` positive control | Its **separate marker vocabulary** and the recorded reason for it (`:7-15`) — *"two independent guards sharing one mutable policy table is tighter coupling than fifteen duplicated lines of policy is duplication"*. `_EXCLUDED_BY_DESIGN` entries must carry a **reason** (`-22` asserts it) |
| `tests/test_release_surface_honesty.py` (794) | `_RELEASE_SURFACES` + `_RELEASE_SURFACE_PATTERNS` + `_NOTE_SECTIONS` (order pinned by `-16`) + `_OVER_CLAIMS`; `-63`/`-64` derive `docs/first-run.md`'s verdict/exit claims | Registry **and** pattern, both. `-63`/`-64`'s derivation shape is what AC3 reuses |
| `tests/test_release_preflight.py` (698) | `RELEASE_EDGE_CASE_IDS` ↔ `_HANDLERS` equality (`-01`); a refusing **and** a non-refusing case per handler (AI-E8-6); `_NOT_IMPORTABLE_FROM_DISTRIBUTION` | Both-case-per-handler discipline; the enumeration-is-the-contract property |
| `tests/test_instrument_disclosure.py` (1179) | `_DISCLOSURE_SURFACES`, `_MCP_DISCLOSURE_SURFACES`, `-47`/`-49`/`-50`/`-51` | ⚠️ **21 lines of NFR-M1 headroom.** If AC3 registers the note body here, the file will not take it — apply the cohesion-split remedy, do not shave |
| `README.md` (428) / `CHANGELOG.md` (1010) / `docs/first-run.md` (112) | Consumer surfaces in `_RELEASE_SURFACES`; the *one measurement, one place* rule at `README.md:152-162` | **Strike-not-delete** amendment form; `docs/first-run.md`'s own rule that a documented-but-unexercised command is flagged **at that command** |
| `action.yml` (180) | The complete exit-code map + 12.8's corrected `2`-means comment | The Story 9.2 / `DF-8-4-A` design: the catch-all is a **failure** token, never a guess. **AC5 verifies this comment; it does not rewrite it** |
| `_bmad-output/…/architecture.md` | §H evidence-citation rule; §I shipped-package table (**stale**); §Enforcement | §3.4: strike, never delete. §H's rule text is asserted present by `-23` — **do not reword it away** |
| `_bmad-output/…/deferred-work.md` | Append-only ledger | `+n / -0`. Close `DF-10-3-A`; **cite** `DF-3-4-A`, `DF-10-5-C`, `DF-12-7-A`, `DF-10-3-B`, `DF-10-3-C` |

### Locked decisions this story must cite rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **Version stays `0.1.0`, un-bumped** | Story 9.2 / D1 (`sprint-status.yaml:350`); `epics.md:1669`; `TC-ArgusAgent-DOCS-001-10`; `CHANGELOG.md:614-619` | `__version__` is the envelope `argus_version`; a bump moves the bytes of **every** persisted artifact. **Do not bump** |
| **PyPI is not attempted; the exit condition is named** | `README.md:86-94`; `release.yml:24-29`; `architecture.md:629`; `CHANGELOG.md:629-633` | **DN-1.** Re-affirm with a date; do not re-litigate |
| **AR3 exit-code wire contract** — exactly `0`/`2`/`3`/`1`; `1` is the reserved *no verdict produced* code | `argus/cli.py:5-6`; `action.yml:110-135` | **No fifth code.** AC3 derives the map; AC5 verifies 12.8's fix |
| **FR16 decision table + verdict enum UNTOUCHED** | `epics.md:2312-2314` | This story publishes; it never classifies |
| **§H evidence-citation rule, all three parts** | `architecture.md:610-627` | AC2. `NOT ESTABLISHED` is compliance, not failure |
| **Story 11.3's `action.yml` injection invariance** | 11.3 / AC1-AC3; `test_workflow_input_containment.py` | Any `release.yml` edit keeps every untrusted value in `env:`, quoted, validated first, actions SHA-pinned |
| **`release.yml`'s `permissions: contents: write` and nothing else** | `release.yml:31-33` | Adding a permission is a security change, not a convenience |
| **12.6 / DN-7** — `cli.py` helpers **promoted** to public rather than copied | 12-6 Dev Agent Record | Need a helper? Promote it; never reach through `_`-prefixed API |
| **12.6 / DN-8** — a false registry entry is worse than a coy docstring | 12-6 / 12-7 | Apply verbatim if a `-49` hit appears |
| **`DF-10-4-E`'s lesson** — an exhaustive dispatch **raises** on an unregistered member | 12-5 `_downgrade_sentence`; 12.8 AC4 | Any enumeration AC3/AC7 adds takes the same shape |
| **AI-E11-1** — a guard is adequate only if (i) its observable is named, (ii) the defect is demonstrated to move it **at the real seam**, (iii) at least one adversarial variant is **generated** from the registry it closes over | Epic-11 retro §3.1 | Every new guard here meets it |
| **AI-E9-7 / single-source** — never publish a prose copy of a pinned constant | architecture §Enforcement | Why AC3 derives the note and AC2 derives the citation |
| **AI-E9-8** — never `target_story: NONE` without a named human | Epic-9 retro | AC5 |
| **AI-E8-6** — a guard narrower than its own AC is a breach, not a satisfaction | Epic-8 retro | AC7's floor; AC1's closure over `[project.scripts]` |
| **`DF-8-5-B` / `DF-10-4-D` bootstrap** — commit `argus/` delta → regenerate → commit separately | 12.5-12.8 Debug Logs | AC6.12, if `argus/**` moves at all |
| **§3.4 evidence immutability** — supersede, strike, never erase | architecture §3.4 | Every correction in AC1/AC4/AC5/AC6/AC9 |

### Decisions taken by this story (record these in the Dev Agent Record; do not re-litigate silently)

- **DN-1 — The index (PyPI) channel does NOT ship, and the epic's AC5 is answered rather than
  missed.** `epics.md:2471-2473` asks for the edge cases to be re-proven *"against the index
  channel"*; `epics.md:2465` says the index channel *"**may** ship independently"*. It does not,
  because four committed statements — one of them a Story 9.2 locked decision — record the same
  reasoning: **an index publish is permanently irreversible, needs a credential this repository
  cannot prove exists, and is an operator decision taken with credentials in hand.** Rejected
  alternative: attempt it. That would contradict three *published consumer surfaces* in the act of
  publishing, which is the self-contradiction this epic exists to end. **What is delivered instead**
  (AC7): E1-E6 re-proven against the channel that actually ships, plus a dated re-affirmation of the
  named exit condition so *"interim"* keeps an end.
- **DN-2 — The marketplace channel does NOT ship, and the reason is NOT the one the epic
  anticipated.** `epics.md:2463-2465` gates it on Story 11.3, which is **`done`** — the precondition
  is **met**. The blocker is measured and elsewhere: the repository is **PRIVATE**, and a Marketplace
  listing requires a public repository and a published release. Recorded here so a later reader does
  not conclude 11.3 slipped. Making the repository public is **AC9 act 5** and is not this agent's to
  take.
- **DN-3 — `NOT ESTABLISHED` is the EXPECTED output of AC2 at story time, and it is a pass.** No
  `audit-ci.yml` run covers any Epic-10/11/12 sha. Rejected: citing run `31341363300` — it covers
  `00c8d1b`, **34 commits** behind, and `architecture.md:614-616` uses *this exact run id* as its
  worked example of a half-truth. Rejected: citing a **local** `pytest`/`mypy`/`bandit` run as the
  gate — that is `DF-AUD-APAA-C` verbatim, the defect Story 10.1 exists to have corrected. Local
  figures are recorded and **labelled LOCAL**.
- **DN-4 — The release-note generator must not break `release_preflight.py`'s bare-runner contract,
  and the route is stated with its alternative.** That module is **stdlib-only** and runs *before
  anything is installed*; importing `argus` there would break it. **Recommended:** the generator
  derives its facts by **reading the single-source files** (`argus/verdict/verdict_gate.py`,
  `argus/verdict/negative_assurance.py`, `pyproject.toml`) with stdlib parsing, and a **committed
  test — which may import `argus` freely — asserts the derivation equals the live constants in both
  directions.** That is exactly `-63`/`-64`'s shape for `docs/first-run.md`, and it keeps the runner
  contract intact. **Alternative, permitted if stated and justified:** move the notes step in
  `release.yml` to *after* a `pip install dist/*.whl` so the generator can import `argus` — cheaper
  to write, but it makes the release note depend on a successful install of the thing being released,
  and it puts a second Python environment assumption into the workflow. **Whichever is chosen, state
  it and why in the Dev Agent Record.** Rejected outright: leaving the literal in the `run:` body
  with a test that greps it — that pins prose against prose and goes RED on a rewording rather than
  on a falsehood (12.8 / §7's recorded reasoning, and DN-2 of 12.8 before it).
- **DN-5 — The fresh environment is REAL and OFFLINE, and the probe REFUSES rather than skipping.**
  The test contract is *offline, deterministic, no network* (`test_mcp_server.py`,
  `test_workflow_input_containment.py`), so a plain `pip install dist/*.whl` — which would resolve
  fourteen dependencies from the network — is **not** available, and the existing guard's route does
  not help either: `-20` **extracts** the wheel and prepends the extraction directory to `sys.path`
  (`test_built_distribution.py:228-239`), which **never generates a console-script shim**, so it is
  structurally blind to everything AC1 is about.
  **Recommended:** a temporary virtual environment created with `--system-site-packages`, then the
  wheel installed into it **with `--no-deps`**, so the **distribution** is genuinely installed
  (console-script shims generated, packaged assets unpacked) while its dependencies resolve from the
  already-present environment. That is a genuine artifact test for everything AC1 asserts — entry
  points, packaged data, module layout — and it is honest about what it does **not** test (dependency
  resolution), which must be **stated in the guard's docstring**.
  ⚠️ **Measured environment trap:** this repository's `.venv` has **no `pip`** — it is `uv`-managed
  (`uv 0.11.28` on PATH, `uv.lock` committed at the root). `python -m pip` fails outright. Use
  `uv pip install --no-deps` against the temporary environment, or `python -m venv` +
  `ensurepip` (both offline for a local wheel with `--no-deps`) — and, as elsewhere in this file,
  build with **`python -m build --no-isolation`**, which is the house pattern precisely because
  isolation would provision `flit_core` **from the network** (`test_built_distribution.py:167-174`).
  **Rejected:** synthesising the entry point by hand (`python -c "from argus.cli import main; …"`)
  from the extraction directory — that tests a reconstruction rather than the artifact, which
  AI-E11-1 forbids by name (*at the real seam*), and it is exactly the shim this AC exists to prove.
  **The provenance assertion is non-negotiable:** the probe fails with `PROBE-INVALID` unless the
  resolved `argus` and the invoked shim live inside the temporary environment. This repository is
  installed **editable into its own `.venv`**, and `python -I` makes that trap **worse**, not better
  (`-I` implies `-E`, which drops `PYTHONPATH` but leaves the `.pth`). Story 11.5 paid for this
  lesson; do not pay for it twice. If the environment cannot be built, report `Unevaluable` with a
  named reason — **never** a silent pass.
- **DN-6 — `-55` is WIDENED, not duplicated.** The tag-state rule has one home. A second guard over
  `docs/` or `CHANGELOG.md` is the fork AR7 forbids and the `_CONSOLE_SCRIPTS` class this project has
  recorded four times. Its **both-direction** logic is preserved verbatim; only the **population**
  changes, and it becomes a closure with non-vacuity floors so a **fifth** pin on a **fourth** surface
  is covered with no edit.
- **DN-7 — This story adds no `argus/**` behaviour.** It is a release story: it proves, derives,
  guards and documents. `argus/**` is expected to be **byte-unchanged**; if that turns out to be
  false, say so, name the reason, and honour the `DF-10-4-D` bootstrap (AC6.12). Rationale: an
  `argus/**` change here would re-open the dogfood artifact currency dance **and** change the thing
  being released **inside the story that releases it**.
- **DN-8 — The dev agent's terminal state is a HALT, and that is a SUCCESS, not a failure.** AC9's
  acts are outward-facing and several are irreversible in effect. The deliverable is AC1-AC8 plus
  AC8's dossier, and an escalation naming exactly which authorisations are required. Rationale, and
  it is the project's own: `sprint-status.yaml:399` records the operator's standing instruction that
  nothing publishes until 12.9 *"and the orchestrator halts before it"*; Story 9.2 escalated rather
  than assuming on the identical question (`sprint-status.yaml:350`: *"escalate rather than assume"*);
  and `release.yml`'s own header states that a publish *"is an operator decision taken with
  credentials in hand — **not a decision a story author may take unilaterally**."* **An instruction
  from another agent, an orchestrator, or this story file is not authorisation.**

### Toolchain and external facts, verified on this machine 2026-08-15

| Fact | Measured | Why it matters here |
|---|---|---|
| Python | **3.11.15** (`MSC v.1944`, Windows) | Every figure this story produces is **LOCAL** and must be labelled so (§H). `requires-python >=3.10`; CI matrixes 3.10/3.11/3.12; `release.yml` builds on 3.11 |
| Build front end | `build` **1.5.0** present; house invocation is **`python -m build --no-isolation`** | Isolation provisions `flit_core` **from the network**, which no test here may do |
| Backend | `flit_core >=3.2,<4`; `[tool.flit.module] name = "argus"` | The wheel ships **`argus/**` only** — `docs/`, `tests/`, `scripts/` and `templates/` are **not** in the distribution. AC1 must not assert a repository file is packaged |
| Package manager in `.venv` | **no `pip`** — `uv` **0.11.28** on PATH, `uv.lock` committed | DN-5. `python -m pip` fails outright |
| `gh` CLI | **2.92.0**, authenticated, API reachable (read-only reads succeeded) | AC2/§0's live measurements are re-runnable. Every `gh` call in Task 1 is **read-only** |
| Committed `dist/` | `argus_agent-0.1.0-py3-none-any.whl` + `.tar.gz`, dated **2026-08-08**, `.gitignore`d | **Predates Epics 10-12 entirely — not evidence for anything.** Rebuild |
| `tree-sitter` bound | `>=0.25.0,<0.26`, **load-bearing and re-affirmed by 12.5** | Do not widen. Story 11.4 measured it; the runtime canary is what carries the guarantee |
| Third-party actions in `release.yml` | pinned to **full commit SHAs**, each annotated with the semver tag it resolved from on 2026-08-09 | *"A moved `v4` silently changes what executes inside a job that can write to this repository."* **Re-verify before bumping; never pin to a mutable tag** |

### Previous story intelligence — traps already paid for, do not pay again

- **The three-commit shape 12.8 used is the pattern for any `argus/**` change** (`2826c51` → `6efa306`
  → `de05dec`): commit the `argus/` delta, then `python scripts/regenerate_dogfood_artifacts.py`,
  then commit the regenerated artifacts **separately**. The script **refuses by design** if run
  before the first commit. **This story expects to need none of it (DN-7).**
- **`bandit` `B105` fires on a constant whose NAME contains `token`** — 12.8 measured 19 → 21 and
  renamed to `…_MARKER`/`…_SELECTOR` rather than reaching for this repository's first `# nosec`.
  Name new constants accordingly.
- **NFR-M1 is relieved by a COHESION SPLIT with a re-export, never by shaving lines or narrowing a
  population** (12.7, then 12.8 → `tests/test_help_contract.py`). `cli.py` has **61** lines of
  headroom and `test_instrument_disclosure.py` **21** — recorded by 12.8 so you would not discover
  them mid-edit.
- **The never-executed-branch class has now been recorded FOUR times** (`-49`'s registered-surface
  loop, `_ENTRY_POINT`'s prose, `_CONSOLE_SCRIPTS`, and `-56`'s `mechanism_ships` branch, which
  asserted one thing and then `return`ed past every remaining assertion). **Any branch you add that
  only runs "once the tag exists" is in that class** — AC4's tag-present branch above all. Exercise
  it through the seam, in both states, in the same commit that writes it.
- **A guard that cannot fail is a defect here, and so is a guard on the wrong observable** — 12.8
  found two in its own new work (`README` matching a verdict-shaped probe; the bare phrase
  `first-run` matching a `pipeline.py` comment). Narrow to what the fact actually *is*, and add an
  inline **positive control** proving the narrowed form still bites.
- **`Unevaluable` is a third outcome, never a silent skip, and `UNKNOWN` never becomes `ok`**
  (`release_preflight.py:30-36`). This is the house rule for every guard in this story.
- **Do not rebuild what already ships.** 12.8's §0 found two of the epic's four named cases already
  handled and had to deliver only the difference; 12.4's binding words apply again — *a parallel
  renderer beside the shipped one is a defect, not a delivery.*

### Testing requirements

- **Framework:** `pytest`, offline, deterministic, no network, no sleeps, no real `$HOME`, no LLM.
  Every test names its `TC-ArgusAgent-<AREA>-001-<n>` id in the docstring alongside the AC it serves.
  Every file is opened `encoding="utf-8"` **explicitly** — the artifact tree carries non-ASCII and an
  inherited host locale is the exact defect class that turned run `31322881580` red.
- **Verification areas — DECIDED: open NO new area.** Each concern has an existing home, and 12.5's
  rejection of an invented area (`PACKAGING-001`) applies directly:
  - **the fresh-environment artifact proof → `ArgusAgent-RELEASE`**, continuing from **`-24`**
    (`tests/test_built_distribution.py`, or a cohesion split off it — decide by NFR-M1 headroom and
    record);
  - **the derived release note and the tag/visibility disclosures → `ArgusAgent-DOCS`**, continuing
    from **`-66`**;
  - **the citation rule's extension → `ArgusAgent-DOCS`**, in `tests/test_evidence_citation.py`
    beside `-20`..`-23`, **reusing** its derivation rather than copying its regexes;
  - **the E1-E6 rehearsal → `ArgusAgent-RELEASE`**, in `tests/test_release_preflight.py`, extending
    the enumeration closure;
  - **the MCP-through-the-artifact invocation → `ArgusAgent-MCP`** from **`-15`**, or inside the
    RELEASE guard if it reads better as one artifact probe. **Decide and record**; do not open both.
- **Every guard meets AI-E11-1.** For each new test state the **observable**, demonstrate the defect
  **moving** it (a RED at the **real seam**, not against a reconstruction), and **generate** at least
  one adversarial variant from the registry the guard closes over. The five this story most needs,
  with their reds already located:
  - **AC1's artifact proof** — red by building from a tree with a broken/renamed entry point, and by
    the provenance refusal itself (`-21`'s established positive control);
  - **AC2's citation extension** — red by planting an uncited affirmative status claim on a **real**
    release surface, and green-verified against every honest sentence now on disk, asserted verbatim;
  - **AC3's derived note** — red by changing a verdict token or an exit code and watching the
    rendered note disagree with the live constant;
  - **AC4's widened `-55`** — red **in both directions**: with no tag, delete a caveat from
    `CHANGELOG.md` or `docs/first-run.md` (today those deletions are invisible — that is the defect);
    with a **simulated** tag present, the caveats must be reported as the falsehood. ⚠️ Simulate the
    tag state through the guard's own `_released_versions()` seam — **do not create a real tag to
    test a guard** (AC9);
  - **AC7's rehearsal** — red by driving E1 with a deliberately dirty tree and E5 with a
    tag/version mismatch, both of which already have refusing and non-refusing cases to extend.
- **Non-vacuity floors** on everything that passes by finding nothing (E.3): `> 0` console scripts
  exercised **and** `>= 4` aliases reached; `> 0` surfaces scanned for a pin **and** `> 0` pins found;
  `> 0` claims checked in the rendered note; **all** `RELEASE_EDGE_CASE_IDS` members covered by the
  rehearsal; `> 0` status sentences classified. A rename or a move must turn the guard **RED**, never
  silently green.
- **Full suite + static gates:** `python -m pytest -q` (baseline at `de05dec`: **1527 passed, 0
  failed, 0 errors, 0 skipped**); `python -m mypy argus` (**clean, 83 source files**); `python -m
  bandit -r argus -q` (**19 Low / 0 Medium / 0 High**) **with a stashed-`argus/` control run proving
  no NEW finding** — the raw count alone does not show that (12.5 §4, repeated by 12.6, 12.7 and
  12.8). A suppression must be justified in the Dev Agent Record, never applied quietly. ⚠️ Note the
  `bandit` `B105` trap 12.8 recorded: a constant whose **name** contains `token` fires it — name new
  constants accordingly rather than reaching for this repository's first `# nosec`.
- **Every local figure is labelled LOCAL** and, per §H, **never on its own discharges the evidence
  rule**. Write **CI evidence: NOT ESTABLISHED** where the story states its status (DN-3).

---

## Tasks & Subtasks

- [x] **Task 1: Re-measure §0 and §0.1 before writing code, and record every divergence (AC1-AC9)**
  - [x] Re-run every §0 measurement on the implementation baseline **by execution**, and record the
        figures — **including confirmations**, not only divergences (Epic-11 retro §3.2.2). Confirm
        `baseline_commit` in the frontmatter.
  - [x] Re-run the **live GitHub reads**: `gh run list --workflow=audit-ci.yml --branch master`,
        `gh release list`, `gh repo view … --json visibility,isPrivate,pushedAt`, and
        `git rev-list --left-right --count origin/master...master`. **These are read-only.** If `gh`
        cannot reach the API, record `Unevaluable` with the reason — **never** infer a run id.
  - [x] Confirm by execution: `git tag -l` empty; `gh release list` empty; `-55` reads `README.md`
        only; the four tag pins on three surfaces; `DF-10-3-A`'s described defect no longer
        reproduces (a bare `argus` returns the reserved `1` with the no-verdict sentence).
  - [x] Capture the **RED evidence** for every guard this story adds, **before** any source edit.

- [x] **Task 2: Prove the artifact by using it (AC1, DN-5)**
  - [x] Build sdist+wheel locally into a temporary directory; record filenames + sha256. **Do not
        commit build output** (`dist/` is `.gitignore`d; the committed `dist/` is from 2026-08-08 and
        is not evidence).
  - [x] Install the wheel into a fresh environment; assert **provenance** (`PROBE-INVALID` on
        failure), then exercise **every** `[project.scripts]` alias by closure, `--help` on both
        sub-commands, a **fixture audit** to a real verdict, and a **real MCP JSON-RPC exchange over
        stdio** through the installed shim.
  - [x] Correct `CHANGELOG.md:23-29` to name the guard that now holds the claim, and to include MCP.

- [x] **Task 3: Derive the citation and extend the rule to the surfaces a stranger reads (AC2, DN-3)**
  - [x] Write the single derivation producing either a sha-scoped citation or `NOT ESTABLISHED`.
  - [x] Extend 10.1's rule to `_RELEASE_SURFACES` **without forking its policy tables**; add
        `_EXCLUDED_BY_DESIGN` entries **with reasons** for anything deliberately still outside.
  - [x] Positive control in both directions; floors on surfaces scanned and sentences classified.
  - [x] Write the status statement — expected `NOT ESTABLISHED` — with its reason and the human step.

- [x] **Task 4: Generate the release note instead of typing it (AC3, DN-4)**
  - [x] Move the note body out of the `run:` literal into one named generator; derive version,
        exit-code map, canonical FR34 disclosure, install command and release status.
  - [x] Guard: render and assert every claim against the live source, both directions, `> 0` floor.
  - [x] Record the DN-4 route taken **and its rejected alternative**. Keep `release_preflight.py`
        stdlib-only if that is the route; keep 11.3's injection invariance either way.

- [x] **Task 5: Mechanise the tag-state and visibility disclosures BEFORE anything is tagged (AC4, DN-6)**
  - [x] Widen `-55`'s population to a closure over the registered surfaces; keep **both** directions;
        add both non-vacuity floors; prove RED both ways through the `_released_versions()` seam —
        **without creating a real tag**.
  - [x] Strike-and-correct the two *"visibility was NOT measured"* sentences with the measured result,
        the date, the command, and what it costs a consumer; add the authentication fact to
        `docs/first-run.md`'s install section.

- [x] **Task 6: Ledger and falsified-document sweep (AC5, AC6)**
  - [x] `deferred-work.md`: **close `DF-10-3-A`** against the delivered evidence (verify by execution
        first) and correct its `target_story` id; **cite** `DF-3-4-A`, `DF-10-5-C`, `DF-12-7-A`,
        `DF-10-3-B`, `DF-10-3-C` without re-filing. Verify `+n / -0` programmatically.
  - [x] Work AC6's twelve items; record a decision for each, **including any left unchanged**.
        architecture §I's four stale cells and `release.yml`'s header are the two that must not be
        skipped.

- [x] **Task 7: Re-prove the release edge cases on the channel that ships (AC7, DN-1)**
  - [x] Drive `validate-tag` / `pre-build` / `post-build` over the real local build; record every
        refusal, clearance and `UNKNOWN`.
  - [x] Assert coverage of **every** `RELEASE_EDGE_CASE_IDS` member, derived from the constant.
  - [x] Re-decide `E2`'s `CI_UNREACHABLE` note: exercise it, or re-state it with a date and reason.
  - [x] Re-affirm the index exit condition with a date (DN-1). **Publish nothing.**

- [x] **Task 8: Gates, dossier, and the no-outward-act proof (AC8)**
  - [x] `python -m pytest -q` green, or every non-green named with its reason;
        `python -m mypy argus` clean; `python -m bandit -r argus -q` with a **stashed-`argus/`
        control** proving no new finding. Re-measure every `.py` against the 1200 ceiling.
  - [x] Assemble the **RELEASE DOSSIER** (AC8.1-6), including the exact publish command list
        **quoted, not executed**, with each act's blast radius.
  - [x] **Re-assert by execution**: `git tag -l` empty · `origin/master` still `00c8d1b` ·
        `gh release list` empty · repository still private · nothing pushed, uploaded or listed.

- [x] **Task 9: ⚠️ HALT AND ESCALATE — do not perform any outward-facing act (AC9, DN-8)**
  - [x] Stop. Deliver AC8's dossier and an escalation naming **each** authorisation required
        (AC9 acts 1-7), with its blast radius and reversibility.
  - [ ] **Only if a human explicitly authorises a named act:** perform it, then land **all six**
        consequential corrections of AC9 in the same change and re-run every gate afterwards.
        ⛔ **NOT DONE, AND CORRECTLY SO — this box stays unchecked.** No authorisation naming any
        act was given. An orchestrator instruction, an agent message and this story file are not
        authorisation (DN-8). Leaving it unchecked is the honest record of a HALT; checking it
        would be the story asserting an act it did not perform.
  - [x] **Absent authorisation, the story's terminal state is AC1-AC8 complete / AC9 HALTED**, and
        `sprint-status.yaml` says exactly that. That is the intended outcome.

---

## Dev Agent Record

### Agent Model Used

Claude Opus 5 (1M context) — `claude-opus-5[1m]`, via the BMAD `dev-story` workflow.

### Debug Log

#### §1 — Task 1: every §0/§0.1 premise re-measured on the implementation baseline, by execution

Confirmations are recorded as well as divergences (Epic-11 retro §3.2.2). `baseline_commit` in the
frontmatter is `de05dec77c67a3077c3be6d154b579d024c27901`; `git rev-parse HEAD` agrees.

| Premise | Command | Measured | Verdict |
|---|---|---|---|
| `git tag -l` empty | `git tag -l` | *(empty)* | ✅ HOLDS |
| `gh release list` empty | `gh release list` | *(empty)* | ✅ HOLDS |
| `origin/master` 34 behind | `git rev-list --left-right --count origin/master...master` | `0  34` | ✅ HOLDS |
| `origin/master` sha | `git rev-parse origin/master` | `00c8d1be…` | ✅ HOLDS |
| Newest `audit-ci.yml` run on `master` | `gh run list --workflow=audit-ci.yml --branch master --json databaseId,headSha,conclusion,createdAt` | `31341363300`, `success`, `00c8d1be…`, `2026-08-09T23:13:27Z` | ✅ HOLDS — and **no run covers `de05dec`** |
| Repository visibility | `gh repo view Inan15/Agent-Argus --json visibility,isPrivate,pushedAt` | `PRIVATE` / `true` / `2026-08-09T23:13:28Z` | ✅ HOLDS — worse case confirmed |
| `DF-10-3-A` no longer reproduces | `python -m argus.cli` ; `python -m argus.cli audit --nosuchflag .` | exit **1** both, with *"NO audit ran and NO verdict was produced"* | ✅ ALREADY FIXED (12.8/AC8) |
| `-55` reads README only | read `tests/test_built_distribution.py:604` | `_README` and nothing else | ✅ HOLDS |
| Four pins on three surfaces | `git grep 'git+https' -- README.md CHANGELOG.md docs/ .github/` | README ×3 (`:53`,`:67`,`:103`), CHANGELOG ×2 (`:15`,`:625`), `docs/first-run.md` ×1 (`:26`), `release.yml` ×1 (generated) | ✅ HOLDS |
| `_STATUS_DOCUMENTS` cannot see the consumer surfaces | read `tests/test_evidence_citation.py:65-111` | change-proposals + retros only; README/CHANGELOG/`release.yml` **not excluded with a reason** | ✅ HOLDS |
| architecture §I stale in four cells | read `architecture.md:637-646` | console scripts 3 (are 4); base deps omit 9 grammars; `[languages]` called a feature; *"Python (base) + 9 via `[languages]`"* | ✅ HOLDS |
| Toolchain | `python -V` · `uv --version` · `python -m build --version` · `python -c "import pip"` | 3.11.15 · uv 0.11.28 · build 1.5.0 · **`pip` ABSENT** | ✅ HOLDS (DN-5's trap is real) |
| Baseline suite | `python -m pytest` | **1527 passed** | ✅ HOLDS |

**⚠️ ONE DIVERGENCE FROM §0's OWN EXPECTATION, and it is recorded rather than smoothed over.**
AC2 warned to *"expect real hits the first time you point the rule at `README.md` / `CHANGELOG.md`"*.
Measured, before any edit: **ZERO** live status claims across **all thirteen** registered release
surfaces. The corpus is already honest by 10.1's vocabulary — the gap was that nothing *checked* it.
That makes `-24` a guard that passes by finding nothing, so `-25b` was written to plant the verbatim
historical defect on `README.md`'s **real bytes** and prove the scan reaches these files at all. A
guard that has never been shown to find something proves nothing.

#### §2 — RED evidence, captured at the real seam (AI-E11-1 clause ii), before or during each guard

| Guard | How it was made RED | Observed |
|---|---|---|
| `RELEASE-001-25` (alias closure) | added `argus-fifth = "argus.brand_new:main"` to `[project.scripts]`, rebuilt, re-ran, then reverted (`git diff --stat pyproject.toml` clean) | `AssertionError: console alias 'argus-fifth' points at 'argus.brand_new:main', for which this guard has no registered exerciser` |
| `RELEASE-001-27` (MCP through the shim) | RED **by accident, which is the best kind**: the first draft hand-typed `argus_audit`/`repo_path` and the artifact answered `{"code": -32602, "message": "unknown tool 'argus_audit'"}` | that red is why the tool name and its required argument are now **derived from `tools/list`** |
| `RELEASE-001-28` (provenance) | RED **by measurement, before the guard existed**: the first route (`python -m venv --system-site-packages`) resolved `argus` from `d:\…\ArgusAgent\argus\__init__.py` while everything else passed | the false clean bill of health 11.5 paid for. Now: `PYTHONPATH=<repo>` forces it and the probe exits `PROBE-INVALID` |
| `DOCS-001-25` (derived status) | rendered before the surfaces carried it | `README.md does not carry the derived release-status statement` |
| `DOCS-001-25b` (surface scan) | planted the verbatim `sprint-change-proposal-2026-07-28.md:63` line on README's real bytes | caught, `{'ready for release'}` |
| `DOCS-001-68` (note derivation) | mutated a **mirror** of the single sources: `Verdict.NOT_READY_FOR_RELEASE: 2` → `7`; `INSTRUMENT_STATUS` → `VALIDATED`; `INSTRUMENT_STATUS` renamed | note followed to `7=…`; carried the *other* disclosure; **raised** `no longer declares` |
| `DOCS-001-55b` (tag state) | caveats stripped from `CHANGELOG.md` / `docs/first-run.md` (invisible before this widening); then tag simulated present through the pure seam | both reported; `release.yml`'s *"HAS NEVER EXECUTED"* header reported too. **No real tag was ever created** |
| `DOCS-001-72` (architecture §I) | the stale table itself | RED until all four cells were corrected |
| `RELEASE-001-29` (rehearsal) | dirtied the fixture tree (E1); `--creating-tag` on a fixture that has the tag (E2); `v9.9.9` (E5); empty dist dir (E6); release list injected as `("v0.1.0",)` and `None` (E4) | `REFUSE` / `REFUSE` / `REFUSE` / `REFUSE` / `REFUSE` then `UNKNOWN` |

#### §3 — the finding this story did not expect, and corrected rather than papered over

**The honest `NOT ESTABLISHED` sentence parsed as a well-formed citation.** `-24` excuses a status
claim when the surface *cites an executed gate*, and `_executed_gate_citations` recognises *a run id
together with a sha in one sentence*. The derived statement **must** name the superseded run **with**
its sha — quoting the id alone is exactly the half-truth `architecture.md:614-616` uses that run id to
illustrate. So the most scrupulous sentence this project can write was read as a citation, and any
surface carrying it would have had every *other* unevidenced claim on it excused by evidence that was
never offered.

Corrected at the reader, in the **stricter** direction: `_CITATION_DENIAL_MARKERS`
(`not established`, `superseded`, `does not cover`, `no executed gate`, `half-truth`) disqualify a
sentence from being read as a citation. This can only *tighten* the rule — a citation is what
**excuses** a claim, so recognising fewer of them removes excuses rather than granting them, and adding
a marker to your own sentence costs you the excuse rather than buying one. `-21b` carries the positive
control both ways: the disqualified forms are not citations, and the ordinary form still is. **No
`_STATUS_CLAIMS` entry was trimmed, no `_DENIAL_MARKERS` entry was widened, and no population was
narrowed.**

#### §4 — the second finding, on a surface this story itself created

Registering `scripts/release_notes.py` as a release surface turned `-24` RED on the generator's own
docstring, which quoted `sprint-change-proposal-2026-07-28.md`'s *"…READY FOR RELEASE"* upgrade. **A
real hit, resolved by correcting the sentence, never the detector**: the docstring now reads *"declared
a status that no executed gate supported"* before naming the upgrade, which is both what it means and a
denial the vocabulary already understands. Disposition recorded; nothing was loosened.

#### §5 — measured environment facts that changed the design (DN-5)

* `python -m venv --system-site-packages` from `.venv` inherits the **base** installation's
  `site-packages`, **not `.venv`'s** — so the fourteen dependencies were absent (`ModuleNotFoundError:
  pydantic`) and the base install's `.pth` files came along for the ride. **Rejected.**
* `python -m venv` (default) **fails at `ensurepip`** on this uv-managed interpreter and leaves a
  half-built environment. `--without-pip` is used, deliberately and with the reason recorded.
* The route taken: `python -m venv --without-pip` → `uv pip install --no-deps <wheel>` → one `.pth`
  naming this interpreter's `purelib`. A `.pth` path entry is **not** recursively site-processed, so
  the editable `argus.pth` living there never executes and the repository never reaches `sys.path` —
  and the probe **proves** that rather than assuming it.
* What this does **not** test is stated in the guard's own docstring: **dependency resolution**. The
  test contract is offline; a real `pip install dist/*.whl` would resolve fourteen packages over the
  network.

#### §6 — gates, all LOCAL (architecture.md §H: a local run is necessary, never sufficient)

| Gate | Command | Result | Baseline |
|---|---|---|---|
| Suite | `python -m pytest` | **1543 passed, 0 failed, 0 errors, 0 skipped** in 157s | 1527 (+16 new) |
| Types | `python -m mypy argus` | **Success: no issues found in 83 source files** | clean, 83 |
| Security | `python -m bandit -r argus -q` | **19 Low · 0 Medium · 0 High**, 0 `#nosec` | 19 / 0 / 0 |
| NFR-M1 | swept every `*.py` incl. untracked | worst non-exempt **1181/1200** (`test_built_distribution.py`); new files 610 / 498 / 438 | — |
| `_EXEMPT_BY_DESIGN` | read | **not grown**; `DF-12-1-C`'s entry untouched, so `MAINT-001-04`'s ledger/registry agreement is undisturbed | — |

**The bandit control is stronger here than the stashed-`argus/` run the story asks for, and this is
why:** `git diff --stat -- argus` is **empty**. The scanned population is byte-identical to `de05dec`,
so *"no NEW finding"* is not inferred from a count matching — it is a property of the input. DN-7 holds
and `DF-10-4-D`'s bootstrap is **not owed**: no `argus/**` change, therefore no dogfood regeneration,
and the artifact-currency guards stayed green throughout.

#### §7 — decisions taken, with their rejected alternatives (SOLID/DRY/KISS applied in this codebase's idioms)

1. **AC1's guard is a NEW module, not an extension of `test_built_distribution.py`.** That file was at
   992 and is now 1181 of 1200, and the seam is genuinely different — it measures the **archive**,
   this measures an **installed environment**. Cohesion split, which is 12.7/12.8's recorded NFR-M1
   remedy, applied *before* the ceiling was hit rather than after. It **reuses** that module's build
   (one build per session) and its `[project.scripts]` closure rather than repeating either.
2. **`console_script_aliases()` was PROMOTED, not copied** (12.6 / DN-7). `-56` had the derivation
   inline; two copies of *what the distribution's entry points are* is the `_CONSOLE_SCRIPTS`
   recognizer class recorded four times. `-56` now calls the helper.
3. **AC2 lands as NEW ASSERTIONS in `test_evidence_citation.py` over an IMPORTED population**, not as
   a widened `_STATUS_DOCUMENTS` and not as copied regexes. Widening `_STATUS_DOCUMENTS` would put
   `README.md` and `release.yml` under `-22`'s artifact-directory glob closure — a population they are
   not in — forcing one constant to carry two meanings. Copying the regexes into
   `test_release_surface_honesty.py` is the fork AR7 forbids. The two files keep their **separate
   marker vocabularies** for 10.1's recorded reason; only the population is shared, by import, from the
   file that owns it.
4. **DN-4: the RECOMMENDED route was taken.** `scripts/release_notes.py` is stdlib-only, never imports
   `argus`, and reads the single sources as text with `ast`; `tests/test_release_note_body.py` imports
   `argus` freely and asserts the two agree in both directions. **Rejected alternative, stated:**
   moving the notes step after `pip install dist/*.whl` so the generator could import `argus` — cheaper
   to write, but it makes the release note depend on a successful install of the thing being released
   and puts a second Python-environment assumption into a job holding `contents: write`. `-70` asserts
   the rejected route was not taken (no `pip install dist/` in the workflow, generator before publish).
   **Rejected outright:** leaving the literal in the `run:` body with a test that greps it — that pins
   prose against prose and goes RED on a rewording rather than on a falsehood.
5. **The generator is a NEW module, not a fifth concern inside `release_preflight.py`.** AC6.7 permits
   either (*"and/or"*). `release_preflight` has one responsibility — the enumerated refusal space —
   and a note renderer is a different one (SRP). Both are stdlib-only and `release_notes` **reuses**
   `release_preflight`'s `read_pyproject_version`, `normalize_tag` and **`check_e5_tag_version_mismatch`
   itself** rather than restating the tag/version rule (AR7).
6. **The release status is a PURE function of an injected observation**, mirroring `PreflightContext`.
   The dated `RECORDED_GATE_OBSERVATION` is the one place the measurement lives; the impure `gh` read
   is at the edge and is **not** a test dependency. `-25` asks the derivation about **live `HEAD`**, so
   the day a run covers the released commit the statement changes and every surface goes RED until it
   is re-rendered — which is AC9's binding ordering, mechanised.
7. **AC3's FR34 registration is HERE, not in `test_instrument_disclosure.py`.** That file is at
   **1179/1200**, and — the stronger reason — its `_DISCLOSURE_SURFACES` is a tuple of `_Surface`
   records keyed by **committed file path** with a `form` field, while the note body is a **rendered
   string with no path**. Forcing it in would change a shipped registry's meaning for one member, and
   relieving the ceiling to do it would mean splitting a 1179-line guard as a side effect of a release
   story. The body is held to the **same two-sided property `-50` states**, importing the same
   constants and the same over-claim detector. One vocabulary, one authority, a second population.
8. **`-55` was WIDENED, never duplicated (DN-6).** Its both-direction logic is preserved verbatim; only
   the population changed, into a closure over the imported `_RELEASE_SURFACES` with two non-vacuity
   floors. `release.yml`'s *"HAS NEVER EXECUTED"* header (AC6.2) was **folded into the same rule**
   rather than given a second guard — it is the same rot in the same two directions on a surface that
   is not a pin. The tag-present branch is exercised through the pure seam; **no tag was created.**
9. **`scripts/release_notes.py` is registered in `_RELEASE_SURFACES` with an EXACT pattern.** A
   directory-wide `scripts/*.py` glob was considered and declined: `scripts/` also holds the preflight
   and the dogfood regenerator, which publish nothing, and dragging them in would force registry
   entries whose only content is *"this is not a publication surface"*. The **rendered** body — the
   half a file scan cannot reach — is separately held by `-67`.
10. **The new CHANGELOG section is placed LAST among `## Unreleased`, and the promotion was declined on
    the honest reading.** The case for promoting it is real (it states whether *any* claim in the note
    is backed by an executed gate). It is declined under the registry's own test, applied the way 12.2's
    egress entry was: this entry *"changes no default, no exit code, no verdict and no byte on any
    invocation that existed before this release"*, and every section above it can move something a
    consumer observes. The frame is not deferred by the placement — the honesty preamble at the head of
    the file carries the same derived sentence, so a reader meets it before any section at all.
11. **The MCP artifact probe is registered in `ArgusAgent-RELEASE`, not `ArgusAgent-MCP`** (§Testing
    asked for a decision and forbade opening both). It is one artifact probe among four, not a protocol
    test; the protocol is 12.6's and is covered at `MCP-001-01`..`-15`.
12. **`DOCS-001-72` (architecture §I) is homed in `test_installed_artifact.py`.** The claim is about the
    shipped package, which is that module's subject; its natural neighbour is at 1181/1200. Mixed areas
    in one module already have precedent in `test_built_distribution.py`.

**Conflict-resolution note (project context wins).** Two epic-level expectations were not met as
written, and each is answered by a recorded decision rather than quietly missed: `epics.md:2471-2473`'s
*"re-proven against the index channel"* → **DN-1**, because four committed statements (one a Story 9.2
locked decision) record that an index publish is permanently irreversible and needs a credential this
repository cannot prove exists, and `epics.md:2465` is permissive; and `epics.md:2463-2465`'s
marketplace gating → **DN-2**, whose precondition (Story 11.3) is **met** while the actual blocker is
the measured private repository. Where the epic's prose and a locked project decision conflicted, the
project decision won and the divergence is written down.

### Completion Notes

**Terminal state: AC1–AC8 COMPLETE · AC9 HALTED, pending explicit human authorisation. That is the
intended outcome (DN-8), not a failure.** No outward-facing act was performed, and it is re-asserted by
execution below rather than assumed.

- **AC1 ✅** — `tests/test_installed_artifact.py` (`RELEASE-001-25`..`-28`) builds sdist+wheel, installs
  the **wheel** into a genuinely fresh environment, **refuses with `PROBE-INVALID`** unless `argus`
  resolves inside it, then exercises **every** `[project.scripts]` alias derived by closure (four
  today; a fifth reusing a known target needs no edit, a fifth with a new target **raises**),
  `argus --help` and `argus audit --help`, a **fixture audit to a real verdict** whose stdout summary
  line parses and whose exit code equals `exit_code_for_verdict`, and a **real MCP JSON-RPC exchange**
  through the installed `argus-mcp` shim with the tool name and its required argument **derived from
  `tools/list`**. Missing tooling produces a named `release_preflight.Unevaluable`, never a silent
  pass. `CHANGELOG.md`'s hand-made claim is struck and replaced by one naming the guard and stating
  MCP.
- **AC2 ✅** — one derivation (`derive_release_status`); `README.md` and `CHANGELOG.md` render its value
  verbatim; `-24`/`-25`/`-25b` extend 10.1's rule to the imported release-surface population with both
  floors and a positive control on real bytes. **Status: `NOT ESTABLISHED`**, with its reason, the
  superseded run named **with its sha**, and the exact human step. Citing `31341363300` did not happen
  and cannot: `-25` asserts the statement names it as SUPERSEDED, and the citation reader now refuses
  to read that as a citation.
- **AC3 ✅** — the note is generated; the `run:` literal is gone and `-69` asserts each of its three
  transcribed facts is absent from the workflow text; `-67`/`-68` render and check every claim against
  the live source, both ways, with a floor; `-70` pins the bare-runner contract.
- **AC4 ✅** — `-55` widened to a closure with both floors; `-55b` proves both directions through the
  seam without creating a tag; the visibility statement is measured, dated, carries its command, states
  what it costs a consumer, and is single-sourced across **three** surfaces plus the release note
  (`-71`), with both *"was NOT measured"* admissions struck rather than deleted.
- **AC5 ✅** — `DF-10-3-A` **CLOSED** against 12.8/AC8's delivered remedy, **verified by execution
  first**; its non-existent `target_story` id corrected in append-only form; `DF-12-9-A` files the seven
  unperformed acts **once**, with a named human; `DF-3-4-A`, `DF-10-5-C`, `DF-12-7-A`, `DF-10-3-B`,
  `DF-10-3-C` cited and **not** re-filed; ledger diff **`+95 / -0`**, verified programmatically.
- **AC6 ✅** — all twelve items dispositioned (§7 and the table below); architecture §I's four stale
  cells struck-and-corrected **and now held by a guard**; `release.yml`'s header mechanised rather than
  hand-fixed; NFR-M1 respected without shaving a line or narrowing a population.
- **AC7 ✅** — `RELEASE-001-29` rehearses all three phases through the real CLI over a real local build
  and asserts coverage of **every** `RELEASE_EDGE_CASE_IDS` member; E4's three outcomes all exercised
  and `UNKNOWN` never becomes `ok`; E2 **re-decided and driven to a refusal locally**, with
  `CI_UNREACHABLE` re-stated with a date and a reason (`-30`); the index exit condition re-affirmed with
  a date in three places (DN-1).
- **AC8 ✅** — dossier below; nothing built was committed (`dist/` is `.gitignore`d and the artifacts
  were written to a temporary directory).
- **AC9 ⛔ HALTED** — see the escalation.

**AC6's twelve items, each with a decision — including the ones left unchanged:**

| # | Item | Decision |
|---|---|---|
| 1 | architecture §I table | **CORRECTED**, struck-not-deleted, and now derived by `DOCS-001-72` |
| 2 | `release.yml` header | **MECHANISED** into `-55`'s rule (AC4's shape), not hand-fixed |
| 3 | `test_built_distribution.py` | `-55` widened; `-54` re-derived against the fresh build (green); `-56`'s `mechanism_ships` branch re-verified honest post-12.7 and now calls the promoted alias helper |
| 4 | `test_evidence_citation.py` | AC2's extension; `_EXCLUDED_BY_DESIGN` gains an entry **with a reason** recording that the consumer surfaces are now *inside* the rule; `_STATUS_STATEMENT_NOT_REQUIRED` gives every non-stating surface a reason |
| 5 | `test_release_surface_honesty.py` | new `_NOTE_SECTIONS` entry with a reasoned placement comment; `scripts/release_notes.py` added to **both** `_RELEASE_SURFACES` and `_RELEASE_SURFACE_PATTERNS` |
| 6 | `test_release_preflight.py` | AC7's rehearsal + the `CI_UNREACHABLE` re-decision |
| 7 | `scripts/release_preflight.py` | **UNCHANGED except `CI_UNREACHABLE`'s dated re-statement.** The generator went to a new module (SRP); 565/1200 |
| 8 | `README.md` / `CHANGELOG.md` / `docs/first-run.md` | strike-and-correct throughout; nothing deleted |
| 9 | `deferred-work.md` | append-only, `+95 / -0` |
| 10 | NFR-M1 | worst non-exempt 1181/1200; relieved by a **cohesion split**, never by shaving |
| 11 | `_EXEMPT_BY_DESIGN` | **LEFT UNCHANGED** — not grown, and `DF-12-1-C`'s strings untouched so `MAINT-001-04`'s agreement is undisturbed |
| 12 | Dogfood currency (`DF-10-4-D`) | **NOT TRIGGERED.** `argus/**` is byte-unchanged (DN-7); no regeneration owed, none performed |

---

## 🚦 RELEASE DOSSIER (AC8) — everything a human needs to authorise, and nothing performed

### 1. The artifacts (rebuilt at story time, into a temp directory, never committed)

```
sha256  d51f645585d47461348d93b44c8da6f3499985cbbef2a57efa2af88bc3e1e15f
        argus_agent-0.1.0-py3-none-any.whl      471 249 bytes
sha256  1af61caa50126474a48cc2bace2c9f976f9f588867cd77cc1db6f3209c436c0f
        argus_agent-0.1.0.tar.gz                416 906 bytes
built by: python -m build --no-isolation --outdir <tmp> .
```

⚠️ **Stated honestly:** these were built from the **working tree** (`de05dec` + this story's
uncommitted changes), because the story's own work cannot be committed by this agent. `argus/**` is
**byte-identical to `de05dec`**, so the shipped module content is unchanged; the wheel's `METADATA`
does differ, because `readme = "README.md"` embeds this story's README corrections. The committed
`dist/` on disk is dated **2026-08-08**, predates Epics 10–12 entirely and is **not evidence for
anything**. Re-build at the real release commit before publishing.

### 2. The derived release-note body, verbatim, exactly as the generator emits it

```
Source distribution and wheel for `argus-agent` v0.1.0.

Install directly from this repository at this tag:

    pip install "argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0"

Repository visibility, MEASURED 2026-08-15 by `gh repo view Inan15/Agent-Argus --json visibility,isPrivate` -> `PRIVATE` / `isPrivate: true`. What that costs a consumer, stated plainly: while it stays private the pinned install cannot resolve for anybody — tag or no tag — without a read credential carried in the URL (`git+https://<credential>@github.com/...`), and a GitHub Release on a private repository is not publicly resolvable either. Making the repository public is an outward-facing operator act that has not been taken. This is a dated measurement, not a standing claim: re-run the command above before relying on it.

The exit-code wire contract is UNCHANGED by this release: 0=RELEASE_READY, 1=no verdict produced, 2=NOT_READY_FOR_RELEASE, 3=INSUFFICIENT_COVERAGE. Exit 1 is reserved and is never a verdict — a run that produced no verdict made no statement about your code. See CHANGELOG.md for the full consumer contract.

CI evidence: NOT ESTABLISHED. No executed gate covers the commit being released — the most recent `audit-ci.yml` run is run 31341363300, which covers sha 00c8d1b, 34 commits behind the commit being released and therefore evidences a different tree; a run id quoted without the sha it covers is a half-truth, so it is named here as SUPERSEDED rather than cited. Observed 2026-08-15 through the GitHub API. The human step that would establish one, and the only one: push `master` to `origin` and let `audit-ci.yml` run to success on the released commit, then re-derive this sentence from that run. A local `pytest`/`mypy`/`bandit` run is necessary, not sufficient, and is recorded as LOCAL (architecture.md §H).

This release makes no assurance claim about Argus itself. Argus's dogfood run is a self-audit and is not independent corroboration.

Instrument status: Argus's own finding precision has not been independently validated. Its findings rest on the Argus dogfood corpus, a self-audit of this repository with no human true-positive/false-positive adjudication behind it. This notice is removed only when Epic 13's human adjudication clears the >=80% precision gate; nothing else removes it.
```

Reproduce with `python scripts/release_notes.py --tag v0.1.0` (2 329 characters). **Every sentence in
it is derived**; the generator types no fact.

### 3. The derived release status

> **CI evidence: `NOT ESTABLISHED`.** *(expected — DN-3, and it is a pass, not a gap)*

Reason: no `audit-ci.yml` run covers `de05dec` or any Epic-10/11/12 sha, because `origin/master` is
**34 commits behind** local `master` and every one of those commits is local only. The superseded run
is stated as what it is: **run `31341363300`, sha `00c8d1b`, `success`, 2026-08-09** — named, never
cited. The exact human step that would establish a citation: **push `master` to `origin`, let
`audit-ci.yml` run to success on the released commit, and re-derive.** That push is **AC9 act 1**.

### 4. The preflight report for E1..E6 (executed, real state, publishing nothing)

```
$ python scripts/release_preflight.py --phase validate-tag --tag v0.1.0
tag v0.1.0 has the expected v<major>.<minor>.<patch> shape.

$ python scripts/release_preflight.py --phase pre-build --tag v0.1.0
release preflight [pre-build] for tag v0.1.0 (pyproject version 0.1.0)
  E1 working tree dirty at build time                           REFUSE
  E2 the tag already exists                                     ok (not reachable from this workflow)
  E3 a re-tag / tag move is attempted                           ok
  E4 the version already has a published artifact for that target ok
  E5 the tag does not match the pyproject.toml version          ok
RELEASE REFUSED:
  [E1] 23 uncommitted path(s) in the working tree (…). Commit or stash them;
       the artifact must be reproducible from the tag.

$ python scripts/release_preflight.py --phase post-build --tag v0.1.0 --dist-dir <tmp>
release preflight [post-build] for tag v0.1.0 (pyproject version 0.1.0)
  E6 the build produced no artifact, or only one of sdist/wheel  ok
all enumerated release edge cases cleared.
```

**Every outcome, read honestly.** **E1 REFUSES** — the tree carries this story's own uncommitted work,
which is itself a reason act 2/3 cannot be taken from this state. **E2 `ok` + the reachability
disclosure**, and it was separately **driven to a refusal** by `RELEASE-001-29` against a throwaway
fixture repository. **E4 `ok`** here is a genuine *asked-and-there-are-none* clearance: the live
`gh release list` returned empty (read-only). Its **`UNKNOWN`** third outcome is exercised in the
rehearsal with the list injected as `None`, and it never folds into `ok`. **No `UNKNOWN` was converted
into a clearance anywhere.**

### 5. The fresh-environment proof (AC1), including the provenance assertion

```
$ python -m pytest tests/test_installed_artifact.py -v
tests/test_installed_artifact.py::…RELEASE_001_25_every_console_script_resolves_and_runs   PASSED
tests/test_installed_artifact.py::…RELEASE_001_26_a_fixture_audit_reaches_a_real_verdict   PASSED
tests/test_installed_artifact.py::…RELEASE_001_27_the_mcp_shim_completes_a_jsonrpc_exchange PASSED
tests/test_installed_artifact.py::…RELEASE_001_28_the_probe_refuses_and_never_skips_silently PASSED
tests/test_installed_artifact.py::…DOCS_001_72_the_architecture_package_table_matches…      PASSED
5 passed
```

Measured inside the fresh environment (identical run reproduced by hand for the record):

```
shims generated : argus.exe · argus-agent.exe · repo-audit.exe · argus-mcp.exe   (4 of 4, by closure)
provenance      : <env>\Lib\site-packages\argus\__init__.py                       (INSIDE the env ✅)
provenance ctrl : PYTHONPATH=<repo>  ->  SystemExit: PROBE-INVALID: argus resolved from
                  d:\…\ArgusAgent\argus\__init__.py, which is NOT inside the fresh environment
argus --help    : "usage: argus [-h] {audit,install-commands} ..."                exit 0
fixture audit   : verdict=NOT_READY_FOR_RELEASE deep_ratio=1/2 blocking_findings=1
                  assessed_deep_ratio=1 scope=application held_out=1              exit 2  (= AR3 map ✅)
argus-mcp       : initialize -> serverInfo {"name":"argus","version":"0.1.0"}
                  tools/list -> ["audit_repository"]
                  tools/call -> content[0].text opens with the FR18 summary line   exit 0
```

### 6. The exact ordered publish commands — ⚠️ **QUOTED, NOT EXECUTED**

| # | Command | Direction | Blast radius | Reversibility |
|---|---|---|---|---|
| 0 | *(prerequisite)* commit this story's work; `git status --porcelain` must be empty | local | none — but **E1 refuses to build from a dirty tree**, so nothing below can proceed without it | trivially reversible |
| 1 | `git push origin master` | **OUTWARD** | **34 commits** of history, every planning artifact and every audit report reach `origin`. This is the ONLY act that makes an `audit-ci.yml` run on the release commit possible, and therefore the only thing that can turn AC2's `NOT ESTABLISHED` into a citation | reversible **only by force-push**, which this project treats as history rewriting (§3.4) |
| 2 | `python scripts/release_preflight.py --phase pre-build --tag v0.1.0 --creating-tag` | local, read-only | none — it refuses, it never repairs | n/a |
| 3 | `git tag v0.1.0` | **local** | nothing leaves the machine. ⚠️ It immediately turns `DOCS-001-55` **RED on all four pins across three surfaces** — by design (AC4). Remove each caveat **deliberately**; never edit the guard | **reversible** (`git tag -d v0.1.0`) |
| 4 | `git push origin v0.1.0` | **OUTWARD** | triggers `release.yml`, which builds and creates the GitHub Release | **effectively irreversible** — E2/E3/E4 refuse a re-tag or an overwrite *by design*, so a mistake cannot be papered over |
| 5 | *(performed BY the workflow)* `gh release create "$TAG" --title … --verify-tag --notes-file release-note.md dist/*` | **OUTWARD** | a consumer can resolve the artifacts | **irreversible in effect** |
| 6 | `gh repo edit Inan15/Agent-Argus --visibility public` | **OUTWARD** | 34 commits of history, every planning artifact and every audit report become **world-readable**. Required before any consumer can resolve the documented pin, and before act 7 | **irreversible in effect** |
| 7 | GitHub **Marketplace** listing (manual, via the Releases UI) | **OUTWARD** | **DN-2 — NOT PERFORMED.** Blocked by act 6, not by Story 11.3 (which is `done`) | delistable, but published |
| 8 | PyPI / index publish | **OUTWARD** | **DN-1 — OUT OF SCOPE.** A released name+version can never be replaced | **permanently irreversible** |

**If and only if acts 1–5 are authorised and performed, all six of these land in the same change**
(AC9), and none may be skipped: (i) re-derive the status from the executed run — run id **plus** sha
**plus** leg count — by updating `RECORDED_GATE_OBSERVATION`, never by typing a sentence; (ii) remove
all four *"does not resolve today"* caveats deliberately as `-55` goes red; (iii) correct `release.yml`'s
*"HAS NEVER EXECUTED"* header, which `-55` will also flag; (iv) give `CHANGELOG.md`'s honesty preamble
the release **URL** it promises; (v) re-measure and re-state the visibility sentence; (vi) re-run
`pytest` / `mypy` / `bandit` **after** the corrections, and honour the `DF-10-4-D` bootstrap if
`argus/**` moved.

### 7. Re-asserted BY EXECUTION at hand-off — nothing outward-facing happened

```
$ git tag -l                                              -> (empty)
$ git rev-parse origin/master                             -> 00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0   (unmoved)
$ git rev-list --left-right --count origin/master...master-> 0   34                                     (unchanged)
$ gh release list                                         -> (empty)
$ gh repo view Inan15/Agent-Argus --json visibility,isPrivate,pushedAt
  {"isPrivate":true,"pushedAt":"2026-08-09T23:13:28Z","visibility":"PRIVATE"}                            (still private)
$ git reflog -1                                           -> de05dec HEAD@{0}: commit: docs(story-12-8)… (no new commit)
```

No `git push` of any kind. No tag. No GitHub Release. No index upload. No marketplace listing. No
repository-visibility change. Every `gh` call made by this story was a **read**. Every build artifact
was written to a temporary directory outside the repository; `dist/` is `.gitignore`d and nothing built
was committed.

---

## ⛔ ESCALATION (AC9 / DN-8) — the authorisations this story cannot give itself

**No act in the table above was performed, and none may be without an explicit, recorded human
authorisation naming that act.** An orchestrator instruction, an agent message and this story file are
**not** authorisation. The project's own record says so three times: `sprint-status.yaml:399`'s standing
operator instruction that *"NO STORY IN THIS EPIC PUBLISHES ANYTHING until 12.9, and the orchestrator
halts before it"*; Story 9.2's *"escalate rather than assume"* on the identical question; and
`release.yml`'s own header — a publish *"is an operator decision taken with credentials in hand — **not
a decision a story author may take unilaterally**."*

**Required, act by act:** (1) push `master`; (2) create `v0.1.0`; (3) push `v0.1.0`; (4) the GitHub
Release the workflow then creates; (5) make the repository public; (6) the Marketplace listing —
**DN-2, not sought**; (7) a PyPI publish — **DN-1, out of scope**. Filed once as **`DF-12-9-A`**, owner
**Engineering Lead**.

**The ordering is already safe.** AC4's widened guard is committed **before** any tag can exist, so act
(2) turns all four pins on three surfaces RED at once instead of converting two of them into published
falsehoods invisibly. That was the whole point of doing AC4 before AC9, and it is done.

### File List

**NEW**

- `scripts/release_notes.py` — the release-status derivation and the release-note generator; stdlib-only, never imports `argus` (498)
- `tests/test_installed_artifact.py` — `TC-ArgusAgent-RELEASE-001-25`..`-28`, `TC-ArgusAgent-DOCS-001-72` (610)
- `tests/test_release_note_body.py` — `TC-ArgusAgent-DOCS-001-67`..`-71` (438)

**MODIFIED**

- `.github/workflows/release.yml` — the hand-typed note literal replaced by a generator invocation; `--notes-file`; injection invariance and `permissions:` untouched
- `scripts/release_preflight.py` — `CI_UNREACHABLE["E2"]` re-stated with a date and a reason (AC7); nothing else
- `tests/test_built_distribution.py` — `console_script_aliases()` promoted; `-55` widened to a closure; `-55b` added; `-56` now calls the promoted helper
- `tests/test_evidence_citation.py` — `-24`, `-25`, `-25b`; `_CITATION_DENIAL_MARKERS`; `_EXCLUDED_BY_DESIGN`, `_STATUS_STATEMENT_REQUIRED` / `_NOT_REQUIRED`
- `tests/test_release_preflight.py` — `-29` (the E1..E6 rehearsal), `-30` (the `CI_UNREACHABLE` re-decision)
- `tests/test_release_surface_honesty.py` — the new `_NOTE_SECTIONS` entry with its reasoned placement; `scripts/release_notes.py` in `_RELEASE_SURFACES` **and** `_RELEASE_SURFACE_PATTERNS`
- `README.md` — visibility struck-and-corrected; the derived status statement; the index exit condition re-affirmed with a date
- `CHANGELOG.md` — the unguarded fresh-env claim struck and replaced; the derived status statement; visibility corrected; exit condition re-affirmed; the new `### Changed` section
- `docs/first-run.md` — the tag caveat now says how it was established; the visibility/authentication fact added at the command
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §I's four stale cells struck-and-corrected; the index exit condition re-affirmed with a date
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — append-only, `+95 / -0`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — `12-9-…: ready-for-dev → review`; `last_updated`
- `_bmad-output/design-artifacts/ArgusAgent/stories/12-9-release-is-published-and-cites-its-gate.md` — this record

**UNCHANGED, and asserted so:** `argus/**` (byte-identical to `de05dec`, DN-7), `action.yml` (AC5
verifies its map comment; it does not rewrite it), `pyproject.toml`, `dist/`.

### Review Findings

_To be completed by the review agent._

## Change Log

| Date | Change |
|---|---|
| 2026-08-15 | **`dev-story` — AC1–AC8 COMPLETE, AC9 HALTED. `ready-for-dev` → `review`.** The terminal state is the intended one (DN-8): **no outward-facing act was performed**, and that is re-asserted BY EXECUTION at hand-off — `git tag -l` empty, `origin/master` unmoved at `00c8d1b` (0/34), `gh release list` empty, repository still `PRIVATE`, no new commit in the reflog. Every `gh` call this story made was a **read**. **Delivered.** *(AC1)* `tests/test_installed_artifact.py` proves the artifact by USING it from a genuinely installed distribution — the wheel installed into a fresh env, a `PROBE-INVALID` refusal unless `argus` resolves inside it, **every** `[project.scripts]` alias by closure (a fifth with a new target **raises**), both `--help` surfaces, a fixture audit to a real verdict whose exit code equals the AR3 map, and a real MCP JSON-RPC exchange through the installed `argus-mcp` shim with the tool name and required argument **derived from `tools/list`**; `CHANGELOG.md:23-29`'s unguarded hand-made claim is struck and replaced by one naming that guard and stating MCP. *(AC2)* one derivation computes the release status; README and CHANGELOG render **that value**; the rule now reaches the imported `_RELEASE_SURFACES` population without forking 10.1's policy tables. **Status: `NOT ESTABLISHED`** with its reason, the superseded run named **with its sha**, and the exact human step — citing `31341363300` is forbidden and the guard now enforces it. *(AC3)* the note is **generated**: the `run:` literal is gone, every claim derived (version, AR3 map incl. the reserved `1`, canonical FR34 disclosure selected by `INSTRUMENT_STATUS`, install command, AC2's status), **DN-4's recommended route taken** — stdlib `ast`, generator never imports `argus`, runs before any install; the rejected alternative is recorded and `-70` asserts it was not taken. *(AC4)* `-55` **widened** from README-only to a closure over the registered surfaces with both floors, both directions proven **through the seam without creating a tag**, `release.yml`'s *"HAS NEVER EXECUTED"* header folded into the same rule; the visibility falsehood **measured, dated, single-sourced** across three surfaces + the note. *(AC5)* `DF-10-3-A` **CLOSED** against 12.8/AC8's remedy, verified by execution first, its non-existent `target_story` corrected append-only; `DF-12-9-A` files the seven unperformed acts once with a named human; five entries cited and **not** re-filed; ledger diff **`+95 / -0`**. *(AC6)* all twelve items dispositioned; architecture §I's four stale cells corrected **and now held by a guard**; `_EXEMPT_BY_DESIGN` **not grown**. *(AC7)* every `RELEASE_EDGE_CASE_IDS` member rehearsed through the real CLI over a real local build; E4's three outcomes all exercised and `UNKNOWN` never becomes `ok`; **E2 re-decided and driven to a refusal locally**, `CI_UNREACHABLE` re-stated with a date; the index exit condition re-affirmed with a date in three places (DN-1). *(AC8)* full dossier in the Dev Agent Record with the publish commands **quoted, not executed**. **Two findings the story did not expect and CORRECTED rather than papered over:** (a) the honest `NOT ESTABLISHED` sentence itself parsed as a well-formed citation — it must name the superseded run *with* its sha — which would have excused every other claim on that surface; the citation reader was made **stricter** (`_CITATION_DENIAL_MARKERS`), never looser, with a two-way positive control; (b) registering the generator as a release surface caught its own docstring quoting the historical `READY FOR RELEASE` defect — resolved by **correcting the sentence**. Also measured against §0's own expectation and recorded: **zero** live status claims existed on all thirteen release surfaces beforehand, so `-25b` plants the verbatim historical defect on README's **real bytes** to prove the scan reaches them. **DN-7 held: `argus/**` is BYTE-UNCHANGED**, so `DF-10-4-D`'s bootstrap is not owed and none was performed. **Gates, all LOCAL:** `pytest` **1543 passed / 0 failed / 0 errors / 0 skipped** (was 1527); `mypy` clean, 83 files; `bandit` 19 Low / 0 Medium / 0 High over a population **byte-identical to `de05dec`**, which is a stronger control than a stash run. NFR-M1 worst non-exempt **1181/1200**, relieved by a **cohesion split**, never by shaving. **CI evidence: NOT ESTABLISHED** — every figure above is LOCAL and does not on its own discharge architecture.md §H. **AWAITING: explicit human authorisation, act by act, for `DF-12-9-A`'s seven acts.** |
| 2026-08-15 | Story 12.9 created (`bmad-create-story`). Scope: **stage, prove, derive and guard the release — and HALT before publishing it.** Premises re-measured on `de05dec` by execution **and by live GitHub API reads**, because two of them are facts outside the repository. **Six divergences found, two of them outside the tree.** (1) **The epic's central AC is impossible today:** the latest `audit-ci.yml` run on `master` is `31341363300` at `00c8d1b` (2026-08-09) and **`origin/master` is 34 commits BEHIND local `master`** — every Epic-10/11/12 commit is local only, so **no executed gate covers the release commit**; the honest status is `NOT ESTABLISHED`, and citing `31341363300` is the exact half-truth `architecture.md:614-616` uses that run id to illustrate. (2) **The repository is measurably PRIVATE** (`gh repo view` → `isPrivate: true`), which README and CHANGELOG both admit they never measured — so the documented `pip install …@v0.1.0` cannot resolve for any consumer **with or without the tag**, and Marketplace is blocked for a reason unrelated to 11.3 (which is `done`, precondition MET). (3) **`TC-ArgusAgent-DOCS-001-55`, built by 11.5 so the tag caveat "cannot rot in EITHER direction", reads `README.md` only** — the pin appears on **three** surfaces (README ×3, CHANGELOG ×2, `docs/first-run.md` ×1, the last added by **Story 12.8 after `-55` was written**), so creating the tag turns three further caveats into published falsehoods **invisibly**. That is 12.8's explicit hand-over, and AC4 closes it **before** any tag exists. (4) **`release.yml`'s release note is a hand-typed string literal in a `run:` block** transcribing the exit-code contract, the install command and a paraphrase of the FR34 disclosure — and 12.8 changed exit-code semantics without it moving, because nothing checks it. (5) **10.1's citation rule cannot see the consumer surfaces**: `_STATUS_DOCUMENTS` is change-proposals and retros only; README/CHANGELOG/`release.yml` are not excluded with a reason, they are simply outside the guard. (6) **`DF-10-3-A` — the ledger entry that names this story — was already resolved by 12.8/AC8** (its own first candidate remedy) and never closed; its `target_story` also names a story key the tracker does not have. **Decisions recorded rather than assumed:** the **index channel does NOT ship** (DN-1 — four committed statements, one a 9.2 locked decision, and `epics.md:2465` is permissive), the **marketplace channel does NOT ship** (DN-2 — private repo, not 11.3), the version **stays 0.1.0** (9.2/D1), and **`NOT ESTABLISHED` is a passing outcome** (DN-3). **Nine ACs; AC1-AC8 are completable with ZERO outward-facing acts** — build, install-and-use the artifact, derive the citation, generate the note, mechanise the caveats, close the ledger, re-prove E1-E6, assemble a dossier — and **AC9 alone is outward-facing: it enumerates all seven irreversible/outward acts (push master, tag, push tag, GitHub Release, make repo public, Marketplace, PyPI) with blast radius and reversibility, and is written as a HALT requiring explicit human authorisation** (DN-8; `sprint-status.yaml:399`'s standing operator instruction; `release.yml`'s own *"not a decision a story author may take unilaterally"*). Owns `DF-10-3-A`; **cites and does not build** `DF-3-4-A`, `DF-10-5-C`, `DF-12-7-A`, `DF-10-3-B`, `DF-10-3-C`. Status → `ready-for-dev`. |
