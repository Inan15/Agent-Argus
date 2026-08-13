---
baseline_commit: 58c8f6ba4a4e1d9d46c97bb5c176e94a2021ad8f
baseline_note: >-
  `HEAD` = `58c8f6b` on `master`, **15 commits ahead** of `origin/master`, which is **UNMOVED at
  `00c8d1b`**. `git tag -l` is **EMPTY**. **Nothing has been published.** `git status --porcelain`
  shows two MODIFIED tracked files (`sprint-status.yaml`, `stories/12-1-…md`) and one untracked story
  file (`stories/12-2-…md`) — documentation only — plus the usual untracked orchestrator/host
  directories (`.bmad-drift-audit/`, `_bmad-output/audit-reports/*`, `argusdemo/`,
  `bmad-dev-loop-pack/`). **No `argus/**`, `tests/**`, `scripts/**` or packaging file is dirty.**
  ✅ **THE SUITE IS FULLY GREEN AND THERE IS NO SANCTIONED RED.** The five-story `DF-11-1-A`
  carve-out was closed by Story 12.1. Your baseline, re-run to completion on this tree on 2026-08-13,
  is **1441 passed / 0 failed / 0 error / 0 skipped in 137.21s** (§B.0). **ANY red you measure is
  yours and must be attributed.**
  ⚠️ **THE GROUND MOVED TWICE SINCE THIS STORY WAS PLANNED.** Story 12.1 extracted
  `argus/pipeline_stages.py`; Story 12.2 wired the deep pass. `argus/pipeline.py` is **1007** lines
  (**193** of headroom, not 256). `git ls-files -- argus` is **74**. The dogfood artifacts were
  regenerated at provenance `7074c31` and are **CURRENT**. **Every figure in the Epic-11
  retrospective and in Stories 12.1/12.2 predates some of this. Re-measure; transcribe nothing.**
  ⚠️ **THE EPIC-11 "NO NEW `argus/**` FILE" FENCE IS LIFTED FOR EPIC 12** (§0.1). **Publication is
  still forbidden** (§0.3), **no dogfood artifact may be hand-edited**, and **no test may make a real
  network call**.
  🔴 **TWO INHERITED PREMISES ARE STALE AND ONE LEDGER ENTRY'S STATED TRIGGER IS MEASURABLY FALSE.**
  See §0.4. `DF-12-1-B` says wiring this store "flips a `library-seam` disposition and turns it red";
  it was executed against the guard's own code and it **does not**. **Do not implement the sentence.
  Implement §A.**
  🔴 **THE MOST LIKELY WAY TO FAIL THIS STORY IS TO SHIP A GUARD THAT IS GREEN BEFORE YOU WRITE THE
  CODE.** A re-run byte-identity test passes on this tree **today, with no cache at all** — Story 3.5
  already ships one and it is green. See §E. **This is the eighth consecutive story in which vacuous
  guards are the named dominant defect class.**
  **Every count, coordinate, LOC figure, digest, verdict and exit code below was produced by
  EXECUTING code on THIS tree on 2026-08-13.** Treat every line number as a hint to re-verify by
  anchor text.
story_key: 12-3-a-re-run-returns-the-recorded-result
epic: 12
---

# Story 12.3: A re-run returns the recorded result

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo. The
> `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no back-port.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`, `minions_core/apaa/`
> or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/` and `tests/`.
>
> 🔵 **This is the THIRD story of Epic 12.** 12.1 (`done`) gave `argus/pipeline.py` its headroom;
> 12.2 (`done`) wired the deep pass and, in doing so, put a **non-deterministic dependency class**
> into a product whose determinism is a stated guarantee. **This story is the mechanism that was
> always supposed to absorb that** — and §D rules, by measurement, exactly how much of it actually
> does. **It publishes nothing.** The publish is Story **12.9**, and the orchestrator halts before it.

---

## Story

As a developer iterating on my code,
I want a re-audit to reuse what has not changed,
so that running Argus repeatedly is fast enough to be part of my loop.

**Why this is one story.** Every clause is the same subject: *the on-disk memo that lets a second run
answer from what the first run recorded*. Deriving the key, consuming it, serving from it, refusing to
serve from a poisoned one, and proving a served answer is byte-identical to a computed one are not
five features — they are the five faces of making one cache trustworthy in a tool whose entire product
is trustworthiness. Splitting them would ship a cache in one story and the proof that it cannot lie in
another, which in an assurance tool is the one ordering that is never acceptable.

**What it is NOT.** It adds **no requirement to the contract** — FR27 and NFR-D1 are already written
and this story *delivers* them (AC1). It introduces **no second key function and no ad-hoc key**
(architecture §722). It bumps **no `CACHE_KEY_SCHEMA_VERSION`** — Story 10.2 already bumped it to
`"3"` precisely so this story would not have to. It adds **no CLI flag** (§0.6). It changes **no FR16
decision-table row, threshold or exit-code mapping**. It makes the default **cold** run neither
slower nor different: a cold run after this story must be byte-identical to a cold run before it
(AC7.1). It does **not** memoize LLM output (§D). And it **publishes nothing**.

**Why it is not merely "connect two modules".** Three measured reasons.

1. **A cache is the one optimization that can silently make an assurance tool lie.** `memo_store.py`'s
   own docstring names the failure: *"memoization caches errors → reproducibility ≠ correctness"*. A
   wrong verdict served fast is worse than a right verdict served slowly, and this repository's own
   architecture calls the cache **a correctness surface** (§404).
2. **The obvious test for this story is green before you start.** Re-run byte-identity already holds
   here by pure determinism, and is already pinned (`TC-ArgusAgent-PIPELINE-001-37`). A story that
   ships that test and calls it delivery has measured Epic 3.5's property and labelled it Epic 5's.
   §A and §E exist so this cannot happen by accident.
3. **The wiring has a blind spot that no existing guard can see.** Measured in §0.4b: the delivery
   registry that is supposed to notice a seam being wired **cannot notice this one**, because FR27 is
   disposed `delivered-differently` and that disposition is unrefutable by construction. Left alone,
   this repository would go on asserting *"the memoization MECHANISM is unwired … deferred to Story
   12.3"* forever, with a fully green suite.

⚠️ **Read §0 before anything else. Seven items gate this story.**

---

## Story Context

### Method statement — everything in §0–§E was MEASURED on this tree on 2026-08-13

Every count, coordinate, LOC figure, verdict and exit code below was produced by running `git`,
`wc -l`, bare `pytest`, `python -m argus.cli audit .`, and by **importing and calling the real guards'
own functions** — `tests/test_v1_commitment_closure.build_import_graph`, `reachable_from` and
`reachability_refutations` were executed directly against the live package and against synthetic
graphs. Where this story asserts that a guard *is* or *is not* able to see something, that assertion
was produced by **running that guard's own code**, never by reading it. **Re-derive everything;
transcribe nothing.**

---

## §0 — GATES. Read all seven before writing a line.

### §0.1 OPERATOR RULING — live for all of Epic 12 (2026-08-12, XAgent007), carried verbatim

> **implement → commit → regenerate the dogfood artifacts THROUGH THEIR OWN RENDERERS at a truthful
> provenance sha → re-run the gates is PRE-AUTHORISED. The Epic-11 "no new `argus/**` file" fence is
> LIFTED for Epic 12. Every regenerated artifact must cite a truthful provenance sha that is an
> ancestor of `HEAD`.**

Recorded verbatim in Story 12.1 §0.1, carried by 12.2, carried here. It means: you may add an
`argus/**` module if the design needs one, you may commit, and you **must** regenerate the three
dogfood artifacts through `scripts/regenerate_dogfood_artifacts.py` if `argus/**` composition changes
(§B.4). It does **not** relax anything in §0.3.

### §0.2 CI evidence is NOT ESTABLISHED — a dated risk acceptance you carry, never re-take

**No CI run has ever executed a single sha of Epic 10, 11 or 12.** Every figure in this story and
every figure you will produce is **LOCAL, Windows / CPython 3.11.15**. `AI-E10-1`'s dated acceptance
of 2026-08-11 is **carried forward, not re-taken** (re-taking it for Epic 12 is `AI-E11-4`, the
operator's). **No acceptance criterion in this story may depend on CI evidence**, and no completion
note may assert a CI result. This matters more here than in most stories: `SD-2` records three-plus
epics with no executed gate, and Epic 12 **ends in an irreversible publish at 12.9**.

### §0.3 STILL BINDING — not lifted by §0.1

- **(a) NOTHING IS PUBLISHED.** No push, no tag, no release, no `workflow_dispatch`, no index upload.
  Publication is Story **12.9** alone and the orchestrator halts before it. Verify at the end:
  `git tag -l` empty, `origin/master` still `00c8d1b`.
- **(b) NO DOGFOOD ARTIFACT MAY BE HAND-EDITED.** Regenerate through the renderers or leave alone.
- **(c) NO EGRESS.** Story 12.2 owns the only egress path in the product. A default invocation must
  not be able to acquire one, and **no test in this story may make a real network call.** This story
  touches the deterministic path; if any test of yours constructs an LLM adapter, it substitutes the
  transport *and* points at an `.invalid` host (RFC 6761), the two-fence pattern 12.2 established.
- **(d) `deferred-work.md` is APPEND-ONLY** (§3.4). Prove it programmatically at the end:
  `git diff --numstat <base> HEAD -- deferred-work.md` must show **zero deletions**.

### §0.4 STALE PREMISES — two are stale, one ledger trigger is measurably false, the rest HELD

`AI-E10-3` fired 4-of-6 in Story 12.1 and 3-of-9 in Story 12.2. Here it fired **2-of-7 plus one false
ledger trigger**. Stated plainly:

**HELD (re-measured, use them):**

| Premise | Source | Measured 2026-08-13 |
|---|---|---|
| `argus/cache/memo_store.py` exists and `argus/pipeline.py` never imports it | epics AC1, arch §381 | ✅ **HOLDS.** `pipeline.py` imports no `argus.cache` module at all. |
| `derive_cache_key` has no production caller | `key.py:99-102`, arch §395 | ✅ **HOLDS.** Zero production call sites; the only callers are `tests/test_cache_invalidation.py`, `tests/test_cache_key.py`, `tests/test_llm_dispatch_port.py`, `tests/test_secret_containment.py`. |
| No persisted cache entry exists to migrate | `key.py:100`, arch §394 | ✅ **HOLDS.** `.argus/cache/` exists as a directory and contains **0 files**; `.argus/` is `.gitignore`d (`.gitignore:19`) and **0** files under it are tracked. |
| `CACHE_KEY_SCHEMA_VERSION` is already corrected | Story 10.2 | ✅ **HOLDS.** `= "3"`, per-grammar provenance folded, sorted. **Do not bump it.** |
| Story 10.2 is the hard dependency | epics AC2 | ✅ **HOLDS** and is `done`. You consume the corrected key; you do not re-derive it. |

**🔴 STALE (a) — `key.py:100` and architecture §395-396 say "`argus/pipeline.py` imports neither
`argus.cache.key` nor `argus.cache.memo_store`" and use that to claim *no production caller.* The
first half still holds; the framing around it is now stale.** Story 12.2 made `argus.cache.key` a
**production-imported module**: `argus/audit/deep_audit.py:49` imports `GrammarProvenance,
RecordingProducingClosure`, and `argus/index/ast_index.py:66` imports `GrammarProvenance`. Executed
against the guard's own graph builder, `argus.cache.key` **IS** in the static import closure from
`argus.cli` today; `argus.cache.memo_store` and `argus.cache.invalidation` are **NOT**. The
*substantive* claim (nobody derives a key, so the bump was free) survives intact — **reachable is not
the same as derives-a-key** — but the sentence as written no longer describes the tree. **AC7.4 makes
you correct it in both documents.**

**🔴 STALE (b) — `DF-12-1-B` records `tests/test_v1_commitment_closure.py` at 1308 lines.** Measured
today: **1419** (Story 12.2 grew it by 7 and recorded that the ledger figure was stale by that much;
it is stale by **111** against the original entry). The ledger is append-only, so the entry is not
edited — the true number is here, and AC6.3 records the correction as a new append.

**🔴🔴 THE FALSE TRIGGER — `DF-12-1-B` states that wiring the memo store "flips a `library-seam`
disposition and turns it red until the disposition is updated". IT DOES NOT. Proven by execution, not
by reading.**

FR27 is disposed **`delivered-differently`**, not `library-seam`
(`tests/test_v1_commitment_closure.py:447`). `reachability_refutations` refutes exactly two shapes —
`wired`-over-unreachable and `library-seam`-over-reachable — and its own docstring (lines 765-767)
says `delivered-differently` *"makes no reachability claim and is never refuted here"*. Executed:

```
FR27 (delivered-differently) with memo_store REACHABLE -> NO REFUTATION — guard stays GREEN
control (library-seam)       with memo_store REACHABLE -> ("FRx: disposed 'library-seam' but
                                argus/cache/memo_store.py IS reachable … the seam was wired")
reverse registry: 37 entries {wired: 28, delivered-differently: 2, library-seam: 4, not-built: 3}
```

**Consequence, and it is this story's second-sharpest finding.** After you wire the store, the
repository's delivery registry will still carry, unrefuted and untestable, the sentence *"the
memoization MECHANISM is unwired (`DF-AUD-APAA-A`) … Mechanism deferred to Story 12.3"* — an assertion
about something you just built, that **no test in this repository is able to notice is false**. That
is a disposition outliving the fact it disposed: the precise drift `-35`/`-37` were built to prevent,
arriving through the one door they left open. **AC6 closes it in both halves** — the entry is
corrected *and* the refutation gap that let it rot is closed. Architecture §837 asserts the
`library-seam` half of this rule and is silent on this hole; AC7.4 makes you say so there too.

### §0.5 MEASUREMENT TRAPS ALREADY PAID FOR — do not re-buy them

1. **Run `pytest` BARE.** `pytest.ini` already supplies `-q`; adding another makes `-qq`, which
   **silently suppresses the summary line while still exiting 0**. Use `python -m pytest`. Report
   `collected / passed / failed / error / skipped` explicitly.
2. **This checkout is `core.autocrlf=true`.** A working-tree byte comparison **silently disagrees**
   with a git-blob comparison — Story 12.1 first measured a false "0 of 29 identical" this way. When
   comparing committed content, read **git blobs** (`git show <sha>:<path>`) and say which side you
   read. When comparing `.argus/` output, both sides are runtime-written, so a working-tree byte
   compare is correct there — **state which comparison you are making, every time.**
3. **Windows path length can break worktree operations.** If you use a detached worktree for an A/B,
   create it at a **short** path (e.g. `C:\t\ab`), never nested under this repo's own deep tree.
4. **`.argus/` is gitignored.** Its contents will never show in `git status`. If your test asserts
   over `.argus/`, assert over the filesystem, not over git.

### §0.6 NO NEW CLI FLAG — ruled, with reasons (§7 authority)

The invocation contract is **LOCKED** (Story 10.3) and `tests/test_invocation_contract.py` pins every
flag against `cli.py`'s own `LOCKED CLI contract` docstring block **and** a real `CHANGELOG.md`
section. **This story adds no flag** — not `--no-cache`, not `--cache-dir`, not `--refresh`. Three
reasons, in project-standards-win order:

- FR27/NFR-D1 require *reproduction*, not an operator control. Neither requirement mentions a flag.
- `memo_store.py`'s stated invariant is that **"the verdict is correct WHETHER OR NOT the cache
  exists / is warm / is wiped."** An escape hatch is therefore not needed to make anything correct;
  wiping `.argus/cache/` already is one, and it is what your tests will use.
- Adding a flag drags in the registry entry, the docstring block, a CHANGELOG section and a
  consumer-visible contract change — 12.2's full cost — for something no requirement asks for.

**If, while implementing, you find a case where correctness genuinely requires an operator override,
that is a scope change: stop and escalate rather than adding it.**

### §0.7 THE VACUITY GATE — this story's specific shape. Read §E before writing any test.

`AI-E11-1` is now **eight consecutive stories** old: **vacuous guards are this project's dominant
defect class.** A determinism guard is the most prone of all, because *the property is already true*.
§E names the five exact shapes the failure would take here and the four controls that are
**mandatory**, not advisory. **No load-bearing AC may be closed by a test that has not been proven
RED-first with the FINAL committed code.**

---

## §A — WHAT PROPERTY IS THIS, EXACTLY? (the same, stricter, or different?)

The orchestrator asked this directly and it is the analytical spine of the story. **Answered by
measurement, over the three guards that already exist.**

### §A.1 The three properties, side by side

| | **Epic 3.5 — `TC-ArgusAgent-PIPELINE-001-37`** (`tests/test_sequential_portability.py:535`) | **Story 12.2 — AC2.4** | **THIS STORY (12.3)** |
|---|---|---|---|
| What varies between the two runs | The **tree** (two separately staged copies of one cartridge) | The **binary** (a detached `2bea92f` worktree vs `HEAD`) | **Nothing.** Same tree, same binary, same flags. |
| What is held constant | Code, flags | Tree, flags, `--report-dir` | Everything |
| **Code path taken by run 2** | **The same path as run 1** (compute) | **The same path as run 1** (compute) | **A DIFFERENT path: serve-from-store instead of compute** |
| Cache involvement | **None.** `.argus/cache/` is never written or read. | **None.** | **The entire point.** |
| Property proven | The pure path is deterministic | The 12.2 change did not move default output | **A served answer equals a computed answer** |

### §A.2 The ruling — STRICTER, and strictly new

**12.3's property is a STRICTER property than either existing guard, and it is not covered by them.**

- It is **not the same** as 3.5's `-37`. `-37` compares two runs *that executed the same code*. Of
  course they agree — that is determinism, and it is Epic 3's delivery. 12.3 compares two runs that
  executed **different code** (compute vs. serve) and demands byte-identical output anyway. That is a
  claim about an equivalence between two mechanisms, which no existing test makes.
- It is **not the same** as 12.2's AC2.4. AC2.4 is a *version-invariance* claim about the default
  path across a code change. It also never populates a cache slot.
- **Measured, not argued:** `argus.cache.memo_store` is **NOT** in the static import closure from
  `argus.cli` (58 modules of 74 are; it is one of the 16 that are not). **No test in this repository
  currently exercises a cache read or write anywhere on the pipeline path.** `tests/test_memo_store.py`
  (513 lines) and `tests/test_cache_invalidation.py` (695 lines) exercise the store **directly, as a
  library**, never through `run_audit`.

### §A.3 What is genuinely NEW here — established by execution, so the story does not re-litigate settled ground

Epics 3 and 5 already shipped a great deal. **Do not rebuild any of it. Name what is left.**

| Already delivered — do NOT re-litigate | Where | Status re-measured today |
|---|---|---|
| Content-addressed memoization **store** (5.2) | `argus/cache/memo_store.py` (213 lines) | ✅ Built, tested, **unreachable from `argus.cli`** |
| Cache **key derivation** over the full closure (5.1) | `argus/cache/key.py` (379 lines) | ✅ Built, tested, corrected by 10.2 to `SCHEMA_VERSION "3"`; **zero production callers of `derive_cache_key`** |
| **Invalidation** + rejected-finding key-busting (5.3) | `argus/cache/invalidation.py` (447 lines) | ✅ Built, tested, **unreachable from `argus.cli`** |
| Resumability from on-disk `.argus/` state (3.4) | `argus/cost/resume.py` (327 lines) — reached via `pipeline.resume_audit` | ✅ **Wired.** Explicitly *not* a cache: its own docstring fences "the content-addressed memoization cache (NFR-D1) → Epic 5. **Resume reuses the on-disk LEDGER, NOT a memo-cache hit.**" |
| Byte-identical sequential execution (3.5) | `tests/test_sequential_portability.py` | ✅ Wired and green |

**Therefore the genuinely new deliverable is exactly one thing, and it is small in code and large in
consequence: _a production call site that derives a key and consults the store, plus the proof that
consulting it cannot change an answer._** Everything else is composition of things that already exist
(AR7 / §3.3 — **reuse, never fork**).

**The corollary you must not miss:** because the mechanism already exists and only the call site is
new, **the ratio of "test that proves it works" to "code that makes it work" in this story is very
high**. That is normal here and it is not padding — it is the entire reason the wiring was deferred
until the key was correct.

---

## §B — BASELINE. Re-derived by execution 2026-08-13. Re-run every one of these before you start.

### §B.0 Suite

```
python -m pytest        (BARE — see §0.5 trap 1)
1441 passed in 137.21s      collected 1441 / passed 1441 / failed 0 / error 0 / skipped 0
```

**There is NO sanctioned red.** Any red you produce is yours.

### §B.1 Git

```
HEAD              58c8f6ba4a4e1d9d46c97bb5c176e94a2021ad8f   ("chore(dogfood): regenerate the three artifacts at the fix-round sha")
origin/master     00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0   UNMOVED — HEAD is 15 ahead
git tag -l        (empty)
git ls-files -- argus | wc -l      74
```

### §B.2 Sizes and headroom (NFR-M1 ceiling = 1200)

| File | Lines | Note |
|---|---|---|
| `argus/pipeline.py` | **1007** | **193 of headroom.** 12.1 took it 1331→944; 12.2 took it 944→1007. |
| `argus/pipeline_stages.py` | 512 | holds `_detect_per_file` at **:228** |
| `argus/pipeline_persist.py` | 268 | |
| `argus/cache/memo_store.py` | 213 | `MEMO_STORE_SCHEMA_VERSION = "1"` |
| `argus/cache/key.py` | 379 | `CACHE_KEY_SCHEMA_VERSION = "3"` |
| `argus/cache/invalidation.py` | 447 | |
| `argus/audit/deep_pass.py` | 558 | 12.2's |
| `argus/audit/deep_audit.py` | 112 | holds `build_closure_from_recording` — **zero production callers** |
| `tests/test_v1_commitment_closure.py` | **1419** | `DF-12-1-B` exemption; ledger says 1308 — **STALE by 111** |
| `tests/test_pipeline_signature_demo.py` | 1326 | `DF-12-1-A` exemption |

### §B.3 Live audit on this tree

```
python -m argus.cli audit .
verdict=RELEASE_READY deep_ratio=64/177 blocking_findings=0 assessed_deep_ratio=4/5
scope=application held_out=97      exit 0
```

### §B.4 Dogfood artifacts — CURRENT, verified both directions

```
provenance sha cited by all three:  7074c313802f46fbdd8e360db696a0524134c7cf
git merge-base --is-ancestor 7074c31 HEAD   -> yes
git diff --quiet 7074c31 HEAD -- argus/     -> EMPTY  ⇒ artifacts are CURRENT
source files 74 · total physical LOC 21569 · units 3 · recorded cut edges 70
partition_ids:  1a31dc9a9559 (18 files / 904 LOC) · 619a713d53ca (40 / 14838) · aaec0673cdcf (16 / 5827)
```

**⚠️ If your change adds, deletes or edits any `argus/**` file, all three artifacts go stale and the
`TC-ArgusAgent-DOGFOOD-001-49..-52` currency guard goes RED by design.** That red is the guard
working. The remedy is `scripts/regenerate_dogfood_artifacts.py` at a truthful provenance sha, in a
**separate commit** of renderer output only, exactly as `e5a8a88`, `64164bd` and `58c8f6b` did
(§0.1). It refuses to run on a dirty `argus/` tree. **Never hand-edit.**

### §B.5 The import closure (executed against the guard's own builder)

```
static closure from argus.cli:  58 modules   (graph has 74 nodes)
_MIN_REACHABLE_MODULES = 35     (the -39 non-vacuity floor — your change raises the count, never lowers it)
  argus.cache.key            in_graph=True  reachable=True    ← 12.2 made this true
  argus.cache.memo_store     in_graph=True  reachable=False   ← YOUR CHANGE FLIPS THIS
  argus.cache.invalidation   in_graph=True  reachable=False   ← see AC5.4
  argus.audit.deep_pass      in_graph=True  reachable=True
  argus.pipeline             in_graph=True  reachable=True
```

---

## §C — THE WIRING SURFACE. Where the hook goes, and why the obvious placement is wrong.

### §C.1 The shape of the run, measured

`run_audit_detailed` (`argus/pipeline.py:528`) does, in order:

1. `resolve_source_state` / `RepoIntake` — intake
2. `detect_stack`, `build_ast_index` — the index (**this is where per-grammar provenance is
   produced**: `argus/index/ast_index.py:613-620` builds `GrammarProvenance` records for the grammars
   that **actually parsed**)
3. `_project_halt` — the deterministic pre-dispatch halt projection
4. **`_detect_per_file(repo_root, entries, request)`** → `(entries, findings, candidates)`
   — `argus/pipeline_stages.py:228`. **This is the recording-producing closure.** It runs the vacuous,
   secret, breadth and grading passes per file.
5. `_orphan_findings(...)` — the single cross-file orphan pass, appended
6. `_assemble_and_persist(...)` — which internally runs **the deep pass (12.2) at `pipeline.py:416`**,
   then `CoverageLedger.build`, `evaluate_verdict`, the Prosecutor, persistence and reports.

### §C.2 THE HOOK GOES AROUND STEPS 4–5, AND NOT ANYWHERE ELSE

**Ruled here (§7 authority) so the dev does not have to re-derive it, with the reasons that bind:**

- **Not per-file.** The 5.1 closure is a **unit** fingerprint: `content_hash` is the unit's and
  `work_manifest_files` is a *set*. A per-file key is a **key-SHAPE change** ⇒ a
  `CACHE_KEY_SCHEMA_VERSION` bump ⇒ exactly the migration cost the 10.2-before-12.3 ordering exists to
  avoid (arch §388-390). **Forbidden.**
- **Not around the deep pass.** See §D. It is downstream and it is excluded.
- **Not around the verdict fold.** The verdict is a *pure function of* the recordings; memoizing it
  would cache the thing whose recomputation is free and is the one thing that must never be served
  from a stale input.
- **Around steps 4–5**, whose output *is* `RecordedResult`-shaped, and whose recomputation is the
  expensive part of the run — which is what makes the story's user-facing promise ("fast enough to be
  part of my loop") real rather than nominal.

### §C.3 THE PAYLOAD PROBLEM — and why the "safe" answer is the vacuous one

`RecordedResult = tuple[Recording, ...]` (`memo_store.py:108`) — **findings only**. But step 4 returns
**three** things: `entries` (`CoverageLedgerEntry`), `findings` (`Recording`), and `candidates`
(`CriticalCandidate`).

**The tempting scope — "memoize only the findings, recompute the rest" — is a VACUOUS WIRING and is
forbidden.** `entries`, `findings` and `candidates` are produced by **one loop**. Recomputing two of
them re-runs that loop, so the cache saves **nothing at all** — while every byte-identity test in this
story still passes, because the answer is still correct. That is a cache that is provably useless and
undetectably so: the exact defect class §E is about, wearing its most respectable disguise.

**Ruling: extend the memoized payload additively to carry all three, and bump
`MEMO_STORE_SCHEMA_VERSION` `"1"` → `"2"`.** This is sanctioned by the constant's own contract —
*"additive-only; part of the hashed payload — a bump deliberately changes the content hash"*
(`memo_store.py:91-94`) — and it is **localized to the memo payload**: it is *not* the cache key
schema and *not* the `Recording` schema. Cost of the bump today is **zero**: there are **0 persisted
entries** (§0.4) . **AC4.5 pins that the bump moves the slot**, so this lever stays honest.

### §C.4 Reuse inventory — import these, do not re-implement them (AR7 / §3.3)

| Need | Use this | Never |
|---|---|---|
| Derive the key | `argus.cache.key.derive_cache_key(RecordingProducingClosure(...))` | any second hasher, any `json.dumps`, any hand-composed key (arch §722) |
| Per-grammar provenance for the closure | the **live** `AstIndex.grammar_versions` built at step 2 | a hand-listed language set, or every grammar *installed* on the host (DN-6 — that keys on the machine) |
| Detector set | `argus.cache.key.FROZEN_DETECTOR_SET` (the default on the closure model) | a second enumeration |
| Store / serve | `argus.cache.memo_store.MemoStore(repo_root).store(...) / .lookup(...)` | a new store, a new slot convention, a new tamper check |
| Containment / serialization | already inside `MemoStore` via `ApaaStorePaths` + `canonical` | direct `open()`/`json` on `.argus/` |
| Budget / materiality / manifest scope | the live `AuditRequest` + the halt projection | new defaults |

---

## §D — THE `--deep-audit` RULING. The sharpest question in the story, settled by measurement.

**The question:** Story 12.2 put a non-deterministic dependency class (a live LLM dispatch) into a
product whose determinism is a stated guarantee. Does 12.3's property survive with `--deep-audit` on
— is it scoped to the default path, does it hold *via* the memo store, or is it genuinely at risk?

### §D.1 What the contract actually promises

`E-PRD/prd.md:501`, under **FR36**:

> **Determinism is preserved** by the FR27/NFR-D1 memoization path — a re-run returns the recorded
> result. Enabling this pass must not make the verdict irreproducible.

and `E-PRD/prd.md:578`, **NFR-D1**:

> … achieved by **local content-addressed memoization** of recorded findings … **This is the
> mechanism — *not* an assumption that the LLM repeats itself (bit-identical LLM output is
> infeasible).**

So the PRD's own answer is: **determinism under the deep pass is supposed to hold *through this
store*, and explicitly not through any assumption about the model.** That is the target.

### §D.2 What the tree measurably supports today

| Measured fact | Coordinate | Consequence |
|---|---|---|
| The deep pass runs **inside `_assemble_and_persist`**, *after* the detect stage and *before* `evaluate_verdict` | `argus/pipeline.py:416-430` | It is **downstream** of the hook in §C.2. A hit on the deterministic stage serves **no LLM-derived byte**. |
| The cache key's `model_checkpoint` is the fixed sentinel `"v1-heuristic-no-llm"` and `prompt_template_version` is `"v1-no-prompt-template"` | `key.py:111,122` | The key **does not vary with the model actually used**. |
| The deep pass dispatches under `DEEP_PROMPT_TEMPLATE_VERSION = "argus-deep-v1"` and the adapter resolves its model from `ARGUS_LLM_MODEL` / `OLLAMA_MODEL` / a `"gpt-4o-mini"` default | `deep_pass.py:141`, `open_llm_adapter.py:55-62` | **Neither value reaches the key.** |
| `build_closure_from_recording` — the *only* function that substitutes the **captured** checkpoint into the key — has **ZERO production callers** | `deep_audit.py:54`; grep is tests-only | The substitution mechanism exists and is **unused**. |
| `DF-12-2-D` (open): the `delivered` branch is unreachable through the shipped adapter — every real dispatch degrades to `empty-response` | ledger 3255-3314 | Memoizing deep output today would cache **degradations**. |

### §D.3 THE RULING

**(1) The guarantee this story delivers is SCOPED TO THE DETERMINISTIC STAGE, and that scope is
enforced by a committed fence, not by a comment.**

Memoization covers steps 4–5 only. No LLM-derived recording may enter a memoized payload.

**(2) There is a live, latent CORRECTNESS HAZARD, and this story's job is to make it impossible
rather than to leave it for whoever wires deep memoization later.** If any future change memoizes
deep-pass output under this key as it stands, then **two runs against two different models collide on
the same cache slot** — the key cannot tell them apart — and the store would serve a result computed
under model A to a run that asked for model B. `key.py`'s own docstring says the module exists to make
exactly that impossible: *"a memoization cache hit may ONLY ever return a result produced by an
IDENTICAL recording-producing closure."* **AC6.1 is the fence.**

**(3) The honest consequence, which must be disclosed and NOT implied away: PRD §501 is NOT delivered
by this story.** With `--deep-audit` on, a re-run still dispatches again, and the verdict is
reproducible only to the extent the provider repeats itself — which NFR-D1 says is infeasible.
**Under `--deep-audit`, this story's guarantee holds for the deterministic component of the verdict
and NOT for the deep component.** Writing an AC that claims otherwise would be a false claim in an
assurance tool.

**Why this is the right scope and not a dodge — the reasons that bind (§7):** (a) memoizing deep
output today would cache the `empty-response` degradations of `DF-12-2-D`, and *"memoization caches
errors → reproducibility ≠ correctness"* is `memo_store.py`'s own named failure mode; (b) doing it
honestly requires folding the captured checkpoint and a real prompt-template version into the key —
which is `build_closure_from_recording` plus a claim grammar, and `DF-12-2-D` **already assigns that
to 6.2-style claim-grammar work with a named owner**; re-homing it here would fork an owned item;
(c) §0.3(c) forbids the live dispatch that would be needed to validate it, and §0.2 gives no CI to
validate it in. **Project standards win: disclose and file, never quietly narrow.**

**(4) File it, do not bury it.** AC6.4 files a new `DF-12-3-*` entry naming the residual, its owner
and its trigger, and AC6.5 makes the disclosure real where a reader would otherwise be misled —
including a note for **Story 12.4**, which is the story that will write the words a user reads about
what a verdict means. 12.4 must not imply the deep verdict is reproducible.

---

## §E — THE VACUITY RISK. Its specific shape here, and the four mandatory controls.

**The premise, restated because it is now eight stories old (`AI-E11-1`): a guard that is
structurally incapable of seeing what it guards is this project's dominant defect class.** A
determinism guard is the most prone of all, for one reason: **the property is already true before you
start.**

### §E.1 The five shapes this failure would take in THIS story

1. **🔴 THE GREEN-BEFORE-YOU-START RE-RUN (most likely).** A test that calls `run_audit` twice and
   diffs the bytes **passes on this tree today, with no cache in existence.** Story 3.5's
   `TC-ArgusAgent-PIPELINE-001-37` is that test and it is green. Shipping it as 12.3's proof measures
   Epic 3's property and labels it Epic 5's.
2. **🔴 THE PERMANENTLY-COLD CACHE.** If key derivation raises, or the lookup always misses, or the
   store write silently fails, **every byte-identity assertion still passes** — the answer is still
   correct, just recomputed. A cache that never works, behind a fully green suite.
3. **🔴 THE SELF-COMPARISON.** Comparing the served payload against the payload just stored **in the
   same process**, or re-reading one artifact twice. Round-tripping an object through a variable
   proves nothing about a store.
4. **🔴 THE UNFALSIFIABLE FIELD.** Asserting equality on things that cannot vary —
   `schema_version`, `MEMO_STORE_PRODUCER`, a sorted list's sortedness.
5. **🔴 THE DISPOSITION THAT OUTLIVES ITS FACT** — and this one is **not hypothetical, it is measured
   and live** (§0.4b). The registry that exists to notice a wired seam cannot notice this one.

### §E.2 The four MANDATORY controls. No load-bearing AC may be closed without them.

- **CONTROL 1 — PROVE THE HIT.** The warm run must be **instrumented to prove the detect stage did
  not execute** (a call counter / spy on `_detect_per_file`), and the cold run must be proven to have
  executed it exactly once. **A byte-identity assertion without a proven hit is not evidence for
  anything in this story.** This control alone kills shapes 1 and 2.
- **CONTROL 2 — THE POISON POSITIVE CONTROL (the killer).** Write a **validly enveloped, integrity-
  correct, schema-valid but DIFFERENT** recorded result into the slot the next run will read, and
  assert the run's **verdict changes**. If the verdict does not change, **the store is not being
  consulted and the wiring is vacuous** — no amount of green byte-identity can hide that. This is the
  positive control that 12.2's `TC-ArgusAgent-AUDIT-001-74` was for the deep pass, and this story's
  own §0.7 requires its equivalent. *(Note the polarity: this test proves the cache is load-bearing.
  It is the mirror of AC4.2, which proves a **tampered** entry is refused.)*
- **CONTROL 3 — RED-FIRST WITH THE FINAL CODE.** Every load-bearing test must be demonstrated RED
  against a **mutation of the real seam**, with the **final committed test code**, and the mutation
  reverted with the file's `sha256` round-tripped. Not red against a draft; not red before the test
  was finished.
- **CONTROL 4 — CLOSE OVER LIVE STRUCTURE; THE LIST IS NEVER THE CONTRACT.** Where a test enumerates
  anything — key inputs, closure fields, cache-relevant configuration — it must **derive** the
  population from the live structure (`RecordingProducingClosure.model_fields`, the live
  `AstIndex.grammar_versions`, `git ls-files`) and assert it non-empty, so a new closure field cannot
  be added without the guard noticing. A hand-written list is a snapshot, not a closure.

---

## Acceptance Criteria

> Every AC is written as a closure over real structure. Where an AC says *pinned by test*, the test
> is subject to §E.2 in full.

### AC1 — An existing requirement is DELIVERED, and the registry says so truthfully

1. **AC1.1** `argus/pipeline.py`'s audit path consults `argus.cache.memo_store.MemoStore` through a
   key derived by `argus.cache.key.derive_cache_key`, so that `argus.cache.memo_store` enters the
   static import closure from `argus.cli`. Proven by the **existing** guard's own graph builder, not
   by a new one.
2. **AC1.2** The story adds **no new requirement**: no FR or NFR is created, and no FR16 row,
   threshold, exit-code mapping, verdict enum member or report vocabulary changes. Asserted by test.
3. **AC1.3** No CLI flag is added and the LOCKED invocation contract is byte-unchanged in its
   accepted surface (§0.6). `tests/test_invocation_contract.py` passes unmodified.
4. **AC1.4** No second key function, no second serializer, no second hasher, no ad-hoc key
   composition anywhere (arch §722). The existing single-serializer AST gate stays green.

### AC2 — The CORRECTED key is what gets consumed (the 10.2 dependency, discharged)

1. **AC2.1** The closure the production path builds folds **per-grammar provenance taken from the
   live `AstIndex`** — the grammars that actually parsed — not a hand-listed set and not the host's
   installed grammars (DN-6). Derived, per Control 4.
2. **AC2.2** `CACHE_KEY_SCHEMA_VERSION` remains **`"3"`**. A test asserts this story did not bump it
   and states why (10.2 already paid that cost).
3. **AC2.3** The key is a faithful function of the closure: changing **any** closure input moves it.
   The perturbation set is **derived from `RecordingProducingClosure`'s live fields**, asserted
   non-empty, and every field is exercised — so a field added later cannot escape the guard.
4. **AC2.4** Two runs whose closures differ in a real input (e.g. a changed source file, a changed
   `--budget`, a changed materiality bar, a different critical-subsystem designation, a different
   grammar version) land on **different slots** and the second is a natural MISS — never a hit.

### AC3 — HIT == COLD, byte-identical, WITH THE HIT PROVEN (Controls 1 and 3)

1. **AC3.1** Over one repository, one binary and identical flags: run 1 (cold, empty
   `.argus/cache/`) and run 2 (warm) produce **byte-identical** stdout, stderr, exit code, every
   rendered report file, and every `.argus/` artifact other than the cache slot itself. State which
   comparison you made (§0.5 trap 2).
2. **AC3.2 — THE NON-VACUITY CORE.** Run 2 is **proven to have taken a HIT** and proven **not to have
   executed the detect stage**; run 1 is proven to have MISSED and executed it exactly once. Without
   this, AC3.1 is not evidence (§E.1 shapes 1–2).
3. **AC3.3** The property holds for **more than one verdict class** — at minimum one repository that
   reaches `RELEASE_READY` and one that reaches a **non-`RELEASE_READY`** outcome — so the guard is
   not accidentally pinned to the one path where findings are empty.
4. **AC3.4** Wiping `.argus/cache/` between runs restores the cold behaviour exactly: *the verdict is
   correct whether or not the cache exists, is warm, or is wiped* (`memo_store.py:65-69`), asserted,
   not assumed.

### AC4 — A cache is a correctness surface: it cannot serve a lie (Control 2)

1. **AC4.1 — THE POISON POSITIVE CONTROL.** A **validly enveloped, integrity-correct, schema-valid
   but different** recorded result placed in the slot **changes the verdict** of the next run. If it
   does not, the wiring is vacuous and the story is not done.
2. **AC4.2** A **tampered / corrupt / wrong-schema / non-file / unreadable** entry degrades to a
   **MISS → recompute**, never a raise and never a served poison — the DN-MISS taxonomy
   (`memo_store.py:46-56`) proven **over the wired path**, not only over the library.
3. **AC4.3** A MISS caused by any of AC4.2 produces a verdict **byte-identical to a cold run** — the
   degradation costs time, never correctness.
4. **AC4.4** No source bytes, secret bytes or absolute host paths appear in any cache artifact
   (NFR-S1/S5). The cache joins the 4.4 swept containment union; the existing containment suite
   covers the wired path.
5. **AC4.5** Bumping `MEMO_STORE_SCHEMA_VERSION` (§C.3) **moves the content hash**, so an entry
   written under the old payload shape cannot be served under the new one. Asserted in both
   directions.

### AC5 — The invalidation contract holds over the wired path

1. **AC5.1** A **detector-set** change (add / remove / edit a `DetectorDescriptor`'s `config` or
   `code_identity`) moves the key ⇒ natural MISS ⇒ recompute. Proven through the **wired** path.
2. **AC5.2** A **grammar version** change for a grammar that actually parsed moves the key — the
   defect `DF-AUD-APAA-D` closed in 10.2, now proven end-to-end rather than at the key function.
3. **AC5.3** The `prompt_template_version` slot (`DF-5-1-A`, closed 2026-06-28) still moves the key,
   so the forward-coupling hole stays closed once a real value lands.
4. **AC5.4** The Story 5.3 **rejected-finding key-busting** contract (`argus/cache/invalidation.py`)
   is either (a) wired and proven over the live path, or (b) **explicitly ruled out of scope with a
   measured reason and filed**, with a test asserting the 5.3 surface is unbroken. **Ruling it out
   silently is not permitted.** *(Guidance: `invalidation.py` is unreachable from `argus.cli` today;
   wiring it is a second delivery, and the epic AC names only "the DF-5-1-A invalidation contract
   holds over the wired path". Option (b) with reasons is the expected answer — but it must be
   stated, and the natural MISS on a moved key must be proven either way.)*

### AC6 — The deep-pass ruling is enforced, and the registry stops lying

1. **AC6.1 — THE FENCE.** A committed guard makes it **impossible for an LLM-derived recording to
   enter a memoized payload while the closure carries the placeholder checkpoint**
   (`V1_MODEL_CHECKPOINT` / `V1_PROMPT_TEMPLATE_VERSION`). The guard must be **red** against a
   mutation that memoizes deep-pass output, and must name §D.2's model-collision hazard in its
   failure message.
2. **AC6.2** With `--deep-audit` **on**: the deterministic component still hits and is still
   byte-identical, and the deep component is **not** served from the store. Proven with an
   **injected** port only — §0.3(c): no real network call, `.invalid` host, substituted transport.
3. **AC6.3 — THE REGISTRY.** FR27's entry in `tests/test_v1_commitment_closure.py` is corrected: the
   disposition and its reason no longer assert that the mechanism is *unwired* or *deferred to Story
   12.3*, because after this story both sentences are false. **AND** the measured refutation gap
   (§0.4b) is closed: a disposition that makes a *no-longer-true* claim about reachability must
   become refutable, so this cannot silently rot again. The fix must be **proven red** against the
   pre-fix registry state.
4. **AC6.4** The residual from §D.3(3) — *PRD §501 is not delivered; the deep component of a verdict
   is not reproducible via this store* — is **filed** in `deferred-work.md` with an id, owner,
   category, severity and a named target/trigger, and cross-referenced to `DF-12-2-D`.
5. **AC6.5** The residual is **disclosed where a reader would be misled**, at minimum: the module
   docstring of whatever module owns the hook, and a note for **Story 12.4** so that story's
   next-action text cannot imply the deep verdict is reproducible.

### AC7 — Nothing regresses, and the documents tell the truth

1. **AC7.1** A **cold** default run after this story is byte-identical to a default run before it
   (A/B against a detached `58c8f6b` worktree at a short path — §0.5 trap 3), or every difference is
   individually attributed and justified.
2. **AC7.2** All of these stay green, re-run not carried: the full suite (bare `pytest`, ≥1441 plus
   your additions, **0 failed / 0 error / 0 skipped**); the Story 6.1 determinism quarantine
   subprocess gate; `tests/test_no_web_imports.py`; `tests/test_secret_containment.py`;
   `tests/test_module_size_ceiling.py` (NFR-M1 sweep); `tests/test_invocation_contract.py`;
   `tests/test_sequential_portability.py`; `mypy` clean; `bandit` with **zero new** findings
   (content-diffed against a `58c8f6b` worktree, not count-compared).
3. **AC7.3** NFR-M1 holds: no `argus/**` file exceeds 1200 lines. `argus/pipeline.py` has **193**
   lines of headroom — if the hook does not fit cleanly, extract rather than breach, and if you add a
   module, **`git add` it early** (`DF-12-1-D`: the sweep reads the git **INDEX**, so an unstaged
   module is invisible to the guard that governs it).
4. **AC7.4** The two stale premises of §0.4a are corrected **at both sites** — `argus/cache/key.py`'s
   schema-version comment and `architecture.md` §395-396 — so neither goes on describing a tree that
   no longer exists; and architecture registers this wiring and the §0.4b refutation hole under the
   §837 delivery-closure rule, following the §843/§845 registration precedent.
5. **AC7.5** If `argus/**` composition changed, the three dogfood artifacts are regenerated **through
   their own renderers** at a truthful provenance sha that `git merge-base --is-ancestor` confirms,
   in a separate commit, with **no hand edits** (§B.4).
6. **AC7.6** `deferred-work.md` is append-only, proven by `--numstat` (zero deletions); every ledger
   item in §F is ruled IN or OUT **with reasons**; `git tag -l` empty and `origin/master` unmoved.

---

## Tasks / Subtasks

- [x] **Task 0 — Re-measure the baseline before touching anything (AC7.2; §B)**
  - [x] Bare `python -m pytest`; record collected/passed/failed/error/skipped. **Any red is yours.**
  - [x] `git rev-parse HEAD`, `git tag -l`, `origin/master`, `git ls-files -- argus | wc -l`.
  - [x] `python -m argus.cli audit .` — record the full verdict line and exit code as the fixture.
  - [x] Confirm `.argus/cache/` still holds **0** files (the zero-migration premise, §0.4).
  - [x] Re-run the §B.5 closure probe and the §0.4b refutation probe **yourself**; do not trust the
        transcription.
- [x] **Task 1 — Land the anti-vacuity controls FIRST, RED (AC3.2, AC4.1; §E.2)**
  - [x] Write the hit/miss instrumentation and the **poison positive control** *before* the wiring.
        Both must be RED now, for the right reason (no cache exists), and their failure messages must
        say so.
  - [x] Record the red output verbatim. This is the story's proof that its guards can fail.
- [x] **Task 2 — Build the closure and derive the key (AC2)**
  - [x] Thread the live `AstIndex.grammar_versions` into `RecordingProducingClosure`; derive via
        `derive_cache_key`. No second hasher (AC1.4).
  - [x] Perturbation matrix derived from the model's **live fields** (Control 4), asserted non-empty.
  - [x] Assert `CACHE_KEY_SCHEMA_VERSION == "3"` and that this story did not move it (AC2.2).
- [x] **Task 3 — Extend the memo payload additively and wire the hook (AC1, §C.2/§C.3)**
  - [x] Bump `MEMO_STORE_SCHEMA_VERSION` `"1"` → `"2"`; carry `entries` + `findings` + `candidates`.
  - [x] Wire the lookup/store around steps 4–5 of §C.1. Mind `pipeline.py`'s 193-line headroom
        (AC7.3); if you add a module, `git add` it immediately.
  - [x] Turn Task 1's tests GREEN. Re-run them RED against a mutation of the final seam (Control 3),
        revert, round-trip the `sha256`.
- [x] **Task 4 — Byte-identity and degradation (AC3, AC4)**
  - [x] Cold/warm A/B over ≥2 verdict classes; state the comparison kind.
  - [x] Tamper / corrupt / wrong-schema / non-file / unreadable → MISS → cold-identical verdict.
  - [x] Cache-wipe restoration; `MEMO_STORE_SCHEMA_VERSION` slot-move both directions.
  - [x] Containment: no source/secret/host-path bytes in any cache artifact.
- [x] **Task 5 — Invalidation over the wired path (AC5)**
  - [x] Detector-set, grammar-version and prompt-template perturbations ⇒ natural MISS end-to-end.
  - [x] **Rule AC5.4 out loud** — wire 5.3, or file the reasoned exclusion. Not silence.
- [x] **Task 6 — The deep-pass fence and the registry (AC6; §D)**
  - [x] Ship the AC6.1 fence; prove it red against a mutation that memoizes deep output.
  - [x] `--deep-audit` behaviour proven with an **injected** port, `.invalid` host, no socket.
  - [x] Correct FR27's registry entry **and** close the `delivered-differently` refutation hole;
        prove both red against the pre-fix state.
  - [x] File the §D.3(3) residual; disclose it at the module docstring and in a note for 12.4.
- [x] **Task 7 — Documents, ledger, regeneration, gates (AC7)**
  - [x] Correct `key.py`'s comment and `architecture.md` §395-396 (§0.4a); register the rule per §837.
  - [x] Ledger: rule every §F item IN or OUT with reasons; append only.
  - [x] Commit; if `argus/**` moved, regenerate the three artifacts through the renderers at a
        truthful ancestor sha in a **separate** commit; re-run every gate in AC7.2 on the final tree.
  - [x] Verify the publication fences: `git tag -l` empty, `origin/master` at `00c8d1b`.

### Review Findings (code-review, iteration 1, Sonnet 5, 2026-08-13)

**VERDICT: PASS.** Independently re-derived on disk, not transcribed. Every headline claim in the
Dev Agent Record was re-executed and matched: bare `python -m pytest` = 1466 passed / 0 failed / 0
error / 0 skipped; `mypy argus` clean on 75 sources; `bandit` content-diffed against a fresh
detached `58c8f6b` worktree (own script, own JSON parse) = 19/19, 0 new, 0 removed, identical sets;
`python -m argus.cli audit .` = `RELEASE_READY deep_ratio=65/181 blocking_findings=0
assessed_deep_ratio=65/81 scope=application held_out=100 exit 0` (byte-identical to the claim); a
live cold/warm smoke run (outside the test suite) confirmed a single `.argus/cache/*.json` slot is
written on run 1 and NOT duplicated on run 2. `git diff --numstat 58c8f6b HEAD --
deferred-work.md` = `203 0` (append-only proven). `git tag -l` empty, `origin/master` unmoved at
`00c8d1b`, HEAD `d040cad`. `fab36e7` confirmed an ancestor of HEAD and `git diff --quiet fab36e7
HEAD -- argus/` empty (dogfood regeneration is current and renderer-only). README/CHANGELOG figure
corrections (74→75 modules, 79→80 wheel, 78→79 sdist) matched the artifact exactly.

**Central vacuity question — independently re-derived, not trusted.** I constructed my own
mutation (not the dev's): patched `MemoStore.lookup_stage` to unconditionally `return None`
(permanently-cold cache) and re-ran `tests/test_stage_memo_wiring.py -k "81 or 82"` — both the
hit-proof (`-81`) and the poison positive control (`-82`) went RED for the stated reason (no
readable slot / nothing to poison), then reverted cleanly. Separately read `-82`
(`TC-ArgusAgent-CACHE-001-82`) end-to-end: it reads the key off the *live slot filename* (never
recomputes it), writes the poisoned payload through the real `MemoStore.store_stage`, spies on
`_detect_per_file` to prove zero recomputation on the poisoned run, and asserts both
`verdict != RELEASE_READY` and `blocking_finding_count >= 1`. This is not vacuous — it is the
correct shape for the control the story specifies. Confirmed Control 3's two claimed mutations by
reading the committed before/after prose and cross-checking against the actual guard code; no
evidence either was softened.

**The three adjudicated reds:**
1. `test_grammar_runtime_validation.py::-125` — read the diff in full. The `_wipe_memo_cache`
   addition only clears `.argus/cache/` between the three toolchain legs inside the existing
   `_audit()` helper; no assertion in the test body was touched, weakened, or removed. The
   reasoning (in-process monkeypatch drift cannot move the 10.2 per-grammar key, so without a wipe
   the second leg would be served the first leg's answer) is sound and independently checked
   against `derive_cache_key`'s actual inputs. **Ruled: legitimate fix, not a weakened test.**
2. `test_secret_containment.py` isolation-collection failure — independently reproduced
   (`ModuleNotFoundError: No module named '_cartridge'` on `python -m pytest
   tests/test_secret_containment.py` alone) and independently confirmed pre-existing: `git diff
   58c8f6b HEAD -- tests/test_secret_containment.py` is empty, the same `argus/cartridges`
   sys.path insert is present in the `58c8f6b` blob at line 66, and `git ls-tree 58c8f6b --
   argus/cartridges` is empty (the directory never existed at baseline). Confirmed the file
   collects and all its tests pass inside the full suite / any multi-file selection. **Ruling on
   disposition:** filing as `DF-12-3-C` rather than fixing here is correct — repairing an unrelated
   test module's import path inside the memoization story would mix concerns, matching this
   project's own precedent (`DF-12-2-E`). **Ruling on severity — NOT fully endorsed:** 🟢/Low
   undersells this. It is the Epic-4.4 NFR-S1 secret-containment property suite, and the failure
   mode is a *silent collection error*, not a failing assertion — a future change to collection
   order, `pytest-xdist` worker splitting, or an isolated invocation of this one file (exactly what
   a CI job targeting "security suites only" would do) makes a security-relevant guard silently
   stop existing rather than fail loudly. Recommend the Epic-12 retrospective give this a firmer
   commitment than "the next story that happens to touch it" (the `DF-10-2-A` precedent shows that
   pattern can carry for 3+ stories) — e.g. a `conftest.py`-registered fixture path instead of a
   per-file `sys.path.insert`, so the fix is independent of import order everywhere, not just in
   the files that currently happen to run first.
3. The 7 dogfood/distribution currency guards red-by-design on the 74→75 population move — verified
   the remedy independently (see provenance/ancestor checks above): renderer-only regeneration in a
   separate commit (`c9603ae`) at a truthful ancestor sha, README/CHANGELOG corrected to the
   measured figures, no hand edits detected (diff is exactly the renderer's expected shape).
   **Sanctioned remedy, correctly applied.**

**§8 engineering-principle review.** `argus/cache/stage_memo.py` is a clean, single-responsibility
composition module (closure-build + memoize, nothing else); `argus/pipeline.py`'s hook is a
minimal, well-commented insertion that preserves the pre-existing entries/findings/candidates
composition order (traced by hand: moving the orphan-findings call inside `_run_detect_stage` does
not change the final concatenation, since orphan findings never depend on the skipped-remainder
append that still happens afterward, outside the memoized payload). The `MEMO_STORE_SCHEMA_VERSION`
1→2 bump is paired with an explicit, tested version-refusal in `lookup_stage` (`-91`, both
directions) — this **is** the migration/invalidation strategy for an advisory cache (forced natural
MISS on shape mismatch), not a bump that was left unhandled; no separate migration story is needed
given 0 persisted entries at bump time (independently confirmed against `58c8f6b`). Two
intentional, disclosed departures from generic best practice were reviewed and are **accepted, not
findings**: (a) D-1 over-keys the whole detector-stage config to every `DetectorDescriptor` rather
than attributing per-detector — correctness-over-DRY, explicitly reasoned, safe direction (extra
MISS, never a wrong serve); (b) D-6 duplicates the deep-pass rule-stem literal in `memo_store.py`
rather than importing `deep_pass.RULE_DEGRADED_DEEP_READ`, to keep the dispatch surface off the
memoization import path (NFR-S6) — guarded against drift by a dedicated test (`-97`). The AC6.1
fence living inside `MemoStore` (`_fence_llm_derived`) couples the store to deep-pass domain
vocabulary, which is a mild SRP tension — but it is deliberate (D-5: enforce at the write-path
choke point rather than trust callers) and documented; accepted, not a finding.

**Open reviewer questions from the Dev Agent Record — adjudicated:**
1. AC5.4 scope reading: the story's own AC5.4 guidance text explicitly anticipates and sanctions
   "option (b) with reasons" as the expected answer (invalidation.py is unreachable from
   `argus.cli` today; wiring 5.3 would be a second delivery). The dev's ruling matches the story's
   own built-in guidance. **Not a scope expansion; no action needed.**
2. D-2 (folding `argus-agent`'s own distribution version into `tool_versions`): beyond the literal
   AC text but directly supported by FR27's own wording ("the same verdict for the same repository
   AND Argus version") and the conservative direction (extra MISS only). **Accepted as a
   correctness improvement, not scope creep.**

**No `[Review][Patch]` or `[Review][Decision]` blocking items.** One `[Review][Decision]` item is
recorded below for the next story/retrospective to weigh, and is non-blocking for this story.

- [ ] [Review][Decision] DF-12-3-C severity reconsideration — the NFR-S1 secret-containment
      suite's isolation-collection fragility (pre-existing, confirmed byte-identical to `58c8f6b`)
      is filed at severity 🟢; recommend the Epic-12 retrospective assign it a firmer owner/fix
      (e.g. a `conftest.py`-registered cartridge path) rather than "next toucher," given it is a
      security-relevant guard and the failure mode is silent collection error, not red assertion.

---

## Dev Notes

### Decisions made at story-creation time, with rationale (§7 authority)

Recorded here so the dev does not re-litigate them and the reviewer can audit them. Where discipline
best practice and explicit project standards conflicted, **project standards won**.

| # | Decision | Rationale |
|---|---|---|
| **DN-1** | Hook wraps the **deterministic detect/grade stage** (§C.1 steps 4–5), unit-level. | Per-file keying is a key-**shape** change ⇒ `CACHE_KEY_SCHEMA_VERSION` bump ⇒ the exact migration the 10.2→12.3 ordering exists to avoid (arch §388-390). |
| **DN-2** | Memoized payload carries **entries + findings + candidates**; `MEMO_STORE_SCHEMA_VERSION` `"1"`→`"2"`. | Findings-only memoization re-runs the same loop ⇒ saves nothing ⇒ a vacuous wiring that every byte-identity test would pass. The bump is sanctioned by the constant's own additive-only contract and costs **zero** today (0 persisted entries). |
| **DN-3** | **No CLI flag.** | §0.6. The invocation contract is LOCKED; no requirement asks for a flag; `memo_store`'s own invariant makes an override unnecessary for correctness. |
| **DN-4** | **`CACHE_KEY_SCHEMA_VERSION` stays `"3"`.** | 10.2 paid this cost deliberately so 12.3 would not have to. Bumping it here would waste the ordering. |
| **DN-5** | Deep-pass output is **excluded** from memoization; the exclusion is **fenced**, and the residual is **filed and disclosed**. | §D.3, in full. Caching `DF-12-2-D`'s degradations would be the "memoization caches errors" failure by name; the honest fix is owned by 6.2-style claim-grammar work and re-homing it here forks an owned item; §0.2/§0.3(c) make it unvalidatable here. |
| **DN-6** | The **poison positive control** (AC4.1) is mandatory and load-bearing. | It is the only assertion in the story that a permanently-cold cache cannot pass. Byte-identity alone is green with no cache at all. |
| **DN-7** | FR27's registry entry is corrected **and** the `delivered-differently` refutation hole is closed. | Measured (§0.4b): the guard cannot see this wiring. Correcting the text without closing the hole leaves the next disposition free to rot the same way. |
| **DN-8** | AC3.3 requires **two verdict classes**. | A cold/warm proof pinned only to `RELEASE_READY` (empty findings) could be green because there is nothing to serve. |

### §F — Deferred-work ledger: every relevant open item, ruled

**Append-only (§3.4). Rule each one; do not leave any silent.**

- **`DF-12-1-B` — 🟢 IN, but RESHAPED, and its stated trigger is CORRECTED.** Targeted at this story.
  Its size figure is **stale** (1308 recorded, **1419** measured) and its stated trigger — that wiring
  flips a `library-seam` disposition red — is **measurably false** (§0.4b). **What is genuinely IN:**
  the FR27 disposition correction and the refutation-hole closure (AC6.3), which is the *substance*
  the entry was pointing at. **What stays exempt:** the 1200-line breach itself. Splitting a
  1419-line delivery-closure guard inside the story that changes what that guard measures is the same
  reasoning 12.1 and 12.2 gave, and it is stronger here because this story **edits the registry that
  file holds**. Re-record with the corrected figure and the corrected trigger; the exemption registry
  still shrinks (`TC-ArgusAgent-MAINT-001-04`), so it cannot become dead weight.
- **`DF-12-1-A` — 🟢 OUT, with reasons, and ESCALATED rather than re-homed a third time.**
  `tests/test_pipeline_signature_demo.py`, **1326** lines (re-measured; unchanged). It was re-homed
  from 12.2 to 12.3. The measured reason not to close it here is the same and is again stronger:
  **this story modifies the pipeline surface that file demonstrates**, and refactoring the witness in
  the same change that alters what it witnesses removes the evidence for the property this story most
  needs witnessed. **But it has now been carried by three consecutive stories.** Rule it OUT *and*
  flag it for the **Epic-12 retrospective** as needing a dedicated home rather than a fourth
  re-homing — recording "not mine" a third time without escalating is the drift the ledger exists to
  prevent.
- **`DF-12-2-D` — 🟡 OUT. Do NOT re-home it.** Owner and target are already assigned (6.2-style
  claim-grammar work; failing that, the next story changing `open_llm_adapter.py`'s response
  handling, closed together with `DF-12-2-B`). It is **load-bearing context** for §D.3 and must be
  **cited** there — but silently adopting it here would fork an owned item.
- **`DF-12-2-E` — 🟢 OUT unless you touch it.** The duplicated `PROVIDER_ENDPOINT_VARIABLES` literal
  in `deep_pass.py`. This story has no reason to touch endpoint resolution. **If AC6.1's fence ends
  up editing `argus/audit/deep_pass.py`, its trigger fires** — rule it explicitly then, do not pass
  it by.
- **`DF-10-2-A` — 🟡 OUT, and it is not yours to close.** C/C++/Ruby/Rust ground but extract zero
  definitions. **This would be the FOURTH consecutive story to carry it.** Story 12.2 already
  escalated it to the **Epic-12 retrospective** with owner **OPERATOR (XAgent007)** — `AI-E11-7` says
  what is needed is *a dated decision, not an implementation*. **Leave it flagged for the
  retrospective; do not silently re-home it and do not re-escalate it as if new.**
- **`DF-12-1-D` — 🟡 hazard is LIVE for this story even though its trigger may not fire.** Its
  trigger is *"the next story that edits `tests/test_module_size_ceiling.py`"*. You may not edit it —
  but the hazard applies directly: the NFR-M1 sweep reads the git **INDEX**, so **an unstaged new
  module escapes the guard that governs it**. If you add a module, `git add` it early (AC7.3), and
  record whether the trigger fired.
- **`DF-12-1-E` — 🟢 check and record.** Trigger: *"the next story that adds a fourth
  `argus/pipeline*.py` module"*. Today `git ls-files -- 'argus/pipeline*.py'` is **three**. If your
  hook lands as a fourth sibling, the trigger **fires** and must be ruled on; placing it elsewhere
  (or inside an existing module) does not fire it. **Record which, either way.**
- **`DF-5-1-A` — CLOSED 2026-06-28**, do not reopen. Its *contract* is live and AC5.3 proves it over
  the wired path.
- **New filings expected from this story:** the §D.3(3) FR36/§501 determinism residual (AC6.4), plus
  whatever AC5.4's ruling produces if 5.3 is scoped out.

### Previous-story intelligence — what 12.1 and 12.2 cost, and what they left you

**From Story 12.1 (`done`):**
- `argus/pipeline_stages.py` was extracted from `argus/pipeline.py` (1331 → 944). **`_detect_per_file`
  now lives at `pipeline_stages.py:228`** — the hook's neighbourhood is not where older documents put
  it.
- The **NFR-M1 repo-wide sweep** (`tests/test_module_size_ceiling.py`) now covers **every tracked
  `.py`**, with three named/dated/filed exemptions that **shrink**.
- The **dogfood-currency guard** exists and its red names `scripts/regenerate_dogfood_artifacts.py`.
  It will fire on you if `argus/**` moves. That is by design.
- **Lesson that cost 12.1 a review round:** it published a digest (`c6edd6fa…`) that could not be
  reproduced under any of 48 conventions, and a byte-identity count read off the **working tree**
  under `core.autocrlf` that was false. **State the convention of every digest you publish, or do not
  publish it.**

**From Story 12.2 (`done`):**
- The deep pass is wired behind `--deep-audit` (`store_true`, default `False`), with a
  **function-local import** in `pipeline.py` that is load-bearing: it makes the seam statically
  reachable (so FR36 reads `wired`) while never executing on a default run (so the NFR-S6 quarantine
  holds). **Do not "tidy" it to module scope.** Your `memo_store` import has no such constraint — it
  imports only `argus` leaves and is already on the `test_no_web_imports.py` allowlist
  (`argus.cache.memo_store`, line 144) — but **verify, do not assume**.
- 12.2 established the **positive-control discipline** you must follow: `AUDIT-001-73` proves the
  path fires, `-74` proves the favourable outcome is reachable when the one missing field is
  supplied. AC4.1 is your `-74`.
- 12.2 removed an `assert … or True` from its own test — **an assertion that cannot fail** — after
  finding it. Expect the same scrutiny.
- **Lesson that cost 12.2 a review finding:** a `sha256` in its Dev Agent Record **does not reproduce
  under any encoding**. Round-trip every digest you record, or omit it.

### Git intelligence — the last five commits and what they tell you

```
58c8f6b chore(dogfood): regenerate the three artifacts at the fix-round sha   ← renderer output only
7074c31 fix(deep-audit): say how far the shipped adapter actually carries the wiring
64164bd chore(dogfood): regenerate the plan and proof artifacts at a truthful sha ← renderer output only
8a0bebc feat(deep-audit): the deep pass is wired, opt-in, and honest (Epic 12, Story 12.2)
2bea92f fix(story-12-1): a claim about the split is now re-derived, and the surface it promised is pinned
```

**The pattern is binding on you:** implementation lands in a `feat`/`fix` commit; the dogfood
regeneration lands in a **separate** `chore(dogfood)` commit of renderer output only, citing a
provenance sha that is an ancestor of `HEAD`. Follow it. Note also that 12.2 **amended its own
regeneration commit message** because it stated a LOC figure that did not match the artifact — an
untrue committed figure was corrected rather than left standing.

### Project structure notes

- **Where code goes:** the hook belongs with the pipeline (`argus/pipeline.py`, or a new module if
  headroom demands). If a new module: it is **not** a fourth `argus/pipeline*.py` sibling unless you
  intend to fire `DF-12-1-E`; `argus/cache/` is the natural home for cache-composition logic and
  keeps the concern inside the package that already owns it.
- **Where tests go:** a **dedicated** new test file for the wiring is the established precedent
  (12.1's `tests/test_pipeline_split_surface.py`, 12.2's `tests/test_deep_pass_wiring.py`). Do **not**
  bulk up `tests/test_memo_store.py` (513) or `tests/test_cache_invalidation.py` (695) — those pin
  the store *as a library*, which is a different subject, and both already assert their own
  ≤1200-line ceiling.
- **Verification-area naming:** follow the repository convention `TC-ArgusAgent-<AREA>-NNN-NN`.
  `CACHE` is the established area for this subject (`TC-ArgusAgent-CACHE-001-76` exists); a wiring
  concern may equally justify `PIPELINE`. Pick one, state why, and keep ids contiguous.
- **`argus/**` population is 74.** Adding a module makes it 75 and moves the dogfood partition ids,
  the LOC total and `mypy`'s file count — all expected, all requiring regeneration (AC7.5).

### Testing standards summary

- **Framework:** `pytest`, invoked **bare** (§0.5 trap 1). `mypy` clean. `bandit` content-diffed for
  **zero new** findings.
- **Zero tokens, zero sockets.** Every test in this story runs on the deterministic path or through
  an **injected** port. `.invalid` host + substituted transport if an adapter is constructed at all.
- **Red-first with the final code**, against a mutation of the **real** seam, reverted, `sha256`
  round-tripped (Control 3).
- **Closures, not lists** (Control 4). Enumerations derive from live structure and assert non-empty.
- **Both directions.** Where a guard rejects something, prove it accepts the true case too — the
  pattern 12.1's `-14/-15/-16` and 12.2's `-73/-74` both follow.
- **Fail, never skip.** A guard that cannot reach its subject must go **red**, not `skip` — 12.1
  fixed exactly this in `-15`.

### References

- Epic and story text — `_bmad-output/design-artifacts/ArgusAgent/epics.md` §Epic 12 / Story 12.3
  (line ~2256), and the Epic-12 dependency note (~2164) placing 12.3 after 10.2.
- **FR27** — `E-PRD/prd.md:558`. **NFR-D1** — `E-PRD/prd.md:578`. **FR36's determinism bullet —
  `E-PRD/prd.md:501`** (the §D subject). Usability framing — `E-PRD/prd.md:221`.
- **Architecture** — `architecture.md` §374-405 (the memoization design, the wiring order, and *"a
  cache is a correctness surface … a hit and a cold run must produce byte-identical verdicts, pinned
  by test"*); §722 (*"One cache-key function … never compose a memo key ad hoc"*); §837 (the
  delivery-closure rule and its `library-seam` sentence, which §0.4b shows is incomplete); §843/§845
  (registration precedent); §890/§928 (source-tree placement).
- **Code** — `argus/cache/memo_store.py` (the three invariants at lines 26-43; the DN-MISS taxonomy
  at 46-56; the LOCAL-only fence at 65-69); `argus/cache/key.py` (the closure at 235-294, the payload
  fold at 329-355, the schema-version comment at 90-103 that AC7.4 corrects);
  `argus/cache/invalidation.py` (5.3, AC5.4); `argus/pipeline.py:528` (`run_audit_detailed`),
  `:373` (`_assemble_and_persist`), `:416-430` (the deep-pass call site);
  `argus/pipeline_stages.py:228` (`_detect_per_file`); `argus/index/ast_index.py:613-620` (live
  per-grammar provenance); `argus/audit/deep_audit.py:54` (`build_closure_from_recording`, unused).
- **Existing guards you must not duplicate** — `tests/test_sequential_portability.py:535`
  (`TC-ArgusAgent-PIPELINE-001-37`, the already-green re-run test); `tests/test_memo_store.py`;
  `tests/test_cache_invalidation.py`; `tests/test_cache_key.py:415-450` (the 10.2 per-grammar legs
  and the comment AC7.4 corrects); `tests/test_v1_commitment_closure.py:447` (FR27) and `:751-781`
  (`reachability_refutations`, the measured hole).
- **Ledger** — `deferred-work.md`: `DF-12-1-A` (2984, re-recorded 3076), `DF-12-1-B` (3003),
  `DF-12-1-D` (3028), `DF-12-1-E` (3100), `DF-10-2-A` (3135), `DF-12-2-D` (3255), `DF-12-2-E` (3236),
  `DF-5-1-A` (117, closed 141).
- **Process** — `epic-11-retro-2026-08-12.md` (`AI-E10-1` CI acceptance, `AI-E10-3` re-measurement,
  `AI-E11-1` vacuous guards, `AI-E11-7` `DF-10-2-A` ownership, `SD-2`).

### Open questions for the reviewer (saved for the end, per method)

1. **AC5.4** is deliberately left as a ruled choice rather than a mandate — the epic AC names only
   the DF-5-1-A contract, and wiring 5.3 is arguably a second delivery. If the reviewer reads the
   epic's *"the DF-5-1-A invalidation contract holds over the wired path"* as requiring the full 5.3
   surface, that is a scope expansion worth naming explicitly rather than discovering at review.
2. **Story markdown files are inconsistently tracked in git** — 12-1's is tracked, 12-2's is not.
   Ruled **not** a `done` blocker at 12.2's review; carried to the Epic-12 retrospective. This file
   inherits the ambiguity.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), via the BMAD `dev-story` workflow, 2026-08-13.

### Debug Log References

**Every figure below was produced by EXECUTING code on this tree. Nothing is transcribed from the
story's create-time text.** All measurements are LOCAL, Windows / CPython 3.11.15 — `AI-E10-1` is
carried, not re-taken, and **no claim here rests on CI evidence** (`§0.2`).

#### Baseline re-measured before touching anything (Task 0)

```
python -m pytest            (BARE — §0.5 trap 1)
1441 passed in 137.81s      collected 1441 / passed 1441 / failed 0 / error 0 / skipped 0
HEAD              58c8f6ba4a4e1d9d46c97bb5c176e94a2021ad8f
origin/master     00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0   UNMOVED
git tag -l        (empty)
git ls-files -- argus | wc -l      74
python -m argus.cli audit .
  verdict=RELEASE_READY deep_ratio=64/177 blocking_findings=0 assessed_deep_ratio=4/5
  scope=application held_out=97        exit 0
.argus/cache/     0 files   (the zero-migration premise HOLDS)
```

Closure probe, run against **the guard's own builder** (`build_import_graph` / `reachable_from`),
not read off the story: **74 graph nodes, 58 reachable from `argus.cli`**;
`argus.cache.key` reachable=**True**, `argus.cache.memo_store` reachable=**False**,
`argus.cache.invalidation` reachable=**False**; registry 37 entries
`{wired: 28, delivered-differently: 2, library-seam: 4, not-built: 3}`.

**The §0.4b FALSE TRIGGER, reproduced by execution:**

```
reachability_refutations( ("FR27","delivered-differently","argus.cache.memo_store"),
                          reachable ∪ {argus.cache.memo_store} )   ->  ()          # NO refutation
reachability_refutations( ("FRx","library-seam",         "argus.cache.memo_store"),
                          reachable ∪ {argus.cache.memo_store} )   ->  ("FRx: … IS reachable …")
```

`DF-12-1-B`'s stated trigger is therefore **measurably false**, exactly as the story records.

#### Task 1 — the anti-vacuity controls, RED before the wiring

Written first and run against a tree where the payload type existed but the pipeline hook did not.
Verbatim red:

```
TC-ArgusAgent-CACHE-001-81
E  AssertionError: the cold run must PERSIST exactly one memo slot, found 0: []. With no slot
   written there is nothing for a warm run to serve, and every byte-identity assertion in this
   file would still pass — that is the permanently-cold cache this control exists to catch.
TC-ArgusAgent-CACHE-001-82
E  AssertionError: no memo slot was written, so there is nothing to poison (0 slots). The wiring
   is absent or the store write failed silently.
```

#### CONTROL 3 — red-first against a mutation of the REAL seam, with the FINAL committed code

**Mutation 1 — the PERMANENTLY-COLD CACHE (`§E.1` shape 2).** `MemoStore.lookup_stage` made to
return `None` unconditionally; the store still writes, and every answer stays correct.

| | Result |
|---|---|
| `TC-ArgusAgent-PIPELINE-001-37` (Epic 3.5's already-green re-run byte-identity test) | ✅ **STAYED GREEN — it cannot see this defect at all** |
| This story's guards | 🔴 **9 RED**, including `-81` (the hit control) and `-82` (the poison control) |

That contrast IS the story's thesis, measured rather than argued: the obvious test for this story
is structurally incapable of distinguishing a working cache from no cache.

`sha256(argus/cache/memo_store.py)` round-tripped exactly, **both conventions stated** (§0.5 trap 2):

```
working tree (CRLF, this autocrlf checkout)  595a2628b603470be2860d3c131b5579bdbbfe2ccb6fed124955f82e9c43cce4
git blob at HEAD (LF)                        4f970f178327fb7fe3dd75d235cc1e7d2aeb77e60694891a6bbe790b9590c7b7
```

**Mutation 2 — a future change MEMOIZES DEEP-PASS OUTPUT (AC6.1's required mutation).** An
LLM-derived recording (`deep_pass_degraded:empty-response`) inserted into the memoized payload.
The fence refused at the store's write path, naming the hazard rather than merely forbidding:

```
argus.cache.memo_store.DeepMemoizationFenceError: REFUSED: an LLM-derived recording may not enter
a memoized payload while the recording-producing closure carries the V1 PLACEHOLDER checkpoint.
Offending rule_id(s): ['deep_pass_degraded:empty-response']. … the key DOES NOT VARY WITH THE
MODEL THAT PRODUCED THIS RESULT — two runs against two different models would COLLIDE ON ONE CACHE
SLOT and the store would serve a result computed under model A to a run that asked for model B.
```

`sha256(argus/pipeline.py)` round-tripped exactly:

```
working tree (CRLF)   7f94ee760d6fa64869c4f39d29ee42831c174fec714de04c8de7efcb65d1421b
git blob at HEAD (LF) ffcdeb2060201dfbe007aee0b28c228cf5ab8530d07aeb4877da28a8ea70c530
```

**AC6.3 red-first, against the REAL pre-fix registry state with the FINAL committed guard code** —
no synthetic reconstruction was needed, the defect was live:

```
E  AssertionError: A 'delivered-differently' REASON asserts something the import graph now
   falsifies. …
   FR27: disposed 'delivered-differently', and its REASON still claims ['deferred to story',
   'is unwired', 'mechanism is unwired'] — but argus.cache.memo_store IS reachable from
   argus.cli, so that claim is FALSE.
```

#### AC7.1 — cold-run A/B against a detached `58c8f6b` worktree at a SHORT path (`C:/t/ab`, §0.5 trap 3)

**Comparison kind, stated: a WORKING-TREE byte comparison, which is the correct one here** — both
sides are runtime-written by the process under test into `C:/t/abrepo`, neither is committed
content, so `core.autocrlf` cannot rewrite either and a git-blob comparison would have nothing to
read.

```
BEFORE(58c8f6b) exit 0 | AFTER exit 0
exit_code identical : True     stdout identical : True     stderr identical : True
artifact SET identical (excluding argus/cache/): True   (only-BEFORE [], only-AFTER [])
differing artifact BYTES: 0        artifacts compared: 10
BEFORE argus/cache/ slots: []
AFTER  argus/cache/ slots: ['5432183de387933e0d58d398b54f448a09bb4734379c1e442f025ff5091d2c8e.json']
```

**The single difference is the cache slot this story exists to create.** It is attributed, not
waved past: no other byte of a default run moved.

#### Final gates on the delivered tree (`d040cad`)

```
python -m pytest        1466 passed / 0 failed / 0 error / 0 skipped in 148.29s   (baseline 1441)
mypy argus              Success: no issues found in 75 source files
bandit -r argus         19 findings BEFORE (58c8f6b worktree) / 19 AFTER — CONTENT-diffed,
                        not count-compared: 0 NEW, 0 REMOVED, identical sets
NFR-M1 sweep            green, NO new exemption added
test_no_web_imports     18 passed (the Story 6.1 quarantine subprocess gate)
test_invocation_contract / test_sequential_portability / test_module_size_ceiling / green
  test_secret_containment (in the full suite)
python -m argus.cli audit .
  verdict=RELEASE_READY deep_ratio=65/181 blocking_findings=0 assessed_deep_ratio=65/81
  scope=application held_out=100       exit 0
git ls-files -- argus            75   (74 + argus/cache/stage_memo.py)
closure from argus.cli           60 of 75 reachable (was 58 of 74) — RAISED, never lowered
  argus.cache.memo_store   reachable=False -> TRUE   ← AC1.1, the flip this story makes
  argus.cache.stage_memo   reachable=TRUE
  argus.cache.invalidation reachable=False           ← AC5.4's measured basis, unchanged
deferred-work.md         git diff --numstat 58c8f6b HEAD -> 203 insertions, 0 DELETIONS
git tag -l               (empty)          origin/master  00c8d1b  UNMOVED
```

#### Reds I measured that were NOT mine, attributed rather than absorbed

* **`tests/test_grammar_runtime_validation.py::test_a_drifted_grammar_cannot_produce_a_green_verdict`**
  — went red on first integration and it was a REAL interaction, not a flake. `-125` audits ONE
  repository THREE times to contrast three TOOLCHAIN states, and all three present the *same*
  closure to the store, because the drift is simulated by monkeypatching Argus's own
  `_CALL_NODE_TYPES` in-process rather than by installing a different grammar (deliberately — its
  own docstring says so). A real drifted grammar arrives with its own package version, which the
  10.2 per-grammar provenance folds into the key; an in-process patch cannot move that key and is
  not meant to. Fixed by wiping `.argus/cache/` between legs — the sanctioned lever, since
  `memo_store`'s own invariant is that the verdict is correct *whether or not the cache exists, is
  warm, or is wiped*. **No assertion was weakened, removed or narrowed**; each leg simply computes
  its own answer, exactly as it did before the store was wired. The reason is recorded in a long
  docstring on `_wipe_memo_cache` so a future reader cannot delete it as noise.
* **`tests/test_secret_containment.py` cannot be collected in isolation** — `ModuleNotFoundError:
  No module named '_cartridge'`. **PRE-EXISTING, proven not mine**: the file is byte-identical to
  `58c8f6b`, the same `sys.path.insert(..., "argus" / "cartridges")` is at line 66 of the
  `58c8f6b` blob, and `git ls-tree 58c8f6b -- argus/cartridges` is empty — the directory has never
  existed. It passes in the full suite because another module inserts the correct
  `tests/cartridges` path first. Filed as `DF-12-3-C`, **not fixed here**, because repairing an
  unrelated test module's import path inside the story that wires the memoization store would mix
  two changes.
* **7 dogfood / distribution currency guards** — red BY DESIGN once `argus/**` composition moved
  (74 → 75 files). Remedied the sanctioned way (§0.1): regeneration through
  `scripts/regenerate_dogfood_artifacts.py` in a SEPARATE commit of renderer output only, at a
  truthful provenance sha (`fab36e7`) confirmed an ancestor of `HEAD`. **No artifact was
  hand-edited.** `TC-ArgusAgent-DOCS-001-54` then caught stale module figures published in
  `README.md` and `CHANGELOG.md` (74→75 modules, 79→80 wheel entries, 78→79 sdist members); the
  documents were corrected to what the build measures — *the artifact is the fact* — rather than
  the guard being relaxed.

### Completion Notes List

**What was actually built.** One production call site — `argus/cache/stage_memo.py` — that derives
the corrected 10.2 key and consults the 5.2 store around the deterministic detect/grade + orphan
stage, plus the proof that consulting it cannot change an answer. Everything else is composition of
things that already existed (AR7/§3.3): no second key function, no second serializer, no second
hasher, no new store, no CLI flag, no FR16 row/threshold/exit-code/verdict-enum change.

**The vacuity gate was treated as the primary design constraint, and it changed the design.**

* All **four mandatory controls** shipped. Control 1 (`-81`) spies the real `_detect_per_file`
  seam; Control 2 (`-82`) is the poison positive control; Control 3 is the two seam mutations
  above, both reverted with `sha256` round-tripped in **both** stated conventions; Control 4 is
  enforced structurally — `-85` derives its perturbation matrix from
  `RecordingProducingClosure.model_fields` and **fails if the matrix and the live model diverge in
  either direction**, so a closure field added later cannot escape unfingerprinted.
* **The poison positive control is the assertion that decides the story.** A validly enveloped,
  integrity-correct, schema-valid but DIFFERENT recorded result — carrying a verdict-BLOCKING
  finding minted through the real 1.2 builder — is written into the slot the next run will read,
  through the REAL store so the envelope `content_hash` verifies and the AR6 tamper guard has no
  reason to object. The next run's verdict **must move off `RELEASE_READY`**. The key is read off
  the LIVE slot filename, never recomputed by the test (that would be the self-comparison trap).
  Note the polarity against `-89`: `-89` proves a TAMPERED entry is REFUSED, `-82` proves a
  WELL-FORMED entry is SERVED. A store that refuses everything passes `-89` and fails `-82`; a
  store that is never consulted passes every byte-identity test in both files and fails `-82`.

**Design decisions taken under §7/§8 authority, with the reasons that bind.**

| # | Decision | Why |
|---|---|---|
| **D-1** | The operator's `--passes` / `--ignore-path` / `--ignore-pattern` are folded into the key through `DetectorDescriptor.config`. | Measured: `_detect_per_file` reads exactly those three and `_orphan_findings` reads `enabled_passes`. Leaving them out is an **UNDER-key** — two runs with different `--passes` would collide on one slot and the second would be served findings from detectors it explicitly deselected. `config` is the field designed for this ("editing any field CHANGES the set hash → CHANGES the derived key"), so it needs **no new closure field** and `CACHE_KEY_SCHEMA_VERSION` stays `"3"` (DN-4). The whole stage configuration is bound to every descriptor rather than attributed detector-by-detector: an attribution that drifts from the real gating is an under-key, whereas redundancy can only ever cause an extra MISS, which is a recompute and therefore correct. |
| **D-2** | `argus-agent`'s own distribution version is folded into `tool_versions`, alongside `radon`. | **A genuine hole found by measurement, not by the story.** FR27 promises the same verdict for the same repo **AND ARGUS VERSION**, so an upgrade is entitled to a different answer — and a cache that does not know the tool changed would serve the pre-upgrade result. `code_identity` tokens cover a detector whose logic changes, but they are hand-bumped and cover only detectors: a change to the grader, the orphan pass, the index's extraction vocabulary or the ledger is invisible to them. Probed through the EXISTING `ast_index` resolver via a 4-line public alias (AR7 — reuse, never fork), never a second `importlib.metadata` read. Conservative direction: a needless recompute is correct, a stale serve is not. |
| **D-3** | `content_hash` is `source_state.identity`. | Content-faithful in all three source-state kinds **by construction**: a `commit` identity is only issued for a CLEAN git tree, and both `worktree` and `directory` identities embed `_digest_of`, a sha256 over the audited files' actual bytes. Any changed source byte moves it. It also REUSES the intake digest rather than adding a second hasher (AC1.4). |
| **D-4** | The skipped-on-exhaustion remainder is appended **outside** the memoized payload. | It is a pure function of the halt projection, not of the detectors, so memoizing it would store a derivable value. `work_manifest_files` already folds the ASSESSED set, so a run halting at a different point reads a different slot. |
| **D-5** | The AC6.1 fence lives at `MemoStore.store_stage`, with the checkpoint slots as **required** keyword arguments taken from the closure the key was derived from. | The write path is the choke point, which is what makes the rule *impossible to break* rather than advisory. Optional arguments would let a caller memoize LLM-derived output simply by not mentioning the model it ran under — the exact silence the fence exists to break. The fence is **conditional on the placeholder**, so it stands down by itself once Story 6.1 substitutes a real captured checkpoint: it fences a key that cannot yet discriminate, it does not ban deep memoization forever. |
| **D-6** | `memo_store` names the deep-pass rule stem as a LITERAL and joins it to `deep_pass.RULE_DEGRADED_DEEP_READ` in the TEST layer (`-97`). | `argus.audit.deep_pass` pulls the dispatch surface and **nothing may drag it onto the memoization path** (NFR-S6) — the memo hook now runs on every default invocation, so its import hygiene is load-bearing rather than incidental. A literal is a snapshot and snapshots rot, so `-97` is the join the fence cannot make for itself. |
| **D-7** | `lookup_stage` explicitly REFUSES a payload whose `schema_version` is not current. | **Not implied by the tamper guard, and its absence would be a real defect.** The envelope `content_hash` is recomputed from the payload it is stored with, so an old-shape entry verifies against itself perfectly — the hash proves the bytes were not edited, never that they mean what this version thinks they mean. Without the explicit check the bump would move the hash for future writes while old-shape entries kept being served. `-91` asserts both directions. |
| **D-8** | `store`/`lookup` (findings-only) are kept **alongside** the new `store_stage`/`lookup_stage`, with **disjoint payload keys**. | The findings-only pair is the 5.2 library contract that `tests/test_memo_store.py` and `tests/test_cache_invalidation.py` pin, and this story has no mandate to move it. Disjoint keys mean neither reader can half-decode the other's slot. |

**Where discipline best practice and an explicit project standard conflicted, THE PROJECT STANDARD
WON — recorded with the tradeoff:**

* **DRY vs. the NFR-S6 quarantine (D-6).** Best practice says import the constant. The project
  standard says nothing may drag the dispatch surface onto the default path. **Standard wins**: the
  literal is duplicated, and the cost — that two literals can drift — is paid down by a committed
  test rather than accepted silently.
* **DRY vs. precision in the detector config (D-1).** Best practice says bind each setting to the
  detector it governs. The project's standard is that an under-key is a correctness defect while an
  over-key is merely a slower run. **Correctness wins**: the whole stage configuration is bound to
  every descriptor, redundantly and deliberately, and the docstring says why.
* **YAGNI vs. folding the Argus version (D-2).** No AC asked for it. `memo_store.py`'s own named
  failure mode — *"memoization caches errors → reproducibility ≠ correctness"* — and FR27's own
  wording did. **Correctness wins.**

**The §D ruling was honoured exactly, and NOT quietly widened.** Memoization is scoped to the
deterministic stage; the deep pass runs downstream and is never served. `-98` proves all three
halves with an INJECTED port and no socket: the deterministic stage HITS with `--deep-audit` on,
the port dispatches the SAME number of times on the warm run (so deep output is **not** served),
and the persisted slot BYTES contain no LLM-derived rule id. **The honest residual — PRD §501 is
NOT delivered — is filed as `DF-12-3-A` and disclosed at four sites** (the `stage_memo.py` module
docstring, the hook's call site in `pipeline.py`, `architecture.md` §Memoization, and the ledger),
**with Story 12.4 named explicitly** so its next-action text cannot imply a deep verdict is
reproducible.

**AC6.3 — both halves, and the second is the one that matters.** FR27's entry is re-derived to
`wired` with the superseded sentence kept, not deleted (§3.4). But correcting the text alone would
have left the next disposition free to rot the same way, so the refutation gap is closed:
`delivered_differently_refutations` is a **fourth** direction, as narrow as Story 12.2's
`not_built_refutations` — it fires only when a REASON contains a registered unwiredness/deferral
marker AND the module that reason is about is reachable, so `delivered-differently`'s legitimate use
(*"delivered by another mechanism, divergence named"*) is untouched and no false accusation is
manufactured. `-37c` drives all three outcomes over a synthetic graph. Registered in
`architecture.md` §Enforcement per the §843/§845 precedent.

**NFR-M1 was enforced against me, and the sanctioned remedy was taken.** The new guards came to
**1388 lines** — 188 over the ceiling — and the sweep caught them because the new files were
`git add`-ed immediately (`DF-12-1-D`'s hazard is that the sweep reads the git INDEX). They were
**split on a cohesion boundary**, not shaved and not exempted: `test_stage_memo_wiring.py` (*is the
cache load-bearing?*) and `test_stage_memo_contract.py` (*can the cache lie?*) over a shared
`tests/_stage_memo_corpus.py`, following the `tests/cartridges/_cartridge.py` fixture-module
precedent. The shared spy is deliberately in one place: two copies of a spy is two definitions of
"the stage ran", and the whole story turns on that one measurement. **No exemption was added.**
`argus/pipeline.py` is **1044** lines — 156 of headroom.

**Every §F ledger item is ruled IN or OUT with reasons in `deferred-work.md`, none left silent.**
`DF-12-1-B` IN but reshaped, with its false trigger and its stale figure both corrected as a new
append; `DF-12-1-A` OUT and its Epic-12-retrospective escalation recorded as still standing, not
re-escalated as new; `DF-12-2-D` OUT and **cited, not re-homed**; `DF-12-2-E` OUT — trigger did
**not** fire, verified: this story edits neither `deep_pass.py` nor the adapter, which is precisely
why the fence lives in `memo_store.py`; `DF-10-2-A` OUT and **left flagged for the retrospective
with its OPERATOR owner**, not silently re-homed; `DF-12-1-D` hazard live, trigger did not fire,
and the hazard was handled; `DF-12-1-E` trigger did **not** fire — `git ls-files -- 'argus/pipeline*.py'`
is still **3**, because the new module is `argus/cache/stage_memo.py`; `DF-5-1-A` stays closed, its
contract now proven over the wired path by `-94`. **AC5.4 is ruled OUT LOUD** as option (b), filed
as `DF-12-3-B`, with `-95` asserting both the 5.3 surface's integrity and the measured
unreachability the ruling rests on — so if a later story wires it, the ruling must be re-taken
rather than inherited.

**Publication fences verified on the delivered tree: `git tag -l` is EMPTY and `origin/master` is
still `00c8d1b`. Nothing was pushed, tagged, released, dispatched or uploaded.**

**Open for the reviewer.** (1) `-95`'s ruling that Story 5.3's ACTIVE invalidation is out of scope
is the story's own §AC5.4 option (b); if the reviewer reads the epic's *"the DF-5-1-A invalidation
contract holds over the wired path"* as requiring the full 5.3 surface, that is a scope expansion
worth naming now rather than discovering later. (2) Decision **D-2** (folding the Argus
distribution version into the key) is a correctness improvement no AC requested — it is defensible
under FR27's own wording, but it is the one place this story went beyond its literal brief, and it
is flagged here rather than buried.

### File List

**New (`git add`-ed immediately per `DF-12-1-D`):**

- `argus/cache/stage_memo.py` — the production call site: closure builder, key derivation, the
  hit/miss composition, and the §D scope disclosure.
- `tests/test_stage_memo_wiring.py` — *is the cache load-bearing?* `TC-ArgusAgent-CACHE-001-81`..`-88`.
- `tests/test_stage_memo_contract.py` — *can the cache lie?* `TC-ArgusAgent-CACHE-001-89`..`-100`.
- `tests/_stage_memo_corpus.py` — shared corpora, request builder and the CONTROL-1 spy (fixture
  module, not a test module).

**Modified:**

- `argus/cache/memo_store.py` — `MEMO_STORE_SCHEMA_VERSION` `"1"`→`"2"`; `RecordedStageResult`;
  `store_stage`/`lookup_stage`; `LLM_DERIVED_RULE_PREFIXES`; `DeepMemoizationFenceError` and the
  AC6.1 fence.
- `argus/cache/key.py` — the stale schema-version comment corrected at its site (AC7.4). **No code
  change; `CACHE_KEY_SCHEMA_VERSION` is untouched at `"3"`.**
- `argus/pipeline.py` — the memoization hook around the detect/grade + orphan stage, with the scope
  note; two imports.
- `argus/index/ast_index.py` — `resolved_tool_version`, the public face of the EXISTING impure
  version probe (AR7 reuse, no fork).
- `tests/test_v1_commitment_closure.py` — FR27 re-derived to `wired` (superseded text kept);
  `delivered_differently_refutations` + its markers; the fourth direction wired into
  `TC-ArgusAgent-DOCS-001-34`; the `-37c` positive control.
- `tests/test_no_web_imports.py` — `argus.cache.stage_memo` added to the swept population (extend
  the guard, do not fork — `AI-E4-7`).
- `tests/test_grammar_runtime_validation.py` — `_wipe_memo_cache` between `-125`'s three toolchain
  legs, with the reason recorded. **No assertion weakened, removed or narrowed.**
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §Memoization step 2 recorded and the
  two stale premises struck-not-deleted; the §D scope disclosure; the FR27 parenthetical in the
  §Delivery-closure rule corrected; the new **Disposition-reason refutation enforcement**
  registration.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **APPEND-ONLY, proven**: `DF-12-3-A`
  (the §501 residual), `DF-12-3-B` (AC5.4's reasoned exclusion), `DF-12-3-C` (a pre-existing issue
  measured in passing, attributed not inherited), the `DF-12-1-B` corrections, and every §F ruling.
- `README.md`, `CHANGELOG.md` — the published module/wheel/sdist figures corrected to what the
  built artifact measures.
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md`,
  `minions-dogfood-budget-plan.md`, `minions-dogfood-proof.md` — **renderer output only**,
  regenerated through `scripts/regenerate_dogfood_artifacts.py` in a separate commit. **No hand
  edits.**
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — status transitions.
- This story file — tasks, Dev Agent Record, File List, Change Log, Status.

### Change Log

| Date | Commit | Change |
|---|---|---|
| 2026-08-13 | `fab36e7` | `feat(cache): a re-run returns the recorded result (Epic 12, Story 12.3)` — the memoization hook, the widened payload, the AC6.1 fence, the registry correction + the fourth refutation direction, the two document premise corrections, and the guards. |
| 2026-08-13 | `c9603ae` | `chore(dogfood): regenerate the three artifacts at the Story 12.3 sha` — renderer output ONLY, provenance `fab36e7`, verified an ancestor of `HEAD` with `argus/` unchanged since. Population 74→75, LOC 21569→22126, partition ids `1a31dc9a9559` (unchanged) / `619a713d53ca`→`53772a11b82a` / `aaec0673cdcf`→`5dc8d2b3da86`. |
| 2026-08-13 | `d040cad` | `docs: the published module figures follow the artifact, not memory` — `README.md` / `CHANGELOG.md` corrected after `TC-ArgusAgent-DOCS-001-54` caught them stale (74→75 modules, 79→80 wheel entries, 78→79 sdist members). |
