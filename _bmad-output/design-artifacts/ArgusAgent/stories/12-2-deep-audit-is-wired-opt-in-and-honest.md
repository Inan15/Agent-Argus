---
baseline_commit: 2bea92fa93a5b7ef711cfd205bac01568ef4c781
baseline_note: >-
  `HEAD` = `2bea92f` on `master`. **`argus/` is CLEAN.** `git status --porcelain` shows exactly two
  MODIFIED tracked files — `sprint-status.yaml` and `stories/12-1-pipeline-stops-breaching-its-own-limit.md`,
  both **documentation only**, both the trailing review-round record of Story 12.1 — plus the usual
  untracked orchestrator/host directories (`.bmad-drift-audit/`, `_bmad-output/audit-reports/*`,
  `argusdemo/`, `bmad-dev-loop-pack/`). No `argus/**`, `tests/**`, `scripts/**` or packaging file is
  dirty. `git tag -l` is **EMPTY**; `origin/master` has **not** moved from `00c8d1b`; `HEAD` is 11
  ahead. **No CI run has ever seen a line of Epic 10, Epic 11 or Epic 12.** Every figure in this story
  is **LOCAL, Windows / CPython 3.11.15** under the dated risk acceptance in §0.2 — carried forward,
  not re-taken. **Make no CI claim.**
  ✅ **THE SUITE IS FULLY GREEN AND THERE IS NO SANCTIONED RED.** Story 12.1 closed the five-story
  `DF-11-1-A` node-id carve-out. Your baseline is **1418 collected / 1418 passed / 0 failed / 0 error
  / 0 skipped**, re-run to completion on this tree (§B.0). **ANY red you measure is yours and must be
  attributed.**
  ⚠️ **THE GROUND MOVED UNDER THIS STORY.** Story 12.1 extracted `argus/pipeline_stages.py` out of
  `argus/pipeline.py` (1331 → **944**, 256 lines of headroom). `git ls-files -- argus` is **73**, not
  72. The dogfood artifacts were regenerated at provenance `c4bd769`. **Every figure in the Epic-11
  retrospective predates this.** Re-measure; carry nothing forward.
  ⚠️ **THE EPIC-11 "NO NEW `argus/**` FILE" FENCE IS LIFTED FOR EPIC 12** (§0.1). **Publication is
  still forbidden** (§0.3).
  🔴 **THIS TREE ALREADY EMITS A FALSE DEEP CLAIM, TODAY, BEFORE YOU CHANGE ANYTHING.** See §0.5. It
  is reproducible in one command and it is the sharpest thing this story closes.
  🔴 **THREE OF THIS STORY'S INHERITED PREMISES ARE STALE, INCLUDING THE SOURCE COORDINATE THE EPIC
  AND THE ARCHITECTURE BOTH CITE.** See §0.4. **Do not implement the sentence. Implement §A.**
  **Every count, line number, LOC figure, verdict and exit code below was produced by EXECUTING code
  on THIS tree on 2026-08-12.** Treat every line number as a hint you must re-verify by anchor text.
story_key: 12-2-deep-audit-is-wired-opt-in-and-honest
epic: 12
---

# Story 12.2: The deep audit is wired, opt-in, and honest about what it costs and sends

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
> 🔵 **This is the SECOND story of Epic 12 and the epic's first capability delivery.** Story 12.1 (the
> hard enabler) is `done` and gave you 256 lines of headroom in `argus/pipeline.py`. The epic's
> dependency note says **12.2 EARLY**, because the reachability measurement it carries (AC6) can
> change what Story 12.4 must say. **It publishes nothing.** The publish is Story **12.9** and the
> orchestrator halts before it.

---

## Story

As a developer who wants a real answer on the code that matters,
I want to enable a deeper pass on demand, with its cost and its egress stated up front,
so that I can get depth when I want it without paying for it or leaking source when I don't.

**Why this is one story.** Every clause is the same subject: *the one seam in this system through
which repository content can leave the machine*. Wiring it, fencing it off by default, disclosing it
before it fires, funding it from the existing ceiling, and degrading it honestly are not five features
— they are the five faces of making one dangerous capability safe to reach. Splitting them would ship
a reachable egress path in one story and its disclosure in another, which is the only ordering the
requirement explicitly forbids.

**What it is NOT.** It ships **no new cost-governance mechanism** (FR21/FR22 already govern spend —
AR7/§3.3: reuse, never fork). It changes **no FR16 decision-table row, threshold or exit-code
mapping**. It adds **no network listener and binds no port**. It does **not** make the default run
slower, chattier, keyed, accounted or online — the default run after this story must be
**byte-identical** to the default run before it (AC2.4). And it **publishes nothing**.

**Why it is not merely "connect two modules".** `DeepAuditSeam` has, measured today, **zero production
callers anywhere in `argus/**`** — it is more unwired than the epic says. Meanwhile the tree already
ships a code path that *tells the operator a deep read happened when none did* (§0.5). This story is
therefore not "add a capability"; it is **make a claim the tool already makes become true, or stop
making it**.

⚠️ **Read §0 before anything else. Six items gate this story.**

---

## Story Context

### Method statement — everything in §0–§E was MEASURED on this tree on 2026-08-12

Every count, coordinate, LOC figure, verdict and exit code below was produced by running `git`,
`wc -l`, `pytest`, `python -m argus.cli audit …` against **purpose-built synthetic repositories**, and
by importing and calling `argus.audit.open_llm_adapter.OpenLLMAdapter`,
`argus.reports.plain_english.render_depth_meaning` and — critically — the **real**
`tests/test_v1_commitment_closure.build_import_graph` / `reachable_from` against a synthetic package,
directly. Where this story asserts that a guard *is* or *is not* able to see something, that assertion
was produced by **running that guard's own code**, never by reading it. **Re-derive everything;
transcribe nothing.**

---

## §0. The six gates on this story — read these first

### 0.1 — 🔴 OPERATOR RULING: THE EPIC-11 FENCE IS LIFTED FOR EPIC 12 (carried from Story 12.1 §0.1)

**Granted by XAgent007 (operator), 2026-08-12.** It was recorded verbatim in Story 12.1 §0.1 and it is
**live for all of Epic 12**, not just for 12.1. Carried forward here:

> **RULING:** for **EPIC 12** (not just Story 12.1), the following sequence is **PRE-AUTHORISED** —
> implement → commit → regenerate the dogfood artifacts **THROUGH THEIR OWN RENDERERS** at a truthful
> provenance sha → re-run the gates. The Epic-11 "no new `argus/**` file" fence is **LIFTED for Epic
> 12**. Every regenerated artifact must cite a truthful provenance sha that is an **ancestor of HEAD**,
> and the story must say so as an AC.
>
> **STILL BINDING, NOT LIFTED:** (a) nothing is published — no push, no tag, no release, no
> `workflow_dispatch`, no index upload. Publication is Story 12.9 alone. (b) A regeneration is only
> legitimate when produced by the artifacts' **own renderers** at a truthful sha; **hand-editing a
> dogfood artifact is still forbidden.**

**What this means for you, concretely.** You may create `argus/**` modules (§A.1 recommends exactly
one). **You WILL move the dogfood-audited population** the moment you `git add` it, and the currency
guard Story 12.1 landed will go red *by design*. Verified on this tree: `c4bd769` **is** an ancestor of
`HEAD` and `git diff --quiet c4bd769 HEAD -- argus/` is **empty**, so
`TC-ArgusAgent-DOGFOOD-001-49..-52` are **green right now** and will go red the moment you touch
`argus/`. You fix that by running **`scripts/regenerate_dogfood_artifacts.py`** — never by loosening an
assertion, never by editing an `.md` by hand. Sequencing is §C.

### 0.2 — 🔴 DATED RISK ACCEPTANCE, CARRIED FORWARD (AI-E10-1)

**Recorded by XAgent007 (operator), 2026-08-11.** Carried forward, **not re-taken by this story**. No
CI run covers any Epic 10, 11 or 12 sha. Every figure in this story and every figure you produce is
**LOCAL, Windows / CPython 3.11.15**. CI evidence for your delta is **NOT ESTABLISHED** and you must
write that phrase rather than imply a run.

**SD-2 standing, restated because this story is where it bites hardest.** Three consecutive epics have
run with no executed CI gate, and Epic 12 **ends in an irreversible publish** (12.9). This story adds
the only code path in the product that can transmit data off the machine. **No AC below depends on CI
evidence, and none may be written to.** Every gate this story ships must be a committed test that runs
locally, in the shape of the existing import-isolation gates — which is what NFR-S6 asks for in any
case. Re-taking the acceptance for Epic 12 is **AI-E11-4**, owned by the operator, and is **not this
story's to take**.

### 0.3 — 🔴 NOTHING IS PUBLISHED

No `git push`, no `git tag`, no GitHub release, no `workflow_dispatch`, no PyPI/index upload, no
marketplace listing. `git tag -l` is empty and must stay empty; `origin/master` is `00c8d1b` and must
stay there. Publication is Story **12.9**. **You DO commit locally** — see §C.

**A second publication-shaped fence, specific to this story: NO LIVE DISPATCH.** You must not, at any
point, cause this tree to transmit repository content to a third-party provider — not to validate your
work, not "just once against a local Ollama", not with a throwaway key. Every test you write dispatches
through an **injected fake** (`FakeDispatch`, the NFR-D2 idiom this codebase already uses in
`tests/test_llm_dispatch_port.py`). The one legitimate live-egress observation is the **absence** of
one. If you believe an AC cannot be satisfied without a real dispatch, **HALT** (§E).

### 0.4 — 🔴 THREE INHERITED PREMISES ARE STALE (AI-E10-3, discharged at create-story time)

Re-measured by **execution** on this tree, 2026-08-12. Full table in §B.1. What HELD and what did not:

**STALE — do not transcribe these:**

1. **The seam's coordinate is wrong in BOTH the epic and the architecture.** Both say
   `DeepAuditSeam` is at **`argus/audit/deep_audit.py:91`**. Measured: `class DeepAuditSeam:` is at
   **line 98**; line 91 is inside `build_closure_from_recording`'s kwargs dict. The file is 112 lines.
   *Impact: low, but it is the coordinate two planning documents agree on, which is exactly the kind of
   agreement that reads as verification and is not. Anchor on the text `class DeepAuditSeam:`.*
2. **The seam is MORE unwired than the epic claims — it has ZERO production callers.** The epic and the
   architecture both say it is *"referenced only from `argus/audit/*` and `argus/dogfood/proof_run.py`"*.
   Measured over every `.py` in the repo, the identifier `DeepAuditSeam` appears in exactly **three**
   places: its own `class` statement, its own `__all__` (`argus/audit/deep_audit.py:51`), and
   `tests/test_llm_dispatch_port.py`. **`argus/dogfood/proof_run.py` does not import it** — its only
   mention is a *docstring* at line 80 saying the seam is *"a SEPARATE injected port NOT"* used.
   *Impact: this strengthens the story. There is no existing production caller whose behaviour you must
   preserve, and no import you can piggyback on. The wiring is genuinely from nothing.*
3. **The `[llm]` extra is NOT an egress gate, and the architecture implies it is.** Architecture §E
   says the live dispatch path is *"behind the opt-in `[llm]` extra"*. Measured in `pyproject.toml`:
   the `[llm]` extra contains **only `litellm`**, while **`httpx>=0.24.0` is a BASE dependency** of
   `argus-agent`. `OpenLLMAdapter.dispatch` falls back to `_dispatch_httpx` when litellm is absent, and
   `_dispatch_httpx` performs a real `httpx.Client().post(...)`. **So a plain `pip install argus-agent`
   — no extras — contains a complete, working egress path.** *Impact: HIGH, and it decides AC2. The
   opt-in cannot be a packaging extra. It must be an explicit act at the invocation.*

**HELD — you may rely on these (but re-verify by anchor, not line number):**

4. `argus/pipeline.py` is **944** lines (cap 1200, **256 free**); `argus/pipeline_stages.py` **512**;
   `argus/cli.py` **522**. `git ls-files -- argus` = **73**.
5. **Story 6.1's determinism quarantine exists and is green**, as `TC-ArgusAgent-AUDIT-001-10` in
   `tests/test_no_web_imports.py` — a real subprocess gate. §0.6 explains why "it still passes" is
   **not** a sufficient AC.
6. **FR21/FR22 spend governance exists and is reusable as-is**: `argus/cost/budget_governor.py`
   (`BudgetConfig`, `budget_config_from_budget`, `account_spend`) and `argus/cost/exhaustion.py`
   (`CostUnit`, `HaltProjection`, `project_halt_point`, `would_breach`, `build_halt_report`). The
   pipeline already funds the deterministic passes through them via
   `argus/pipeline_stages.py::_build_cost_units` / `project_halt_point`. **There is nothing to build
   here and you must not build any of it.**
7. **The `deep` pass-name convention already exists.**
   `argus/reports/plain_english.py:114` defines `LLM_DEEP_PASSES: tuple[str, ...] = ("deep",)` and
   `render_depth_meaning` already branches on it. Reuse this token; do not mint a second vocabulary.

### 0.5 — 🔴 THE TREE ALREADY EMITS A FALSE DEEP CLAIM. REPRODUCE IT BEFORE YOU WRITE ANY CODE.

This is the single most important finding in this story, it is **live on `2bea92f`**, and it gives you
a **free RED-first demonstration** exactly as §0.5 did for Story 12.1.

`argus/cli.py:334` computes the enabled pass set as `_split_csv(args.passes, _ALL_PASSES)`.
`_ALL_PASSES` at `argus/cli.py:138` is the **default**, *not a validator* — an unrecognised token in
`--passes` flows straight through into `AuditRequest.enabled_passes`. And
`render_depth_meaning` (`argus/reports/plain_english.py:129`) keys the depth disclosure on
`any(name in LLM_DEEP_PASSES for name in enabled_passes)`.

Measured, on a synthetic two-file repository, on this tree:

```
$ python -m argus.cli audit <repo> --passes coverage,deep
  - What `audited_deep` means in this run: a deep read was dispatched for the file and
    its claim was validated against the repository AST.
verdict=RELEASE_READY deep_ratio=1/2 blocking_findings=0 assessed_deep_ratio=1 scope=application held_out=1
exit 0
```

**No deep read was dispatched.** No LLM was contacted. `DeepAuditSeam` has zero production callers. The
sentence is produced entirely by the presence of the string `deep` in a CSV.

**This is FR36's central prohibition — *"It never produces a false deep claim"* — being violated by the
shipped tool, before this story adds a single line.** And it is this project's dominant defect class in
its purest form: `tests/test_plain_english.py` has a test named
`test_depth_meaning_strengthens_automatically_when_a_deep_pass_is_enabled`, it passes, and it is
**structurally incapable** of noticing that nothing is enabled — it asserts that the *sentence* changes
when the *token* is present, and no assertion anywhere connects the token to work performed.

**Consequences you must accept as given:**

- **AC1's opt-in cannot be "pass `--passes …,deep`".** That spelling is already accepted, already
  claims depth, and already does nothing. Whatever you build, the *old* spelling must stop lying.
- **You get your RED for free.** A test that asserts *the strengthened disclosure appears only when a
  deep pass actually produced a recording* is **red on this tree right now**, before your
  implementation. Land it that way and say so.
- **Do not "fix" this by deleting the strengthened sentence.** The sentence is correct; its *predicate*
  is wrong. §A.4 rules on the remedy.

### 0.6 — 🔴 FOUR GUARDS CANNOT SEE WHAT THIS STORY CHANGES (AI-E11-1 / AI-E10-5)

**Vacuous guards are this project's dominant defect class.** Story 12.1 found the headline instance
(three stale artifacts, five green assertions). Before you write an AC, here is where the same failure
is already waiting for *this* story. Each was confirmed by running the guard's own code.

| # | Guard | What it claims | What it can actually see | Why it goes blind on THIS story |
|---|---|---|---|---|
| 1 | `TC-ArgusAgent-PIPELINE-001-10` (`test_pipeline_is_zero_token`) | *"the pipeline path imports NO LLM dispatch surface"* | A **runtime** subprocess import of a **hard-coded three-tuple** — `argus.models`, `argus.pipeline`, `argus.cli` — against a **hand-listed** forbidden set `_PIPELINE_LLM_FORBIDDEN_PREFIXES` = `minions_core.providers`, `argus.audit.ports`, `argus.audit.deep_audit`, `argus.audit.minions_llm_adapter`. | **Two independent holes.** (a) The forbidden set is a **list**, so a NEW `argus/audit/*` module (which §A.1 recommends you create) is **not** on it and leaks past. (b) If you wire the seam with a **function-local** import — which §A.2 shows you must — the module-level import never executes, so this gate stays green **by construction**. Its green would then prove *nothing*. AI-E10-5: the list is never the contract. |
| 2 | `TC-ArgusAgent-DOCS-001-34/-37` (`test_v1_commitment_closure.py`) | *"a `wired` disposition is PROVEN, never asserted"* | `reachability_refutations` refutes `wired`-over-unreachable and `library-seam`-over-reachable. | FR36 is currently disposed **`not-built`**, and — verified in the function's own docstring and body — **`not-built` makes NO reachability claim at all**. So when you wire FR36, **nothing goes red**. The registry will keep asserting FR36 is not built *after you build it*, silently, forever. This one is a **guaranteed** rot unless AC7 forces the flip. |
| 3 | `TC-ArgusAgent-DOGFOOD-001-48` + the two committed proof artifacts | the externalization honesty flag is intact | `DOGFOOD_EXTERNALIZATION_GUARD` is pinned **byte-for-byte**. | Its text says *"the AST-grounding deep-audit seam is **NOT wired in**, so every finding is advisory"*. Your story **makes the first clause false**. Worse, the **causal claim was already false** — §B.3 proves a blocking finding on the default, unwired path. This guard will go red (good) and you must fix it by making the sentence **true**, not by deleting the honesty language. |
| 4 | `test_depth_meaning_strengthens_automatically_when_a_deep_pass_is_enabled` | the disclosure *"cannot drift out of date"* | that the sentence changes when the token `deep` is in `enabled_passes`. | It is the guard that **certifies** the §0.5 false claim. It is green over the defect. |

**Binding consequence.** Every load-bearing AC below must be a **closure over the real structure**, not
a list; must be proven **RED at the real seam with the FINAL committed test code**; and — the clause
this story adds to the standard house rule — **must not be able to pass by not executing.** A gate that
is green because the code it guards was never reached is the deferred-import version of a vacuous
guard, and this story creates exactly that hazard on purpose.

---

## Acceptance Criteria

> **Guard-adequacy clause (AI-E11-1) — binding on every AC that ships a test.** For each committed
> guard, the implementation notes must state (i) the guard's **observable**, (ii) a demonstration that
> the defect **moves that observable** — proven RED at the **real seam**, with the **final** test code,
> not a reconstruction — and (iii) at least one adversarial variant **generated** from the structure
> the guard closes over (with its count), not hand-listed. A guard that cannot be shown to bite is not
> evidence.
>
> **Additional clause for this story (§0.6):** for any guard whose subject is a **deferred** code path,
> the notes must also state **the positive control** — the observation that the guarded thing *does*
> happen when it is supposed to. A one-directional "it did not leak" over a path that never ran is not
> a measurement.
>
> **Measurement-trap warning, inherited from Story 12.1 and re-confirmed here.** This checkout is
> `core.autocrlf=true`: a working-tree byte comparison silently disagrees with a git-blob comparison.
> Compare **blobs** when you compare bytes. A second trap was found writing this story: `pytest -q`
> when `pytest.ini`'s `addopts` **already** contains `-q` becomes `-qq` and **suppresses the summary
> line entirely** — you get a clean exit code and no counts. Run `python -m pytest` bare (§B.0).

### AC1 — The seam is reachable from the audit pipeline through an explicit opt-in (FR36)

**Given** `DeepAuditSeam` (anchor: `class DeepAuditSeam:` in `argus/audit/deep_audit.py`) has, measured
on this tree, **zero production callers** — the identifier appears only in its own class statement, its
own `__all__`, and one test file (§0.4 item 2)
**When** this story completes
**Then** the seam is reachable from the audit pipeline through an **explicit operator opt-in at the
invocation**, and that reachability is **PROVEN by the existing static import closure**, not asserted:
`argus.audit.deep_audit` appears in `reachable_from(build_import_graph(argus), "argus.cli")`.

- **AC1.1** The opt-in is a **dedicated, registered CLI flag** — not a bare `--passes` token (§0.5
  forecloses that spelling), not an environment variable (§0.4 item 3 and AC2.3 forbid it), and not a
  packaging extra. §A.3 rules on the spelling and gives the reasons; you may re-rule it with measured
  reasons, but you may not choose an environment variable or an extra.
- **AC1.2** The flag is registered in `tests/test_invocation_contract.py::CONTRACT_REGISTRY` with a
  real documentation site, and `TC-ArgusAgent-CLI-001-35`/`-36` pass in **both** directions. *This red
  is expected and is the guard working: the registry is derived from `build_parser()` at run time, so
  an unregistered flag fails as "ACCEPTED BUT UNSPECIFIED".*
- **AC1.3** The dispatch reaches the LLM **only** through `LLMDispatchPort` (AR7 / architecture
  Decision E). No pipeline module may import a concrete adapter type at module scope, and no new port,
  protocol or second seam is introduced.
- **AC1.4** With the opt-in **enabled** and a `FakeDispatch` injected, an end-to-end audit runs, the
  recording reaches the fold, and **zero LLM tokens** are consumed (the NFR-D2 idiom already used in
  `tests/test_llm_dispatch_port.py`). No test in this story performs a live dispatch (§0.3).

### AC2 — Off by default; the default run transmits nothing; egress is disclosed before the first byte

**Given** FR36 (*"Off by default, always"*) and NFR-S6 (*"No source code, prompt, or repository content
leaves the machine on the default path"*)
**Then** all four of the following hold, each by a committed gate:

- **AC2.1 — OFF BY DEFAULT.** The default invocation runs zero-token, offline and key-free. Proven by a
  gate in **the shape of the existing import-isolation tests** (NFR-S6 names that shape explicitly): in
  a fresh interpreter, a default `argus audit` run leaves every LLM-dispatch module **absent from
  `sys.modules`**.
- **AC2.2 — THE POPULATION IS DERIVED, NOT LISTED (closes §0.6 hole 1).** The forbidden-surface set
  must be **computed from the real structure** — every module under `argus/audit/**` that is not the
  provider-free pure leaf (`grounding`, and the pure `deep_audit`/`ports` only where the existing
  carve-out already reasons about them) — so that a module **added after this story** is covered
  without anyone remembering to add it. Demonstrate non-vacuity by **generating** the population and
  asserting its count and its non-emptiness, and by showing a synthetic new `argus/audit/*` module is
  caught. Equally, the **entry-point** population must be derived (every `argus/pipeline*.py` and
  `argus/cli.py`), not the current hard-coded three-tuple.
- **AC2.3 — THE ENVIRONMENT IS NEVER AN OPT-IN.** Measured on this tree:
  `OpenLLMAdapter.__init__` silently absorbs `ARGUS_LLM_MODEL`, `OLLAMA_MODEL`, `OPENAI_BASE_URL`,
  `OLLAMA_HOST`, `OLLAMA_URL` and `OPENAI_API_KEY`, and defaults the key to the literal `"mock-key"`.
  Confirmed by execution: with `OLLAMA_HOST=http://127.0.0.1:99999` set, a freshly constructed adapter
  reports `_api_base = 'http://127.0.0.1:99999'`. **A gate must prove that with every one of those
  variables set to a live-looking value and the opt-in absent, the run still transmits nothing and
  still constructs no adapter.** The variable list must be **derived from the adapter's own source**
  (an `ast` walk over its `os.getenv` calls), not transcribed — or the next variable someone adds
  escapes the gate.
- **AC2.4 — THE DEFAULT RUN IS BYTE-IDENTICAL.** Same repository, same flags, pre-story code vs
  post-story code: identical verdict, exit code, coverage figures, report bytes and `.argus/` bytes.
  Follow Story 12.1's method (a detached worktree at the pre-story sha, A/B with an identical
  `--report-dir`), and **separate population effects from behaviour effects** — adding tracked `.py`
  files moves the in-place ratios for arithmetic reasons that are not behaviour.
- **AC2.5 — DISCLOSURE BEFORE THE FIRST BYTE.** When the pass is enabled, the invocation states **what
  will be transmitted** and **which provider will receive it**, **before** any dispatch occurs. The
  gate must prove the **ordering**, not merely the presence of a sentence: with a fake port that
  records the disclosure stream at the moment `dispatch` is entered, the disclosure is already present.
  *A test that checks the final stdout contains a provider name cannot distinguish "before" from
  "after" and does not satisfy this AC.*
- **AC2.6 — NO NEW LISTENER.** No network listener, no bound port, no HTTP stack (NFR-S6 second
  sentence). `fastapi`/`uvicorn`/`starlette` remain absent — extend the existing guard, do not fork it.

### AC3 — Story 6.1's determinism quarantine still passes, AND its green is proven non-degenerate

**Given** `TC-ArgusAgent-AUDIT-001-10` (`test_pure_audit_seam_is_provider_free`) and
`TC-ArgusAgent-PIPELINE-001-10` (`test_pipeline_is_zero_token`) in `tests/test_no_web_imports.py`, and
architecture §E's rule *"Wiring is an adapter change, never a purity change"*
**Then** both still pass unchanged in intent —
**And** because §A.2's deferred-import design would make `PIPELINE-001-10` green *by construction*, a
**positive control** is committed: with the opt-in **enabled**, the LLM dispatch surface **IS** present
in `sys.modules`, and with it **absent**, it is **NOT**. Both directions, in one gate, in a fresh
subprocess each.

- **AC3.1** The pure seam (`argus.audit.ports`, `argus.audit.deep_audit`) must remain importable with
  **no provider import** — unchanged.
- **AC3.2** No provider import may move into the pure path. If satisfying any AC appears to require it,
  **HALT** (§E) — that is an architecture change, not a story decision.
- **AC3.3** State plainly in the notes: *a one-directional import-absence gate over a deferred path is
  a guard that passes by not executing.* The positive control is what makes AC3 evidence.

### AC4 — Spend flows through the EXISTING FR21/FR22 ceiling — no new mechanism

**Given** FR21/FR22 and AR7/§3.3 (*reuse, never fork*), and given that `argus/cost/budget_governor.py`
and `argus/cost/exhaustion.py` already implement halt → mark `skipped` → downgrade → report, and
`argus/pipeline_stages.py` already funds the deterministic passes through them
**Then** deep-pass spend is accounted through **those same functions**, and:

- **AC4.1** **No new cost module, no new config surface, no new ceiling, no new schema version, and no
  new numeric default.** `--budget` remains the ceiling; `0`/omitted remains a first-class *no ceiling*
  (OI3). If you find yourself adding a threshold, you have forked the mechanism — stop.
- **AC4.2** A ceiling reached mid-pass **halts**, marks the remainder `skipped`, **downgrades coverage**
  and reports — reusing `project_halt_point` / `build_halt_report`, proven with an injected fake port
  and a ceiling small enough to bite. The resulting verdict must be **honest about what was not
  examined**, never a `RELEASE_READY` computed over a truncated pass.
- **AC4.3** The `LLMRecording.credits_used` exact-numeric **string** (AR4 — never `float`) is what
  reaches the accounting. A `float` anywhere on this path is a defect: the canonical serializer raises
  on a float leaf, and this is the one new path that carries a cost number.

### AC5 — Degradation is honest: NFR-R1's behaviours are supplied HERE, not inherited

**Given** architecture §E justified omitting fallback, circuit-breaking and cost attribution because
they came *"for free"* from the Minions orchestrator, **and Story 9.1 removed that orchestrator** — the
architecture already records that *"those behaviours are now Argus's own responsibility on the
`OpenLLMAdapter` path. Story 12.2's honest-degradation ACs (NFR-R1) are what supply them"*
**Then** an **unavailable**, **erroring**, or **budget-halted** provider **downgrades coverage and
records a finding**. No false deep claim. No crash. No `RELEASE_READY` computed over a failed pass.

- **AC5.1 — THE FAILURE MATRIX IS ENUMERATED AND EXHAUSTIVE.** Cover at minimum: provider unreachable
  (transport), provider errors (HTTP status), malformed/empty response, checkpoint drift
  (`CheckpointDriftError`), and budget halt. **Derive the enumeration from the typed error surface**
  (`LLMDispatchError` and its subclasses in `argus/audit/ports.py`) so a future error type cannot be
  silently unhandled — do not hand-list five cases and call the set closed.
- **AC5.2 — 🔴 THE ADAPTER CURRENTLY FABRICATES A RECORDING, AND YOU MUST NOT WIRE THAT UP.** Measured:
  `argus/audit/open_llm_adapter.py::_dispatch_httpx` contains, at the anchor
  `if not self._api_base:` with the comment `# Fake/Mock dispatch mode when no live endpoint is
  configured`, a branch that **returns a synthetic `LLMRecording`** — `input_tokens=10`,
  `output_tokens=5`, `credits_used` from `0.000025`, `finish_reason="stop"` — **indistinguishable at
  the port boundary from a real dispatch.** Wiring this into the verdict path would manufacture deep
  claims out of an unconfigured environment: precisely *"a false deep claim"*, which FR36 forbids by
  name. **This story must ensure that branch can never reach the verdict.** §A.5 rules on how, and
  records the alternatives; whichever you choose, a committed gate must prove that an
  **unconfigured** provider produces a **degradation**, never a recording the fold treats as depth.
- **AC5.3 — NEVER AN UNCAUGHT RAISE.** Nothing on this path propagates a bare exception out of the
  pipeline (AR10). A failure becomes a typed error → a recorded finding / coverage downgrade → an
  honest verdict. Prove the no-crash property by driving each enumerated failure through the **real**
  pipeline entry point, not by unit-testing the adapter in isolation.
- **AC5.4 — DOWNGRADE, DON'T DELETE.** A failed deep pass must leave the affected files graded at the
  depth they actually earned (the zero-token grade), never silently dropped from the denominator —
  FR37's *"names what was never examined"* principle applies even though FR37 itself is 12.4's.

### AC6 — The absorbed Story-11.2 question is MEASURED and recorded as a yes or a no

**Given** `DOGFOOD_EXTERNALIZATION_GUARD` (`argus/dogfood/proof_render.py:42`) asserts that *"the
AST-grounding deep-audit seam is NOT wired in, **so** every finding is advisory / verdict-ineligible
(`depth_supported is None`)"*, while the epics frontmatter records the vacuous cartridge emitting a
verdict-**blocking** finding — *"and both may be true if the paths supply depth differently — not
verified"*
**Then** this story **measures**, on the **default** invocation (no LLM, no cartridge harness), whether
`NOT_READY_FOR_RELEASE` is reachable, and **records the result as a yes or a no**, with the mechanism
named and the measurement reproducible.
**And** a measured **"no"** is **reported and escalated** — never a licence to loosen a gate and never
grounds for softening Journey 6.

- **AC6.1 — THE ANSWER, MEASURED AT CREATE-STORY TIME, IS *YES*.** §B.3 records the full reproduction.
  On a synthetic repository, a **default** `python -m argus.cli audit` (no flags, no LLM, no cartridge
  harness) returned `verdict=NOT_READY_FOR_RELEASE blocking_findings=1` and **exit code 2**. The
  mechanism is `argus/detectors/vacuous_test.py` (anchor: `depth = CoverageDepth.AUDITED_SHALLOW if
  corroborated else None`), which emits `RULE_AST` findings with a **non-`None` `depth_supported`**
  whenever the two-fact AST corroboration holds. **You must independently re-derive this**, not
  transcribe it, and land it as a **committed** test so the answer cannot rot.
- **AC6.2 — THE ESCALATION BRANCH THEREFORE DOES NOT FIRE**, and you must say so explicitly rather than
  silently omitting it. If your independent re-derivation returns **no**, the branch **does** fire:
  report it and escalate; do not adjust a gate.
- **AC6.3 — THE GUARD'S SENTENCE IS FALSE IN TWO WAYS AND BOTH ARE FIXED HERE.** (a) Its **causal**
  claim — *seam not wired in, **so** every finding is advisory* — is refuted by AC6.1: advisory-ness
  was never a consequence of the seam being unwired; it is a contingent property of the *Argus dogfood
  corpus*. (b) Its **factual** first clause becomes false the moment AC1 lands. The sentence is pinned
  byte-for-byte by `TC-ArgusAgent-DOGFOOD-001-48` and embedded in two committed artifacts, so it will
  go red — **that red is the guard working.** Repair it by making the sentence **true and precisely
  scoped**; the honesty language (*"NOT presented as externalization or assurance evidence"*, *"does
  NOT clear the >=80%-precision gate"*) must survive intact or be **strengthened**, never softened.
  Confirm against `TC-ArgusAgent-DOGFOOD-001-48`'s own over-claim check.
- **AC6.4** Record the measurement where Story 12.4 will find it: 12.4 must be able to state plainly
  whether a blocking verdict is available on the default path. Leave it in the Dev Agent Record **and**
  in the ledger note, not only in a test docstring.

### AC7 — The delivery is registered honestly, and the registry that would have missed it is fixed

**Given** §0.6 hole 2 — verified by reading `reachability_refutations`' own body — that FR36's current
`not-built` disposition makes **no reachability claim**, so wiring FR36 would leave
`tests/test_v1_commitment_closure.py` asserting *"FR36 is not built"* **after it is built**, with
nothing red
**Then** FR36's disposition is flipped to `wired` with a real module + anchor, and the flip is
**PROVEN** by `TC-ArgusAgent-DOCS-001-34` against the live import closure — not merely edited.

- **AC7.1** The `_Delivery` entry for FR36 names the module and an anchor that resolves, and its note
  states what changed and when. `TC-ArgusAgent-DOCS-001-32`/`-33` (reverse closure, vocabulary, and the
  *"`not-built` names no module"* rule) stay green.
- **AC7.2 — CLOSE THE HOLE, NARROWLY.** Add the missing refutation direction: a `not-built` disposition
  whose owning FR **is** in fact deliverable — i.e. whose named seam modules are reachable from
  `argus.cli` — must be **refuted**. Keep it a pure function driven by `-37`'s synthetic-graph positive
  control, exactly as the two existing directions are, so the new direction is proven to fire **and**
  proven not to fire on honest input. *Scope fence: this closes the direction that this story's own
  delivery would otherwise rot. It is not a licence to re-litigate any other disposition.*
- **AC7.3 — `architecture.md` §Enforcement registers the new rules** in the established form (rule text
  + enforcing module + test ids), as `10.1`/`10.5`/`11.1`/`11.2`/`11.4`/`12.1` did, and
  `TC-ArgusAgent-DOCS-001-41`-style registration assertions cover them. At minimum: (a) *the opt-in
  egress rule* — no egress path is reachable without an explicit invocation-level opt-in, and neither
  an environment variable nor a packaging extra constitutes one; (b) *the deferred-import positive
  control* — an import-absence gate over a deferred path must carry its positive direction.
  **Also correct §E's `deep_audit.py:91` coordinate and its *"behind the opt-in `[llm]` extra"*
  implication** (§0.4 items 1 and 3), striking rather than deleting, per §3.4.
- **AC7.4 — Derived figures follow the artifact, not a memory.** If `git ls-files -- argus` changes,
  the README/CHANGELOG derived module counts move with it (`TC-ArgusAgent-DOCS-001-54`: *the artifact
  is the fact*). Regenerate the three dogfood artifacts through `scripts/regenerate_dogfood_artifacts.py`
  at a provenance sha that `git merge-base --is-ancestor` confirms is an ancestor of `HEAD` (§0.1).
  **No artifact is hand-edited.**
- **AC7.5 — The ledger is updated, append-only.** Rule on every item in §A.8, including the ones ruled
  **OUT**. Prove append-only programmatically (`git diff --numstat <base> HEAD -- deferred-work.md`
  showing zero deletions), as Story 12.1 did — do not eyeball it.

---

## Tasks / Subtasks

- [x] **Task 0 — Baseline, reproduced by execution (AC2.4, AC6.1)** *(no code)*
  - [x] Confirm the tree: `git status --porcelain` shows only the two documentation modifications and
        the untracked host dirs; `git rev-parse HEAD` = `2bea92f`; `git tag -l` empty;
        `origin/master` = `00c8d1b`.
  - [x] Run **`python -m pytest`** (bare — see the `-qq` trap in the AC preamble). Record
        collected/passed/failed/error/skipped. Expect **1418/1418/0/0/0**. Any red is yours.
  - [x] Capture the Task-0 fixture: `python -m argus.cli audit .` verdict line + exit code, and
        `git ls-files -- argus | wc -l`. This is AC2.4's comparison baseline.
  - [x] **Reproduce §0.5 yourself**, in one command, and paste the output. Do not proceed until you
        have seen the false claim with your own eyes.
  - [x] **Reproduce §B.3 yourself** (AC6.1) and record the verdict, `blocking_findings` and the **exit
        code** (measure the exit code without a pipe — `| tail` reports the pipe's status, a trap this
        story hit while being written).

- [x] **Task 1 — Land the §0.5 red FIRST, before any wiring (AC6.3, AC1.1)**
  - [x] Write the assertion that the strengthened depth disclosure appears **only** when a deep pass
        actually produced a recording. **It is red on this tree now.** Record the red with the final
        test code.
  - [x] Rule (§A.4) and implement the remedy: the disclosure's predicate becomes *work performed*,
        not *token requested*. Keep the sentence; fix what it is derived from.
  - [x] Confirm `tests/test_plain_english.py`'s existing two-directional tests still express a true
        property after the change, strengthening rather than narrowing them.

- [x] **Task 2 — The opt-in surface (AC1.1, AC1.2)**
  - [x] Add the flag to `argus/cli.py::build_parser`, `store_true`, **default `False`**.
  - [x] Update the `LOCKED-CLI-CONTRACT-BLOCK` docstring and add the `CONTRACT_REGISTRY` entry with a
        real doc site. Watch `TC-ArgusAgent-CLI-001-35` go red first, then green.
  - [x] Add the CHANGELOG entry. **Check `_NOTE_SECTIONS` ordering rules before adding a release-note
        section** — `tests/test_release_surface_honesty.py` pins presence **and order**, and
        `DF-11-4-D`/`AI-E11-6` are live about that registry (they are targeted at 12.4; §A.8 rules on
        whether you touch it).

- [x] **Task 3 — The wiring (AC1.3, AC1.4, AC3)**
  - [x] Create the deep-pass orchestration module per §A.1 (recommended: `argus/audit/deep_pass.py`).
  - [x] Wire it from the pipeline with a **function-local** import (§A.2 — and read §A.2's proof of
        why this satisfies the static closure while keeping the runtime quarantine green).
  - [x] Prove AC1's reachability by calling the **real** `build_import_graph`/`reachable_from` from
        `tests/test_v1_commitment_closure.py`, not a reimplementation.
  - [x] Land AC3's **positive control** in the same change as the wiring, never after.

- [x] **Task 4 — The default-path fences (AC2.1, AC2.2, AC2.3, AC2.6)**
  - [x] Convert `test_pipeline_is_zero_token`'s hard-coded populations to **derived** ones (both the
        entry points and the forbidden surface). Demonstrate non-vacuity by generating a synthetic
        new `argus/audit/*` module and showing it is covered without a registry edit.
  - [x] Land AC2.3's environment gate, with the variable list derived by `ast` from the adapter's own
        `os.getenv` calls.
  - [x] Land AC2.5's **ordering** proof (disclosure observed at `dispatch` entry, not at end of run).

- [x] **Task 5 — Honest degradation (AC5)**
  - [x] Enumerate the failure matrix from the typed error surface (AC5.1).
  - [x] Rule and implement AC5.2 — the fabricated-recording branch must not reach the verdict.
  - [x] Drive every enumerated failure through the **real pipeline entry point** (AC5.3), asserting a
        recorded finding / coverage downgrade and no uncaught raise.

- [x] **Task 6 — Spend (AC4)**
  - [x] Account deep-pass spend through the existing `budget_governor`/`exhaustion` functions.
  - [x] Prove the halt → `skipped` → downgrade → report path with an injected fake and a biting
        ceiling. Assert **no new** module/threshold/schema version was introduced.

- [x] **Task 7 — Commit the implementation** *(local only — §0.3)*

- [x] **Task 8 — Regenerate and re-commit (AC7.4)**
  - [x] `python scripts/regenerate_dogfood_artifacts.py`. Verify the provenance sha is an ancestor of
        `HEAD` and `git diff --quiet <sha> HEAD -- argus/` is empty.
  - [x] Separate commit, renderer output only, exactly as `e5a8a88` / `93adc94` did. **No hand-edits.**

- [x] **Task 9 — Registration and the ledger (AC6.3, AC6.4, AC7)**
  - [x] Flip FR36's disposition and land AC7.2's narrow refutation direction.
  - [x] Repair `DOGFOOD_EXTERNALIZATION_GUARD` and its pinned test; regenerate the artifacts that
        embed it.
  - [x] `architecture.md` §Enforcement registration + the two §0.4 corrections (struck, not deleted).
  - [x] Ledger rulings per §A.8, append-only, proven by `--numstat`.

- [x] **Task 10 — Final gates, all LOCAL (AC2.4)**
  - [x] `python -m pytest` (bare) · `mypy` · `bandit` · `python -m argus.cli audit .`
  - [x] AC2.4's A/B over a detached pre-story worktree, separating population from behaviour.
  - [x] Confirm the publication fence: `git tag -l` empty, `origin/master` unmoved, no push/dispatch.
  - [x] Write **"CI evidence: NOT ESTABLISHED"**. Do not imply a run.

### Review Findings (code-review, iteration 1, 2026-08-13, reviewer model Sonnet 5)

**Independent re-verification performed, all confirmed on disk, not transcribed from the story:**
`python -m pytest` (bare) → **1439 passed / 0 failed** (141.29s). `python -m mypy argus` →
**Success: no issues found in 74 source files**. `python -m bandit -r argus -q` → **19 Low / 0
Med / 0 High**, and a byte-for-byte diff of the bandit JSON against a `2bea92f` worktree shows the
**identical 19 findings** (same `test_id`/file/line/text) — ZERO new, confirming the dev's claim by
content rather than count. `git ls-files -- argus` = **74**; `8a0bebc` is a confirmed ancestor of
`HEAD`; `git diff --quiet 8a0bebc HEAD -- argus/` empty. `git tag -l` empty; `origin/master` =
`00c8d1b`, unmoved. `git diff --numstat 2bea92f HEAD -- deferred-work.md` → **166 insertions, 0
deletions** (append-only proven programmatically). AC2.4 byte-identity re-derived independently on
a fresh synthetic repo (two clean copies, same `--report-dir` semantics): stdout, stderr, exit code
and every rendered report file were byte-identical between a `2bea92f` worktree and `HEAD`; the one
`.argus/state/*.json` filename difference was fully attributable to the different `--report-dir`
paths used for the two runs, not to any behaviour change.

**The three named judgement calls — adjudicated:**

1. **AC5/AC5.4 tension (re-grade to `audited_shallow` via the existing `grade_entry(claim_present=
   False)`, stays in the denominator).** Correct reading and correctly implemented. Verified by
   reading `argus/ledger/coverage_ledger.py::grade_entry` directly: `proposed_depth=AUDITED_DEEP,
   claim_present=False` returns `AUDITED_SHALLOW` (the pre-existing FR6/FR7 "silence → shallow"
   keystone, reused verbatim, byte-identical to its Story-1.2 shape). `deep_pass.py::_downgrade`
   calls it exactly that way and the entry stays in `regraded` (never dropped). Confirmed live: an
   `argus audit --deep-audit` run with no provider configured against a repo that would otherwise be
   `RELEASE_READY` returns `verdict=INSUFFICIENT_COVERAGE`, `deep_ratio=0`, exit `3` — the downgrade
   demonstrably moves the FR16 table's input, not merely a cosmetic note. No row/threshold/exit-code
   mapping changed (`argus/verdict/verdict_gate.py::evaluate_verdict` diff confirms `deep_pass` is
   carried, never branched on).
2. **Advisory, not verdict-blocking, degradation findings.** Verified `is_verdict_blocking` in
   `argus/verdict/verdict_gate.py` is keyed on `depth_supported is not None`, and
   `deep_pass.py::_degradation_finding` passes `depth_supported=None` — so a degradation finding is
   structurally incapable of blocking. Constructed the exact adversarial repo the brief asked for
   (a repo that would otherwise clear `RELEASE_READY`, `--deep-audit` on, no provider configured —
   the downgrade the ONLY signal): the operator is **not misled** — `Ship-readiness: NOT ASSESSED`,
   `verdict=INSUFFICIENT_COVERAGE`, and both the summary line and the depth-meaning callout state in
   plain language that the deep pass was requested but not completed. This design holds up under
   direct execution, not just under its own tests.
3. **Two production `assert`s removed; `RULE_DEGRADED_DEEP_PASS` → `RULE_DEGRADED_DEEP_READ`.**
   `mypy --strict`-adjacent config still reports zero issues over the module with the asserts gone,
   and the current control flow (`_dispatch_one`'s `isinstance` checks, `_resolve_dispatcher`'s
   explicit `if port is not None / if endpoint is None` chain) does not rely on narrowing that an
   `assert` would have provided — nothing load-bearing found missing. The bandit-diff re-run above
   independently confirms the rename left the security-scan delta at zero.

**One substantive finding, not previously filed — recommend filing before the next round:**

- **[Medium] `argus/audit/deep_pass.py::_dispatch_one` / `argus/audit/open_llm_adapter.py`
  (`_dispatch_litellm`, `_dispatch_httpx`) — the "delivered" branch is provably unreachable through
  the real, unmodified production adapter, and this is undisclosed.** `LLMRecording.structured_output`
  defaults to `()` and **neither** `_dispatch_litellm` nor `_dispatch_httpx` ever populates it — both
  discard the model's actual completion content and only ever construct
  `structured_output=()` (confirmed by reading both methods; independently corroborated by
  `tests/test_open_llm_adapter.py:208`, a pre-existing, unrelated test that already asserts
  `rec.structured_output == ()` for a real dispatch). `deep_pass.py::_dispatch_one` treats
  `not recording.structured_output` as `REASON_EMPTY_RESPONSE` **before** `_claim_is_ast_grounded`
  is ever reached. Consequence, verified by inspection of every code path: **a real, successfully
  configured provider that responds correctly can never produce a `delivered` deep read** — every
  live dispatch, success or failure, degrades to `audited_shallow` via `empty-response`. This is not
  a safety hole (it fails safe — the tool still never fabricates a deep claim; AC5.1's own
  "malformed/empty response" failure mode is exactly what fires) and it does not make any written AC
  false as literally worded, since every test in this story is (correctly, per §0.3) restricted to
  injected fakes and none of the ACs promise real-provider delivery. But it means the entire
  "requested-and-delivered" branch of the new three-state disclosure (`render_depth_meaning`'s
  strengthened sentence) and every `delivered_count > 0` outcome are **reachable only through test
  doubles**, never through the shipped `OpenLLMAdapter` — the positive half of the capability this
  story wires is dead code against the real adapter. This is a pre-existing limitation of
  `open_llm_adapter.py` (unmodified by this diff) made load-bearing for the first time by this
  story's wiring, and — unlike `DF-12-2-A`/`-B`/`-C` — it was not measured or filed. **Recommended
  disposition:** file it as a new `DF-12-2-*` entry (severity 🟡, correctness/completeness) naming
  the gap precisely, and add a test that exercises `_dispatch_httpx`/`_dispatch_litellm` with a
  **mocked** HTTP/litellm response (no live call — the same idiom `tests/test_open_llm_adapter.py`
  already uses) to make the "delivered" path's actual unreachability an explicit, measured,
  committed fact rather than an implicit one a future reader has to re-derive. Does not block this
  story's shipped safety properties; does undercut the story's "wired" framing as a functioning
  capability rather than a reachable-but-inert one.

- **[Low] `argus/audit/deep_pass.py::PROVIDER_ENDPOINT_VARIABLES` (3 vars) duplicates
  `open_llm_adapter.py::OpenLLMAdapter.__init__`'s `_api_base` derivation (`OPENAI_BASE_URL` /
  `OLLAMA_HOST` / `OLLAMA_URL`) instead of importing or deriving it from the adapter.** Verified the
  two lists are currently identical and the duplication is on the *safe* side (a variable added only
  to the adapter's `_api_base` chain would make `resolve_provider_endpoint()` under-report
  configuration, i.e. degrade rather than fabricate) — so this is not a security defect, but it is
  the same "two literals that can drift apart" shape `deep_pass_enabled()`/`with_deep_pass()`
  elsewhere in this same story deliberately collapsed to one. Minor DRY/coupling nit; does not block.

### Review Findings (code-review, iteration 2, 2026-08-13, reviewer model Sonnet 5)

**Scope: narrow confirmation of the fix round, per the orchestrator's instruction. AC5/AC5.4, the
advisory-not-blocking degradation design, the two removed asserts, AC2.4's base byte-identity, the
append-only ledger mechanics, the publication fences and bandit-zero-new were NOT relitigated — they
were confirmed already-adjudicated at iteration 1 and are carried forward, not re-derived here.**

**Independently re-verified on disk, not transcribed:**

- `python -m pytest` (bare) → **1441 passed / 0 failed / 0 error / 0 skipped** (142.36s). Matches the
  claim exactly.
- `python -m mypy argus` → **Success: no issues found in 74 source files.**
- `python -m bandit -r argus -q` → **19 Low / 0 Med / 0 High**, `test_id` set `{B105×6, B603×5,
  B404×4, B607×4}`. Diffed against a **fresh worktree checked out at `2bea92f`** (not the story's own
  prior figures) — the baseline set is byte-for-byte the same 19 findings. Zero new, zero removed,
  confirmed by content, not count.
- `python -m argus.cli audit .` → `verdict=RELEASE_READY deep_ratio=64/177 blocking_findings=0
  assessed_deep_ratio=4/5 scope=application held_out=97`, exit `0`. `git ls-files -- argus` = **74**.
- `git diff --quiet 7074c31 HEAD -- argus/` is **empty**, and `git merge-base --is-ancestor 7074c31
  HEAD` passes — the regeneration commit `58c8f6b` touches only the three dogfood doc artifacts (9
  lines each) and nothing under `argus/`, confirming renderer-output-only.
- `git diff 64164bd 7074c31 --stat` matches the story's own File List for the fix round **exactly**:
  `CHANGELOG.md`, `deferred-work.md` (+84), `argus/audit/deep_pass.py` (docstring-only, verified by
  reading the diff — no logic changed), `tests/test_deep_pass_wiring.py`, and
  `tests/test_v1_commitment_closure.py`. No undisclosed file moved.
- `git diff --numstat 2bea92f HEAD -- deferred-work.md` → **250 insertions, 0 deletions**;
  `git diff --numstat 64164bd HEAD` (this round only) → **84 insertions, 0 deletions**. Append-only
  confirmed programmatically, both cumulative and this-round figures.
- `git tag -l` **empty**; `origin/master` = `00c8d1b`; `git rev-list --count 00c8d1b..HEAD` = **15**.
  Fences intact.
- `_bmad-output/design-artifacts/ArgusAgent/stories/12-1-...md` is git-tracked (confirmed via
  `git log --follow`); `.../12-2-deep-audit-is-wired-opt-in-and-honest.md` is confirmed **untracked**
  (`git ls-files --error-unmatch` fails on it). See the process ruling below.

**The central question adjudicated: is `TC-ArgusAgent-AUDIT-001-73`/`-74`'s discrimination real, or
asserted noise?** Read both tests in full and attacked them with two mutations I constructed myself
(independent of the ones the story names):

1. Edited `open_llm_adapter.py::_dispatch_httpx`'s success branch to carry the response's actual
   `message.content` onto `structured_output` (a different, more realistic mutation than a literal
   revert-and-diff — I built the "real fix" shape by hand). Result: **`-73` fails** at
   `assert recording.structured_output == ()` with the message *"`OpenLLMAdapter` now populates
   `structured_output` — DF-12-2-D IS CLOSED"*, exactly as designed. `-74` stays green. Reverted with
   `git checkout --`; `git status --porcelain -- argus/` clean afterward.
2. Edited `deep_pass.py::_claim_is_ast_grounded` to unconditionally `return False` before its real
   body. Result: **`-74` fails** at `assert outcome.delivered_count == 3` with `delivered_count=0,
   reasons=('claim-ungrounded',)`, exactly as designed. `-73` stays green. Reverted with
   `git checkout --`; `git status --porcelain -- argus/ tests/` clean afterward.

Both directions independently reproduced. **The discrimination is real, not asserted noise.** I also
independently confirmed, by reading `argus/audit/deep_pass.py::_resolve_dispatcher` and
`argus/pipeline.py`, that `-73`'s "no injected port" claim is literal: with `port=None` and an
endpoint configured, `_resolve_dispatcher` constructs the real, unmodified `OpenLLMAdapter` — this is
not a second fake dressed up as the real adapter. And I independently confirmed `.invalid` (RFC 6761)
does not resolve on this host (`socket.gethostbyname` raises `gaierror`), so the "two independent
fences" claim (substituted `httpx.Client` **and** an unresolvable host) is literally true, not
belt-and-suspenders rhetoric.

**Ruling on the DF-12-2-D decision itself.** NOT VACUOUS is the correct call. A vacuous guard is green
when it should be red (over-claims silently); this is the mirror image — the guard is *red* about a
real, disclosed gap, and the only thing unreachable is the favourable branch, which fails safe by
construction (`REASON_EMPTY_RESPONSE` before grounding is even consulted — read directly in
`_dispatch_one`). Read FR36's `_Delivery` note, the `deep_pass.py` module docstring, and the
CHANGELOG's KNOWN LIMITATION paragraph directly: all three are honest, specific, and none over-claims
what the shipped adapter does. A reader of any of the three is not misled.

**Ruling on option (a) (closing the adapter gap) vs option (b) (disclose and file).** Read as an
argument, not transcribed: (1) there genuinely is no claim grammar — `_build_messages` asks for free
prose; (2) `ports.py`'s own `structured_output` contract is claim/locator-shaped strings, never raw
completion bytes (NFR-S1), so populating it with the raw completion is a documented contract
violation, not a fix; (3) the existing `tests/test_open_llm_adapter.py` assertion that
`structured_output == ()` is itself an NFR-S1 security assertion that would need to be re-baselined;
(4) a real claim-grammar response contract is an AR5 `DEEP_PROMPT_TEMPLATE_VERSION` / cache-key
change, not cosmetic; (5) it is unvalidatable under this round's own §0.3 no-live-dispatch fence, and
`deep_audit.py` and `_claim_is_ast_grounded` both already name full claim-grammar grounding as Story
6.2's. This is a substantive engineering argument grounded in a real security contract and a real
provenance mechanism, not scope-avoidance dressed up in prose. **Sound.**

**Ruling on the `-69` `assert … or True` removal.** Confirmed removed; confirmed the property it
named is now proven more strongly by `TC-ArgusAgent-PIPELINE-001-11` in a fresh subprocess per leg
(read directly). Searched `tests/test_deep_pass_wiring.py`, `argus/audit/deep_pass.py`,
`argus/pipeline.py` and `argus/cli.py` for any surviving `or True` / vacuous-assert shape — none found
beyond the explanatory comment recording the removal.

**Ruling on DF-12-2-E (re-ruled, left deferred).** Confirmed by reading both files directly:
`PROVIDER_ENDPOINT_VARIABLES` (`OPENAI_BASE_URL`, `OLLAMA_HOST`, `OLLAMA_URL`) is byte-for-byte the
same set `OpenLLMAdapter.__init__` reads for `_api_base`. The duplication is genuinely on the safe
side (drift would under-report configuration, never fabricate). Re-ruling to leave it deferred rather
than fix it inside this fix round is reasonable risk/benefit; **sound**.

**AC2.4, independently re-derived from scratch (not merely re-read).** Reproduced the dev's own
described method with two clean synthetic repos, first across *different* paths (which reproduced a
single differing `.argus/state/*.json` filename — an artifact of my own methodology, not the code:
confirmed by checking `git status` on the reused directory, which the first run had made "dirty"),
then correctly with a **single identical repo path and a single identical `--report-dir` path**,
sequential clean runs across a fresh `2bea92f` worktree vs `HEAD`. Result: stdout, stderr, exit code
`0`/`0`, the full `--report-dir` tree, **and** the `.argus/` state directory (same 9 files, same
filenames) were byte-identical. **The claimed elimination of iteration 1's one caveat is confirmed.**

**One finding, Low, informational — not blocking.** The Dev Agent Record's fix-round entry states the
mutation-revert sha256 round-trip as `open_llm_adapter.py 4a820e77…97ca, deep_pass.py 6cc79bf3…3ff7`.
I independently recomputed both: `open_llm_adapter.py` matches exactly
(`4a820e77e12d4037a5c6a957d868750a884c2ce5a1cd04aa89dbd311749397ca`). `deep_pass.py` does **not**
match the claimed `6cc79bf3…3ff7` under any variant I tried — raw bytes (`47eadfad9683…8daa2`), the
git blob hash (`b573fe0b7eef…3fb` / content sha256 `531a9c2772f0…33cca`), nor LF/CRLF text-mode
re-encodings. This looks like a transcription error in the completion note (one of two hashes in a
pair, not both, mismatches), not evidence of an unreverted mutation: `git status --porcelain --
argus/` is clean at `HEAD`, the file content matches what `git diff 64164bd 7074c31` shows was
actually committed, and I independently re-verified the *property* the hash was meant to evidence
(clean revert after mutation) via my own two mutation-and-revert cycles above. **Not blocking** —
it is a record-accuracy nit in prose, not a defect in shipped code, a test, or the ledger, and it
does not affect any AC. Recommended for a future pass: correct the `deep_pass.py` hash figure if this
note is ever touched again; not worth reopening a round for on its own.

**Process ruling — the untracked story file.** `_bmad-output/design-artifacts/ArgusAgent/stories/
12-2-deep-audit-is-wired-opt-in-and-honest.md` is untracked in git, while the sibling `12-1-...md` is
tracked and has its own commit history. **Ruling: this is a process note for the Epic-12
retrospective, not a blocker to `done`.** Nothing in this story's ACs, its Definition of Done, or the
project's stated gates (tests, mypy, bandit, `argus audit`, the publication fences, the append-only
ledger) requires the *story markdown file itself* to be git-tracked as a precondition of closing the
story — the artifacts that actually carry the delivered behaviour and its evidence (code, tests,
CHANGELOG.md, architecture.md, deferred-work.md) are all tracked and committed. The inconsistency with
12.1's tracking status is real and should be resolved as a repo-hygiene item — flagged here for the
Epic-12 retrospective — but it does not gate this story's status.

**Disposition: PASS.** No unresolved `decision-needed` or `patch` finding. No unresolved High or
Medium issue. The one Medium from iteration 1 (`DF-12-2-D`) is resolved: filed, disclosed at every
site a reader would be misled, and proven both directions with committed, RED-first tests that I
independently attacked with my own mutations and could not break. The one Low from iteration 1
(`DF-12-2-E`) is soundly re-ruled and left deferred. The one new Low finding this round (the sha256
transcription mismatch) is informational and does not block. Tests/mypy/bandit/self-audit all green
and independently re-run, not carried forward. AC2.4 byte-identity independently re-derived from
scratch. Publication fences intact. **Story 12.2 moves to `done`.**

- [x] [Review][Note] Iteration-2 confirmation: `DF-12-2-D` verified resolved by independent mutation
      attack (two mutations, both directions, self-constructed) — not blocking
      [`tests/test_deep_pass_wiring.py:916-1105`, `argus/audit/deep_pass.py`,
      `argus/audit/open_llm_adapter.py`].
- [x] [Review][Note] Minor record-accuracy nit: the `deep_pass.py` sha256 figure in the Dev Agent
      Record's fix-round entry does not match the file on disk (the `open_llm_adapter.py` figure
      does). Not blocking; correct if this note is touched again — see finding above.
- [x] [Review][Note] Process ruling: the story file's untracked git status is a retrospective item,
      not a `done` blocker — see ruling above.

**Everything else reviewed and found sound:** the CLI flag wiring, the derived
forbidden-surface/entry-point populations (`-12`'s generated-module non-vacuity proof re-read and
verified), the AC2.3 environment gate (matches the adapter's real `_api_base`/`_api_key`/`_model`
sources exactly), the AC2.5 ordering proof (genuinely observes at `dispatch()` entry, not
end-of-run), the AC3 positive control (both directions, fresh subprocess each), the FR36
`not_built_refutations` closure (fires on the live registry, both directions tested on a synthetic
graph), the `DOGFOOD_EXTERNALIZATION_GUARD` repair (old sentence's causal claim genuinely refuted by
a committed measurement, honesty clauses asserted separately from the byte pin), and the ledger
rulings (`DF-12-1-A` re-recorded with a measured reason, `DF-12-1-E`/`DF-12-1-D` correctly recorded
as non-firing-but-heeded, `DF-10-2-A` escalated rather than silently carried a fourth time). No
vacuous guard found among the ones this story added. No engineering-principle violation (SOLID/DRY/
YAGNI/coupling) found beyond the Low item above. No egress observed at any point during this
review's own executions.

**Disposition:** no `decision-needed` or `patch` item blocks this story's core delivery; the one
Medium finding is a disclosure/filing gap on a pre-existing adapter limitation, not a defect in the
code this story wrote. Recommended action for the next round: file `DF-12-2-D` per the finding
above (and add the mocked-adapter test), then return to `done`. Everything else may stay as committed.

- [x] [Review][Patch] File `DF-12-2-D` (the `structured_output` real-adapter gap) in
      `deferred-work.md` and add a mocked-transport test proving/documenting the "delivered" branch's
      current unreachability via the real `OpenLLMAdapter` — see finding above
      [`argus/audit/deep_pass.py`, `argus/audit/open_llm_adapter.py`].
      **RESOLVED (fix round, 2026-08-13, `7074c31`).** Option **(b)** taken, with (a) measured and
      rejected on evidence rather than assumption. `DF-12-2-D` filed with an owner and a target;
      `TC-ArgusAgent-AUDIT-001-73` (the gap, over a mocked transport) and `TC-ArgusAgent-AUDIT-001-74`
      (its positive control — the delivered branch DOES work when `structured_output` is populated)
      both landed RED-first with the final code; the honesty made explicit in the three places a
      reader would otherwise be misled. Full reasoning in *Fix round — iteration 1* below.
- [x] [Review][Defer] `PROVIDER_ENDPOINT_VARIABLES` duplicates the adapter's `_api_base` derivation —
      deferred as `DF-12-2-E` in `deferred-work.md`, pre-existing shape, Low severity, not blocking
      [`argus/audit/deep_pass.py:114`].

---

## §A. What to build — the rulings

### A.0 — The single sentence that decides this story's shape

**The opt-in must be a per-invocation operator act, and everything else must be derived from it.** Not
an extra (measured: the base install already contains a complete egress path — §0.4 item 3), not an
environment variable (measured: the adapter already reads six of them — AC2.3), not a bare CSV token
(measured: it already exists and already lies — §0.5). Every other ruling below follows from this one.

### A.1 — Where the wiring lives: a measured recommendation, not a prescription

**Recommended: a new module `argus/audit/deep_pass.py`.** Reasoning, in the order it should be
re-checked rather than trusted:

1. **`pipeline.py` has room but should not be the home.** 944 lines, 256 free. It *could* hold the
   orchestration. But `DF-12-1-E` is filed exactly against *"the next story that adds a fourth
   `argus/pipeline*.py` module (12.2 is the likely trigger)"* and notes there is **no layering guard**
   over the family. Putting a provider-adjacent concern in a fourth `pipeline*.py` sibling triggers a
   filed defect you would then be expected to fix, in a story that already has seven ACs.
2. **`argus/audit/` is where the quarantine already reasons.** The whole determinism-quarantine
   vocabulary — pure seam, allowed importer, forbidden prefixes — is written in terms of
   `argus.audit.*`. A new module there is **inside** the fence AC2.2 is widening, rather than a new
   place the fence has to learn about.
3. **It keeps `pipeline.py`'s delta to a handful of lines** — a call site and a deferred import —
   which is what makes AC2.4's byte-identity argument cheap to make and easy to believe.

**You may overrule this with measured reasons, exactly as Story 12.1 overruled its own §A.1
recommendation** (SA.1 recommended extracting the resume family; the dev measured an import cycle and
extracted the derivation stages instead, and that was correct). What you may **not** do is put the
concrete adapter behind a module-level import on the default path (AC1.3), or create a fourth
`argus/pipeline*.py` without also ruling on `DF-12-1-E`.

### A.2 — The deferred import: why it is right, and why it is dangerous

**The property you need looks contradictory and is not.** You need:

- `argus.audit.deep_audit` to be in the **static** import closure from `argus.cli` (AC1 / `DOCS-001-34`
  proves `wired` that way), **and**
- `argus.audit.deep_audit` to be **absent from `sys.modules`** after a default run (AC2.1 / NFR-S6 /
  `PIPELINE-001-10`).

**A function-local import satisfies both.** This was **verified by execution** while writing this
story, using the *real* `build_import_graph` and `reachable_from` imported from
`tests/test_v1_commitment_closure.py`, run against a synthetic package whose only edge was an import
nested inside an `if` inside a function:

```
graph:  {'pkg.entry': ['pkg', 'pkg.sub', 'pkg.sub.deep'], ...}
reachable from pkg.entry: ['pkg', 'pkg.entry', 'pkg.sub', 'pkg.sub.deep']
```

The static walk uses `ast.walk`, which descends into function bodies, so **the deferred import is
statically visible while being runtime-inert**. Re-run this yourself before relying on it.

**The danger, stated so you cannot walk into it.** The moment you adopt a deferred import,
`TC-ArgusAgent-PIPELINE-001-10` becomes green **for a reason that has nothing to do with safety** — it
is green because the code never ran. That is a vacuous guard created by this story's own design, which
is why **AC3's positive control is not optional**. State this trade-off in your notes explicitly; do not
present the quarantine's continued green as evidence on its own.

### A.3 — The flag: spelling, shape, and what happens to `--passes …,deep`

**Ruling (mine, recorded — §7 authority):**

- **Spelling.** A dedicated `store_true` flag on the `audit` subcommand. `--deep-audit` reads best
  against the FR's own language (*"an LLM-backed deep-audit pass"*) and against the module name; you
  may choose differently with a stated reason, but it must be a **flag**, not a value, not a token.
- **Why not reuse `--passes …,deep` as the opt-in** — even though AR7 says *reuse, never fork*, and the
  `deep` token already exists (§0.4 item 7)? Three measured reasons. (i) **It already means something
  else and lies about it** (§0.5); making the same spelling *also* the egress consent means the fix and
  the feature collide in one token. (ii) `--passes` is an **exact selection**, so `--passes deep` alone
  silently disables every deterministic pass — an egress opt-in that quietly turns off the safety
  passes is a footgun on the one flag that must be unambiguous. (iii) NFR-S6 requires a **committed
  gate** that egress is unreachable without opt-in; a free-form CSV that accepts unknown tokens is a
  poor subject for such a gate.
- **What is reused, so this is not a fork.** The **internal** `deep` pass token stays: the flag *sets*
  it, `LLM_DEEP_PASSES` still recognises it, and `render_depth_meaning` still branches on the pass set.
  One vocabulary, one disclosure function, one pass-plumbing path. The flag is a new *entrance*, not a
  new *mechanism*.
- **Where best practice and project standard were weighed.** General practice would say "don't add a
  flag when a value channel exists". This project's explicit standard — the LOCKED invocation contract
  (§A of `architecture.md`, FR30, `tests/test_invocation_contract.py`) — makes adding a *specified,
  registered* flag the sanctioned way to add an operator-facing capability, and makes an *unspecified
  accepted token* the named defect (`DF-AUD-APAA-E`). **Project standard wins**, and it happens to
  agree with the safety argument.

**What must happen to the old spelling.** `--passes …,deep` must stop producing the strengthened
disclosure without a real dispatch. **Ruled IN** (Task 1) because it is this story's own requirement —
FR36's *"never produces a false deep claim"* — not a drive-by fix.

**Ruled OUT, with reasons: making `--passes` reject unknown tokens.** That is the more general fix and
it is tempting. It is **out of scope** because (a) it changes the behaviour of a LOCKED flag for every
pass, not just `deep`; (b) `.github/workflows/argus-student-audit.yml` depends on `--passes`, and this
story has **no CI evidence** (§0.2) with which to verify a workflow-affecting change; (c) the narrower
fix in §A.4 removes the false claim completely, so strict validation would be defence-in-depth, not the
remedy. **File it** (§A.8).

### A.4 — The disclosure predicate: derive it from work performed

`render_depth_meaning(enabled_passes)` currently answers *"was depth requested?"* and prints a sentence
that answers *"was depth delivered?"*. Those differ, and §0.5 is the gap.

**Ruling: the strengthened sentence must be derived from the run's actual outcome** — that a deep pass
executed and produced at least one recording that reached the fold — in the same spirit as
`TC-ArgusAgent-DOCS-001-54`'s *the artifact is the fact* and Story 12.1's *the label tells the truth
rather than pinning the enumeration*. Keep the function pure; change **what the caller passes it**, or
give it the outcome rather than the request. Do not delete either sentence: there are now **three**
honest states (not requested; requested and delivered; **requested and not delivered**), and the third
is the one FR36's NFR-R1 clause and AC5 care about most.

**Fence.** This is a change to a *depth-honesty disclosure*, which is squarely FR36's *"never produces
a false deep claim"*. It is **not** a licence to restructure report content generally — FR37 and the
report's next-action vocabulary are **Story 12.4's**, and `AC5` of Story 12.1 already fenced report
content away from restructuring stories. Touch this sentence and its predicate; leave the rest.

### A.5 — The fabricated recording (AC5.2): the options, and the property that must hold

The property is non-negotiable: **an unconfigured provider must never yield something the fold treats
as depth.** The mechanism is yours; the honest options, with their costs:

1. **Refuse to construct.** The deep pass validates its provider configuration *before* dispatch and,
   finding none, degrades immediately (records a finding, downgrades coverage) without ever calling
   `dispatch`. *Cheapest, most local, does not touch the adapter, and composes with AC2.5's
   before-the-first-byte disclosure.* **Recommended.**
2. **Fix the adapter.** Make `_dispatch_httpx` raise `LLMDispatchError` instead of fabricating.
   *Strictly more correct and removes the hazard for every future caller — but it changes a module with
   its own committed tests (`tests/test_open_llm_adapter.py`, `tests/test_minions_llm_adapter.py`) that
   assert the mock-mode behaviour, so it is a behaviour change with a test-suite blast radius inside a
   story that already carries seven ACs.*
3. **Both**, with (2) fenced to a follow-up.

**If you choose (1), you MUST file the residual** — the adapter still fabricates for any other caller —
as a `DF-12-2-*` entry with an owner and a target story. Do not leave the hazard undisclosed because
your own path avoids it. **That is the disclosure discipline this project runs on.**

### A.6 — The wiring map: the exact seams, so you do not invent a parallel one

**🔴 DO NOT ADD A FIELD TO `AuditRequest`. The channel already exists.** Measured:
`argus/models.py:108` already carries `enabled_passes: tuple[str, ...]` with the default
`("coverage", "vacuous", "security", "orphan", "prosecutor")`, and `argus/cli.py:349-363` already
populates it. `AuditRequest` is `frozen=True, extra="forbid"` with a localized
`AUDIT_REQUEST_SCHEMA_VERSION = "1"` and an **additive-only NFR-M2 discipline** — adding a field means
a schema decision, a round-trip byte-identity question, and a provenance change, **all of which you can
avoid entirely**. The flag's job is to put the existing `deep` token into `enabled_passes`. That is one
vocabulary end to end: flag → `enabled_passes` → `LLM_DEEP_PASSES` → `render_depth_meaning`.

*Bonus property you get for free:* `enabled_passes` is already serialized into run provenance
(`AuditRequest.to_payload`, `argus/models.py:166`), so **the run record already states whether the deep
pass was requested**, with no new field and no schema bump. A default run's payload is unchanged
because the token is absent.

| Seam | Coordinate (anchor, not line) | What you do with it |
|---|---|---|
| Flag definition | `argus/cli.py::build_parser`, the `audit` subparser | Add `store_true`, default `False` |
| Flag → pass set | `argus/cli.py::_resolve_passes` (anchor: `_split_csv(args.passes, _ALL_PASSES)`) | Add the `deep` token when the flag is set; **compose in one direction** — `--skip-pass` must still be able to subtract it |
| Request contract | `argus/models.py::AuditRequest.enabled_passes` | **Unchanged.** No new field |
| Pipeline branch | `argus/pipeline.py`, the existing `if "prosecutor" in request.enabled_passes:` (anchor at ~`:427`) is the precedent for how a pass is gated | Follow that shape; deferred import per §A.2 |
| The port | `argus/audit/ports.py::LLMDispatchPort` | The only LLM seam. Inject it; never construct a concrete adapter in the pipeline |
| Spend | `argus/cost/exhaustion.py::project_halt_point` / `build_halt_report`; `argus/cost/budget_governor.py::account_spend` | Reuse; `argus/pipeline_stages.py::_build_cost_units` is the existing call pattern |
| Disclosure | `argus/reports/plain_english.py::render_depth_meaning` / `LLM_DEEP_PASSES` | Fix the predicate (§A.4); keep the function pure |

### A.7 — Where each gate lands (extend, do not fork — AI-E2-5 / AI-E3-6)

| AC | Home | Note |
|---|---|---|
| AC1.1/AC1.2 | `tests/test_invocation_contract.py` (`CONTRACT_REGISTRY`) + `tests/test_cli_flag_contract.py` for behaviour | The registry entry is mandatory; the *behavioural* AC belongs in the flag-contract file, following `--strict`'s `-46`/`-47` precedent |
| AC1's reachability | `tests/test_v1_commitment_closure.py` | Use its **own** `build_import_graph`/`reachable_from`; do not reimplement |
| AC2.1/2.2/2.3/2.6, AC3 | `tests/test_no_web_imports.py` | **Extend** the existing quarantine. Derive both populations (AC2.2) |
| AC2.4 | A/B over a detached pre-story worktree | Method: Story 12.1 AC5 |
| AC2.5 (ordering) | With the wiring's own tests | Needs a fake port that observes the disclosure stream **at `dispatch` entry** |
| AC4, AC5 | With the wiring's own tests, driven through the **real pipeline entry point** | Not adapter unit tests (AC5.3) |
| AC6 | A dedicated file is appropriate (precedent: `tests/test_module_size_ceiling.py`, `tests/test_pipeline_split_surface.py`) | The measurement must be **committed**, not only recorded in prose |
| AC6.3 | `tests/test_dogfood_module_split.py` (`TC-ArgusAgent-DOGFOOD-001-48`) | Repair the pinned text; keep the over-claim check |
| AC7.1/7.2 | `tests/test_v1_commitment_closure.py` | Mind `DF-12-1-B` — the file is already 108 over the cap |
| AC7.3 | `architecture.md` §Enforcement + its registration assertion | Established form: rule text + enforcing module + test ids |

### A.8 — Ledger rulings required of this story (AC7.5)

Rule on each **in the story file and in `deferred-work.md`**, including the ones ruled OUT:

| Item | Its stated target | Ruling for 12.2 |
|---|---|---|
| **`DF-12-1-A`** — `tests/test_pipeline_signature_demo.py` 1326 lines, 126 over NFR-M1; exemption registered in `test_module_size_ceiling.py::_EXEMPT_BY_DESIGN` | **`12-2-…`, i.e. THIS story** — *"the next story to edit the pipeline surface this file demonstrates"* | **RULE IT EXPLICITLY.** The trigger is *"edits the pipeline surface"*. If your wiring lands in `argus/audit/deep_pass.py` with a small `pipeline.py` call site, decide honestly whether that fires the trigger. **Either close it** (split the file) **or re-record it** with a measured reason and a live target — what you may not do is leave the only ledger item that names this story unmentioned. Note the registry **shrinks**: `TC-ArgusAgent-MAINT-001-04` fails if the entry names a file that is gone or no longer over the cap. |
| **`DF-12-1-E`** — three `argus/pipeline*.py` siblings, no layering guard | `NONE` — *"the next story that adds a fourth `argus/pipeline*.py` module (12.2 is the likely trigger)"* | **Fires only if you create a fourth `pipeline*.py`.** §A.1 recommends you do not. If you follow §A.1, record that the trigger **did not fire** and why; if you overrule §A.1, the trigger fires and you own it. |
| **`DF-12-1-D`** — the NFR-M1 sweep reads the git INDEX, so an unstaged module escapes it | `NONE` — *"the next story that edits `tests/test_module_size_ceiling.py`"* | **Conditional.** Fires only if you edit that file. Likely you will not. Say so. **But heed the hazard directly**: it *"bit during 12.1's own implementation"*, and this story creates a new `argus/**` module. **Stage your new module early** or the sweep will not see it. |
| **`DF-10-2-A`** — C/C++/Ruby/Rust ground but extract zero definitions | `NONE` — **unowned for a third consecutive epic**; `AI-E11-7` wants a **dated operator decision** (type (H)) | **RULED OUT of 12.2, and flagged for the retrospective.** No relationship to the LLM seam, egress, opt-in or spend. It is a **governance decision outside a dev agent's authority** (`AI-E11-7`'s own words: *"a fix is probably not needed … what is needed is a dated decision"*). This is now the **third** story to carry it forward without a home. **Escalate it in the Epic-12 retrospective as an operator-level item, and do not fold it in silently.** |
| **`DF-11-2-A` / `-B`**, **SD-4's four convergent filings** | **12.5** | **OUT** — grammar/test-name-convention surface, not this story's. Confirm untouched. |
| **`DF-8-3-A`**, **`DF-11-4-D` / `AI-E11-6`** | **12.4** | **OUT** — both were deliberately re-recorded to 12.4 by Story 12.1 with measured reasons. *Caveat:* if you add a release-note section (Task 2), you touch `_NOTE_SECTIONS`, which is `DF-11-4-D`'s subject. **Adding a section is not the same as re-opening the impact-rank question** — add it in registry order, do not re-litigate the rank, and say that is what you did. |
| **New: the `--passes` validation gap** (§A.3, ruled OUT) | — | **FILE IT** as `DF-12-2-*`: unknown `--passes` tokens are silently accepted; the narrow fix landed here, strict validation deferred with the workflow-dependency reason. |
| **New: the adapter's fabricated recording** (§A.5, if you choose option 1) | — | **FILE IT** as `DF-12-2-*` with an owner and a target story. |

---

## §B. Measured evidence

### B.0 — Baseline, 2026-08-12, `HEAD` = `2bea92f`, LOCAL Windows / CPython 3.11.15

| Measurement | Value | How |
|---|---|---|
| Full suite | **1418 collected / 1418 passed / 0 failed / 0 error / 0 skipped** | `python -m pytest`, run to completion twice |
| Tracked `argus` files | **73** | `git ls-files -- argus \| wc -l` |
| `argus/pipeline.py` | **944** lines (256 under the 1200 cap) | `wc -l` |
| `argus/pipeline_stages.py` / `argus/cli.py` | **512** / **522** | `wc -l` |
| `git status --porcelain` (tracked) | **2 modified, both documentation** (`sprint-status.yaml`, the 12.1 story file) | — |
| `git tag -l` | **empty** | — |
| `origin/master` | **`00c8d1b`**, unmoved; `HEAD` 11 ahead | — |
| Dogfood currency | `c4bd769` **is** an ancestor of `HEAD`; `git diff --quiet c4bd769 HEAD -- argus/` **empty** | the AC3-of-12.1 guard is **green now** |

> ⚠️ **Trap, hit while measuring this.** `pytest.ini`'s `addopts` already contains `-q`. Adding your
> own `-q` yields `-qq`, which **suppresses the summary line**: you get progress dots, a clean exit
> code, and **no counts**. Run `python -m pytest` bare.

### B.1 — Premise re-measurement (AI-E10-3), by execution, not by reading

| # | Inherited premise | Source | Verdict | Measured |
|---|---|---|---|---|
| 1 | `DeepAuditSeam` at `deep_audit.py:**91**` | epics.md; architecture §E | **STALE** | `class DeepAuditSeam:` is at **line 98**; file is 112 lines |
| 2 | Seam *"referenced only from `argus/audit/*` and `argus/dogfood/proof_run.py`"* | epics.md; architecture §E | **STALE (overstated)** | **Zero** production callers. `DeepAuditSeam` appears in 3 places total: its `class`, its `__all__`, and `tests/test_llm_dispatch_port.py`. `proof_run.py` mentions it **only in a docstring** (line 80) and does not import it |
| 3 | Live dispatch is *"behind the opt-in `[llm]` extra"* | architecture §E | **STALE / MISLEADING** | `[llm]` = **litellm only**; **`httpx` is a BASE dependency**; `_dispatch_httpx` is a complete egress path in a no-extras install |
| 4 | Seam *"never referenced from `argus/pipeline.py`"* | epics.md | **HELD** | no `deep_audit`/`DeepAuditSeam`/`LLMDispatch` reference in `pipeline.py` or `pipeline_stages.py` |
| 5 | Story 6.1's determinism quarantine exists and passes | epics.md; architecture §E | **HELD** (with a caveat) | `TC-ArgusAgent-AUDIT-001-10` + `PIPELINE-001-10` in `tests/test_no_web_imports.py`, green. **Caveat: §0.6 hole 1** |
| 6 | FR21/FR22 spend machinery exists and is reusable | PRD; architecture §E | **HELD** | `budget_governor` + `exhaustion`, already used by `pipeline_stages.py` |
| 7 | §E's *"for free"* fallback/circuit-breaker rationale died with Story 9.1 | architecture §E | **HELD** — and the architecture **already says so**, naming Story 12.2's NFR-R1 ACs as the replacement | quoted in AC5 |
| 8 | `pipeline.py` is under the cap with room for this story | Story 12.1 | **HELD** | 944 / 1200 |
| 9 | Suite fully green, no sanctioned red | Story 12.1 | **HELD** | 1418/1418/0/0/0 |

**Two of the three stale premises are the *same defect class this story is about*:** a document
describing an egress path as gated by something that does not gate it, and a coordinate two documents
agree on that neither checked.

### B.2 — 🔴 The live false deep claim (§0.5), reproduced

Synthetic repo: one application module (`app/service.py`, three real definitions) and one test file.

```
$ python -m argus.cli audit <repo> --passes coverage,deep
  - What `audited_deep` means in this run: a deep read was dispatched for the file and
    its claim was validated against the repository AST.
verdict=RELEASE_READY deep_ratio=1/2 blocking_findings=0 assessed_deep_ratio=1 scope=application held_out=1
```

Mechanism: `argus/cli.py:334` `_split_csv(args.passes, _ALL_PASSES)` does **not** validate against
`_ALL_PASSES` (`argus/cli.py:138`, which is the *default* set) → the token `deep` reaches
`enabled_passes` → `argus/reports/plain_english.py:129` flips the disclosure. **Nothing dispatched.**

### B.3 — 🔴 AC6 ANSWERED: `NOT_READY_FOR_RELEASE` **IS** reachable on the default invocation

Same synthetic repo, with the test file rewritten so the `vacuous_test` detector's **two-fact AST
corroboration** holds: the test reaches a candidate SUT (a non-assertion, non-mock call) **and** its
assertions are mock-dominated (`mock_ratio > 1/2` with `mock_sites >= 1` and `assertion_sites >= 1`).

```
$ python -m argus.cli audit <repo>          # NO flags. No LLM. No cartridge harness.
Ship-readiness: BLOCKED - 1 verdict-blocking finding(s) must be resolved.
  - Verdict-blocking findings: 1
verdict=NOT_READY_FOR_RELEASE deep_ratio=1/2 blocking_findings=1 assessed_deep_ratio=1 scope=application held_out=1
exit code = 2
```

**Answer: YES.** The mechanism is `argus/detectors/vacuous_test.py` (anchor: `depth =
CoverageDepth.AUDITED_SHALLOW if corroborated else None`), which emits a `RULE_AST` finding carrying a
**non-`None` `depth_supported`** — the FR16 row-2 eligibility predicate — with **no LLM involved at
all**. The `prosecutor` promotion path (`argus/verdict/prosecutor.py`) is a *second* producer but
requires explicit sign-offs; the vacuous-AST path requires nothing.

**Therefore the escalation branch of AC6 does not fire**, and `DOGFOOD_EXTERNALIZATION_GUARD`'s causal
claim — *"the seam is NOT wired in, **so** every finding is advisory"* — is **refuted**: advisory-ness
is a contingent property of the Argus dogfood corpus, not a consequence of the seam being unwired.
*Both halves of the epics-frontmatter tension were indeed simultaneously true, and the reason is now
measured rather than hypothesised.*

**Two traps this measurement hit — do not repeat them.** (1) A first attempt used one `MagicMock()` and
one SUT call: `mock_ratio` was exactly `1/2`, and the ceiling is strict `>`, so nothing fired. The
thresholds are `ASSERTION_DENSITY_FLOOR = Fraction(1, 4)` (strict `<`) and `MOCK_RATIO_CEILING =
Fraction(1, 2)` (strict `>`). (2) The exit code was first read through `| tail`, which reports the
**pipe's** status (`0`), not the audit's. Measure it with no pipe.

### B.4 — The static closure sees a deferred import (the keystone for §A.2)

Run with the **real** `build_import_graph` / `reachable_from` imported from
`tests/test_v1_commitment_closure.py`, against a synthetic package whose only edge is
`from pkg.sub.deep import Seam` nested inside an `if` inside a function:

```
graph: {'pkg': [], 'pkg.entry': ['pkg', 'pkg.sub', 'pkg.sub.deep'], 'pkg.sub': [], 'pkg.sub.deep': []}
reachable from pkg.entry: ['pkg', 'pkg.entry', 'pkg.sub', 'pkg.sub.deep']
```

**A deferred import is statically visible and runtime-inert.** That is what lets AC1 and AC2.1 both
hold — and exactly why AC3's positive control exists.

### B.5 — The ambient-environment egress hazard (AC2.3)

```
$ OLLAMA_HOST=http://127.0.0.1:99999 python -c "from argus.audit.open_llm_adapter import OpenLLMAdapter; \
    a = OpenLLMAdapter(provider_id='probe', use_litellm=False); print(a._api_base, a._api_key, a._model)"
http://127.0.0.1:99999 mock-key gpt-4o-mini
```

The adapter absorbs the ambient environment on construction and defaults the API key to the literal
`"mock-key"`. **Constructing the adapter is therefore already a configuration decision made by the
environment.** AC2.3 exists because of this measurement.

### B.6 — The precedent you are following

- **Story 12.1** — the two-commit sequence (implement → commit → regenerate through renderers →
  commit), the RED-first-with-final-code discipline, generated adversarial variants with counted
  populations, ledger rulings **including the ones ruled OUT**, and the git-blob-vs-working-tree trap.
- **Story 10.3** — the LOCKED invocation contract and how a flag is added *specifiably*
  (`CONTRACT_REGISTRY` + a doc site + a CHANGELOG entry).
- **Story 10.5** — the delivery-disposition closure you must flip and narrowly extend (AC7).
- **Story 6.1** — the `FakeDispatch` zero-token idiom (`tests/test_llm_dispatch_port.py`) that every
  test in this story uses instead of a live provider.

---

## §C. Sequencing (why the order in Tasks is not negotiable)

1. **Task 0 before everything.** The §0.5 and §B.3 reproductions are premises three ACs rest on. If
   either fails to reproduce, **stop and re-derive** — do not build on this story's word.
2. **Task 1 (the §0.5 red) before Task 3 (the wiring).** The false claim is red on this tree *now*, for
   free. Wire the seam first and you lose the clean RED-first demonstration forever, and you will be
   asserting a fix against code you just changed.
3. **Task 4's derived populations before or with Task 3's wiring.** If you wire first, the window in
   which a new `argus/audit/*` module is uncovered by the forbidden set is a window in which the gate
   was structurally blind — and reviewers will (correctly) ask which order it happened in.
4. **AC3's positive control lands in the same change as the wiring**, never after. A deferred-import
   design without its positive control is the vacuous guard this story is chartered to avoid creating.
5. **Task 7 (commit) before Task 8 (regenerate).** The renderers stamp `git rev-parse HEAD`; the
   provenance sha must be an **ancestor of HEAD** and must **contain** what the artifacts describe.
   This is the operator-ruled sequence (§0.1), and `e5a8a88` / `93adc94` are the precedents.
6. **Task 9's FR36 flip after the wiring exists.** `TC-ArgusAgent-DOCS-001-34` proves `wired` against
   the live closure; flipping the disposition first makes it red for the right reason at the wrong time.
7. **Task 10 last, on the final tree.** Do not carry forward a gate result from an earlier round.

---

## §D. Fences — what you must not touch

- **No publication.** No push, tag, release, `workflow_dispatch`, index upload (§0.3).
- **No live dispatch, ever, for any reason** (§0.3, second half). Injected fakes only.
- **No hand-edited dogfood artifact.** Regeneration through `scripts/regenerate_dogfood_artifacts.py`
  only (§0.1).
- **No new cost-governance mechanism** — no new module, ceiling, threshold, schema version or numeric
  default (AC4.1, AR7/§3.3).
- **No FR16 decision-table change.** No row, threshold, boundary or exit-code mapping moves. If the
  deep pass appears to require one, **HALT** (§E).
- **No provider import in the pure path** (AC3.2).
- **No network listener, no bound port, no web stack** (AC2.6).
- **No report-content restructuring beyond the depth-honesty disclosure** — FR37 and the next-action
  vocabulary are **Story 12.4's** (§A.4 fence).
- **No weakening.** No assertion deleted, loosened, skipped, `xfail`-ed or re-baselined. If a guard
  goes red, it is telling you something — the honesty language in
  `DOGFOOD_EXTERNALIZATION_GUARD` must survive intact or be strengthened, never softened (AC6.3).
- **Do not re-take AI-E10-1's risk acceptance** (§0.2). Carry it; label figures LOCAL.
- **Do not touch `minions_core/apaa/`** (RS-1).

---

## §E. HALT conditions

Stop and escalate rather than deciding, if any of these arise:

1. **Any AC appears to require a live dispatch** to a third-party provider to verify. There is no
   sanctioned way to take that step in this story (§0.3).
2. **Any AC appears to require moving a provider import into the pure path**, or otherwise changing the
   determinism quarantine's *intent* rather than its *population* (AC3.2).
3. **Any AC appears to require an FR16 decision-table change**, a new verdict, or a new exit code.
4. **Your independent re-derivation of §B.3 returns "no"** — `NOT_READY_FOR_RELEASE` unreachable on the
   default path. That is AC6.2's escalation branch: **report and escalate**, do not adjust a gate to
   make the story finishable.
5. **The default-run byte-identity of AC2.4 cannot be established** for a reason you cannot attribute
   to population arithmetic. A behaviour change on the default path contradicts a stated project goal
   (NFR-S6, FR36 *"off by default, always"*).
6. **`DF-12-1-A` cannot be honestly closed or re-recorded** — e.g. you conclude the exemption should be
   removed but the split is larger than this story can carry. Say so; do not let the entry lapse.
7. **A guard must be weakened to pass.** Always a halt, never a judgement call.

---

## Dev Notes

### Testing standards

- **Verification areas and ids.** Continue the existing indexes rather than minting new ones without
  reason: `TC-ArgusAgent-AUDIT-001-NN` for the seam/port, `TC-ArgusAgent-PIPELINE-001-NN` /
  `-002-NN` for pipeline properties, `TC-ArgusAgent-CLI-001-NN` for the invocation surface,
  `TC-ArgusAgent-DOCS-001-NN` for the closure/registration guards, `TC-ArgusAgent-DOGFOOD-001-NN` for
  the artifacts. Read the neighbouring file's header before choosing a number.
- **Red-first with the FINAL committed code.** A reconstruction of a red is not a red. Story 12.1's
  review re-derived every such claim independently; expect the same.
- **Generated adversarial variants, with counts.** Never a hand-listed sample. `TC-ArgusAgent-MAINT-001-05`
  (generates an over-cap variant from every one of the live population) and the 12.1 `-16` mutation
  generator (`4n-1` mutants from the live surface) are the house patterns.
- **Both directions.** Every closure asserts the true input is **accepted** before the mutants are
  **rejected**; a guard that only ever rejects cannot be shown to be reachable.
- **Fail, never skip.** A guard that cannot reach its corpus must be RED, not silently green
  (the `_read` idiom in `tests/test_v1_commitment_closure.py`).
- **Subprocess isolation for import gates** (`tests/test_no_web_imports.py`'s idiom) — a fresh
  interpreter per assertion, so an unrelated earlier import cannot mask a real leak.
- **Zero tokens.** `FakeDispatch`-style injected ports (`tests/test_llm_dispatch_port.py`). NFR-D2 is a
  requirement, not a convenience.

### External / latest-technology research: performed, and what it found

Deliberately **bounded**. The story adds no dependency and pins no new version, so version research
would be theatre. Two things were checked because they are load-bearing:

- **`httpx` is already a base dependency** (`pyproject.toml`), so the egress capability is present in
  every install — this is a *packaging fact of this tree*, established by reading the manifest, not a
  question about the upstream library.
- **`litellm` is the only member of the `[llm]` extra**, so the extra gates the *multi-provider
  convenience layer*, not egress. This is what makes §0.4 item 3 a correction rather than a nitpick.

No new library, version bound or API surface is introduced by this story. If you conclude one is
required, that is a scope change — **HALT** (§E).

### Project structure

- `argus/audit/` — the LLM seam. `ports.py` (pure Protocol + frozen DTOs), `deep_audit.py` (the pure
  seam, **zero production callers today**), `grounding.py` (pure FR7 validator, *allowed* on the
  pipeline path), `open_llm_adapter.py` (the **impure** live dispatch), `minions_llm_adapter.py` (a
  backward-compatible wrapper delegating to `OpenLLMAdapter`).
- `argus/pipeline.py` (944) — orchestration + typed contracts. `argus/pipeline_stages.py` (512) —
  derivation stages (Story 12.1). `argus/pipeline_persist.py` (268) — `.argus/` writes. **The layering
  is documented in three docstrings and enforced by nothing** (`DF-12-1-E`).
- `argus/cost/` — FR21/FR22, complete and reusable as-is.
- `argus/reports/plain_english.py` — `LLM_DEEP_PASSES`, `render_depth_meaning` (§0.5's site).
- `tests/test_no_web_imports.py` — the determinism quarantine (AC2/AC3's home).
- `tests/test_invocation_contract.py` — the LOCKED CLI contract (AC1.2's home).
- `tests/test_v1_commitment_closure.py` — the delivery-disposition closure (AC7's home; **1308 lines,
  exempted under `DF-12-1-B`, targeted at 12.3** — mind the cap if you add much).

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md` — Epic 12 header and Story 12.2 (six
  Given/Then clauses, all mapped into AC1–AC6 above)]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` — FR36 (§497-502), FR21/FR22
  (§550-551), NFR-S6 (§588), NFR-D2 (§579), NFR-C3 (§593), NFR-R1 (§596), FR37 (§507, 12.4's)]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §E *Deep audit is OFF by
  default* (the four sub-rules, and the *"Consequence of the separation, recorded"* paragraph naming
  this story's NFR-R1 ACs as the replacement for the dead *"for free"* rationale); §Enforcement
  (AC7.3's registration site and its established form)]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — `DF-12-1-A` (targets this
  story), `-D`, `-E`, `DF-10-2-A` (ruled OUT, escalated), `DF-11-2-A`/`-B`, `DF-8-3-A`, `DF-11-4-D`]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/12-1-pipeline-stops-breaching-its-own-limit.md`
  — §0.1 operator ruling (carried verbatim), the regeneration sequence, the guard-adequacy clause, the
  `core.autocrlf` blob-vs-worktree trap]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epic-11-retro-2026-08-12.md` — AI-E10-1 (dated
  risk acceptance), AI-E10-3 (re-measure by execution), AI-E10-5 (*the list is never the contract*),
  AI-E11-1 (vacuous guards are the dominant defect class), AI-E11-7 (`DF-10-2-A` needs a dated
  operator decision), SD-2 (no executed CI gate for three epics). **Every numeric figure in that
  retrospective predates Story 12.1 and is stale — §B.0 supersedes it.**]

### Project Structure Notes

This story **adds** to `argus/**` (§A.1 recommends one module under `argus/audit/`) and **extends**
four existing test files rather than forking them (`test_no_web_imports.py`,
`test_invocation_contract.py`, `test_v1_commitment_closure.py`, `test_plain_english.py`) — per AI-E2-5
/ AI-E3-6, *extend the guard, do not fork it*. New tests that do not belong in an existing subject file
get a dedicated file, following `tests/test_pipeline_split_surface.py` (Story 12.1) and
`tests/test_module_size_ceiling.py`.

**Known variance, recorded:** `tests/test_v1_commitment_closure.py` is already 108 lines over the
NFR-M1 cap under exemption `DF-12-1-B` (targeted at 12.3). AC7 requires edits to it. Keep them small;
if your addition would materially grow it, prefer a dedicated file and say why.

### Decisions taken under §7 authority, with rationale

1. **The opt-in is a registered CLI flag, not `--passes …,deep`, not an env var, not an extra.**
   Project standard (the LOCKED invocation contract; `DF-AUD-APAA-E`'s *unspecified accepted flag* is
   the named defect) **and** the measurement in §0.4 item 3 / §0.5 point the same way. §A.3.
2. **Fixing the §0.5 false deep claim is IN scope**; making `--passes` reject unknown tokens is **OUT**
   and filed. The first is FR36's own prohibition; the second is a LOCKED-flag behaviour change with a
   CI-verified workflow dependency this story has no CI evidence for (§0.2). §A.3.
3. **A seventh AC (AC7) was added beyond the epic's six clauses.** Justification: §0.6 hole 2 proves
   that this story's own delivery would otherwise leave a committed guard asserting *"FR36 is not
   built"* forever, with nothing red. An epic clause cannot foresee a guard's blind spot; leaving it
   unwritten would ship the exact defect class the retrospective named dominant. Its scope is fenced
   to the direction this story's delivery rots.
4. **The wiring is recommended into `argus/audit/deep_pass.py`, not `pipeline.py` and not a fourth
   `pipeline*.py`.** Measured reasons in §A.1; explicitly overrulable with measured reasons, following
   Story 12.1's own §A.1 precedent.
5. **`DF-10-2-A` is ruled OUT and escalated rather than silently carried.** It requires a *dated
   operator decision* (type (H)), which is outside a dev agent's authority; this is the **third**
   consecutive story to carry it. Recorded in §A.8 for the Epic-12 retrospective.
6. **AC5.2 (the fabricated recording) is stated as a property with ruled options rather than a
   prescribed mechanism**, because option (2) has a test-suite blast radius that only measurement on
   the day can size. The **property** is non-negotiable; the mechanism is the dev's, and the residual
   must be filed if the local option is chosen.

---

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (`claude-opus-4-6-20260501`) — BMAD `dev-story`, single pass, 2026-08-13.

### Debug Log References

All figures **LOCAL, Windows / CPython 3.11.15**. **CI evidence: NOT ESTABLISHED** — no CI run has
executed any Epic 10, 11 or 12 sha. The dated risk acceptance of 2026-08-11 is carried forward, not
re-taken. `python -m pytest` was run **bare** throughout (the `-qq` trap in §B.0 is real: `pyproject.toml`
carries `addopts = "-ra -q"`).

| # | Measurement | Result |
|---|---|---|
| 1 | Baseline suite at `2bea92f` | **1418 passed / 0 failed / 0 error / 0 skipped**, 140.80s — matches §B.0 exactly |
| 2 | Baseline fences | `git tag -l` empty · `origin/master` = `00c8d1b` · `git ls-files -- argus` = **73** · `pipeline.py` 944 / `pipeline_stages.py` 512 / `cli.py` 522 |
| 3 | **§0.5 reproduced** (`--passes coverage,deep`) | *"a deep read was dispatched … validated against the repository AST"*, `verdict=RELEASE_READY deep_ratio=1/2 blocking_findings=0`, **exit 0**. Nothing dispatched. |
| 4 | **§B.3 re-derived independently** (AC6.1) | **YES.** Bare `argus audit <repo>`, no flags/LLM/harness → `verdict=NOT_READY_FOR_RELEASE blocking_findings=1`, **exit 2** (measured with NO pipe). Thresholds re-read from the detector, not transcribed. |
| 5 | Final suite | **1439 passed / 0 failed / 0 error / 0 skipped**, 143.78s (+21 tests) |
| 6 | mypy / bandit | `Success: no issues found in 74 source files` · bandit **19 low / 0 med / 0 high — ZERO new findings vs `2bea92f`** (diffed by content, not by count) |
| 7 | Self-audit on the final tree | `verdict=RELEASE_READY deep_ratio=64/177 blocking_findings=0 assessed_deep_ratio=4/5 scope=application held_out=97`, exit 0 |
| 8 | Post-story fences | `git ls-files -- argus` = **74** · `pipeline.py` **1007** (+63, 193 under cap) · `pipeline_stages.py` 512 · `cli.py` 600 · `deep_pass.py` 519 |
| 9 | Publication fence | `git tag -l` **empty** · `origin/master` **`00c8d1b`, unmoved** · 13 ahead · no push, no tag, no release, no `workflow_dispatch`, no index upload |
| 10 | Ledger append-only | `git diff --numstat 2bea92f HEAD -- deferred-work.md` → **`166  0`** — 166 insertions, **0 deletions**, proven programmatically |

**Commits (local only):** `8a0bebc` (implementation) → `64164bd` (regenerated artifacts). Provenance
`8a0bebc` verified an **ancestor of HEAD** by `git merge-base --is-ancestor`, and
`git diff --quiet 8a0bebc HEAD -- argus/` is **empty** — the artifacts describe exactly the tree they
cite. Regeneration was `python scripts/regenerate_dogfood_artifacts.py` only; **no artifact was
hand-edited**.

**🔴 NO EGRESS OCCURRED AT ANY POINT.** No provider was contacted, no socket opened to any host, no
key used. Every test dispatches through an injected `FakeDispatch`-shaped port (NFR-D2, zero tokens).
The AC2.3 gate deliberately uses `*.invalid` (RFC 6761 — can never resolve) so that even a total
failure of the gate could not reach a real host.

### Completion Notes List

#### Guard adequacy (AI-E11-1) — observable · defect moves it · generated adversarial variant · positive control

Every load-bearing guard below was proven **RED at the real seam with the FINAL committed test code**,
never a reconstruction.

1. **`TC-ArgusAgent-AUDIT-001-60` / `TC-ArgusAgent-REPORT-002-20` — the false deep claim.**
   *Observable:* the depth-disclosure line on stderr from the **real CLI**. *Defect moves it:* landed
   RED on `2bea92f` before any wiring existed — `assert "a deep read was dispatched" not in err` failed
   with the exact output §B.2 records. *Why end-to-end:* the defect lived in the **join** between an
   unvalidated CSV, a pass set and a disclosure predicate; no unit test of any one of the three could
   see it, so `-20` is the unit half and `-60` proves the join. *Adversarial variants:* `-21` generates
   all three disclosure states from the real predicate inputs and asserts they are mutually distinct
   (3 of 3), including that a delivered outcome attached to a run that never requested the pass still
   yields the not-requested wording — the request is necessary, not merely sufficient.

2. **`TC-ArgusAgent-PIPELINE-001-10/-12` — the derived forbidden surface (§0.6 hole 1).**
   *Observable:* the derived populations and the subprocess `sys.modules` check. *Defect moves it:*
   the hand-written tuple omitted **`argus.audit.open_llm_adapter`** — the one module that can open a
   socket — and the entry-point tuple `(models, pipeline, cli)` had never learned about
   `pipeline_persist.py` (6.3) or `pipeline_stages.py` (12.1), so **two thirds of the pipeline surface
   sat outside the gate**. Measured: forbidden **4 → 6**, entry points **3 → 5**.
   *Generated adversarial variant:* `-12` **writes a real `argus/audit/_synthetic_egress_probe.py` to
   disk**, re-derives, and requires it to appear with **no registry edit** and the count to grow by
   **exactly one** (so a derivation returning a fixed superset also fails). Removed in a `finally`
   with its `.pyc`; the package was verified clean afterwards.

3. **`TC-ArgusAgent-PIPELINE-001-11` — the AC3 POSITIVE CONTROL. Not optional, and stated plainly:
   *a one-directional import-absence gate over a deferred path is a guard that passes by not
   executing.*** §A.2's deferred import makes `-10` green **by construction** — green because the code
   never ran, which is the deferred-import form of a vacuous guard, created by this story's own design.
   *Observable:* which modules are resident after a run, one fresh subprocess per leg.
   *Both directions measured:* opt-in **absent** → `set()`; opt-in **present** →
   `{argus.audit.deep_audit, argus.audit.deep_pass}`. The observable genuinely moves, which is what
   makes the absence evidence. Neither leg configures a provider, so no leg can dispatch.

4. **`TC-ArgusAgent-AUDIT-001-62` — the environment is never an opt-in (AC2.3).** *Observable:* modules
   resident after a run with **every** adapter environment variable set to a live-looking value and the
   flag absent → must be `set()`. *Population derived by `ast`* over the adapter's own `os.getenv`
   calls: **6 variables** (`ARGUS_LLM_MODEL`, `OLLAMA_HOST`, `OLLAMA_MODEL`, `OLLAMA_URL`,
   `OPENAI_API_KEY`, `OPENAI_BASE_URL`) — matching §B.5 exactly, and derived so the seventh someone
   adds is covered the day it lands.

5. **`TC-ArgusAgent-DOCS-001-34` + `not_built_refutations` — §0.6 hole 2, the guaranteed rot.**
   *Defect moves it, observed live:* the new direction was added **before** the disposition flip and
   fired immediately on the real registry against the real closure —
   *"FR36: disposed 'not-built' but its dedicated seam ['argus.audit.deep_audit', 'argus.audit.ports']
   IS reachable from argus.cli"*. Without it, wiring FR36 would have left a committed guard asserting
   *"FR36 is not built"* after it was built, silently, forever. *Positive control:* `-37b` drives the
   pure function over the same synthetic graph as `-37`, proving it fires **and** stays silent on
   honest input, and that it names **only** the module that actually became reachable (an imprecise
   accusation being the very defect class here). *Scope fence honoured:* it fires only on modules an
   entry names as that FR's **dedicated** seam, so no other disposition is re-litigated.

6. **`TC-ArgusAgent-DOGFOOD-001-48` — the externalization guard.** *Defect moves it, demonstrated by
   controlled experiment:* the pre-story sentence was re-inserted, the guard **failed**, and the file
   was restored — **sha256 round-trip verified byte-identical**
   (`2093059b9fd720b76eb90a4ae4fdf63c98ba5ddf6c8c8d3faa60ca20e360e652` before and after). The honesty
   clauses are now asserted **separately from the byte pin**, so a future rewrite cannot drop them
   while updating the pinned string to match.

7. **`TC-ArgusAgent-CLI-001-35` — the invocation contract.** Went RED first with exactly the predicted
   message (*"ACCEPTED BUT UNSPECIFIED — the parser accepts ['--deep-audit']"*), then green after
   registration. That red is the guard working.

8. **`TC-ArgusAgent-AUDIT-001-67` — the failure matrix is DERIVED, not hand-listed (AC5.1).** The
   enumeration walks `LLMDispatchError`'s transitive subclass tree, so a future error type joins it
   automatically. `_instantiate` **fails loudly rather than skipping** if a type cannot be constructed
   (*fail, never skip*). Each member is driven through the **real pipeline entry point** (AC5.3), not
   an adapter unit test.

#### Rulings taken under §7/§8 authority

- **§A.1 followed, not overruled.** The wiring lives in **`argus/audit/deep_pass.py`**. `argus/audit/`
  is where the quarantine already reasons, so the module was **inside** the fence AC2.2 widened before
  it had any behaviour; `DF-12-1-E`'s trigger did **not** fire (still three `pipeline*.py` siblings).
  `pipeline.py`'s delta is a call site plus two optional seams, which is what makes AC2.4's
  byte-identity argument cheap to make and easy to believe.
- **§A.3 followed.** `--deep-audit`, `store_true`, default `False`, registered. It **adds** the existing
  `deep` token before `--skip-pass` subtracts, deliberately: adding *after* would let a convenience
  flag override an operator's explicit exclusion, on the one pass where that exclusion means *do not
  transmit my source*.
- **§A.4 — the disclosure predicate.** Kept the sentence, fixed what it is derived from. **Three**
  honest states now exist; the third (*requested and not delivered*) is new and is the one FR36/NFR-R1
  care about most — falling back to the not-requested wording would be a *different* lie.
- **§A.5 option 1 (recommended) taken:** the pass **refuses to construct** an adapter when no provider
  endpoint is configured, so `_dispatch_httpx`'s fabricating branch is unreachable from the verdict.
  **The residual is filed, as §A.5 requires: `DF-12-2-B`** — the adapter still fabricates for every
  other caller.
- **§A.6 honoured: no field was added to `AuditRequest`.** The flag's job is to put the existing token
  into `enabled_passes`. The **outcome** travels on `AuditVerdict.deep_pass`, which follows the
  codebase's own **omit-when-unengaged** precedent (`coverage_scope`, `critical_subsystems_not_deep`):
  the key is dropped from the canonical payload when `None`, so a default run's `.argus/` bytes are
  unchanged and **no schema bump is owed**.
- **AC5's "no `RELEASE_READY` over a failed pass" vs AC5.4's "the zero-token grade" — a tension, ruled
  and recorded.** Read literally as *keep `audited_deep`*, AC5.4 would make a run with a dead provider
  return `RELEASE_READY`, contradicting AC5's operative sentence. Ruled: a failed target is re-graded
  **`audited_shallow`** through the **existing** `grade_entry(claim_present=False)` (*silence →
  shallow*, the FR6/FR7 honesty keystone reused verbatim — no new grading rule, no new depth state).
  It **stays in the denominator** (AC5.4's actual prohibition — *never silently dropped*), the ratio
  moves, and the FR16 table decides as it always did. **No row, threshold, boundary or exit-code
  mapping changed.** *Tradeoff:* the phrase *"(the zero-token grade)"* is read as *the grade earned
  without the deep read*, because the alternative reading contradicts the same AC's own **Then**
  clause.
- **Degradation findings are `advisory=True`, `depth_supported=None` — deliberately NOT
  verdict-blocking.** An unreachable provider is a fact about *the audit*, not a defect in the audited
  code; routing it through FR16 row 2 would print *"BLOCKED — 1 verdict-blocking finding(s) must be
  resolved"* about somebody else's clean repository. The honesty is carried by the **coverage
  downgrade** instead, which is a statement about the audit — exactly the register FR16 rows 1/4 use.
- **A design improvement made under §8 authority:** the deep-pass token is no longer a second constant.
  `plain_english` exposes `deep_pass_enabled()` / `with_deep_pass()`, so the CLI and pipeline never
  spell the token at all — one vocabulary, asked one way (AR7/§3.3). This also removed the last new
  bandit finding, keeping the security-scan delta at **zero new** on the story that adds the only
  egress path.
- **Two production `assert`s were removed** from `deep_pass.py` before commit: they are stripped under
  `python -O`, so production logic must not rest on them (bandit B101). One guarded a type narrowing
  (restructured into explicit control flow); the other was propping up an otherwise-dead local.

#### AC6 — the absorbed Story-11.2 question, ANSWERED (AC6.4: recorded here, and in the ledger)

**YES.** `NOT_READY_FOR_RELEASE` **is reachable on the default invocation.** Independently re-derived,
not transcribed: a bare `argus audit <repo>` — **no flags, no LLM, no cartridge harness** — returned
`verdict=NOT_READY_FOR_RELEASE blocking_findings=1` with **exit code 2** (read from the process, never
through a pipe). The mechanism is `argus/detectors/vacuous_test.py` (anchor `depth =
CoverageDepth.AUDITED_SHALLOW if corroborated else None`) emitting a `RULE_AST` finding with a
**non-`None` `depth_supported`** — the FR16 row-2 eligibility predicate — with no LLM involved and no
sign-offs required. **The AC6.2 escalation branch therefore does NOT fire.** The measurement is
**committed** as `TC-ArgusAgent-VERDICT-001-30/-31` so it cannot rot back into a guess, and the
thresholds the fixture is built against are **imported** from the detector rather than transcribed.

**Consequence for AC6.3:** the guard's causal claim — *seam not wired in, **so** every finding is
advisory* — is **refuted**. Advisory-ness was never a consequence of the seam being unwired; it is a
contingent property of the **Argus dogfood corpus**. **Story 12.4 can state plainly: a blocking verdict
IS available on the default path.**

#### Ledger (AC7.5) — every §A.8 item ruled, including those ruled OUT

`DF-12-1-A` **re-recorded** (trigger fired — the pipeline surface *was* edited; not closed, with a
measured reason: splitting the 1326-line guard that would notice a pipeline regression, inside the
change that modifies the pipeline, removes the witness for the property this story most needs
witnessed; re-targeted at **12.3**, which already owns the sibling `DF-12-1-B`). `DF-12-1-E` **did not
fire** (no fourth `pipeline*.py`) and that is recorded rather than left silent. `DF-12-1-D` did not
fire, but its **hazard was live and heeded** — the new module was `git add`-ed early so the
index-reading NFR-M1 sweep could see it. `DF-10-2-A` **ruled OUT and ESCALATED** to the Epic-12
retrospective as an operator-level item (third consecutive story to carry it; a type-(H) dated decision
is outside a dev agent's authority). `DF-11-2-A`/`-B` + SD-4 → **OUT** (12.5, confirmed untouched).
`DF-8-3-A` → **OUT** (12.4). `DF-11-4-D`/`AI-E11-6` → **OUT**, with the caveat discharged explicitly:
a section *was* added to `_NOTE_SECTIONS` because the contract registry requires a real CHANGELOG site,
but it is a **pure insertion** with its placement reasoned and **no existing section moved relative to
any other** — the impact-rank question was not re-opened. **New:** `DF-12-2-A` (the `--passes`
validation gap, ruled OUT of scope with the LOCKED-flag + no-CI-evidence reasons), `DF-12-2-B` (the
adapter's fabricated recording — the §A.5 residual, filed as required), `DF-12-2-C` (an honest
disclosure that `tests/test_v1_commitment_closure.py` grew 1308 → 1412, so 12.3's split is bigger than
`DF-12-1-B` estimated).

#### Known variances, stated rather than discovered later

- `tests/test_v1_commitment_closure.py` is now **1412** lines (212 over the NFR-M1 cap, up from 108),
  under the existing `DF-12-1-B` exemption and newly filed as `DF-12-2-C`. Prose was trimmed once
  specifically to reduce it. Moving `-37b` to a dedicated file was **considered and declined**:
  separating a positive control from the function it controls is how a control stops being maintained.
- The `README.md` / `CHANGELOG.md` derived module figures moved **73 → 74** and the wheel/sdist entry
  counts **78/77 → 79/78**, because `TC-ArgusAgent-DOCS-001-54` measures the **built artifact** — *the
  artifact is the fact*. The `0.1.0` section's figure is restated with a dated note rather than frozen,
  precisely because a frozen number is the defect that guard exists to catch; nothing about the release
  itself is amended.

#### Fix round — iteration 1 (2026-08-13, commits `7074c31` → `58c8f6b`)

Two findings stood from code-review iteration 1. The reviewer's confirmations (the AC5/AC5.4
resolution, advisory-not-blocking degradation, the two removed asserts, AC2.4, the append-only
ledger, the publication fences, bandit-zero-new) were **not relitigated and not re-touched**.

**THE DECISION OF THE ROUND — `DF-12-2-D`: is this story's wiring VACUOUS?**

*The finding, re-derived by execution before deciding anything.* Neither
`OpenLLMAdapter._dispatch_litellm` nor `._dispatch_httpx` ever populates
`LLMRecording.structured_output`; both capture the response's `model`, `usage` and `finish_reason`
and discard the completion. Measured over a substituted transport (no socket — a `.invalid` host per
RFC 6761): a **fully successful** dispatch to a **healthy** provider returning **well-formed
content** comes back with `structured_output == ()`, and `_dispatch_one` returns
`REASON_EMPTY_RESPONSE` before `_claim_is_ast_grounded` is ever consulted. So through the shipped
adapter `delivered_count` is always `0`.

*Ruling: **NOT vacuous** — adapter-limited, and in the fail-SAFE direction. Recorded with its
reasons because it is a judgement, not a fact.* A vacuous guard is **green when it should be red**:
it over-claims, and the observer cannot see the defect. This is the **mirror image**. The
discrimination is empirical, not rhetorical, and `-73` asserts it: the egress path **genuinely
fires** — the real pipeline constructs the real adapter and the request really reaches the transport,
with the right per-file targets and the right URL. A capability that never fired would indeed be
inert; this one fires. What is unreachable is only the **favourable outcome**. Every safety property
this story ships is about the path that does fire and is exercised on it: off-by-default, disclosure
before the first byte, the environment is never an opt-in, spend through the existing ceiling, no
listener, honest degradation. And FR36's operative prohibition — *"never produces a false deep
claim"* — is **made unconditional by this gap, not weakened by it**: the pass cannot over-claim
because the adapter cannot hand it anything to over-claim with.

*But the word `wired` WAS over-readable, and that half of the finding is upheld.* A reader of FR36's
flipped disposition would reasonably take `wired` to mean the capability completes end to end through
a shipped adapter. It does not. That is a disclosure defect, and it is fixed here rather than argued
away.

*Option (a) — close the gap in the adapter — was MEASURED, then rejected.* Five findings, each
established by reading or running the tree, not assumed:

1. **There is nothing to parse.** `_build_messages` never asks the model for structured output —
   there is no claim grammar and no response contract. The model is told its role and given a path,
   a tier and a run id, and free prose comes back.
2. **Tipping the completion into the field is a documented CONTRACT VIOLATION, not a fix.**
   `structured_output`'s own contract in `argus/audit/ports.py` is *claim/locator-shaped strings,
   **NEVER** raw prompt/response bytes* (NFR-S1, producer-side redaction).
3. **It requires re-baselining a committed NFR-S1 SECURITY assertion on the product's only egress
   path.** `tests/test_open_llm_adapter.py` asserts `rec.structured_output == ()` with the explicit
   rationale *"NFR-S1 — the recording carries metadata only; no prompt/response bytes anywhere."*
   Under this round's binding constraints that is a HALT-class act, not a judgement call.
4. **Doing it honestly is a claim grammar + a prompt contract + a redacting parser + a
   `DEEP_PROMPT_TEMPLATE_VERSION` bump** — and that version is an **AR5 cache-key closure input**
   (`build_closure_from_recording` folds it into the key), so it is a provenance change too.
5. **It could not be validated here and it already has an owner.** §0.3 forbids any live dispatch
   absolutely and CI evidence is NOT ESTABLISHED (AI-E10-1), so a new response contract on the only
   egress path would ship unexercised against any real provider. `deep_audit.py` and
   `_claim_is_ast_grounded` **both already name full claim-grammar grounding as Story 6.2's**.

Designing an unvalidatable prompt/response contract on the one path that can transmit source, inside
a fix round, by weakening an NFR-S1 assertion, in scope another story owns — that is precisely the
blast-radius widening the fix-round constraints forbid. **Option (b) taken.**

*What (b) shipped.*

- **`DF-12-2-D` filed** (🟡, correctness) with a named owner (Engineering) and a target — the
  claim-grammar story, and until one is scheduled, the next story to change
  `open_llm_adapter.py`'s response handling, which is also `DF-12-2-B`'s trigger. **They should be
  closed together: both are about what that module returns.** Append-only proven by `--numstat`.
- **`TC-ArgusAgent-AUDIT-001-73`** — the gap, measured through the **real pipeline entry point** with
  the **real unmodified adapter** over a **substituted transport**. Asserts three things in order:
  the path is live (POSTs, targets and URL), the provider's answer was good and the adapter discarded
  it, and the pass therefore degrades as `empty-response` with the strengthened sentence correctly
  **absent**. It also asserts the provider-reported spend is still accounted (`credits_used != "0"`)
  — a degraded read is not a free read.
  **It is designed to go RED the day `DF-12-2-D` closes**, with a failure message that says so, so
  the record cannot rot into the next stale assertion.
- **`TC-ArgusAgent-AUDIT-001-74` — the POSITIVE CONTROL**, required by this story's own §0.6/AC3.3
  rule that a one-directional observation over a path that stops early is not evidence. Without it,
  *"the adapter is limited"* and *"the delivered branch is broken and the discard was hiding it"* are
  indistinguishable — and the second reading **would** make the wiring vacuous. Same adapter, same
  transport, same response bytes, same pipeline, same repo; the **only** change is that the
  completion the adapter already received is carried onto `structured_output`. **It delivers.** So
  the gap is exactly one field wide, it is the adapter's, and everything wired downstream of the port
  is proven on real provider-shaped input rather than only on a purpose-built fake.
- **RED-first, with the FINAL committed code, both directions, sha256 round-tripped.**
  (i) `_dispatch_httpx` mutated to populate `structured_output` → **`-73` FAILS** at
  `assert recording.structured_output == ()` (`assert ('app/service...',) == ()`) while `-74` stays
  green. (ii) `_claim_is_ast_grounded` mutated to `return False` → **`-74` FAILS** with
  `delivered_count 0 == 3, reasons=('claim-ungrounded',)` while `-73` stays green. Each mutation was
  reverted with `git checkout --` and the file's sha256 verified byte-identical:
  `open_llm_adapter.py` `4a820e77…97ca`, `deep_pass.py` `6cc79bf3…3ff7`.
- **The honesty made explicit at every site a reader would be misled**, not just in the ledger:
  the `deep_pass.py` module docstring (beside `DF-12-2-B`'s residual disclosure — same discipline);
  the **FR36 `_Delivery` note**, which is *where the word `wired` is asserted*, now scoping it
  explicitly (*"`wired` means the seam is reached and the safety properties hold on it, NOT that the
  capability completes end to end through the shipped adapter"*); and a user-facing **KNOWN
  LIMITATION** paragraph in `CHANGELOG.md` telling an operator plainly that today they will get the
  third state, and **not to pay a provider for depth they will not get**.
- **No committed guard or document now asserts something the tree cannot do** — checked by reading
  each: the disclosure strings and the report callout fire only on outcomes that occurred; the
  `render_depth_meaning` "delivered" sentence is never emitted through the shipped adapter; the
  CHANGELOG's three-state description is now qualified; FR36's note is scoped.

**Second finding — `DF-12-2-E`** (🟢, `PROVIDER_ENDPOINT_VARIABLES` duplicates the adapter's
`_api_base` derivation). Already filed by the reviewer and **left deferred, deliberately**. It is a
maintainability nit on the **safe** side (a variable added only to the adapter would make
`resolve_provider_endpoint()` **under**-report configuration — degrade, never fabricate). Deriving it
by `ast` from the adapter is the right fix and is the same shape as `TC-ArgusAgent-AUDIT-001-62`, but
it edits the endpoint-resolution logic guarding the fabricating branch (AC5.2), inside a fix round,
for zero behaviour change — a worse risk/benefit than the entry it closes.

**One thing fixed beyond the two findings, and named rather than slipped in.** `-69` carried
`assert "argus.audit.open_llm_adapter" not in sys.modules or True` — an assertion that **cannot
fail**, i.e. a vacuous guard, in the story chartered against vacuous guards (§0.6). Removed, with a
comment recording why the property cannot honestly be asserted in-process (an unrelated earlier test
may already have imported the module) and that it is held — more strongly, in a fresh subprocess per
leg — by `TC-ArgusAgent-PIPELINE-001-11`. **Deleting an assertion that asserts nothing is not a
weakening**; no property was narrowed, dropped or re-baselined anywhere in this round.

**Gates RE-RUN on the final tree — nothing carried forward from the previous round.** All figures
**LOCAL, Windows / CPython 3.11.15**. **CI evidence: NOT ESTABLISHED.**

| Gate | Result | Movement vs iteration 1 |
|---|---|---|
| `python -m pytest` (bare) | **1441 passed / 0 failed / 0 error / 0 skipped**, 142.03s | 1439 → **1441** (+2: `-73`, `-74`) |
| `python -m mypy argus` | `Success: no issues found in 74 source files` | unchanged |
| `python -m bandit -r argus` | **19 Low / 0 Med / 0 High** | **content-diffed against a `2bea92f` worktree: 0 new, 0 removed, IDENTICAL SET** (`B105`×6, `B603`×5, `B404`×4, `B607`×4) |
| `python -m argus.cli audit .` | `verdict=RELEASE_READY deep_ratio=64/177 blocking_findings=0 assessed_deep_ratio=4/5 scope=application held_out=97`, **exit 0** | unchanged |
| `git ls-files -- argus` | **74** | unchanged — no file added or removed |
| Dogfood unit LOC | total **21530 → 21569** (+39, all in partition 2: 14799 → 14838) | the docstring |
| Dogfood `partition_id`s | `1a31dc9a9559` / `619a713d53ca` / `aaec0673cdcf` | **all three UNCHANGED** — the partitioning did not move |
| `git tag -l` | **empty** | unchanged |
| `origin/master` | **`00c8d1b`, unmoved**; HEAD 15 ahead | no push, no tag, no release, no `workflow_dispatch`, no index upload |
| Ledger append-only | `git diff --numstat 2bea92f HEAD -- deferred-work.md` → **`250  0`** (this round `64164bd..HEAD` → **`84  0`**) | 0 deletions, proven programmatically |
| Module sizes | `deep_pass.py` 519 → **558**; `test_deep_pass_wiring.py` 819 → **1104**; `test_v1_commitment_closure.py` 1412 → **1419** | all under/at their existing dispositions (see variance below) |

**AC2.4 re-derived on the final tree, with the previous round's one caveat ELIMINATED rather than
attributed.** Iteration 1 compared a `2bea92f` worktree against `HEAD` and found one `.argus/state/*`
filename differing, attributed to the two runs' different `--report-dir` values. That attribution was
first reproduced (the two records differ in **exactly one line**, `report_dir`, and the filename is
just that record's content hash) and then **removed as a variable** by re-running both binaries
against the **same repository with the same `--report-dir`**. Result: combined stdout+stderr
byte-identical, exit code `0` both, **all 2 report files byte-identical, all 9 `.argus/` files
byte-identical, identical filenames.** The default path did not move.

**Regeneration (§0.1 sequence honoured).** `7074c31` implementation → `python
scripts/regenerate_dogfood_artifacts.py` → `58c8f6b` artifacts. Renderer output only; **no artifact
hand-edited**. `git merge-base --is-ancestor 7074c31 HEAD` passes and `git diff --quiet 7074c31 HEAD
-- argus/` is empty. The currency guards (`TC-ArgusAgent-DOGFOOD-001-49..-52`) and the two
live-derivation artifact tests went **red on the commit and green after regeneration** — the guards
working, exactly as §0.1 predicts. *Noted for the record:* those guards read **committed** state, so
they were green against a dirty worktree and only fired after `git commit` — the `DF-12-1-D` hazard
shape again, heeded rather than tripped over.

**One commit message was corrected before it could become an untrue committed figure.** The first
regeneration message said total LOC `21540 → 21569`; the artifact's actual prior figure was
**`21530`**. The message was amended on the local, unpublished tip (`bd0e2a3` → `58c8f6b`), which
does not touch the cited provenance `7074c31` or its ancestry. Recorded rather than quietly fixed.

**🔴 NO EGRESS OCCURRED AT ANY POINT IN THIS ROUND.** No provider was contacted, no socket opened, no
key used. The two new tests substitute `httpx.Client` **and** point the endpoint at a `.invalid` host
(RFC 6761 — can never resolve): two independent fences, so even a total failure of the substitution
could not reach a real host.

**Known variance added this round:** `tests/test_deep_pass_wiring.py` is now **1104** lines — still
under the NFR-M1 1200 cap, but with only 96 lines of headroom, so the next addition to it should
consider a dedicated file. `tests/test_v1_commitment_closure.py` moved 1412 → **1419** (7 lines, the
FR36 scope note), i.e. 219 over the cap rather than 212, under the existing `DF-12-1-B` exemption and
`DF-12-2-C`. `DF-12-2-C`'s recorded figure of 1412 is now stale by 7; it is **not edited** (the
ledger is append-only) and the true number is recorded here for 12.3 to size against.

### File List

**Fix round — iteration 1 (`7074c31`, `58c8f6b`):**
- `argus/audit/deep_pass.py` — the `DF-12-2-D` disclosure paragraph in the module docstring
  (docstring only; no behaviour change — the sole `argus/**` delta of this round).
- `tests/test_deep_pass_wiring.py` — `TC-ArgusAgent-AUDIT-001-73`/`-74`, the
  `_MockedProviderTransport` / `_mount_mocked_provider` helpers, and the removal of `-69`'s
  `... or True` vacuous assertion.
- `tests/test_v1_commitment_closure.py` — the FR36 `_Delivery` note now scopes the word `wired`.
- `CHANGELOG.md` — the user-facing **KNOWN LIMITATION** paragraph under `--deep-audit`.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — `DF-12-2-D` appended (+84, **0
  deletions**; +250/0 cumulative vs `2bea92f`).
- The three dogfood artifacts — **renderer output only**, provenance `7074c31`.

**New (`argus/**` — the Epic-11 fence is lifted for Epic 12 per §0.1):**
- `argus/audit/deep_pass.py` (519) — the opt-in deep pass: target selection, budget projection through
  the EXISTING `project_halt_point`, dispatch through the injected `LLMDispatchPort` via `DeepAuditSeam`,
  AST validation of each returned claim, typed degradation, and the egress disclosure.

**New (tests):**
- `tests/test_deep_pass_wiring.py` (819) — `TC-ArgusAgent-AUDIT-001-60`..`-72`, `TC-ArgusAgent-DOCS-001-60`.
- `tests/test_default_path_blocking_verdict.py` (179) — `TC-ArgusAgent-VERDICT-001-30`/`-31` (AC6).

**Modified (`argus/**`):**
- `argus/cli.py` — `--deep-audit` (registered, `store_true`, default `False`); LOCKED-contract block;
  `_resolve_passes` composition; `_emit_egress_disclosure`.
- `argus/pipeline.py` — the gated call site with the **function-local** import; `deep_port` / `disclose`
  seams on `run_audit` / `run_audit_detailed`; `deep_pass` threaded into the verdict fold.
- `argus/verdict/verdict_gate.py` — `DeepPassOutcome`; `AuditVerdict.deep_pass`; the omit-when-unengaged
  rule in `to_canonical_payload`; `evaluate_verdict(deep_pass=...)`.
- `argus/verdict/prosecutor.py` — carries `deep_pass` through the re-fold (it would otherwise blank the
  FR36 disclosure on every prosecuted run).
- `argus/reports/plain_english.py` — the three-state disclosure; `deep_pass_enabled` / `with_deep_pass`;
  struck corrections.
- `argus/reports/generator.py` — the report callout keys on the outcome, so report and CLI agree.
- `argus/dogfood/proof_render.py` — the repaired `DOGFOOD_EXTERNALIZATION_GUARD` (AC6.3).

**Modified (tests — extended, never forked, per AI-E2-5 / AI-E3-6):**
- `tests/test_no_web_imports.py` — derived populations; `-11` positive control; `-12` generated variant;
  `TC-ArgusAgent-AUDIT-001-62` env gate.
- `tests/test_v1_commitment_closure.py` — FR36 `not-built` → `wired`; `seam_modules`;
  `not_built_refutations`; `-37b`.
- `tests/test_plain_english.py` — `-20`/`-21`; the existing disclosure test strengthened, not narrowed.
- `tests/test_invocation_contract.py` — the `--deep-audit` `CONTRACT_REGISTRY` entry.
- `tests/test_dogfood_module_split.py` — the repaired pin + separately-asserted honesty clauses.
- `tests/test_release_surface_honesty.py` — `_NOTE_SECTIONS` insertion, placement reasoned.

**Modified (documents):**
- `CHANGELOG.md`, `README.md` (derived figures follow the artifact — `TC-ArgusAgent-DOCS-001-54`).
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — two §Enforcement registrations; the
  `deep_audit.py:91` → `:98` correction; the `[llm]`-extra correction. Struck, never deleted (§3.4).
- `_bmad-output/design-artifacts/ArgusAgent/epics.md` — the same two stale premises, struck.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — append-only (+166, **0 deletions**).
- The three dogfood artifacts — **renderer output only**, provenance `8a0bebc`.

### Change Log

| Date | Change | By |

|---|---|---|
| 2026-08-13 | **Code review iteration 2 (Sonnet 5): review -> done. VERDICT: PASS.** Narrow confirmation of the fix round, per the orchestrator's scope. Independently re-verified, not transcribed: `python -m pytest` (bare) 1441 passed / 0 failed; mypy clean on 74 files; bandit 19 Low / 0 Med / 0 High, identical `test_id` set diffed against a freshly checked-out `2bea92f` worktree; `argus audit .` RELEASE_READY exit 0; `git ls-files -- argus` = 74; regeneration commit `58c8f6b` touches only the three dogfood docs, `argus/` diff against `7074c31` empty; `git diff 64164bd 7074c31 --stat` matches the story's own fix-round File List exactly; ledger append-only 250/0 cumulative, 84/0 this round (`--numstat`); publication fences intact (`git tag -l` empty, `origin/master` `00c8d1b` unmoved, HEAD 15 ahead). Attacked `TC-ArgusAgent-AUDIT-001-73`/`-74` with two self-constructed mutations (populate `structured_output` with real content; force `_claim_is_ast_grounded` to return `False`) — both directions independently reproduced RED, both reverted clean. Confirmed `-73` drives the real, unmodified `OpenLLMAdapter` with no injected port (read `_resolve_dispatcher` directly) and that `.invalid` genuinely does not resolve on this host. Re-derived AC2.4's byte-identity from scratch with two clean synthetic repos at an identical path and `--report-dir`: stdout, stderr, exit code, the full report tree and the `.argus/` state directory (same 9 filenames) were byte-identical — the caveat elimination confirmed. Read the FR36 `_Delivery` note, the `deep_pass.py` docstring and the CHANGELOG KNOWN LIMITATION paragraph directly — none over-claims. Ruled DF-12-2-E's re-deferral sound (env-var lists genuinely identical, drift is safe-side). One Low, non-blocking finding: the Dev Agent Record's claimed sha256 round-trip for `deep_pass.py` does not match the file on disk under any encoding tried (the `open_llm_adapter.py` figure does match) — a prose transcription nit, not a code defect; the underlying revert-clean property was independently re-verified by direct mutation. Process ruling: the story file's untracked git status (unlike 12.1's tracked file) is a retrospective item, not a `done` blocker — nothing in this story's ACs or gates requires the story markdown itself to be committed. CI evidence: NOT ESTABLISHED (LOCAL, Windows / CPython 3.11.15). | Reviewer (code-review) |
| 2026-08-13 | **Addressed code review findings — 1 of 1 blocking items resolved (`DF-12-2-D`); the second finding (`DF-12-2-E`) re-ruled and left deferred with reasons.** The round's decision: is the wiring vacuous? **Ruled NOT vacuous, adapter-limited, fail-safe** — the egress path genuinely fires (asserted, not argued), only the favourable outcome is unreachable, and FR36's *"never produces a false deep claim"* is made unconditional by the gap rather than weakened by it. Option **(a)** (close the gap in the adapter) was **measured and rejected on five findings**: there is no claim grammar to parse into, `structured_output`'s own NFR-S1 contract forbids raw completion bytes, closing it needs a committed NFR-S1 security assertion re-baselined on the only egress path, it needs an AR5 prompt-template-version bump, and it could not be validated (no live dispatch permitted, CI evidence NOT ESTABLISHED) in scope Story 6.2 already owns. Option **(b)** shipped: `DF-12-2-D` filed with owner + target; `TC-ArgusAgent-AUDIT-001-73` (the gap, over a substituted transport to a `.invalid` host) and `-74` (its **positive control** — the delivered branch DOES work when `structured_output` is populated, isolating the gap to one field) both landed **RED-first with the final code, both directions**, mutations reverted with sha256 round-trip; and the honesty made explicit where a reader would be misled — the module docstring, the **FR36 `_Delivery` note where `wired` is asserted**, and a user-facing KNOWN LIMITATION in `CHANGELOG.md`. Also removed a `assert … or True` vacuous guard this story had shipped in `-69`. Gates **re-run, not carried**: **1441 passed / 0 failed**, mypy clean over 74 files, bandit **19 Low, IDENTICAL finding set** to `2bea92f` by content, self-audit `RELEASE_READY` exit 0, `argus` population **74**, all three `partition_id`s unchanged, ledger **+84/0** (**+250/0** cumulative). AC2.4 re-derived with iteration 1's one caveat **eliminated** rather than attributed: same repo, same `--report-dir` — stdout+stderr, both reports and all 9 `.argus/` files byte-identical. Commits `7074c31` (fix) → `58c8f6b` (regenerated artifacts, provenance `7074c31`, ancestor-verified, `argus/` diff empty). No egress. Nothing published — `git tag -l` empty, `origin/master` `00c8d1b` unmoved. CI evidence: NOT ESTABLISHED. | Dev Agent |
| 2026-08-13 | **Implemented (Story 12.2).** Baseline re-measured by execution (1418/1418, `argus`=73). §0.5 and §B.3 both reproduced independently BEFORE any code changed. The false deep claim landed **RED first** end-to-end with the final committed test code, then fixed by deriving the disclosure from work performed (three honest states). `--deep-audit` registered in the LOCKED contract; the seam wired through a function-local import so it is statically reachable yet runtime-inert, with AC3's **positive control** in the same change. Forbidden-surface and entry-point populations **derived** (they had omitted `open_llm_adapter` and two thirds of the pipeline family). Honest degradation, spend through the existing ceiling, no new mechanism. AC6 answered **YES** and committed. FR36 flipped to `wired` and `not_built_refutations` added — it fired on the live registry before the flip. Two commits: `8a0bebc` implementation, `64164bd` regenerated artifacts at provenance `8a0bebc` (ancestor-verified, `argus/` diff empty). Final: **1439 passed / 0 failed**, mypy clean, bandit **0 new**, default run **byte-identical**. Nothing published. CI evidence: NOT ESTABLISHED. | Dev Agent |
| 2026-08-12 | Story created. Premises re-measured by execution (§B.1: 3 stale, 6 held). Two live defects found and recorded with reproductions: the `--passes …,deep` false deep claim (§B.2) and the adapter's ambient-environment egress absorption (§B.5). AC6's absorbed Story-11.2 question **answered YES by measurement** (§B.3), so the escalation branch does not fire. Four blind guards named (§0.6). The deferred-import keystone proven with the real static closure (§B.4). | Scrum Master (create-story) |
