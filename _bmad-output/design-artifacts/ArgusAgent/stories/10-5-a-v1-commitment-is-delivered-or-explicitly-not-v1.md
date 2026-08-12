---
baseline_commit: 93adc94d0203eaaf4d1cb1d8bc7113e9b885beed
baseline_note: >-
  HEAD is `93adc94` on `master`, **6 commits unpushed**. Stories 10.1–10.4 are `done` **and
  committed** — unlike every prior Epic-10 story, you are NOT building on an uncommitted delta.
  `a9cc933` ("fix(index,reports): a grammar that fails to load names why") carries 10.1–10.4's
  product deltas; `93adc94` ("chore(dogfood): regenerate the plan and proof artifacts at a truthful
  sha") regenerated the three committed dogfood artifacts against it. **No CI run has ever seen
  either sha** — run `31341363300` is sha-scoped to `00c8d1b` and cannot evidence this tree
  (10.1's rule, AC7.5).
  ⚠️ **`bmad-dev-loop-pack/`, `.bmad-drift-audit/`, `_bmad-output/audit-reports/*` and the stray
  untracked `NUL` belong to the orchestrator/host — do not add, move or delete them.**
  THIS FILE is untracked and IS yours: `git add` it with your delta or you repeat AI-E8-1.
  **Every line number below was measured on 2026-08-11 against this tree.** The epic's own AC
  ([epics.md:1932](../epics.md)) still cites the standards commitment at **PRD L168**; it is at
  **L187** today, because 10.2's and the 2026-08-10b amendments moved it. That is the fifth stale
  coordinate this epic has produced in three days. **Locate every site by its ANCHOR TEXT and treat
  every line number in this document as a hint you must re-verify.**
story_key: 10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1
epic: 10
---

# Story 10.5: A V1 commitment is delivered, or it is explicitly not V1

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo, `argus/` tree only.** ArgusAgent (formerly APAA) is a
> self-contained headless audit tool extracted from the Minions monorepo into its own repository
> (`Agent-Argus`, distribution `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in
> THIS repo. The `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no
> back-port.** Planning artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker
> is that folder's `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`,
> `minions_core/apaa/` or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/`
> and `tests/`.

---

## Story

As the ArgusAgent governance owner,
I want a capability the PRD commits to V1 either shipped or explicitly reclassified,
so that the specification and the product stop describing different tools.

**Why this story is Epic 10's last, and why it is one story rather than a sweep.** 10.1 fixed a
**status** claim that cited no gate. 10.2 fixed a **scope** claim that named the wrong languages.
10.3 fixed an **invocation** claim that named the wrong flags. 10.4 fixed a **degradation** claim
that named the wrong cause. 10.5 fixes the claim underneath all four: **that a thing the
specification commits to is a thing the product has.** Every one of the previous four was found by
accident — an audit, a proposal, a reviewer's eye. This story's job is not to find the fifth
instance by hand. It is to make the *class* mechanically inescapable, so there is no sixth found by
accident. The epic closes the **record**; it ships no capability, and it must not.

⚠️ **This story is inherently cross-cutting and must be resisted as such.** Its subject touches
every FR and every scope statement in the PRD. Its *deliverable* is narrow: **a decision, two
classifications, and one guard.** Every temptation to *fix* something the sweep exposes is a fence
breach — see §D. The sweep's output is a **disposition**, never an implementation.

---

## Story Context

### Method statement — everything below was MEASURED on this tree on 2026-08-11

Every figure, coordinate, grep count and reachability claim in §A–§E was produced by executing
`grep`, by reading the file, by running `pytest --collect-only`, `mypy`, `git`, or by walking
`argus/**` with the stdlib `ast` module to build the real import graph. **Five of the measurements
change this story as the epic, the proposal and the sprint-status annotation wrote it.** Re-derive
them; do not transcribe them.

---

### A. The five findings that change this story

#### A.1 — 🚩 The enumeration is wrong a **fourth** time. One site was named; there are **three**

The proposal (§1.4(c)), the epic AC ([epics.md:1932](../epics.md)) and the sprint-status annotation
all name **exactly one** site: *"PRD §Product Scope L168."* Measured on this tree, the
`standards_refs[]` + CWE-on-security commitment lives at **three** PRD coordinates, and the one
named is not even at the line quoted:

| # | Coordinate **on this tree** | Anchor to locate by | What it says |
|---|---|---|---|
| 1 | **`E-PRD/prd.md:187`** *(the proposal says `L168`)* | `- **V1 Core:**` … `` `standards_refs[]` field + **CWE-required-on-security findings** `` | commits the field to **V1 Core**, *"day-one additive; rich mapping → V2"* |
| 2 | **`E-PRD/prd.md:309`** — **NAMED IN NO PLANNING DOCUMENT SINCE 2026-08-03** | `- **Standards anchoring (phased).**` | §Compliance & Regulatory: *"**V1:** `standards_refs[]` field (format-validated, e.g. `^CWE-\d+$`) + **CWE required on every security-category finding**"* — a **second, independent V1 binding**, with a *format* commitment the first site does not make |
| 3 | **`E-PRD/prd.md:214`** | `standards mapping (CWE/ASVS/ISO 25010/SLSA)` | the **V2 Growth Features** line, which **already contains the destination** |

Site 2 is the whole argument for this story's shape. It is in a *different section*, in a *different
sentence shape* (`**V1:**` inside a domain-requirements bullet, not a `·`-separated scope list), and
**a sweep of §Product Scope alone will not see it.** It was last named by
`implementation-readiness-report-2026-08-03.md:353`, which quoted **both** sections
(*"PRD §Compliance and §Product Scope both bind this"*) — and then the 2026-08-10b proposal, working
from the code side, rediscovered only one of them.

Site 3 matters for the opposite reason: **the V2 destination already exists.** Moving the V1
commitment to V2 must be recorded as a **merge into an existing item**, not as a new V2 line — the
inverse of 10.2's rule that *"a delivered capability left on the growth roadmap double-counts the
work"*. Here an undelivered V1 item silently absorbed into an existing V2 item would **under**-count
it, and there would be no record that anything was ever promised for V1.

> **Also measured, and NOT a site:** `product-brief-apaa-distillate.md:47` lists `standards_refs` in
> the frozen `finding` schema ①. The product brief is a **superseded upstream input**, not a binding
> contract — 10.2 amended the PRD and architecture and left the briefs alone. Do the same, and say
> so; leaving it unamended is a decision, and an unrecorded decision is what this epic exists to
> stop.

#### A.2 — 🚩🚩 THE FINDING THAT DECIDES AC5: the code side is not one instance. It is **five**, and four were filed and never swept

The epic asks for a reverse sweep — *FR1–37 for requirements with no reachable production call site*
— and names **one** known hit, FR23. Measured on this tree by building the real import graph of
`argus/**` with the stdlib `ast` module and taking the transitive closure from `argus/cli.py`
(the only entry point: `pyproject.toml:59-62` ships three console aliases, all
`argus.cli:main`):

| Module | The FR it carries | Reachable from `argus.cli`? | Only importer in `argus/` | Prior filing |
|---|---|---|---|---|
| `governance/escalation.py` | **FR23** — HITL STOP/PROCEED gate, default-STOP | ❌ **NO** | **none at all** | `DF-6-7-A` (:1634), targeted at THIS story |
| `governance/decision_record.py` | **FR24** — append-only decision record **[Tier B]** | ❌ **NO** | **none at all** (one prose mention, `store/integrity.py:94`) | **never filed** |
| `evidence/bundle.py` | **FR29** — operator exports an evidence bundle | ❌ **NO** | `dogfood/proof_run.py` only | **never filed** |
| `store/integrity.py` | **FR26 / NFR-A2** — referential-integrity lint **[Tier B]** | ❌ **NO** | `dogfood/proof_run.py`, `evidence/bundle.py` | **never filed** |
| `cache/memo_store.py`, `cache/invalidation.py`, `cache/key.py` | **FR27 / NFR-D1** mechanism | ❌ **NO** | `key.py` reachable? **no** | `DF-AUD-APAA-A` (:464) |
| `audit/deep_audit.py`, `audit/ports.py`, `audit/open_llm_adapter.py`, `audit/minions_llm_adapter.py` | **FR36** (added 2026-08-10b) | ❌ **NO** | — | proposal §1.3, → Story 12.2 |
| `precision/replay_harness.py` | the ≥80% precision protocol | ❌ **NO** | `dogfood/*` only | Epic 13 |
| `index/partitioner.py::read_in_scope` | **NFR-S4** manifest read boundary | function has **no production caller** | — | `DF-AUD-APAA-B` (:481) |

**Reproduce this before you write anything** (three lines of stdlib; it is AC5's RED evidence and
AC4's input):

```python
# walk argus/**, build the import graph, take the closure from argus.cli, print the complement
# measured 2026-08-11: 43 of 72 modules reachable; the 29 unreachable include the four above
```

**Four separate filings of one class, over five weeks, and the class was never swept.**
`DF-AUD-APAA-A` and `DF-AUD-APAA-B` (both 2026-07-04) name it exactly — *"ORPHAN relative to the
shipped `run_audit`/CLI path"*, *"has NO production caller … the security guarantee is proven only
in tests"*. Both carry `target_story: epic-7-minions-dogfood-proof-run` — **an epic that is `done`**,
so both targets are **orphaned**: the entries can never be closed by the thing they point at. Then
`DF-6-7-A` filed FR23. Then `DF-10-4-B` filed `DetectorResult.degraded`. **Each was filed as an
instance. None triggered a sweep.** That is the defect this story's guard exists to close, and it is
why AC5 — not AC3 or AC4 — is load-bearing.

> ⚠️ **The trap inside this measurement, and you must not fall into it.** *Module unreachable* is
> **not** the same as *FR undelivered*, and a guard that equates them will produce false accusations
> — the failure mode this product exists to prevent. **FR27** is the worked example: the
> memoization *mechanism* is unwired, but the default run is zero-token and deterministic, so *"the
> same verdict for the same repository and version"* holds **by determinism**, not by cache. FR27 is
> **delivered by other means, mechanism deferred to 12.3**. The reachability walk is the **closure
> device that forces a classification** — it is never the classifier. AC5.3 encodes exactly that
> asymmetry: the guard may *refute* a `wired` claim mechanically; it may never *assign* a
> disposition.

#### A.3 — 🚩 The architecture already certifies the thing that is false, in one sentence

`architecture.md:905`:

> *"**All 33 FRs of the base contract** map to a concrete module (FR-cluster→location table). No FR
> is unsupported."*

`architecture.md:884` maps *"Governance/Integrity (FR23–29) → `governance/`, `store/envelope.py`,
`cache/`, `evidence/`"*. Every module named exists. **Four of the seven FRs in that one row have no
production call site.** The sentence is true and useless: **mapping to a module is not delivery**,
and a validation section that certifies module *placement* while reading as certification of
*coverage* is the same defect as a status claim that cites no gate (10.1) — one level up, in the
document that reviewers trust most.

The section already carries a scope caveat added 2026-08-10 (`:899-903`) warning that it was
performed against the pre-amendment 33-FR contract. That caveat is about **which** contract; this
story adds the caveat about **what "supported" means**. Both are needed. AC4.5 is that edit, and it
is a single paragraph — ⛔ **do not re-run the architecture's validation method, and do not rewrite
the FR-cluster table.**

#### A.4 — The class was named, and scored, on 2026-08-03 — and the score was never acted on

`implementation-readiness-report-2026-08-03.md:400`:

> *"The failures are all in the same blind spot: **obligations the PRD binds without an FR number**.
> The requirement-ID pass scores 100%; **the unnumbered-obligation pass scores 68%**."*

That is a measured prior estimate that the forward sweep has **real content beyond the one instance**
— roughly a third of the unnumbered obligations were uncovered eight days ago. Its **F2**
(`:351-358`) is this story's AC1 verbatim, recommending the opposite outcome (*ship it, it is cheap
while the schema is unfrozen*). The schema is now frozen, content-hashed and shipped — which is
precisely why the recommendation of record inverted (DN-1).

**F2 also became a retrospective action item and was measured NOT DONE twice.** `AI-E8-9`
(`epic-8-retro-2026-08-08.md:170`) required closing it; `epic-9-retro-2026-08-09.md:130` re-measured:
*"**AI-E8-9 is untouched.** `grep CWE` over the 9.2 story: **0 hits**."* **This story disposes the
F2/CWE half of AI-E8-9 by deciding it** — ⛔ and only that half. F4 (`SC-E`), F10
(`architecture.md`) and D1 (config drift) are **not** yours; naming them closed would be the exact
over-claim this epic exists to stop.

#### A.5 — The code side is confirmed empty, and the severity is 🟡 — keep it there

Re-measured 2026-08-11, whole tree:
`grep -rniE "standards_ref|cwe|asvs|owasp" argus/ --include=*.py` → **0 occurrences.**
`FindingDraft` (`argus/detectors/base.py:63-87`) carries no standards field of any kind. The
proposal's measurement reproduces exactly.

**State the consequence precisely and do not inflate it.** Nothing in this story changes a verdict,
a gate, a coverage grade or a finding. The harm is entirely in the **record**: a reader of the PRD
today would conclude that a security finding carries a CWE reference and that a human STOP gate is
live on the audit path. Neither is true. That is a governance defect, not a correctness defect — and
manufacturing a correctness framing for it would be the same overselling 10.4 was warned off in its
own §A.5.

---

### B. Where the sites actually are — re-measured

| Site | Coordinate **on this tree** | Anchor to locate by |
|---|---|---|
| standards commitment #1 (V1 Core) | `E-PRD/prd.md:187` | `- **V1 Core:**` |
| standards commitment #2 (Compliance) | `E-PRD/prd.md:309` | `- **Standards anchoring (phased).**` |
| the V2 destination that already exists | `E-PRD/prd.md:214` | `standards mapping (CWE/ASVS/ISO 25010/SLSA)` |
| §Product Scope section head | `E-PRD/prd.md:183` | `## Product Scope` |
| V1 Design Invariants | `E-PRD/prd.md:191-196` | `### V1 Design Invariants` |
| the binding-contract preamble | `E-PRD/prd.md:457` | `a capability not listed here will not exist in V1` |
| FR23 | `E-PRD/prd.md:532` | `- **FR23:**` |
| FR24 / FR26 / FR27 / FR29 | `E-PRD/prd.md:533` / `:535` / `:536` / `:538` | `- **FR24:**` … |
| Journey 4 (Dana, regulated) | `E-PRD/prd.md:260-265` | `### Journey 4 — Dana,` |
| PRD frontmatter `amendments` | `E-PRD/prd.md:84-94` | `amendments:` |
| the false-comfort certification | `architecture.md:905` | `No FR is unsupported` |
| its 2026-08-10 scope caveat | `architecture.md:899-903` | `⚠️ **SCOPE, clarified 2026-08-10.**` |
| FR-cluster → location table (⛔ read-only) | `architecture.md:874-885` | `### FR-cluster → location mapping` |
| §Enforcement (register your guard here) | `architecture.md:712-757` | `### Enforcement` |
| `DF-6-7-A` (close by disposition) | `deferred-work.md:1634-1642` | `- **DF-6-7-A — PLAN INCONSISTENCY` |
| `DF-10-4-B` (dispose; it targets you) | `deferred-work.md:1905-1923` | `- **DF-10-4-B**` |
| `DF-AUD-APAA-A` / `-B` (orphaned targets) | `deferred-work.md:464-479` / `:481-494` | `- **DF-AUD-APAA-A**` |
| the entry point | `argus/cli.py` (479 lines) | `def build_parser(` / `def main(` |

---

### C. The instrument — reuse the idiom, do not invent one

10.1, 10.2, 10.3 and 10.4 each landed a guard of the same shape, and all four passed code review on
iteration 1: **registry + closure + both-direction positive control + non-vacuity**. Use it. Only
the closure device changes, and picking it is the one real design decision here:

| Story | Closure device | Why |
|---|---|---|
| 10.1 `test_evidence_citation.py` | **glob** over `sprint-change-proposal-*.md` | a new document cannot escape by being new |
| 10.2 `test_spec_claim_scope.py` | **glob + claim-shape pattern** | a new spec *sentence* cannot escape |
| 10.3 `test_invocation_contract.py` | **live `argparse` walk** | the parser is exactly enumerable |
| 10.4 `test_grammar_diagnosis.py` | **the module's own source, parsed with `ast`** | the failure arms are exactly enumerable from the code |
| **10.5 (this story)** | **two closures that meet in the middle: a *claim-shape pattern over the whole PRD* (forward) × a *static import-reachability walk of `argus/**`* (reverse)** | the commitment side is prose and cannot be enumerated from a heading (§A.1 proves it); the delivery side is code and can be walked exactly (§A.2). Neither closure alone closes the class. |

**This is the point, and §A.1 is its proof.** A sweep anchored on the `## Product Scope` heading
would have missed `prd.md:309` — the site that has been invisible since 2026-08-03 — because the
commitment did not live under the heading anyone thought to sweep. **The claim SHAPE closes what the
section heading does not.** 10.2 reached the same conclusion the hard way after its hand-list was
wrong three times, and recorded it: *"the closure GUARD, not the site list, is the load-bearing AC."*

⚠️ **Both closures go green by finding nothing** — a heading rename, a section move, a package
rename, an `ast.parse` failure. **Non-vacuity is mandatory on both** (AC5.6), and it is the single
most likely thing a reviewer will attack.

⚠️ **The guard must not import `argus`** (DN-6). It reads source as **text**, parses with the stdlib
`ast` module, and resolves imports statically. Three reasons, all measured: an import-time walk can
be defeated by lazy imports (`precision/replay_harness.py:87-90` already does a `sys.path` insert),
importing `argus` would make the guard's own result depend on installed optional extras, and a test
that executes no `argus` line cannot perturb the 95.51% coverage figure the ledger cites.

---

### D. ⛔ FENCES — what this story must NOT touch

**Epic 10 closes the RECORD. It ships nothing.** The single sharpest fence in this story:
**`git status --porcelain -- argus/` must be EMPTY at the end.** Not "small". Empty. 10.1 set this
precedent and stated it in its own AC7; you inherit it.

| Fenced | Owner | Why, and where the line sits |
|---|---|---|
| **Shipping `standards_refs[]` / any `FindingDraft` field** | ⛔ **nobody, by DN-1** | The decision is **V2** (DN-1). Adding the field would spend a `finding`-schema bump (NFR-A1/NFR-M2 additive-only, content-hashed) and widen the redaction surface for an audience that **cannot legally be served until Epic 13 clears the gate**. If you find yourself editing `argus/detectors/base.py`, the decision has been silently overturned — stop. |
| **Wiring FR23, FR24, FR26 or FR29 to a call site** | **12.1 (enabler) → unscheduled** | `argus/pipeline.py` is **1331 lines against the NFR-M1 cap of 1200** and is **12.1's**, byte-unchanged. Every wiring lands in it. A disposition is this story's deliverable; a call site is not. |
| **`argus/pipeline.py` — BYTE-UNCHANGED**, and in fact all of `argus/**` | 12.1 / Epics 11–13 | See above. **Adding no `argus/**` file is also what keeps you clear of `DF-10-4-D`**: that trap fires on `git ls-files argus` moving, i.e. on **staging** an `argus/**` source file — which halted Story 10.4 on five reds. A `tests/`-only delta does not move the dogfood population. **This is a designed property of the write set, not luck.** |
| **`pipeline.py`'s NFR-M1 breach itself** | **12.1** | Measured 1331 today. Record it in the sweep if it surfaces; do not fix it. |
| **The `--help` prose / `cli.py`'s `except ValueError` split** | **12.8** | |
| **`README.md:178-190`, the slash-command claim, any README truth repair** | **12.7 / 11.5** | |
| **Default-install grounding / `pyproject.toml` `[languages]`** | **12.5** (NFR-P3) | |
| **The `tree-sitter <0.26` false-green** | **11.4** | |
| **Publishing, tagging, `workflow_dispatch`, `git push`** | **12.9 / operator** | 10.1's DN-7: triggering a run to manufacture a citation is manufacturing evidence. |
| **The ≥80% precision gate** | **Epic 13** | **NOT CLEARED, and nothing in Epic 10 clears it.** Your Journey-4 edit (AC2) must not read as if it does. |
| **FR34's disclosure** | **11.1** | Untouched. Do not add, remove or reword a disclosure. |
| **🚨 H0 — who files the Minions handoff H1–H4** | **UNOWNED** | **OPEN and UNOWNED, and this story MUST NOT close it.** It will *surface* in the forward sweep: §Product Scope L196 commits *"APAA specifies the cost/memory consumption-contracts it will need from Minions (a)/(d)/(e)"*, and the PRD §Dependencies (`:222-232`) does specify them — but **filing them into the Minions tracker is H0, and no one owns it.** Its disposition is *specified, filing UNOWNED* — never *done*. AC6.5 asserts this in a test. |
| **🚨 DF-7-2-A — the human TP/FP adjudication** | **XAgent007 named 2026-08-10b; adjudication OPEN** | Named owner ≠ done. It **will** surface in the sweep near `precision/replay_harness.py`. Disposition: **OPEN**, owner named, target Epic 13. ⛔ Do not close. AC6.5 asserts this too. |
| **`epics.md`, `E-PRD/addendum.md`, `README.md`, `CHANGELOG.md`, `action.yml`, `audit-ci.yml`, `pyproject.toml`, the product briefs, every Epic 1–9 artifact and retrospective, the three committed dogfood artifacts** | — | ⛔ Byte-unchanged. `epics.md:1932`'s stale `L168` is left as written (§3.4) and noted in your Dev Agent Record as the epic's own instance of the coordinate-drift lesson. |
| **Re-running the architecture's Requirements-Coverage validation method** | — | AC4.5 adds **one caveat paragraph**. It does not re-validate 37 FRs against the architecture. |

---

### E. Traps previous stories already paid for — the five that apply

| # | Trap | What it costs you here |
|---|---|---|
| **E.1** | **AI-E3-1 — a keystone test that was green over its own keystone bug** (3.4). | **RED-first is MANDATORY** for AC5. Run the guard against the **unamended** PRD/architecture and record the failures (`prd.md:187` and `:309` unclassified; FR23 disposed `wired` and mechanically refuted). A guard written after the amendment proves nothing. |
| **E.2** | **The enumeration has now been wrong four times** (10.2 ×3, and §A.1 here). | Do not close this with a hand table of commitments. **AC5's two closures are the load-bearing half**; AC3/AC4's tables are their inputs. |
| **E.3** | **Positive control, both directions** (10.1/10.3/10.4). | An unclassified synthetic claim must **fire**; a classified one must **not**. A `wired` disposition over a synthetic unreachable module must **fire**; over a reachable one must **not**. Pure functions over synthetic inputs — **never** by editing the real PRD or the real package during a test. |
| **E.4** | **A guard that passes vacuously** (10.3's `-39`, 10.4's `-118`). | Assert non-zero: claims parsed, FRs found, registry entries, modules in the graph, edges in the graph. A heading rename, a package move or an `ast.parse` failure must go **RED**. |
| **E.5** | **AI-E8-1 / -E8-2 — `git diff` cannot see an untracked path.** | `git add` this story file **and** the new test before you claim a write-set fence. Verify with `git status --porcelain` **and** `git diff --stat`. |

---

## Acceptance Criteria

### AC1 — The `standards_refs` conflict is DECIDED, dated, and all three sites stop disagreeing

**The decision is LOCKED: V2** (DN-1 — the recommendation of record in the approved
`sprint-change-proposal-2026-08-10b.md:362-364`, and re-derived here on this tree's evidence). It is
not re-litigated by the dev; it is **applied, dated and reasoned**.

1. **`E-PRD/prd.md:187` (§Product Scope V1 Core)** — the `` `standards_refs[]` field +
   **CWE-required-on-security findings** (day-one additive; rich mapping → V2) `` item is **struck,
   not deleted** (§3.4 evidence immutability), with a dated amendment note attributing the decision
   to **this story** and to `sprint-change-proposal-2026-08-10b.md`.
2. **`E-PRD/prd.md:309` (§Compliance & Regulatory, "Standards anchoring (phased)")** — the **second,
   independently-binding V1 site named in no planning document since 2026-08-03** (§A.1) is amended
   the same way. Its `^CWE-\d+$` **format** commitment moves with it. ⛔ **Amending only site 1
   leaves the PRD self-contradicting and fails this AC** — that is precisely the state the story
   exists to end.
3. **`E-PRD/prd.md:214` (V2 Growth Features)** — the item lands on the **existing** *"standards
   mapping (CWE/ASVS/ISO 25010/SLSA)"* entry as a **recorded merge**, not as a new V2 bullet. The
   note states that a V1 commitment was reclassified into it, so the reclassification is discoverable
   from the destination and cannot read as *"it was always V2"*.
4. **The reason is recorded, not asserted.** At minimum: the `finding` schema is now **frozen,
   content-hashed and shipped** (NFR-A1/NFR-M2 additive-only), so the 2026-08-03 *"cheaper now than
   after the schema is frozen"* premise (`implementation-readiness-report-2026-08-03.md:357`) has
   **expired**; a `standards_refs[]` field widens the persisted/redaction surface (NFR-S1/S2); and
   the audience it serves — Journey 4, attested/operated-service — is **gated NOT CLEARED by Epic
   13** regardless, so no reachable user is served by shipping it today.
5. **A dated entry is added to the PRD frontmatter `amendments:` block** (`:84-94`), in the
   established shape (`date` / `scope` / `signal` / `approvedBy` / `sections`), naming **all three**
   sites.
6. **⛔ No code ships.** `argus/detectors/base.py` byte-unchanged; the `finding` schema version
   unchanged; zero occurrences of `standards_ref`/`cwe`/`asvs`/`owasp` in `argus/**/*.py` at the end,
   re-measured (baseline: **0**).
7. **`AI-E8-9`'s F2/CWE half is recorded as disposed by this decision** — and ⛔ **only** that half.
   F4 (`SC-E`), F10 (`architecture.md`) and D1 (config drift) are named as **still open** and not
   yours (§A.4).

### AC2 — The Journey 4 consequence is recorded as a known trade, not an accident

1. **`E-PRD/prd.md:260-265` (Journey 4 — Dana, regulated enterprise)** gains a **dated** consequence
   note: in V1 a security finding carries **no standards reference**, so the evidence bundle is
   **weaker compliance evidence** than §Compliance & Regulatory previously implied — and Dana's
   legal team must map findings to CWE themselves.
2. **The note is scoped honestly and does not double-count the harm.** Journey 4 is the
   **operated-service / attested** path, which the ≥80% gate holds at **NOT CLEARED**
   (`sprint-change-proposal-2026-08-10b.md:245`). No user is served *worse today* than that gate
   already permits. ⛔ **Stating this must not read as clearing, softening or scheduling the gate**
   — Epic 13 owns it and nothing here touches it.
3. **It is a trade, with a re-entry point**, not a shrug: the note names V2's standards mapping as
   where it returns and cites the deferred-work id filed under AC6.
4. **FR11 (secret detection) — the one security-category finding producer in V1
   (`implementation-readiness-report-2026-08-03.md:355`) — is named**, so a future reader knows
   exactly which findings the gap applies to.
5. ⛔ **No other journey, success criterion or NFR is reworded.** Journey 4 only.

### AC3 — Forward sweep: every V1 commitment carries a disposition, and the sweep finds the sites a heading-anchored sweep would miss

1. **The population is derived by CLAIM SHAPE across the whole PRD, not by section heading** (§C,
   §A.1). At minimum the shapes `**V1 Core:**`, `**V1 Differentiator:**`, `**Proof:**`,
   `**V1:**`, *"day-one"*, and the `### V1 Design Invariants` bullets, wherever they occur.
   Inline `·`-separated lists split into atoms; the split must not break inside parentheses.
2. **Every atom takes exactly one disposition** from this **locked vocabulary** (DN-4), each naming
   its evidence **by anchor**, never by line number:
   - `fr-backed` — names the FR(s) that carry it
   - `nfr-backed` — carried by an NFR rather than an FR. **Recorded as specified, NOT as a gap**
     (DN-5) — the FR preamble at `:457` binds *capabilities*, and an NFR is a binding requirement.
     Known: `work_manifest` permission boundary → **NFR-S4**; envelope determinism → **NFR-D3/A1**.
   - `constraint` — a forward-compatibility invariant, not a capability (e.g. `partition_id` always
     `"root"`; curated memory never touches the verdict path). Names where it is enforced.
   - `reclassified-v2` — the AC1 case, with its amendment date.
   - `specified-not-built` — a commitment whose deliverable is a *specification*, with the residual
     named. **Known and load-bearing: L196's Minions consumption-contracts — specified at
     `:222-232`, but the FILING is H0, OPEN and UNOWNED (§D). Disposition MUST record the open
     filing, never `done`.**
   - `delivered-differently` — delivered, but not in the form promised, with the divergence named.
     **Known and load-bearing: L189's `**Proof:** dogfood run against Minions itself` — replaced by
     a self-audit of `argus/` (Story 8.5), which the ledger itself calls *"a materially weaker
     evidence class … not independent corroboration of anything"*.** Record it; ⛔ do not re-open
     Epic 7/8 and do not attempt a Minions run (RS-1).
3. **Every disposition is dated and reasoned in one line.** A disposition with no reason is not a
   disposition.
4. **The result is recorded in TWO places that cannot drift**: the guard's registry (AC5) and this
   story's Dev Agent Record. ⛔ **Not in the PRD** — the PRD records *decisions* (AC1/AC2/AC4), not
   a sweep log.
5. **A count is stated and defended**: how many atoms the parser found, how many of each disposition.
   If your count differs from a hand read, **the parser wins and you say so** — that is the whole
   lesson of §A.1.

### AC4 — Reverse sweep: every FR1–37 carries a delivery disposition, FR23 is decided BY NAME, and "maps to a module" is retired

1. **The population is FR1–37, enumerated mechanically from `E-PRD/prd.md`'s §Functional
   Requirements** by the `- **FR<n>:**` shape — never hand-typed. (Measured note: the FRs are **not**
   in numeric order — FR36/FR37 sit inside the Coverage/Verdict clusters, FR33–35 among the later
   ones. A parser handles this; a hand list has already failed four times.)
2. **Every FR takes exactly one disposition** from this **locked vocabulary** (DN-4):
   - `wired` — a production call site **reachable from `argus/cli.py`**, named by `(module, anchor)`.
     **Mechanically verified by AC5.3 — a `wired` claim is refuted, not trusted.**
   - `delivered-differently` — the capability holds by another mechanism; the named mechanism is
     deferred. **FR27 is this case** (§A.2's trap box): determinism, not memoization; mechanism →
     Story 12.3.
   - `library-seam` — built, correct, test-proven, **no reachable production call site**. Requires a
     dated reason, a named owner, and a ledger entry.
   - `not-built` — specified for V1.5+; names the owning story (FR34→11.1, FR35→12.6/12.7,
     FR36→12.2, FR37→12.4).
3. **FR23 is decided BY NAME, and the decision is LOCKED: `library-seam`** (DN-3). Applied as:
   - **FR23's text at `E-PRD/prd.md:532` is amended** — struck-not-deleted, dated, attributed —
     to record **what is delivered** (the pattern-matched escalation evaluator `escalation_fires` /
     `resolve_escalation`, the resolution model, and `DecisionRecordWriter`, proven by
     **`tests/test_hitl_escalation.py`** — ⚠️ the epic AC cites `tests/apaa/test_hitl_escalation.py`
     and **`tests/apaa/` does not exist on this tree**; use the real path) and that **its invocation
     is deferred**, following the FR7 (10.2) and FR30 (10.3) precedent that *"FRxx is the binding
     contract, so it is corrected to what the code does."*
   - **The amendment states the contradiction it creates, in the amendment itself**: the PRD
     cut-order marks **FR23 non-negotiable core** (only FR24 is `[Tier B]`), and
     `implementation-readiness-report-2026-08-03.md:365` already flagged FR23 as stranded in a
     slippable epic. **A de-scope that hides its own cost is the defect this epic closes.** Record
     it; do not soften it.
   - **The reason is the fence, stated plainly**: the call site lands in `argus/pipeline.py`, which
     is at **1331/1200** and gated to Story 12.1 — and the V1 default path (Journeys 3 and 5) is
     **unattended CI with no human to answer a default-STOP gate**, so a naive wiring would deadlock
     every automated audit. Both halves, or the reason is incomplete.
4. **Every other `library-seam` hit takes the same treatment.** Measured candidates to re-derive,
   **not transcribe** (§A.2): **FR24**, **FR26**, **FR29** — each never filed before — plus
   **NFR-S4**'s `read_in_scope` (already `DF-AUD-APAA-B`). ⚠️ **All three are built, typed and
   test-proven** (`tests/test_hitl_escalation.py`, `tests/test_store_integrity_lint.py`,
   `tests/test_evidence_bundle.py`) — *"it has tests"* is therefore **not** evidence of delivery
   here, and saying so is half the point of the story. An FR whose text reads as
   operator-invocable while no operator can invoke it (**FR29**: *"An operator can export an evidence
   bundle"* — no CLI subcommand exists; the only caller is `dogfood/proof_run.py`) is amended in the
   same struck-not-deleted, dated form. ⛔ `not-built` FRs (34–37) are **not** amended: the PRD
   already dates them and the plan already names their stories.
5. **`architecture.md:905` is corrected** (§A.3). *"No FR is unsupported"* gains a caveat, dated and
   attributed, recording that **the FR-cluster→location table certifies module PLACEMENT, not
   reachability**, that **N FRs in the base contract are library seams with no production call
   site** (state the measured N), and pointing at the guard. ⛔ **One paragraph.** The FR-cluster
   table itself and the rest of §Architecture Validation Results are byte-unchanged.

### AC5 — 🔑 A committed guard makes classification inescapable in BOTH directions, and mechanically refutes a false `wired` claim

**This is the AC that makes the story stick** (DN-2). New file **`tests/test_v1_commitment_closure.py`**,
ids **`TC-ArgusAgent-DOCS-001-30`..** (measured maximum in use: `DOCS-001-29`).

1. **Forward closure — claim shape, whole document (§C).** Parse `E-PRD/prd.md` for the AC3.1 claim
   shapes, atomize, and require **exactly one** registry disposition per atom. **Both directions:**
   an atom with no registry entry **fails**; a registry entry matching no atom **fails** (so a
   disposition cannot outlive the claim it disposed).
2. **Reverse closure — FR enumeration.** Extract FR ids from §Functional Requirements by shape.
   **Both directions:** an FR with no disposition **fails**; a disposition naming an FR the PRD does
   not contain **fails**. **FR38 cannot be added to the PRD without failing this test.**
3. **⛔ `wired` is PROVEN, never asserted — the AC that retires §A.3's sentence.** Build the
   `argus/**` import graph **statically** (stdlib `ast`, source read as text, **no `import argus`** —
   DN-6) and take the transitive closure from `argus/cli.py`. For every `wired` disposition:
   (a) the named module exists, (b) its named **anchor text** is present in that file, and (c) the
   module **is in the closure**. A `wired` claim over an unreachable module **fails**.
   **Symmetrically:** a `library-seam` disposition over a module that **is** reachable **fails** —
   so when 12.1/12.3 wire a seam, this test goes red until the disposition is updated. *That red is
   the guard working.*
4. **Positive control, both directions (E.3)** — pure functions over **synthetic in-memory inputs**,
   never the real PRD and never the real package: a synthetic document with an added unclassified V1
   claim **fires**; a fully-classified one **does not**. A synthetic graph in which a seam module
   becomes reachable **fires** against a `library-seam` disposition; the same graph **does not**
   fire against a `wired` one. **A parenthesised `·` inside an atom does not split it** (AC3.1) —
   pin it with a synthetic case.
5. **The open-and-unowned set is asserted, not remembered (§D).** **H0** and **DF-7-2-A** are pinned
   as **OPEN** by anchor in `deferred-work.md`; the test **fails if either is marked closed**. This
   story is the one most likely to close them by accident, so the guard defends against its own
   author.
6. **Non-vacuity (E.4), on both closures.** Fail if zero claims parsed, zero FRs found, zero registry
   entries, zero modules in the graph, zero import edges, or if §Product Scope / §Functional
   Requirements cannot be located. **A heading rename or a package move must turn this RED, not
   silently green.** State the minimum counts as constants with a comment saying why each floor is
   what it is.
7. **Registered in `architecture.md` §Enforcement** (`:712-757`) beside 10.1's, 10.2's, 10.3's and
   10.4's guards, and the section gains the **one-line rule** this story establishes: **a V1
   commitment is delivered only when a production call site reaches it — mapping to a module is not
   delivery, and a commitment with neither a call site nor a dated reclassification is a defect.**
   The guard asserts **both** the rule text and its own registration are still present — *a rule that
   lives only in a test is not a rule, and a rule that lives only in prose is not enforced* (10.1's
   `-23`, 10.3's `-28`, 10.4's `-29`).
8. **RED first, mandatory (E.1).** Run the guard against the **unamended** `prd.md` and
   `architecture.md` and record the raw failure showing at minimum: `prd.md:187` **and** `:309`
   unclassified, and a `wired` disposition for FR23 **mechanically refuted** by the reachability
   walk. Restore any file you touched to produce the RED state **byte-identically** (sha256
   round-trip, 10.1's D4).
9. **Failure messages state what broke and what to do**, matching `test_evidence_citation.py`,
   `test_spec_claim_scope.py`, `test_invocation_contract.py` and `test_grammar_diagnosis.py`. A
   future dev who adds FR38 must learn from the failure text exactly which registry to edit.

### AC6 — The ledger closes honestly, and the four prior instances of this class stop being orphans

1. **`DF-6-7-A` (`deferred-work.md:1634-1642`) is closed APPEND-ONLY** by the AC4.3 disposition,
   naming FR23's decision, its date and its reason. The original entry stays **byte-intact**;
   `git diff --numstat` on `deferred-work.md` is **`+n / -0`** (10.1's DN-8 / §3.4).
2. **`DF-10-4-B` (`:1905-1923`) is disposed BY NAME.** It targets **this story**. `DetectorResult.degraded`
   is **not an FR**, so it is not an AC4 hit — it is the same class **one level down**, and it is the
   evidence that the class is systemic rather than FR-shaped. Give it a **dated disposition and a
   real forward target** (12.4 owns *outcome names its next action*; 12.5 owns the
   point-of-downgrade surface). ⛔ **It must not still point at 10.5 when 10.5 closes** — that would
   manufacture a fifth orphan.
3. **`DF-AUD-APAA-A` and `DF-AUD-APAA-B` are re-targeted or explicitly re-recorded** (§A.2). Both
   carry `target_story: epic-7-minions-dogfood-proof-run`, **an epic that is `done`** — so both are
   unclosable as written. Append (never rewrite) a dated note giving each a live target or an
   explicit *"open, unowned by decision"* with a named human, per AI-E9-8.
4. **New filings carry an id, an owner and a `target_story`** — never `target_story: NONE` without a
   named human (AI-E9-8; `DF-10-4-E` is the sanctioned form). **At minimum**, one entry per
   `library-seam` FR discovered in AC4.4 that had never been filed (measured: **FR24, FR26, FR29**),
   and one for the `standards_refs` V2 re-entry point (AC2.3).
5. **⛔ Nothing open is silently closed.** **H0** stays OPEN and UNOWNED. **DF-7-2-A**'s adjudication
   stays OPEN (owner named 2026-08-10b ≠ done). The **≥80% gate** stays **NOT CLEARED**. `DF-10-2-A`,
   `DF-10-4-A`, `-C`, `-D`, `-E` are untouched. AC5.5 asserts the first two mechanically; assert the
   rest by inspection and say so.
6. **A closing statement of the class.** The ledger note records, in one paragraph, that this class
   was filed **four times over five weeks** (`DF-AUD-APAA-A`, `-B`, `DF-6-7-A`, `DF-10-4-B`) and
   swept **zero** times, that `implementation-readiness-report-2026-08-03.md:400` scored the
   unnumbered-obligation pass at **68%** and named the blind spot, and that
   `tests/test_v1_commitment_closure.py` is what makes the fifth filing impossible. **This is the
   epic's closing sentence — write it as one.**

### AC7 — The gates run, the fences hold, and the write set is exactly what it says

1. **Gates re-run and LABELLED LOCAL** (10.1's AC6): `mypy argus` · `bandit -r argus
   --severity-level medium` · `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest tests/ --cov=argus
   --cov-fail-under=80`.
   **Baseline RE-MEASURED on this tree by the SM, 2026-08-11:** **1324 tests collected across 82
   test files** under `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; **`mypy` clean on 72 source files**.
   Story 10.4 recorded **coverage 95.51%**, bandit **0 High / 0 Medium (19 Low)** and
   `argus audit .` → **RELEASE_READY, blocking_findings=0** at `a9cc933` — **re-verify these three
   rather than adopting them.** The count grows by **exactly** your new cases; **no test removed,
   skipped, weakened or `xfail`ed.**
2. **Coverage must not move materially, and you should say why.** Your guard executes **no `argus`
   line** (DN-6): it reads source as text. A drop below the 80% floor, or any change beyond rounding,
   means something imported `argus` — investigate rather than adjust the threshold.
3. **The dogfood artifacts stay byte-identical, and this is a designed property** (§D,
   `DF-10-4-D`). No `argus/**` file is created, modified **or staged**, so `git ls-files argus` does
   not move and the five artifact guards that halted Story 10.4 cannot fire. **Verify it, do not
   assume it:** `git diff --quiet -- argus/` **and** `git status --porcelain -- argus/` **empty**.
4. **Evidence-citation compliance** — 10.1's binding rule (`architecture.md` §H + §Enforcement,
   enforced by `tests/test_evidence_citation.py`). Local gates are **necessary, not sufficient**: CI
   runs 3.10/3.11/3.12 on ubuntu; this host is Windows/CPython 3.11.15. **No CI run has ever covered
   `a9cc933` or `93adc94`.** Either cite the `audit-ci.yml` run covering your **own** HEAD *with the
   sha it covers*, or record the status **NOT ESTABLISHED** and name the command a human runs.
   ⛔ **Do not push, tag or `workflow_dispatch`** (10.1's DN-7).
5. **Write set — the fence, checked with `git status --porcelain` AND `git diff --stat`** (E.5):

   | Permitted | For |
   |---|---|
   | `E-PRD/prd.md` (§Product Scope · §Compliance · Journey 4 · FR23/24/26/29 · frontmatter `amendments`) | AC1, AC2, AC4 |
   | `architecture.md` (**§Requirements Coverage Validation + §Enforcement ONLY**) | AC4.5, AC5.7 |
   | `deferred-work.md` (**append-only**) | AC6 |
   | `tests/test_v1_commitment_closure.py` (**NEW**) | AC5 |
   | this story file · `sprint-status.yaml` | process |

   **Byte-unchanged, verified with `git diff --quiet`:** **all of `argus/**`** · `tests/**` except
   the one new file · `epics.md` · `E-PRD/addendum.md` · `E-PRD/.memlog.md` · `README.md` ·
   `CHANGELOG.md` · `action.yml` · `audit-ci.yml` · `pyproject.toml` · the product briefs · the three
   `minions-dogfood-*.md` artifacts · every Epic 1–9 artifact and retrospective. **A diff outside the
   table means scope has leaked — stop and record why rather than widening.**
6. **Whole-system, not just the ACs.** Full suite green; the story leaves the system working
   end-to-end. Since no product code changes, "working" means: **every existing guard still passes,
   and the four sibling guards (`test_evidence_citation`, `test_spec_claim_scope`,
   `test_invocation_contract`, `test_grammar_diagnosis`) still pass against your amended
   documents** — your PRD and architecture edits land inside files three of them read.

---

## Tasks / Subtasks

- [x] **T1 — Re-measure before you edit anything — FIRST**
  - [x] Re-derive the §A.1 site list by grep, by anchor. Confirm **three** PRD sites (`:187`, `:309`,
        `:214`) and record the coordinates you actually found. (AC1)
  - [x] Re-run `grep -rniE "standards_ref|cwe|asvs|owasp" argus/ --include=*.py` → expect **0**. (AC1.6)
  - [x] Build the import graph and print the complement of the `argus.cli` closure. Confirm the §A.2
        table: `governance/escalation.py`, `governance/decision_record.py`, `evidence/bundle.py`,
        `store/integrity.py` all unreachable. **Keep the raw output — it is AC5.8's RED evidence.** (AC4)
  - [x] Re-verify the baseline: **1324 collected / 82 files**, **mypy clean on 72**. Record any
        divergence rather than adopting the story's figure. (AC7.1)
  - [x] Confirm `git status --porcelain -- argus/` is EMPTY *before* you start, so your end-state
        fence means something. (AC7.3)
- [x] **T2 — Write the guard RED, against the unamended documents (AC5) — BEFORE any amendment**
  - [x] `tests/test_v1_commitment_closure.py`, ids `DOCS-001-30..`; forward claim-shape closure,
        reverse FR closure, static reachability refutation of `wired`, both-direction positive
        controls, H0/DF-7-2-A open-pins, non-vacuity floors.
  - [x] Run it. **Record the failure showing `:187` and `:309` unclassified and FR23's `wired`
        claim refuted.** (AC5.8)
  - [x] sha256 round-trip any file you touched to produce the RED state.
- [x] **T3 — The forward sweep (AC3)**
  - [x] Run the parser; disposition every atom; state the counts.
  - [x] Dispose L189's `**Proof:** dogfood run against Minions itself` as `delivered-differently`
        with the 8.5 self-audit named and the ledger's own "materially weaker evidence class" quoted.
  - [x] Dispose L196's Minions consumption-contracts as `specified-not-built` with **H0 recorded
        OPEN and UNOWNED**. ⛔ Do not close H0.
- [x] **T4 — The reverse sweep (AC4)**
  - [x] Disposition all 37 FRs. Get **FR27** right: `delivered-differently`, mechanism → 12.3.
  - [x] **FR23 by name** — amend `:532` struck-not-deleted, dated, with the cut-order contradiction
        and the two-part reason stated.
  - [x] Amend FR24, FR26, FR29 in the same form if the measurement holds. ⛔ Leave FR34–37 alone.
  - [x] Correct `architecture.md:905` — **one caveat paragraph**, with the measured N.
- [x] **T5 — The decision and its consequence (AC1, AC2)**
  - [x] Amend all three standards sites; add the frontmatter `amendments` entry naming all three.
  - [x] Add the Journey 4 consequence note. ⛔ Do not touch the gate's status.
  - [x] Record `AI-E8-9`'s F2 half as disposed; name F4/F10/D1 as still open and not yours.
- [x] **T6 — Architecture (AC5.7)**
  - [x] One-line rule into §Enforcement + the guard registration; the guard asserts both present.
        Expect it RED first (the anchors do not exist yet), then green.
- [x] **T7 — Close the ledger and file forward (AC6)**
  - [x] `DF-6-7-A` closed append-only by disposition; `DF-10-4-B` re-targeted off this story;
        `DF-AUD-APAA-A`/`-B` given live targets or an explicit unowned-by-decision note.
  - [x] File the never-before-filed seams (FR24, FR26, FR29) and the standards V2 re-entry point.
  - [x] Write the closing paragraph of the class (AC6.6). `+n / -0` verified programmatically
        (`after.startswith(before)`).
- [x] **T8 — Gates, fences, write set (AC7)**
  - [x] mypy · bandit · full suite · coverage · re-run `argus audit .` and compare to
        `RELEASE_READY / blocking_findings=0`.
  - [x] Re-run the four sibling guards explicitly against your amended documents. (AC7.6)
  - [x] `git status --porcelain -- argus/` EMPTY; `git diff --quiet` on every byte-unchanged path;
        `git add` the new test and this story file.
  - [x] Record CI evidence per AC7.4 — cite a run covering your own HEAD, or **NOT ESTABLISHED**.

### Review Findings

**Code-review gate, iteration 1, 2026-08-11 (Sonnet).** Independently re-executed rather than read off
the story — every figure below was measured on this tree, not transcribed.

- **Re-run gates, all green, all figures reproduce exactly:** `mypy argus` → clean, 72 files.
  `bandit -r argus --severity-level medium` → clean (0 High/Medium at that threshold). Full suite
  `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest tests/` → **1336 collected across 83 files, exit code 0**
  (no F/E marks; a subprocess capture confirmed `returncode == 0`). `--cov=argus --cov-fail-under=80`
  → **95.51%**, gate reached, unmoved from baseline. `python -m argus.cli audit .` →
  `verdict=RELEASE_READY deep_ratio=61/164 blocking_findings=0 assessed_deep_ratio=61/77`, byte-for-byte
  the figures the story cites. The four sibling guards (`test_evidence_citation`,
  `test_spec_claim_scope`, `test_invocation_contract`, `test_grammar_diagnosis`) and the 49 dogfood/staleness
  tests all pass standalone.
- **New guard `tests/test_v1_commitment_closure.py` (12 tests, `DOCS-001-30`..`-41`) runs green in
  isolation** and its own internal claims were spot-checked: `git diff --numstat` on `prd.md` is
  `+28/-6` and on `architecture.md` is `+4/-0`, exactly as claimed; `deferred-work.md`'s `+240/-0` was
  verified programmatically (`after.startswith(before)` on the raw bytes) — genuinely append-only;
  the FR-cluster→location table at `architecture.md:874-885` is untouched (diff confirms no change
  inside that range). `git status --porcelain -- argus/` and `git diff --quiet -- argus/` are both
  clean — zero `argus/**` changes, DN-7 held.
- **Write-set fence held exactly as declared** (AC7.5): only `E-PRD/prd.md`, `architecture.md`
  (§Enforcement + §Requirements Coverage Validation only), `deferred-work.md` (append-only), the new
  test file, this story file and `sprint-status.yaml` are touched. `epics.md`, `README.md`,
  `CHANGELOG.md`, `action.yml`, `pyproject.toml` and the rest of `tests/**` are byte-unchanged
  (`git diff --quiet` confirmed). PRD frontmatter `amendments:` block re-parses as valid YAML with the
  new 2026-08-11 entry naming all three sites.
- **Ledger dispositions read as claimed**: `DF-6-7-A` closed by disposition, `DF-10-4-B` re-targeted
  off this story onto 12.4/12.5, `DF-AUD-APAA-A`/`-B` un-orphaned off the `done` epic-7 target,
  `DF-10-5-A/-B/-C/-D` filed with id/owner/`target_story` per AI-E9-8, H0/`DF-7-2-A`/the ≥80% gate all
  still recorded open — all independently re-read at their cited coordinates, not taken on faith.
- **[Low][Dismiss] Guard file at 1308 lines exceeds the "same band as 863/1100" the story's own Dev
  Notes suggested for NFR-M1** — `architecture.md:813` and `:660` scope NFR-M1's ≤1200-line rule to
  the `argus/**` package tree, not `tests/`, so this is not a violation of the binding architecture
  constraint, and the Debug Log already reasons about the overage (two closures meeting in the middle
  cost more code than one). No action needed; noted for completeness, not actionable.

No `decision-needed`, `patch`, `defer` or unresolved High/Medium findings. **0 decision-needed · 0
patch · 0 defer · 1 dismissed as noise.**



### LOCKED decisions taken at story design — record these, do not re-litigate

| # | Decision | Rationale |
|---|---|---|
| **DN-1** | **`standards_refs[]` + CWE-on-security-findings is decided **V2**.** Applied at **all three** measured sites, struck-not-deleted, dated, with the V2 merge recorded at the destination. | The recommendation of record in the operator-approved `sprint-change-proposal-2026-08-10b.md:362-364`, re-derived on this tree: (a) the 2026-08-03 case *for* shipping was explicitly *"far cheaper now than after the finding schema is frozen"* — the schema is **now frozen, content-hashed and shipped**, so the premise expired; (b) a persisted `standards_refs[]` widens the redaction/containment surface (NFR-S1/S2) that Epic 4 spent a whole story bounding; (c) the audience it serves is Journey 4 / attested use, which the ≥80% gate holds **NOT CLEARED** — shipping it today serves **no reachable user**; (d) the binding FR contract (`:457`) never listed it, so by the contract its absence is already correct. The decision is **reversible** (a spec amendment) and costs nothing to revisit in V2. |
| **DN-2** | **AC5 (the guard) is load-bearing — not AC3 or AC4 (the sweeps).** | The enumeration in this epic has been wrong **four times** (10.2 ×3; §A.1 here, where one named site is actually three). A sweep closes today's instances; a closure closes the class. §A.2 is the proof at scale: the class was **filed four times and swept zero times**. |
| **DN-3** | **FR23 is disposed `library-seam`, and the FR text is amended to say so** — struck-not-deleted, dated, following FR7's (10.2) and FR30's (10.3) precedent. Owner **XAgent007 (Governance Owner)**; `target_story: NONE — unscheduled; Governance Owner to schedule once Story 12.1 lifts the NFR-M1 gate on `pipeline.py`` (the `DF-10-4-E` form, house-legal because a human is named). | The epic AC pre-authorises exactly this option *by name*. **Wiring is impossible inside this story's fences**: every call site lands in `pipeline.py`, which is 1331/1200 and byte-fenced to 12.1. And a naive wiring would be wrong on its own terms — the V1 default path is unattended CI (Journeys 3, 5) with no human to answer a default-STOP gate. **The amendment must state the cost it incurs**: the PRD cut-order marks FR23 non-negotiable core (only FR24 is `[Tier B]`), and `implementation-readiness-report-2026-08-03.md:365` flagged it as stranded. This is the one decision in the story an operator might overturn — it is surfaced in §Open questions for exactly that reason. |
| **DN-4** | **The two disposition vocabularies are CLOSED SETS** (AC3.2, AC4.2). A hit that fits none of them is a **HALT**, not a new label invented mid-sweep. | An open vocabulary is how *"maps to a module"* became a certification (§A.3). A closed set forces the awkward cases — `delivered-differently`, `specified-not-built` — to be *stated* rather than absorbed into a comfortable word. |
| **DN-5** | **An `nfr-backed` commitment is RECORDED AS SPECIFIED, not as a gap.** | The FR preamble (`:457`) binds *capabilities*; NFRs are equally binding requirements, and the architecture validates them separately. Treating `work_manifest`→NFR-S4 as a "missing FR" would manufacture a defect and dilute the real hits — the over-claiming this epic exists to stop. The *reachability* of NFR-S4's `read_in_scope` is a genuine hit, and it is already `DF-AUD-APAA-B`. |
| **DN-6** | **The guard reads source as TEXT and resolves imports STATICALLY. It must not `import argus`.** | Three measured reasons: lazy imports exist and would defeat a runtime walk (`precision/replay_harness.py:87-90`); importing `argus` makes the result depend on which optional extras are installed, so CI and this host could disagree; and a test that executes no `argus` line cannot perturb the coverage figure the ledger cites (AC7.2). Precedent: 10.1's guard is pure `pathlib` + `re`, 10.4's is pure `ast`. **Add no dependency.** |
| **DN-7** | **Zero `argus/**` changes — not "few". Zero.** | (a) Epic 10 closes the record and ships nothing; (b) DN-1 means no field ships; (c) DN-3 means no wiring; and (d) it is what keeps this story clear of `DF-10-4-D`, which halted Story 10.4 on five reds the moment it **staged** one new `argus/` module. The fence is a designed property of the write set, and AC7.3 verifies it rather than assuming it. |
| **DN-8** | **The sweep log lives in the guard registry and the Dev Agent Record — NOT in the PRD.** | The PRD records decisions and contracts. A 37-row delivery-status table inside it would be stale the day 12.1 lands and would become a second source of truth for reachability — the `source_languages.py` lesson FR7 and FR30 both encode: *"a prose copy of an enumerable fact drifts."* |
| **DN-9** | **⛔ No verdict, gate, threshold or disclosure changes; H0 and DF-7-2-A stay OPEN.** | This story is the one most likely to close an open item by accident, because "sweep everything and classify it" reads like permission to tidy. AC5.5 turns that fence into a test so the guard defends against its own author. |

### Architecture patterns & constraints a reviewer will check

- **§3.4 evidence immutability** — every correction is **struck, not deleted**, dated and attributed.
  `deferred-work.md` is **append-only** (`+n / -0`), verified programmatically.
- **AR8 pure/impure** — the guard is a pure function over file text; no I/O beyond reads, no network,
  no `argus` import (DN-6).
- **NFR-A1 / NFR-M2 additive-only, frozen contracts** — DN-1's central argument. No schema bump.
- **NFR-M1** — every touched file stays ≤1200 lines. Your only new file is a test; keep it under the
  cap (10.4's is 1100, 10.3's 863 — you are in the same band).
- **`E-PRD/prd.md:457`** — *"a capability not listed here will not exist in V1 unless explicitly
  added"* — the sentence that makes DN-1 contract-correct, and the sentence AC4 makes symmetric: a
  capability **listed** here that no code path reaches does not exist either.
- **`architecture.md:874-885`** — the FR-cluster→location table. **Read-only.** AC4.5 caveats the
  claim above it, not the table.

### Testing standards — the house form your new file must match

- `pytest`, one verification-area id per test in the **docstring first line**:
  `"""TC-ArgusAgent-DOCS-001-30 — <what it pins>."""` Measured maxima in use: `DOCS-001-29`,
  `CLI-001-49`, `INDEX-001-119`, `AUDIT-001-58`, `REPORT-002-29`.
- Pure functions over synthetic inputs for controls; `tmp_path` for fixtures. **Never** edit the real
  PRD, architecture or package during a test, and never mutate a module-level registry without
  restoring it.
- Failure messages state **what broke and what to do** — every guard in `test_evidence_citation.py`,
  `test_spec_claim_scope.py`, `test_invocation_contract.py` and `test_grammar_diagnosis.py` does
  this; match it.
- `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` turns optional-grammar skips into hard failures. **Run the
  suite with it set**, as CI does (`audit-ci.yml:75`).
- Artifact paths inside the guard resolve **relative to the repo root**, discovered from
  `__file__` — the four sibling guards already do this; copy their resolution, do not invent a
  third.

### Previous story intelligence — 10.1, 10.2, 10.3, 10.4 (all `done`, all PASS on review iteration 1)

- **10.1** — the citation standard (run id **plus** the sha it covers, or **NOT ESTABLISHED**) in
  `architecture.md` §H + §Enforcement, guarded by `tests/test_evidence_citation.py`
  (`DOCS-001-20..-23`). **AC7.4 is that rule applied to you.** Its **DN-7** (never manufacture a
  citation) and **DN-8** (ledger corrections are append-only) both bind. It also set the
  zero-product-code precedent: *"`git status --porcelain -- argus/` is EMPTY."*
- **10.2** — grounding 8/10 → 10/10; **its hand-list was wrong three times**, and its recorded
  conclusion — *"the closure GUARD, not the site list, is the load-bearing AC"* — is DN-2. Filed
  `DF-10-2-A` (C/C++/Ruby/Rust ground but extract **zero** definitions, so those files cannot reach
  `audited_deep`). ⛔ Not yours; do not conflate it with a reachability hit.
- **10.3** — parser-derived CLI equality guard, both directions, with **named exemptions carrying
  reasons** rather than silence. Blessed `--ignore-pattern` behind the Live-Key Safeguard. Its
  central finding — *"the operator's INPUTS are persisted while the EFFECT leaves no trace"* — is
  your class one level down.
- **10.4** — four grammar-failure tokens, per-class remedies, new `argus/shared/grammar_status.py`;
  closure over the function's own AST. **It filed `DF-10-4-B` FOR YOU** (`DetectorResult.degraded`,
  zero production readers) — AC6.2 is that hand-off discharged. It also halted on `DF-10-4-D` and
  filed `DF-10-4-E`. **Its `git add` of one `argus/` module is what cost it a halt** — DN-7 is the
  lesson applied.
- **Shared review posture across all four**: reviewers **re-derived every mechanical figure by
  execution** rather than reading it off the story. Expect it. Do not hand in a number you did not
  run.

### Runtime & toolchain, verified on this machine 2026-08-11

CPython **3.11.15** (Windows) vs CI's ubuntu × 3.10/3.11/3.12 · `tree-sitter` **0.25.2** ·
`mypy` clean on **72** source files · suite **1324 collected across 82 files** under
`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` · `argus/pipeline.py` **1331** lines (NFR-M1 cap 1200,
fenced to 12.1) · `argus/cli.py` **479** lines · **72 Python modules under `argus/`, of which 43 are
reachable from `argus.cli`**.

**No web research was required and none was used.** This story's every external fact is a property
of documents and code **in this repository**, measured by execution. There is no library, API or
version question in it; a search result would be weaker evidence than the grep.

### Project structure notes

One new file, `tests/test_v1_commitment_closure.py`, flat under `tests/` — the house layout, matching
the four sibling guards. **No new `argus/` module, no new package, no new dependency, no
`__init__.py` change** (DN-6, DN-7). This is the first Epic-10 story whose delta touches `tests/` and
the artifact tree only.

### Open questions for the operator — saved for the end, as the workflow requires

1. **FR23's de-scope (DN-3) is the one decision here an operator may want to overturn.** The PRD
   cut-order marks FR23 **non-negotiable core**, and this story amends it to a library seam with an
   **unscheduled** call site. Ruled **library seam**, because wiring is fenced to 12.1 and a
   default-STOP gate in unattended CI would deadlock Journeys 3 and 5 — but if the Governance Owner
   wants FR23 wired for V1.5, the honest route is a **new Epic 12 story**, which is a correct-course
   decision and **outside this story's authority**. Flagged, not assumed.
2. **The measured N of `library-seam` FRs may exceed the three named here** (FR24, FR26, FR29). If
   the sweep returns materially more, **report the number and dispose them; do not widen scope to fix
   any of them**, and say so in the Dev Agent Record.
3. **`product-brief-apaa-distillate.md:47` lists `standards_refs` in the frozen `finding` schema.**
   Ruled **leave unamended** — the briefs are superseded upstream inputs, and 10.2 set that precedent
   — but the decision is recorded rather than silent (§A.1).
4. **`epics.md:1932` still cites the commitment at PRD `L168`, which is now `L187`.** Ruled **leave
   as written** (§3.4, and `epics.md` is fenced), and record it in the Dev Agent Record as the
   epic's own instance of the coordinate-drift lesson — the fifth in three days.

### References

- [epics.md#Story 10.5](../epics.md) `:1922-1962` — the four ACs this story implements ·
  `:1738-1760` — Epic 10's frame and the citation standard it hands down
- [sprint-change-proposal-2026-08-10b.md](../sprint-change-proposal-2026-08-10b.md) `:99-115`
  (§1.4(c), the conflict) · `:352-364` (Story 10.5 as written + the recommendation of record) ·
  `:410-411` (success criterion 2b)
- [E-PRD/prd.md](../E-PRD/prd.md) `:187`, `:309`, `:214` (the three standards sites) · `:191-196`
  (V1 Design Invariants) · `:222-232` (Minions consumption contracts → H0) · `:260-265` (Journey 4) ·
  `:455-551` (§Functional Requirements, FR1–37) · `:457` (the binding-contract preamble) · `:532`
  (FR23) · `:84-94` (frontmatter `amendments`)
- [architecture.md](../architecture.md) `:874-885` (FR-cluster→location, read-only) · `:897-919`
  (Requirements Coverage Validation — `:905` is the sentence AC4.5 corrects) · `:712-757`
  (§Enforcement — register your guard here)
- [deferred-work.md](../deferred-work.md) `:464-479` `DF-AUD-APAA-A` · `:481-494` `DF-AUD-APAA-B`
  (both orphaned targets) · `:1634-1642` `DF-6-7-A` (close by disposition) · `:1905-1923`
  `DF-10-4-B` (targets this story) · `:1942-1986` `DF-10-4-D` (the trap DN-7 avoids)
- [implementation-readiness-report-2026-08-03.md](../implementation-readiness-report-2026-08-03.md)
  `:351-358` (F2 — this story's AC1, with the opposite recommendation and the premise that expired) ·
  `:365` (FR23 stranded) · `:400` (*"the unnumbered-obligation pass scores 68%"*)
- [implementation-readiness-report-2026-08-10.md](../implementation-readiness-report-2026-08-10.md)
  `:443`, `:583`, `:617`
- [epic-8-retro-2026-08-08.md](../epic-8-retro-2026-08-08.md) `:170` (`AI-E8-9`) ·
  [epic-9-retro-2026-08-09.md](../epic-9-retro-2026-08-09.md) `:130`, `:168` (measured NOT addressed)
- [Story 10.1](10-1-release-status-must-cite-evidence.md) (citation rule, DN-7/DN-8, the
  zero-product-code fence) · [Story 10.2](10-2-multi-language-grounding-is-v1-in-the-specs.md)
  (*"the closure guard, not the site list"*) ·
  [Story 10.3](10-3-invocation-contract-says-what-the-cli-accepts.md) (both-direction registry,
  named exemptions) · [Story 10.4](10-4-a-grammar-that-fails-to-load-names-why.md) `§A.3`
  (`DetectorResult.degraded`, handed to you)
- `argus/cli.py` (479, the only entry point) · `argus/pipeline.py` (1331, fenced) ·
  `argus/governance/escalation.py`, `argus/governance/decision_record.py`, `argus/evidence/bundle.py`,
  `argus/store/integrity.py` (the four unreachable seams) · `argus/detectors/base.py:63-87`
  (`FindingDraft`, no standards field) · `pyproject.toml:59-62` (three aliases, one entry point)

---

## Dev Agent Record

### Context Reference

- This story file (self-contained; §A–§E carry every measurement).

### Agent Model Used

`claude-opus-5[1m]` (Claude Code / BMAD `dev-story`), 2026-08-11.

⚠️ **This story was interrupted TWICE by infrastructure faults and resumed under operator
authorization; it belongs in the record.** Attempt 1 was killed after ~34 tool calls, immediately
before the guard was written, leaving **no output at all** — no test file, sprint-status still
`ready-for-dev`. Attempt 2 was killed mid-stream at the exact moment T7 (the ledger append) was
announced, leaving the PRD and `architecture.md` amended and the ledger **untouched**. Attempt 3
(this one) verified on disk that T7 had not partially landed *before* writing it, so the
append-only guarantee could not be corrupted by a duplicated entry. **Nothing in the delta is a
partial write.** Both interruptions cost re-measurement, not correctness — every figure below was
re-derived by execution on this tree, never transcribed from the story's §A–§E.

### Debug Log References

**T1 — re-measurement (2026-08-11, this tree, HEAD `93adc94`).** Confirmed before editing anything:

- `standards_refs` sites: **three**, exactly as §A.1 measured — `prd.md:187` (V1 Core), `prd.md:309`
  (§Compliance, *"Standards anchoring (phased)"*), `prd.md:214` (the V2 destination). Located by
  anchor, not by line.
- `grep -rniE "standards_ref|cwe|asvs|owasp" argus/ --include=*.py` → **0**. Re-verified at the end:
  still **0**.
- `git status --porcelain -- argus/` → **EMPTY before starting**, so the end-state fence means
  something.
- Import walk (stdlib `ast`, closure from `argus.cli`): the four seams
  `governance/escalation.py`, `governance/decision_record.py`, `evidence/bundle.py`,
  `store/integrity.py` are **all unreachable**, confirming §A.2.

**Two divergences from the story's §A measurements, recorded rather than silently adopted.**

1. **Reachability: 53 of 72 reachable / 19 unreachable, not 43 / 29.** The story's figure omits the
   **ancestor-package edges** an import implies: importing `argus.x.y` also loads `argus.x`, so a
   naive walk reports every `__init__.py` as unreachable and **inflates the seam count**. In a guard
   whose entire purpose is to stop over-claims, shipping the inflated number would have been the
   story's own defect. The committed guard records ancestor edges. **Every load-bearing conclusion
   is identical under both models** — the four seams are unreachable either way — so this changes
   the N quoted in `architecture.md`'s caveat and nothing else. Also: `cache/key.py` **is**
   reachable (§A.2's table asks *"key.py reachable? no"* — measured, yes), and
   `governance/escalation.py` has **one** importer inside the package, not *"none at all"* —
   `governance/decision_record.py`, itself unreachable. Neither changes a disposition.
2. **H0 is not *"OPEN and UNOWNED"* on this tree.** §D and AC5.5 instruct pinning it so. Measured:
   `deferred-work.md` records **H0's *ownership* CLOSED on 2026-08-10b** via the pre-authorised
   option (b), the operator electing to file outside this workflow. What is still open is the
   **execution** — the same entry says *"It does not mean H1–H4 have been filed"* and *"Assumption
   A5 remains ⚠️ UNSUPPORTED"*. **Pinning the stale "UNOWNED" would have pinned a fact that stopped
   being true the day before this story ran** — which is precisely the defect Epic 10 exists to
   close, committed by the guard meant to close it. `-38` therefore pins the **residual that is
   still true**: the filing is not done and A5 is unsupported. AC5.5's intent — *this story must
   not close H0* — is honoured exactly; its wording is not. Recorded in the ledger append too.

**T2 — RED FIRST, discharged twice (AC5.8, E.1).**

*Run 1 — against the genuinely UNAMENDED documents, with the registry in its pre-decision state*
(the two `reclassified-v2` entries absent, FR23 asserted `wired` exactly as `architecture.md:905`
implied for five weeks):

```
E  AssertionError: A V1 commitment in the PRD carries NO disposition. ...
E      prd.md:187 [- **V1 Core:**] `standards_refs[]` field + **CWE-required-on-security findings**
E                 (day-one additive; rich mapping -> V2)
E      prd.md:309 [**V1:**] `standards_refs[]` field (format-validated, e.g. `^CWE-\d+$`) + **CWE
E                 required on every security-category finding** ...
E  AssertionError: A delivery disposition is REFUTED by the static import graph. ...
E      FR23: disposed 'wired' but argus.governance.escalation is NOT in the import closure from
E            argus.cli - a wired claim is proven, never asserted
```

Both AC5.8 conditions met: **`:187` AND `:309` unclassified**, and **FR23's `wired` claim
mechanically refuted**. The guard file was restored byte-identically — sha256
`492d8cd5b154db81f887617a0905517f3ede8060047ce36a0795fdd8731a8b9c` before and after.

*Run 2 — LIVE BITE against the finished tree*, because a RED that only ever existed against deleted
text is weak evidence. Two mutations injected into the real files, then restored: the strike removed
from `prd.md`'s §Compliance site, and FR23 flipped to `wired`. Both fired. Restore verified by
sha256 on both files (`prd.md` `604ac8fb…`, guard `9bc7bd31…`, MATCH on both).

🚩 **The live bite found a real bug in this story's own guard, and it is worth reading.** The
first version of `-40` asserted `"~~" in atom.text`. Deleting only the **opening** `~~` left the
closing marker on the line, so the assertion stayed **true** and the guard stayed **green over a
half-struck commitment**. That is `AI-E3-1` — *a keystone test green over its own keystone bug* —
reproduced inside the guard written to prevent it, and it was caught only because the bite was run
live rather than assumed. Fixed by `struck_spans()`: the assertion is now *"the registry anchor
falls inside a **closed** `~~ … ~~` span"*, not *"a strike marker exists somewhere"*. An unbalanced
marker yields no span and turns the check red. Four synthetic regression cases pinned in `-36`.

**T8 — gates, all LOCAL (this host: Windows / CPython 3.11.15; CI is ubuntu × 3.10/3.11/3.12).**

| Gate | Result | Baseline it is compared to |
|---|---|---|
| `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest tests/` | **1336 passed, 0 failed, 0 error, 0 skipped, 0 xfail** (progress line is 1336 `.` and nothing else) | 1324 — **+12, exactly this story's new cases**; none removed, skipped, weakened or `xfail`ed |
| test files | **83** | 82 — +1, the new guard |
| `--cov=argus --cov-fail-under=80` | **95.51%**, gate reached | 95.51% — **unmoved, not even by rounding**, because the guard reads source as text and executes no `argus` line (DN-6 / AC7.2) |
| `mypy argus` | **Success: no issues found in 72 source files** | 72 clean |
| `bandit -r argus --severity-level medium` | **no output (clean)**; full scan **0 High / 0 Medium / 19 Low** | 0/0/19 |
| `argus audit .` | **`verdict=RELEASE_READY deep_ratio=61/164 blocking_findings=0 assessed_deep_ratio=61/77`**, exit 0 | identical to 10.4's figures at `a9cc933` |
| dogfood staleness guards (`-k dogfood`, `DF-10-4-D`) | **49 selected, 49 passed** | green — as designed: no `argus/**` file was created, modified **or staged**, so `git ls-files argus` did not move |
| four sibling guards (AC7.6) | green inside the full suite — `test_evidence_citation`, `test_spec_claim_scope`, `test_invocation_contract`, `test_grammar_diagnosis` all pass **against the amended `prd.md` and `architecture.md`**, which three of them read | — |

**AC7.4 — CI evidence: NOT ESTABLISHED.** No `audit-ci.yml` run has ever covered `a9cc933`,
`93adc94`, or this working tree; run `31341363300` is sha-scoped to `00c8d1b` and cannot evidence
it. Per Story 10.1's binding rule a status claim carries a run id **plus the sha it covers** or it
is recorded NOT ESTABLISHED — so every figure above is labelled **LOCAL**. ⛔ Nothing was pushed,
tagged or `workflow_dispatch`ed (10.1 DN-7: triggering a run to manufacture a citation is
manufacturing evidence). **The command a human runs to establish it:** push this branch and let
`audit-ci.yml` run, then cite the run id together with the sha it covered.

**Write-set fences — verified, not assumed.**

- `git status --porcelain -- argus/` → **EMPTY**. `git diff --quiet HEAD -- argus/` → clean.
  `git diff --cached --name-only -- argus/` → **0 files**. **Zero `argus/**` changes** (DN-7).
- `deferred-work.md` → `git diff --numstat` = **`240 / 0`**, and append-only proven programmatically
  (`after.startswith(before)` plus a sha256 match on the unchanged prefix), not by eye.
  ⚠️ 26 of those 240 lines are `DF-10-4-E`, appended by **Story 10.4's review agent**, not by this
  story; it was already in the working tree and was left untouched.
- `architecture.md` → `+4 / -0`: two paragraphs appended, nothing replaced. The FR-cluster→location
  table and the rest of §Architecture Validation Results are **byte-unchanged**.
- `prd.md` → `+28 / -6`. The six touched lines are exactly `:187`, `:309`, FR23, FR24, FR26, FR29,
  each struck-not-deleted so the original text survives on the line.
- Byte-unchanged, verified with `git diff --quiet`: `epics.md`, `README.md`, `CHANGELOG.md`,
  `action.yml`, `pyproject.toml`, all of `tests/**` except the one new file, the three
  `minions-dogfood-*.md` artifacts, every Epic 1–9 artifact and retrospective.
- ⚠️ **Two dirty paths that are NOT this story's**, flagged so a reviewer does not read them as
  scope leak: `E-PRD/addendum.md` and `E-PRD/.memlog.md` each carry a **one-line** pre-existing
  change (`**Approved by:** Varin` → `XAgent007`) that was in the working tree **before this story
  started** and is untouched by it. Likewise `stories/10-4-…md` carries 10.4's review writes.
- **Housekeeping:** the stray untracked file literally named `NUL` at the repo root was **deleted**
  on operator instruction. Inspected first — 837 bytes of captured `argus audit .` stdout from a
  `>NUL` redirect run under bash (which creates a real file, unlike `cmd`). ⚠️ The story's own
  `baseline_note` said not to delete it; the **orchestrator that owns that path explicitly
  instructed its deletion twice**, which releases the fence set on its behalf. Untracked, so no
  history was at risk. Recorded because an unrecorded deletion is exactly what this epic exists to
  stop.

### Completion Notes List

**What shipped: a decision, two classifications, and one guard. No capability, by design.**

- **AC1 — the `standards_refs[]` conflict is DECIDED V2 (DN-1), at all three sites.** §Product Scope
  V1 Core and §Compliance & Regulatory are **both** struck-not-deleted, dated and attributed —
  amending only the first would have left the PRD self-contradicting, which is the state the story
  exists to end. The §Compliance site is **the one that had been named in no planning document since
  2026-08-03**, and it carries a `^CWE-\d+$` **format** commitment the other never made; that moves
  with it. The V2 landing is recorded **at the destination** as a **merge into the pre-existing
  *standards mapping (CWE/ASVS/ISO 25010/SLSA)* item** — the inverse of 10.2's rule: a delivered
  capability left on the roadmap double-counts, an undelivered V1 item absorbed silently
  **under**-counts and erases that anything was ever promised. Four reasons recorded, not asserted;
  the load-bearing one is that the 2026-08-03 case *for* shipping was *"cheaper now than after the
  schema is frozen"* and **the schema is now frozen, content-hashed and shipped — the premise
  expired**. Frontmatter `amendments` entry added naming all three sites; YAML re-parsed to confirm
  it is valid. **Zero code shipped**: `detectors/base.py` byte-unchanged, schema version unchanged,
  `grep standards_ref|cwe|asvs|owasp argus/` still **0**. `AI-E8-9`'s **F2/CWE half only** is
  recorded disposed — F4 (`SC-E`), F10 and D1 are named **still open and not this story's**.
- **AC2 — Journey 4 carries the consequence as a known trade.** Dana's bundle carries **no standards
  reference** in V1; **FR11** (hardcoded-secret detection) is named as the one security-category
  finding producer, so a reader knows the exact scope. Scoped honestly: Journey 4 is the attested /
  operated-service path the ≥80% gate already holds **NOT CLEARED**, so no user is served worse
  today than that gate permits — and the note is written so it cannot read as clearing, softening or
  scheduling the gate. Re-entry point named (V2's standards mapping) and filed as `DF-10-5-D`.
- **AC3 — forward sweep: 20 atoms, every one disposed.** Population derived **by claim shape across
  the whole PRD**, not by heading — the whole argument of the story, and `prd.md:309` is its proof.
  Counts, from the parser (which wins over any hand read): **`fr-backed` 11 · `nfr-backed` 2 ·
  `constraint` 3 · `reclassified-v2` 2 · `specified-not-built` 1 · `delivered-differently` 1 = 20**,
  matching the 20 atoms one-to-one in both directions. The two load-bearing awkward cases are
  recorded rather than absorbed into a comfortable word: L189's **`**Proof:** dogfood run against
  Minions itself`** → `delivered-differently` (replaced by Story 8.5's self-audit of `argus/`, which
  the ledger itself calls *"a materially weaker evidence class … not independent corroboration of
  anything"*; ⛔ Epic 7/8 not re-opened, no Minions run attempted, RS-1 respected), and L196's
  Minions consumption-contracts → `specified-not-built` with **the filing recorded OPEN**, never
  `done`. Sweep log lives in the guard registry and here — **not in the PRD** (DN-8).
- **AC4 — reverse sweep: FR1–FR37, enumerated mechanically, every one disposed.** Counts: **`wired`
  27 · `library-seam` 4 · `delivered-differently` 2 · `not-built` 4 = 37**. Every one of the 27
  `wired` claims is **proven** by `-34` — module exists, anchor present, module inside the closure —
  not asserted. **FR23 decided BY NAME, `library-seam` (DN-3)**, amended struck-not-deleted with
  **both halves of the reason** (the call site lands in `pipeline.py` at 1331/1200, fenced to 12.1;
  and the V1 default path is unattended CI with no human to answer a default-STOP gate, so naive
  wiring deadlocks Journeys 3 and 5) **and with the cost it incurs stated rather than hidden** — the
  cut-order marks FR23 non-negotiable core and 2026-08-03 already flagged it stranded. **FR24, FR26
  and FR29 take the same treatment; all three had NEVER been filed in five weeks.** FR29 is the
  sharpest: its text says *"An operator can export an evidence bundle"* and **no operator can** — no
  CLI subcommand exists. **FR27 got the trap right**: `delivered-differently`, delivered by
  determinism, mechanism → 12.3 — classifying it a seam would have manufactured a false accusation,
  the failure mode this product exists to prevent. ⛔ FR34–37 left unamended, as instructed.
  `architecture.md`'s *"No FR is unsupported"* gains **one caveat paragraph** with the measured N;
  the FR-cluster table is byte-unchanged and the validation method was **not** re-run.
- **AC5 — the guard, and it is the load-bearing AC (DN-2).** `tests/test_v1_commitment_closure.py`,
  **12 tests, `TC-ArgusAgent-DOCS-001-30`..`-41`**, 1308 lines (NFR-M1 cap 1200 applies to `argus/**`
  source; the sibling guards sit at 863 and 1100 and this one carries two closures). Two closures
  that meet in the middle, both directions each; `wired` mechanically refutable **and** `library-seam`
  symmetrically refutable, so wiring a seam in 12.1/12.3 turns this red until the disposition is
  updated. Positive controls are pure functions over **synthetic** inputs — the real PRD and the real
  package are never edited by a test. Non-vacuity floors are named constants, each carrying the
  reason its number is what it is. **No `import argus`** (DN-6), stdlib only, **no new dependency**.
  Registered in `architecture.md` §Enforcement with the one-line rule, and `-41` asserts both the
  rule text and the registration are still present.
- **AC6 — the ledger closes honestly.** `DF-6-7-A` closed by disposition; **`DF-10-4-B` re-targeted
  OFF this story** onto 12.4 (secondary 12.5) so 10.5 does not manufacture a fifth orphan;
  `DF-AUD-APAA-A` re-targeted to 12.3 and `-B` re-recorded open-unowned-by-decision with a **named
  human**, both off the `done` epic they had pointed at since 2026-07-04. Four new filings —
  `DF-10-5-A/-B/-C` (the never-filed seams) and `-D` (the V2 re-entry point) — each with an id, an
  owner and a `target_story` in the sanctioned `DF-10-4-E` form. The closing paragraph of the class
  is written as one paragraph, and it is the epic's closing sentence.
- **AC7 — gates green, fences held, write set exactly as declared.** See the Debug Log table.

**⛔ Nothing open was closed.** H0's filing stays open (A5 still UNSUPPORTED), `DF-7-2-A`'s
adjudication stays open, the **≥80% precision gate stays NOT CLEARED** — the first two pinned
**mechanically** by `-38`, the rest verified by inspection and listed in the ledger append. No
verdict, gate, threshold or disclosure changed. FR34's disclosure untouched.

**Fences respected:** `pipeline.py` byte-unchanged (12.1) · `--help` prose untouched (12.8) ·
`README.md` untouched (12.7/11.5) · `pyproject.toml` untouched (12.5) · tree-sitter false-green not
approached (11.4) · nothing published, tagged or dispatched (12.9) · precision gate untouched
(Epic 13).

**Open questions for the operator — carried forward to the Epic 10 retrospective.**

1. **FR23's de-scope (DN-3) is the one decision here an operator may want to overturn**, and it is
   implemented as locked while being recorded loudly enough to overturn. The PRD cut-order marks
   FR23 **non-negotiable core** and this story amends it to a library seam with an **unscheduled**
   call site. If the Governance Owner wants FR23 wired for V1.5, the honest route is a **new Epic 12
   story** — a correct-course decision, outside this story's authority. Everything needed to
   overturn it is in one place: FR23's amended text, `DF-6-7-A`'s closure, and `DF-10-5-A` (FR24,
   which must move with it).
2. **The measured `library-seam` count is exactly the three predicted plus FR23** — no more. Open
   question 2 anticipated it might be materially larger; it is not.
3. **`product-brief-apaa-distillate.md` lists `standards_refs` in the frozen `finding` schema and is
   left unamended**, per the story's ruling and 10.2's precedent that briefs are superseded upstream
   inputs. Recorded here so the decision is not silent.
4. **`epics.md:1932` still cites the standards commitment at PRD `L168`; it is at `L187`.** Left as
   written (`epics.md` is fenced) and recorded as **the epic's own instance of the coordinate-drift
   lesson — the fifth in three days**, and the reason this story's guard locates every site by
   anchor text and forbids line numbers in registry evidence (`-31` asserts it).

### File List

**Modified**

- `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` — AC1 (three standards sites +
  frontmatter `amendments`), AC2 (Journey 4 consequence note), AC4 (FR23/FR24/FR26/FR29 amended
  struck-not-deleted). `+28 / -6`.
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — AC4.5 (one caveat paragraph under
  §Requirements Coverage Validation) and AC5.7 (§Enforcement: the rule + this guard's registration).
  `+4 / -0`; the FR-cluster→location table is byte-unchanged.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — AC6, **append-only `+240 / -0`**
  (26 of which are 10.4's pre-existing `DF-10-4-E`).
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — process; one status value plus a
  dated annotation.
- `_bmad-output/design-artifacts/ArgusAgent/stories/10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1.md`
  — this file (`git add`ed, per AI-E8-1 / E.5).

**Added**

- `tests/test_v1_commitment_closure.py` — AC5, the closure guard
  (`TC-ArgusAgent-DOCS-001-30`..`-41`). `git add`ed.

**Deleted**

- `NUL` (repo root) — untracked shell-redirect debris; see the Debug Log.

**Byte-unchanged and verified:** all of `argus/**` · all of `tests/**` except the one new file ·
`epics.md` · `README.md` · `CHANGELOG.md` · `action.yml` · `pyproject.toml` · the product briefs ·
the three `minions-dogfood-*.md` artifacts · every Epic 1–9 artifact and retrospective.

## Change Log

| Date | Change |
|---|---|
| 2026-08-11 | Story implemented (`dev-story`). **AC1:** `standards_refs[]` + CWE-on-security-findings **decided V2** (DN-1) and applied struck-not-deleted at **all three** measured PRD sites — including `prd.md:309`, a second independently-binding V1 site invisible to every planning document since 2026-08-03 — with the reclassification recorded as a **merge at the V2 destination** and a dated frontmatter `amendments` entry. **AC2:** Journey 4 gains the consequence as a known trade, naming FR11 and leaving the ≥80% gate untouched. **AC3:** forward sweep — 20 V1 commitment atoms, all disposed (11 `fr-backed`, 2 `nfr-backed`, 3 `constraint`, 2 `reclassified-v2`, 1 `specified-not-built`, 1 `delivered-differently`). **AC4:** reverse sweep — FR1–37 all disposed (27 `wired`, 4 `library-seam`, 2 `delivered-differently`, 4 `not-built`); **FR23 decided by name as `library-seam`** with both halves of the reason and its cut-order cost stated; **FR24/FR26/FR29 amended and filed for the first time in five weeks**; `architecture.md`'s *"No FR is unsupported"* caveated with the measured N. **AC5:** new guard `tests/test_v1_commitment_closure.py` (`DOCS-001-30`..`-41`, 12 tests) — two closures, both directions each, `wired` and `library-seam` both mechanically refutable against a static `ast` import walk that never imports `argus`; RED-first discharged twice, and the live bite exposed and fixed a half-struck-commitment hole in the guard's own strike check. **AC6:** `DF-6-7-A` closed by disposition, `DF-10-4-B` re-targeted off this story, `DF-AUD-APAA-A`/`-B` un-orphaned, `DF-10-5-A/-B/-C/-D` filed, closing statement of the class written. **AC7:** 1336/1336 tests pass (0 skipped; +12 = exactly the new cases), coverage 95.51% unmoved, mypy clean on 72, bandit 0 High / 0 Medium / 19 Low, `argus audit .` → `RELEASE_READY / blocking_findings=0`, **zero `argus/**` changes**, ledger append-only `+240/-0`. All gates **LOCAL**; CI **NOT ESTABLISHED** (10.1's rule) — nothing pushed, tagged or dispatched. Status → `review`. |
