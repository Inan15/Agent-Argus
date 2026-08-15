---
baseline_commit: 2f84a0b8ca029de54dc23058d9d741c48593239d
---

# Story 12.8: The tool explains itself

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`.
>
> 🔵 **This is the EIGHTH story of Epic 12.** 12.1–12.7 are `done`. **Only 12.8 and 12.9 remain
> before the epic retrospective.** Three predecessor stories deferred work to this one **by name**,
> and each named the exact function or file:
>
> | Handed to you by | Where it is written | What it hands over |
> |---|---|---|
> | **Story 12.5** | 12-5 Dev Agent Record; `argus/shared/grammar_status.py:62` (*"the report layer owns report wording, and Story 12.8 owns the CLI's"*) | `render_grammar_downgrade_summary` is *"the function 12.8 wires"*. 12.5 deliberately left `argus/cli.py` **untouched** and stated the blocker: the grammar diagnosis does not travel on `AuditVerdict`, and `run_audit` returns only that |
> | **Story 12.6** | 12-6 §What it is NOT, row 1; 12-6 AC7 | *"Operator-error **diagnosis** prose on the CLI (bad path, unreadable repo, **missing grammar**, absent key), `--help` text, a first-run docs page"* — all four causes named, all four fenced here |
> | **Story 12.7** | 12-7 §What it is NOT, row 1; 12-7 Debug Log §7; `argus/cli.py:696`; `tests/test_cli_flag_contract.py:22`; `tests/test_invocation_contract.py` (`derive_arguments` docstring) | *"Authoring new diagnosis prose is Story 12.8's fence"* · *"`--help` PROSE IS NOT THIS STORY'S… do not add help-text assertions here"* · `-h/--help` excluded from the contract walk because *"its prose is Story 12.8's"* |
>
> **Ledger entries this story OWNS** (both `target_story: 12-8-the-tool-explains-itself`):
> **`DF-8-4-D`** (RELEASE-RELEVANT — the base-`ValueError` arm) and **`DF-10-4-C`** (the exception
> class behind a broken grammar).
>
> **Epic dependency flow:** 12.4 → 12.6 → 12.7 are all `done`; this story is unblocked.
> **It publishes nothing: 12.9 publishes.**

---

## Story

As a developer with the tool's output and nothing else,
I want `--help`, error messages, and the docs to answer what I need,
So that I am never sent to a wiki that does not exist.

**Why this is one story.** Every clause serves **one capability: the tool explains ITSELF to the
person holding its output.** FR37 states the binding form — *"the next action is present in the
tool's own output. A user with no colleague and no internal wiki must not be sent elsewhere to
interpret a verdict."* Argus today explains its **verdicts** well (12.4 shipped that) and explains
almost nothing about **the operator's own mistakes**: eight measured argv errors produce no message
at all, four produce a cause with no fix, one leaks an absolute host path, one publishes a
**fabricated verdict** to a CI consumer, and the `AUDIT_FAILED` next action FR37 requires has **zero
production callers**. A flag whose `--help` omits its default, an error that names a cause with no
remedy, and a first-run page that does not exist are three spellings of the same failure: the user
must go somewhere else to find out what happened. There is nowhere else — that is the persona
(PRD Journey 6: *"Whatever Sam learns has to come from a tool Sam can run alone"*).

### What it is NOT

| Not this story | Whose it is | Authority |
|---|---|---|
| Publishing anything — a tag, an index upload, a marketplace listing, a GitHub Release, a release-status claim | **Story 12.9** | `epics.md:2446-2473`. Epic 11 shipped five stories about publishing without publishing anything; 12.7 held the same line. **Do not touch `release.yml`, `git tag`, or any release-status statement** |
| A `--resume` CLI entrance | **Nobody — `DF-3-4-A`, still open** | 12.7 removed the published `/audit resume` command citing this entry and recorded *"stays open and is NOT re-filed"* under its **existing** owner and target. **It was cited by 12.7, not assigned to you.** Cite it; do not build it |
| An `argus evidence-bundle` sub-command (FR29 export) | **Nobody — `DF-10-5-C`, `target_story: NONE — unscheduled; Governance Owner to schedule`** | The entry names *"Story 12.8 (the CLI surface)"* as **where such a sub-command would go**, not as its owner, and leaves it unscheduled with a named human. **Building it is an unscheduled capability addition.** Cite it |
| Registering further assistant hosts | **Nobody — `DF-12-7-A`, unscheduled** | 12.7 shipped one verified host by decision (DN-2) |
| Any new **assurance** capability, pass, detector, report type, verdict, or decision-table change | Nobody — forbidden | PRD §V1.5 / `epics.md:2159`: *"this epic adds no new assurance capability"*. `epics.md:2312-2314`: **no verdict is reworded, upgraded, or hedged** |
| Persisting exception **messages** into `.argus/` artifacts or the AST index | Nobody — refused twice, deliberately | `DF-10-4-C` + Story 10.4 / DN-5: `str(exc)` carries a host filesystem path (NFR-S1) and would cost a second `AstIndex` schema bump. **The type/class only — never the message** — and it belongs on the surface that RENDERS, not on one that persists |
| Tutorial prose, a concepts guide, a novice onboarding path | Nobody — forbidden | `epics.md:2424-2425`: *"no tutorial prose beyond that; this persona is a developer, not a novice"* |
| A second next-action renderer, a second diagnosis vocabulary, a second help-text source | Nobody — forbidden | AR7 / architecture §3.3: **reuse, never fork.** `render_audit_failed_next_action`, `render_grammar_downgrade_summary` and `build_parser` already exist. A parallel renderer beside a shipped one is a defect, not a delivery (12.4's own binding words) |

---

## Acceptance Criteria

> Every AC below is stated against the **measured** tree at `2f84a0b`, not against the epic's prose.
> §0 records where the epic's premise was found **false** — three of its four clauses were, and one
> of those falsehoods is the largest defect this story closes. Re-measure before you code (Task 1).

### AC1: A lean first-run page exists, and every factual claim on it is DERIVED, not typed

- **Given** `epics.md:2421-2425` and the **measured correction** in §0 row 1: `docs/` does **not**
  hold an integrator-shaped README — `docs/README.md` (642 bytes) is a **BMad tooling stub** that
  names which BMad skills read the folder and ends *"Currently empty apart from this file."* The
  integrator-shaped README is the **root** `README.md` (426 lines), and **nothing in it links to
  `docs/` at all** (measured: zero occurrences of `docs/` in `README.md`).
- **Then** a first-run page ships at **`docs/first-run.md`** (DN-1) covering exactly four things:
  **install**, **first audit**, **reading the ledger**, **what each verdict means** — and **nothing
  else**. No tutorial prose, no concepts guide, no second copy of the README's integration material.
- **Then** it is **reachable**: `README.md` links it, and a test asserts the link target resolves to
  a file that exists. An unreachable page is not a first-run surface. ⚠️ **It does NOT ship in the
  wheel** — `flit_core` packages `argus/**` only — so the link is the whole delivery mechanism, and
  the page must say plainly that it is repository documentation.
- **Then** every **checkable** claim on it is **derived by test, never transcribed**:
  1. the verdict vocabulary equals `Verdict` (`argus/verdict/verdict_gate.py:192`) — a fourth member
     added later turns the guard **RED**, not stale;
  2. the exit codes equal the AR3 mapping (`exit_code_for_verdict` + the reserved `1`);
  3. every `argus …` command line on the page is added to **`-28`'s corpus by glob** (through
     `tests/invocation_sources.py::_INVOCATION_SOURCES`) and parsed by the **real**
     `build_parser().parse_args`, with a `> 0` floor on lines extracted.
- **Then** the page **does not become the place the answer lives.** FR37 is explicit: *"the next
  action is present in the tool's own output"*. A guard asserts **no diagnosis message, `--help`
  string or report line added by this story points the user at `docs/first-run.md`** to find out
  what happened. The page orients a first run; it never substitutes for the tool's own explanation.
- **Then** `docs/README.md`'s *"Currently empty apart from this file"* becomes false and is
  **struck-and-corrected in place** (§3.4 evidence immutability), naming the deliberate
  co-tenancy recorded in DN-1.
- **Then** the page is registered as a consumer-facing published surface in
  `tests/test_release_surface_honesty.py` — `_RELEASE_SURFACES` **and** a matching
  `_RELEASE_SURFACE_PATTERN`, both, for 12.7's recorded reason: *"a registry entry no pattern
  resolves proves nothing, and a pattern with no registry lets anything through."*

### AC2: `--help` states what each argument does AND its default — parity asserted against the real parser

- **Given** `epics.md:2427-2429` (*"every CLI flag Story 10.3 blessed … `--help` states what it does
  and its default, and a test asserts parser-vs-help parity alongside 10.3's parser-vs-contract
  test"*), and the **measured gap** (§0.1 §A): the live parser accepts **19** arguments across both
  sub-commands. **8 state their default** (`--commit`, `--strict`, `--budget`, `--passes`,
  `--deep-audit`, `--coverage-scope`, `--host`, `--dest`); **8 value-bearing flags do not**
  (`--materiality-bar`, `--critical-subsystem`, `--exclude-critical`, `--skip-pass`, `--reports`,
  `--report-dir`, `--ignore-path`, `--ignore-pattern`); and **3 more state none** where it is
  arguably implied (`--dry-run`, `--remove`, positional `repo`) — **decide those three explicitly
  rather than by omission**: DN-2's derived rule covers them for free, so an exemption needs a reason.
- **Then** the default is **DERIVED from the parser, never hand-typed into prose** (DN-2): every
  argument's rendered help states the default the parser actually holds, and a guard asserts the
  rendered text contains the live `action.default` for every derived argument. Hand-typing a default
  into a help string re-creates the exact drift `-35`/`-37` exist to close, one layer out.
- **Then** the parity guard **reuses `derive_arguments(build_parser())`** from
  `tests/test_invocation_contract.py` — the closure 12.7 widened to **every** sub-command — so a
  future sub-command's flags enter the help contract with **no edit** to the guard. Writing a second
  walk here is the `_CONSOLE_SCRIPTS` defect class this project has now recorded four times.
- **Then** the guard is **non-vacuous**: `> 0` arguments walked **and** `>= 2` sub-commands reached,
  so a rename, a move, or an argparse change turns it **RED** rather than silently green over an
  empty set.
- **Then** three help strings must carry the **operator-consequence fact** their own contract block
  already records, because omitting it is what costs a user a run (each pinned by exact substring,
  with the reason in the test docstring):
  1. **`--reports`** — ⚠️ **inert without `--report-dir`** (`argus/cli.py:95-97` states this;
     the help does not). Measured: `--reports final-verdict` alone renders nothing and says nothing.
  2. **`--ignore-pattern`** — matched by **bare substring**, and it **cannot suppress a
     high-confidence live production key** (Story 10.3's Live-Key Safeguard).
  3. **`--ignore-path`** — the same safeguard clause.
- **Then** it lands **alongside `-35`**, in `tests/test_invocation_contract.py`, continuing
  `TC-ArgusAgent-CLI-001` from `-51`. ⚠️ **`tests/test_cli_flag_contract.py:22` forbids adding
  help-text assertions there by name** — obey it. Watch NFR-M1: `test_invocation_contract.py` is at
  **968** lines against the **1200** ceiling; if the addition crosses it, apply 12.7's remedy (a
  cohesion split with a re-export), never shaved lines and never a narrowed population.

### AC3: Every operator error names the CAUSE and the FIX — and the SILENT ones stop being silent

- **Given** `epics.md:2431-2433` (*"an operator error (bad path, unreadable repo, missing grammar,
  absent key under the deep pass) … the message names the cause and the fix"*), and the measured
  inventory in **§0.1 §B**, which found the epic's four examples **already handled in two cases**
  and found **eight silent surfaces it does not name**.
- **Then** every message emitted on a typed operator error names **both** the cause and an action
  that changes it. The four **measured exemplars already in the tree** are the register to match —
  reuse their voice, do not invent a second one:
  - `--strict requires a git repository (no git metadata found). Drop --strict to audit the directory as-is.`
  - `working tree drift: uncommitted changes present (…). Drop --strict to audit the working tree as-is.`
  - `unknown --host value(s) ['nosuch']; this build supports ['claude-code']`
  - `no prior .argus/ run-state + halt-report to resume (run a fresh audit first)`
- **Then** the **cause-only** messages gain their fix (measured list, §0.1 §B rows 1-6), and
  `repo path does not exist` / `repo path is not a directory` **stay two distinguishable causes** —
  they have different fixes and today the CLI prints the second for both (measured:
  `argus audit /no/such/path` and `argus audit README.md` produce the **identical** line).
- **Then (the load-bearing half) the SILENT operator errors are silent no longer.** Measured on
  `2f84a0b`, each produces **no message of any kind**:
  1. **`--passes securty`** (a typo) → `resolve_passes` returns `('securty',)`, the pipeline's
     membership tests (`if "security" in enabled_passes`, `pipeline_stages.py:293`) are all False,
     so **every detector pass is silently disabled** and the run can only report **zero blocking
     findings**. ⚠️ **This is a false-green channel opened by a typo, on the flag whose whole
     purpose is to select safety passes** — the false-green direction `epics.md:2336-2339` calls the
     most dangerous.
  2. **`--skip-pass securty`** → silently subtracts nothing; the operator believes a pass was
     skipped and it ran (or vice versa).
  3. **`--reports vacuous-tests`** → silently renders nothing. ⚠️ **This repository's own committed
     CI workflow does exactly this**: `.github/workflows/argus-student-audit.yml:48` requests
     `final-verdict,coverage-ledger,security-review,vacuous-tests`, and `vacuous-tests` **is not a
     rendered report type** (`generator.py:881-907` renders exactly `final-verdict`,
     `coverage-ledger`, `security-review`, `architecture-review`, plus the meta-token `all`).
  4. **`--reports X` with no `--report-dir`** → renders nothing, says nothing.
  5. **`--critical-subsystem does/not/exist`** → accepted; measured, it **changed the verdict from
     `RELEASE_READY` (exit 0) to `INSUFFICIENT_COVERAGE` (exit 3)** and printed *"Critical files not
     examined deeply: 1"* for a path that does not exist. Same for `--exclude-critical`.
- **Then** the **closed** vocabularies are **REFUSED** with a typed error naming the accepted set
  (rows 1-3), and the **open** ones are **DISCLOSED** on stderr (rows 4-5) — the split, and why, is
  **DN-3**. Refusal messages derive the accepted set from the **one** definition of it, never from a
  second hand-list (AR7): pass tokens from `_ALL_PASSES` + the `deep` token's existing home; report
  tokens from a **single** `generator.py` constant the story introduces because **there is none
  today** — the renderer's tokens are inline `if` literals, which is why nothing could validate them.
- **Then** the refusal is reachable from the **guards' own corpus**: it must fire inside
  `build_parser().parse_args`, so `TC-ArgusAgent-DOCS-001-28` (documented invocations must actually
  run) catches a bad token in **every committed invocation** automatically. `argus-student-audit.yml`
  turns RED on that change — **fix the workflow in the same change; do not weaken the check.**
- **Then** this is a **behaviour change on a published surface** and is treated as one: a
  `CHANGELOG.md` entry registered in `_NOTE_SECTIONS` with a **reasoned placement comment** (the
  order is pinned by `-16`), citing the precedent — Story 10.3 made the `--ignore-pattern` layering
  fix the **condition** of its bless and announced it the same way.

### AC4: FR37's next action reaches the CLI — the renderer 12.4 shipped has ZERO production callers

- **Given** FR37 (*"the next action is present in the tool's own output"*) and the measurement:
  **`render_audit_failed_next_action` (`argus/reports/plain_english.py:417`) is referenced only by
  its own `__all__` and `tests/test_outcome_next_action_contract.py`.** Grep over `argus/**` returns
  **zero** production call sites. Meanwhile **both** CLI failure arms print
  `f"{PROG}: audit failed: {exc}"` and stop — cause, no next action.
- **Then** the failure path **renders the existing next action** — extend the shipped mechanism,
  never build a second (AR7; 12.4's own binding words: *"a parallel next-action renderer beside the
  shipped one is a defect, not a delivery"*). The three surfaces that print an audit failure —
  `cli.py`'s audit arm, `cli.py`'s ship-readiness arm, `argus/mcp/server.py:137` — carry the **same**
  words, character for character, exactly as 12.6 required of the success path.
- **Then** the next action is **cause-specific, not generic.** Today's single string
  (*"inspect logs/stderr, verify environment setup, or report unhandled exception if persistent"*)
  is the AUDIT_FAILED **fallback**; a `RepoIntakeError` for a missing path must not be answered with
  *"report an unhandled exception"*. The per-cause remedy is selected by **typed class**, with an
  **exhaustive dispatch that RAISES on an unregistered type rather than falling through to a
  neighbour's remedy** — 12.5 shipped exactly this shape in `_downgrade_sentence` and recorded the
  reason (`DF-10-4-E`'s lesson: a fallthrough hands the operator a remedy that cannot work).
- **Then** a guard **enumerates the typed-failure vocabulary** the way `TERMINAL_OUTCOMES` enumerates
  verdicts, and **fails on an unenumerated one** — the device 12.4 used, at this seam. Non-vacuity
  floor: `> 0` classes enumerated, and each drives a real message.

### AC5: `DF-8-4-D` — an internal defect is DISTINGUISHABLE from an expected degradation

- **Given** `DF-8-4-D` (RELEASE-RELEVANT, `target_story: 12-8-the-tool-explains-itself`) and
  `epics.md:2435-2444`, and the **corrected coordinates**: the epic cites `argus/cli.py:368-372`
  (itself a 2026-08-10 correction of `:295-299`); on `2f84a0b` the arm is at **`argus/cli.py:758-763`**.
  ⚠️ **There are now THREE base-`ValueError` arms in `cli.py`, not the two the citation audit
  recorded** — `:679` (ship-readiness rendering), `:707` (`install-commands`, added by 12.7 and
  therefore invisible to the audit), `:758` (the audit path) — plus a fourth in
  `argus/mcp/server.py:129`. **Anchor on the text, never the line number** (`epics.md:1771`).
- **Then** an internal defect surfaces **as a defect the user can report**, not as a normal outcome:
  a stable, distinguishable stderr token that says plainly *this is a bug in Argus, not a problem
  with your repository*, and where to report it. Pydantic's `ValidationError` **is** a `ValueError`
  subclass, which is the entry's stated mechanism.
- **Then ⚠️ the CLI-level split ALONE does not close it, and this is the trap in this AC.** Measured:
  `argus/pipeline.py:575, 650, 873, 983` already wrap **any** unexpected exception as
  `PipelineError(f"… stage failed: {type(exc).__name__}")`. `PipelineError` is one of the typed
  classes `cli.py`'s comment enumerates, so an internal defect **arrives pre-disguised as an expected
  typed degradation** and a CLI-only `except` split cannot tell them apart. The distinction must be
  carried **from the wrap site** — the smallest honest change is a typed class for it (an
  unexpected-stage-failure subclass) that the renderer dispatches on. Whatever mechanism is chosen,
  **state it and its alternative in the Dev Agent Record.**
- **Then** the exit code stays **`1`** for both — no fifth wire code (AR3 is frozen; AR7: reuse,
  never fork). The distinction is carried in the **message**, which is what the entry asks for.
- **Then** the type name is carried, **never `str(exc)`** — `DF-10-4-C`'s rule and NFR-S1's (see AC6).
- **Then** a test pins **both directions** so the two cannot re-merge: a genuine typed degradation
  (a missing repo path) must **not** print the internal-defect token, and an injected
  `pydantic.ValidationError` at the real seam **must**. Neither direction alone is a guard.
- **Then** `argus/cli.py:19-24`'s module docstring — which enumerates the typed subclasses and says
  *"any `ValueError`"* — is **struck and corrected** to what ships (§3.4). It is the contract
  statement `-35`/`-38` compare against.

### AC6: NFR-S1 — no diagnosis message carries an absolute host path

- **Given** `argus/cli.py:759-761`'s own claim — *"The message names the typed reason only, never
  source / an absolute path"* — and NFR-S1, and the **measured contradiction**:
  `argus/intake/source_state.py:122` raises
  `SourceStateError(f"could not read {rel!r} while pinning source state: {exc}")`, and
  `str(OSError)` is `[Errno 13] Permission denied: 'C:\\Users\\<name>\\…'` — **the absolute host
  path, verbatim, on stderr**. That is the epic's own *"unreadable repo"* case, and it is the one
  case where the published claim and the behaviour disagree.
- **Then** every diagnosis this story touches or emits carries the typed reason and a
  **repository-relative** locator at most — never an absolute host path, never file content, never a
  secret value. The measured raw-`{exc}` interpolation sites reaching the user are
  `intake/source_state.py:122`, `intake/repo_loader.py:122-124` (git's stderr, which routinely
  carries absolute paths), `pipeline.py:886` and `pipeline.py:979`. **Decide each**; a site left
  as-is needs a recorded reason, not silence.
- **Then** the guard is a **property over the surface, not a spot check**: drive the real failure
  paths with a temporary directory whose absolute path is a known string, and assert that string is
  absent from stdout **and** stderr. This is `tests/test_secret_containment.py`'s established shape
  applied to the diagnosis surface; **reuse it, do not fork it.**
- **Then** the same property holds on the **MCP** surface (`argus/mcp/server.py:137` renders the
  same words) — 12.6's parity is a parity of what reaches the consumer, not only of the verdict.

### AC7: A missing or broken grammar reaches the operator on the DEFAULT run

- **Given** `epics.md:2431` names *"missing grammar"*; **`DF-10-4-C`** (`target_story: 12-8`,
  *"the exception detail an operator might want is Story 12.8's surface"*); and 12.5's explicit
  handover — *"`render_grammar_downgrade_summary` is the function 12.8 wires"*.
- **Given** the measured state: `render_grammar_downgrade_summary`
  (`argus/reports/plain_english.py:332`) has exactly **one** production caller,
  `argus/reports/generator.py:516` — which runs **only when `--report-dir` is set**. On the default
  invocation a downgraded grammar is invisible: the operator sees a lower ratio and no reason.
- **Then** the downgrade summary reaches the **default** run's human register (stderr), from the
  **same** function — one renderer, two callers. **Do not copy it, do not re-classify by prefix**:
  `grammar_status.classify_reason` is the single classifier, and its docstring records exactly what
  a second prefix guess costs (silent skip, or `pip install tree-sitter-entrypoint_missing_go`).
- **Then** the plumbing question 12.5 left open is answered **without touching the frozen FR18/AR3
  `AuditVerdict`**: the recommended route is an **additive optional field on `AuditResult`** —
  which is *"a thin value holder (NOT a persisted model)"* (`pipeline.py:321`) and already carries
  three such fields by the same precedent (`floor_report`, `negative_assurance`, `coverage_report`)
  — with `cli.main` calling `run_audit_detailed` instead of `run_audit`. See **DN-4** for the
  measured blast radius (**four** `monkeypatch.setattr(cli, "run_audit", …)` sites) and the
  alternative. **No new persisted artifact, no schema bump, no verdict field.**
- **Then** the exception **class** `DF-10-4-C` asks for is carried **on the rendered surface only**
  — never persisted into the AST index (10.4/DN-5 refused that twice, with reasons) — and the
  entry is **closed, or its remaining scope re-recorded with a reason**, in `deferred-work.md`.
- **Then** it is proven at the **real seam**: patch only the `importlib.import_module` seam
  `tests/test_grammar_diagnosis.py` already uses, run the **real** CLI, and assert the sentence
  reaches stderr on a run with **no `--report-dir`**.

### AC8 (ABSORBED — read the rationale): a usage error must not publish a verdict

> **Absorbed 2026-08-15 by this story, with the reason recorded rather than assumed.** It is not in
> `epics.md`'s Story 12.8 text. It was found by measurement while inventorying this story's own
> surface, it is the single worst *explanation* failure the CLI can produce, and it belongs to no
> other story: 12.9 owns publishing a release, not the exit-code contract; 12.4 owns verdict
> explanation and is `done`; and the arm is `argus/cli.py`'s, which `epics.md:2431` fences to 12.8.
> Leaving it would ship a public CLI that answers a typo with a fabricated assessment.

- **Given** the measurement: **every argparse usage error exits `2`** — `argus audit . --budget 1.5`
  → `2`; `argus bogus` → `2`; bare `argus` → `2` — and **`action.yml:129-132` maps exit `2` to
  `verdict=NOT_READY_FOR_RELEASE` with `assessed=true`**.
- **Given** the corroborating evidence that this project has **already ruled** on the question at
  its other surface: `argus/mcp/server.py:107-112` catches the parser's `SystemExit` and returns
  *"the audit invocation was rejected by the parser"* — **explicitly not a verdict**. The CLI is the
  surface where it is still wrong.
- **Then** a usage error is reported as **no verdict produced**, mapping to the **reserved AR3 crash
  code `1`** — reusing the code the wire contract already publishes for *"the audit did not complete
  and NO verdict was produced"*, and which `action.yml` already renders as `AUDIT_FAILED` /
  `assessed=false` with a `::error::`. **No fifth exit code** (AR3 frozen; NFR-M2 additive-only).
- **Then** `--help` / `-h` still exits **`0`**, unchanged, and `parse_args`' own `SystemExit(0)` is
  re-raised untouched.
- **Then (the seam is load-bearing)** the mapping lives in **`main()`**, NOT in `build_parser()` or
  a parser subclass, so `build_parser().parse_args` stays byte-identical for every guard that
  introspects or drives it — `-28`, `-35`..`-40`, `tests/test_cli_flag_contract.py`,
  `tests/invocation_sources.py:314`, and `argus/mcp/server.py:107`. **DN-5.**
- **Then** the two tests that assert the old shape are **updated deliberately, with the reason
  recorded** — they are your RED evidence, not collateral: `tests/test_cli.py:295-304`
  (`TC-ArgusAgent-CLI-001-05` and `-06`) both use `pytest.raises(SystemExit)` around `cli.main(...)`
  and will fail the moment `main()` returns a code instead. **Do not "fix" them by reverting the
  behaviour.**
- **Then** `action.yml`'s exit-code map comment (`:110-124`), which reasons at length about `1` and
  the catch-all but says nothing about a usage error, is corrected to state what `2` now means and
  cannot mean. `CHANGELOG.md` announces the change; `README.md`'s exit-code statements are checked
  and corrected if they diverge.

### AC9: Every gate and document this story falsifies is CORRECTED, never loosened

**Given** DF-8-5-B's standing rule — *"do not close it by loosening an assertion"* — and the
Epic-11 finding that a stale committed guard publishes a false claim (retro §4.4). Handle each and
record a decision for each:

1. **`tests/test_cli.py`** — `-05` / `-06` (AC8). Updated deliberately, reason in the docstring.
2. **`tests/test_invocation_contract.py`** — the new parity guard (AC2), continuing `CLI-001` from
   `-51`; `derive_arguments`' docstring says `-h/--help` *"is not part of the product's invocation
   contract, and its prose is Story 12.8's"* — that sentence is now half false and is corrected.
   ⚠️ NFR-M1 headroom: **968 / 1200**.
3. **`tests/invocation_sources.py`** — `_INVOCATION_SOURCES` gains `docs/first-run.md` **by glob**,
   with a `> 0` floor (AC1).
4. **`tests/test_release_surface_honesty.py`** — `_RELEASE_SURFACES` **and** a matching
   `_RELEASE_SURFACE_PATTERN` for the new page (AC1); a `CHANGELOG.md` section added to
   `_NOTE_SECTIONS` with a **reasoned** placement comment (order pinned by `-16`).
5. **`tests/test_outcome_next_action_contract.py`** — 12.4's `TERMINAL_OUTCOMES` enumeration is the
   pattern AC4 extends. **Extend, do not fork**; `REPORT-003` continues from `-07`.
6. **`argus/cli.py`** — the module docstring is the contract statement `-35`/`-38` compare against.
   Three blocks become false and are **struck-and-corrected**: the typed-`ValueError` paragraph
   (`:19-24`, AC5), the `--reports`/`--ignore-*` help claims if the help text now carries them
   (AC2), and any statement about what a usage error returns (AC8). **Add no flag** — this story
   adds explanation, not surface. If a flag proves unavoidable, it needs a registry entry **and** a
   findable contract-site anchor (`-38` fails on an anchor it cannot find) — and a recorded reason.
7. **`.github/workflows/argus-student-audit.yml:48`** — `vacuous-tests` corrected (AC3). Verify it
   parses through the real parser afterwards.
8. **`action.yml:110-124`** — the exit-code map comment (AC8).
9. **`README.md` / `CHANGELOG.md`** — the first-run link (AC1), the behaviour-change note (AC3), the
   exit-code note (AC8). Every removal or restatement is a **§3.4 strike-not-delete**, matching the
   form 12.5, 12.6 and 12.7 were each reviewed against.
10. **`docs/README.md`** — the *"Currently empty apart from this file"* sentence (AC1).
11. **`_bmad-output/design-artifacts/ArgusAgent/architecture.md`** — resolve the sites this story
    completes (NFR-R1 / AR10 diagnosis, the CLI entry-point row). **Strike, never delete.**
12. **`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`** — **close `DF-8-4-D` and
    `DF-10-4-C`**, or re-record their remaining scope with a reason. **Cite** `DF-3-4-A`,
    `DF-10-5-C` and `DF-12-7-A`; do **not** re-file them (12.7's recorded rule: *"a gap filed twice
    is a gap that gets closed once and left looking open"*). Append-only.
13. **`tests/test_instrument_disclosure.py`** — two `monkeypatch.setattr(cli, "run_audit", …)` sites
    (`:938`, `:954`) break if AC7 takes the `run_audit_detailed` route (DN-4). Update deliberately.
14. **NFR-M1** — every `argus/**` and `tests/**` `.py` file stays at or under **1200** lines, swept
    by `tests/test_module_size_ceiling.py` over **both** trees (population = `git ls-files -z --
    '*.py'`, re-derived every run). Current headroom: `cli.py` **787**, `pipeline.py` **1044**,
    `plain_english.py` **543**, `generator.py` **909**, `test_invocation_contract.py` **968**,
    `test_cli.py` **355**, `test_instrument_disclosure.py` **1131**.
15. **`tests/test_module_size_ceiling.py::_EXEMPT_BY_DESIGN`** — the exemption for
    `tests/test_grammar_diagnosis.py` (`DF-12-1-C`) names `12-5-…` as its target story; **12.5 is
    `done` and did not split it**. If this story adds to that file, re-record the exemption with a
    live owner, date and reason rather than growing an orphaned one. The registry's own rule is that
    it *"can only shrink"*.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (this project's create-story control, seven-for-seven since Epic 11)

Measured **2026-08-15 on `2f84a0b`** (HEAD; working tree carries only BMAD artifact edits), by
**execution** — the real CLI was driven against fixture repositories — and by file reads, before this
story was written. Per the Epic-11 retro §3.2 refinement, **confirmations are recorded as well as
divergences**.

| Premise, as `epics.md:2421-2444` states it | Re-measured on `2f84a0b` | Consequence |
|---|---|---|
| *"`docs/` contains one integrator-shaped README"* | ❌ **FALSE.** `docs/README.md` is a **BMad tooling stub** (642 B) naming which BMad skills read the folder; it ends *"Currently empty apart from this file."* The integrator-shaped README is the **root** `README.md` (426 lines) | **AC1 / DN-1.** The page's home is a decision, not a given — and `docs/` is BMad's `project_knowledge` root (`_bmad/bmm/config.yaml:15`), so co-tenancy must be stated |
| *"and no first-run surface"* | ✅ **HOLDS** — and stronger than stated: `README.md` contains **zero** occurrences of `docs/`, so nothing links there at all | **AC1.** Reachability is part of the delivery |
| *"every CLI flag Story 10.3 blessed → `--help` states … its default"* | ⚠️ **PARTLY FALSE.** **8 of 19** accepted arguments state no default (§0.1 §A). 10.3's blessed six are split: `--strict`/`--passes` do, `--skip-pass`/`--reports`/`--report-dir`/`--ignore-*` do not | **AC2.** The gap is real but narrower than greenfield — this is a completion, not a rewrite |
| *"an operator error (bad path, unreadable repo, **missing grammar**, absent key under the deep pass)"* | ⚠️ **TWO OF FOUR ALREADY HANDLED.** **absent key under `--deep-audit`** is already excellent (measured verbatim in §0.1 §B row 12, 12.2's work). **`--strict` refusals** already name cause + fix. **bad path** names a cause with no fix and conflates two causes. **missing grammar** is rendered only into a report that requires `--report-dir` | **AC3/AC7.** Do NOT rebuild what ships. The delivery is the **difference** |
| *"`argus/cli.py:368-372` catches the base `ValueError`"* (`DF-8-4-D`) | ⚠️ **LINE STALE, CLAIM HOLDS AND IS WIDER.** The audit arm is at **`:758-763`**. There are **THREE** such arms in `cli.py` (`:679`, `:707`, `:758`) plus one in `mcp/server.py:129`. The citation audit named two and could not have seen `:707` — 12.7 added it | **AC5.** The split must decide **all four sites** |
| `render_audit_failed_next_action` is wired | ❌ **DIVERGES — ZERO production callers.** Grep over `argus/**`: its own `__all__` and nothing else | **AC4.** FR37's next action is satisfied in a test and absent from the tool |
| `render_grammar_downgrade_summary` is reachable on a default run | ❌ **DIVERGES.** One caller, `generator.py:516`, inside the report path — which needs `--report-dir` | **AC7**, and exactly what 12.5 handed over |
| An unknown `--passes` / `--skip-pass` / `--reports` token is rejected | ❌ **DIVERGES — silently accepted.** `resolve_passes` returns `('securty',)`; `enabled_reports` returns `('nope',)`; the pipeline's membership tests simply never match | **AC3.** A typo disables every safety pass and returns exit 0 |
| A usage error is distinguishable from a verdict | ❌ **DIVERGES, and this is the worst of them.** argparse exits **2**; `action.yml:129` maps 2 → `NOT_READY_FOR_RELEASE`, `assessed=true` | **AC8.** A typo publishes a fabricated assessment to a CI consumer |
| The CLI's failure line carries no absolute host path (its own docstring's claim) | ❌ **DIVERGES.** `source_state.py:122` interpolates raw `{exc}`; `str(OSError)` carries the full host path | **AC6.** NFR-S1, at the epic's own *"unreadable repo"* case |
| Test-case id high-water marks | Measured: `CLI-001-**51**`, `DOCS-001-**61**`, `REPORT-002-**37**`, `REPORT-003-**07**`, `RELEASE-001-**24**`, `SECURITY-001-**32**`, `ASSETS-001-**13**`, `MCP-001-**15**` | New ids continue from these. **Open no new area** — see §Testing |
| NFR-M1 headroom | `cli.py` 787 · `pipeline.py` 1044 · `plain_english.py` 543 · `generator.py` 909 · `test_invocation_contract.py` **968** · `test_cli.py` 355 · `test_release_surface_honesty.py` 549 | `test_invocation_contract.py` is the one at risk (AC2/AC9.2) |

### §0.1 — THE INVENTORY: what the tool actually says when the operator gets it wrong

**This table is the core of the story.** Every row was produced by **running the real CLI** on
`2f84a0b` against fixture repositories, or by reading the raise site. Rows are the population AC2 and
AC3 must resolve. Nothing here is quoted from prose.

**§A — `--help`: does it state the default?** (19 accepted arguments, both sub-commands)

| States its default | Does NOT state its default |
|---|---|
| `--commit` (*"Defaults to HEAD"*), `--strict` (*"Off by default"*), `--budget` (*"Omitted / 0 = NO ceiling"*), `--passes` (*"Default: all."*), `--deep-audit` (*"OFF BY DEFAULT, ALWAYS"*), `--coverage-scope` (*"'application' (default)"*), `--host`, `--dest` (*"Defaults to your home directory"*) | **`--materiality-bar`**, **`--critical-subsystem`**, **`--exclude-critical`**, **`--skip-pass`**, **`--reports`**, **`--report-dir`**, **`--ignore-path`**, **`--ignore-pattern`**, `--dry-run`, `--remove`, positional `repo` |

Three of the silent eight also drop a fact their own contract block calls load-bearing: `--reports`
is **inert without `--report-dir`**; `--ignore-pattern` matches by **bare substring**; neither
`--ignore-*` can suppress a live production key.

**§B — operator errors: what the tool prints** (measured by execution unless marked *read*)

| # | Operator input | Measured output | Cause? | Fix? | Verdict |
|---|---|---|---|---|---|
| 1 | `argus audit /no/such/path` | `argus: audit failed: repo path is not a directory: '/no/such/path'` · exit 1 | ✅ | ❌ | **Wrong cause too** — the path does not *exist*; `repo_loader.py:181` has the right message and this path never reaches it |
| 2 | `argus audit README.md` (a file) | **Identical line to row 1** | ✅ | ❌ | Two different causes, one message, two different fixes |
| 3 | unreadable file in the tree | `could not read 'x' while pinning source state: [Errno 13] Permission denied: 'C:\Users\…'` *(read: `source_state.py:122`; `str(OSError)` shape verified by execution)* | ✅ | ❌ | **NFR-S1 LEAK** — absolute host path (AC6) |
| 4 | `--commit deadbeef` (unresolvable) | `commit 'deadbeef' did not resolve to a SHA` *(read; three sites)* | ✅ | ❌ | Cause only |
| 5 | git absent from PATH | `git executable not found on PATH` *(read)* | ✅ | ❌ | Cause only |
| 6 | an unexpected internal exception in a stage | `audit failed: intake stage failed: KeyError` *(read: `pipeline.py:575`)* | ⚠️ | ❌ | **Reads as an expected degradation** — `DF-8-4-D`'s real shape (AC5) |
| 7 | **`--passes securty`** | **nothing** · every pass silently disabled · exit 0 `RELEASE_READY` | ❌ | ❌ | **SILENT — false-green channel** (AC3) |
| 8 | **`--skip-pass securty`** | **nothing** | ❌ | ❌ | SILENT |
| 9 | **`--reports vacuous-tests`** | **nothing** — and this repo's own `argus-student-audit.yml:48` ships it | ❌ | ❌ | SILENT |
| 10 | **`--reports X` without `--report-dir`** | **nothing** rendered, **nothing** said | ❌ | ❌ | SILENT |
| 11 | **`--critical-subsystem does/not/exist`** | **nothing** — but the verdict moved `RELEASE_READY`(0) → `INSUFFICIENT_COVERAGE`(3) | ❌ | ❌ | **SILENT and verdict-affecting** |
| 12 | `--deep-audit` with no provider | `Deep audit: ENABLED, but NO provider endpoint is configured (OPENAI_BASE_URL / OLLAMA_HOST / OLLAMA_URL are all unset), so NOTHING will be transmitted and no deep read will be performed. The pass will degrade and say so; it will not fabricate a deep claim.` | ✅ | ✅ | ✅ **ALREADY EXCELLENT (12.2)** — the register to match. Do not touch |
| 13 | `--strict` on a non-git tree | `--strict requires a git repository (no git metadata found). Drop --strict to audit the directory as-is.` | ✅ | ✅ | ✅ **ALREADY CORRECT** |
| 14 | `--strict` on a dirty tree | `working tree drift: uncommitted changes present (…). Drop --strict to audit the working tree as-is.` | ✅ | ✅ | ✅ ALREADY CORRECT |
| 15 | `install-commands --host nosuch` | `unknown --host value(s) ['nosuch']; this build supports ['claude-code']` | ✅ | ✅ | ✅ ALREADY CORRECT (12.7) — **the model for AC3's refusals** |
| 16 | a downgraded grammar, no `--report-dir` | **nothing** — the sentence exists but only the report renders it | ❌ | ❌ | **SILENT** (AC7) |
| 17 | `argus audit . --budget 1.5` | argparse usage message · **exit 2** → `action.yml` publishes `verdict=NOT_READY_FOR_RELEASE assessed=true` | ✅ | ✅ | ⚠️ **the message is fine; the EXIT CODE fabricates a verdict** (AC8) |
| 18 | `argus resume` / `argus evidence-bundle` | `invalid choice: 'resume' (choose from 'audit', 'install-commands')` · exit 2 | ✅ | ✅ | Adequate as prose — **but row 17's exit-code defect applies.** Do **not** build either command (`DF-3-4-A` / `DF-10-5-C`) |

### Files to touch

**NEW**

| Path | Purpose |
|---|---|
| `docs/first-run.md` | The first-run page — four sections, nothing more (AC1) |

Everything else is a **modification**. This story adds **no `argus/**` module** unless the AC5
mechanism requires one typed class; if it does, it is one small addition, and note that a new
`argus/**` module trips the `DF-10-4-D` artifact-currency guards (Tasks §6).

**UPDATE** — read each completely before editing. What it does today and what must be preserved is
stated so the change is a modification, not a rewrite.

| Path | What it does today | What must be preserved |
|---|---|---|
| `argus/cli.py` (787) | `build_parser()` is the source of truth for the accepted surface (`-35`/`-37`/`-38`). Eight names are **public** (12.6/DN-7, 12.7) and `argus/mcp/**` calls them. `main()` returns an exit code; the wrapper does `sys.exit(main())`. Three base-`ValueError` arms | **Do not change any accepted flag** — 12.6's MCP `inputSchema` and argv projection derive from the `audit` sub-parser (`argus/mcp/protocol.py`). Keep `main()` testable without `sys.exit`. Keep the stderr **order** (`Ship-readiness:` first — pinned by `tests/test_cli.py`) |
| `argus/reports/plain_english.py` (543) | `TERMINAL_OUTCOMES`, `render_audit_failed_next_action`, `render_ship_readiness`, `render_grammar_downgrade_summary`, `ShipReadinessError` | The **PURE, secret-safe** contract — these functions touch no filesystem and emit no absolute path. Extend the existing renderers; add no second one |
| `argus/pipeline.py` (1044) | `run_audit` is a thin wrapper over `run_audit_detailed`. `AuditResult` is *"a thin value holder (NOT a persisted model)"* with three additive optional fields. Four sites wrap unexpected exceptions as `PipelineError(f"… stage failed: {type(exc).__name__}")` | **Persist nothing new.** An added `AuditResult` field must be optional and default-preserving, exactly like `floor_report` / `negative_assurance` / `coverage_report`. NFR-M1 headroom is **156 lines** |
| `argus/intake/source_state.py` (299) / `repo_loader.py` (220) | The typed refusals in §0.1 §B rows 1-5. `source_state.py` already holds the two **best** messages in the tree | Their **voice** — copy it, do not invent a second. `SourceStateError` is a `RepoIntakeError` subclass; the hierarchy is load-bearing for AC5's dispatch |
| `argus/reports/generator.py` (909) | Renders exactly four report types via inline `if "…" in enabled_set` literals — **there is no constant naming them** | AC3 introduces the **one** constant and derives both `cli._DEFAULT_REPORTS`' validation and the refusal message from it. Do not add a second list |
| `argus/shared/grammar_status.py` (563) | `classify_reason` is the **single** classifier; the module deliberately carries no prose and no exception detail | Both refusals stated in its docstring. AC7 renders; it does not persist |
| `argus/mcp/server.py` | Mirrors the CLI's failure wording *"character for character"* (its own comment) and already treats a parser rejection as **not a verdict** | That mirroring — AC4/AC6 change both surfaces or neither |
| `tests/test_cli.py` (355) | `CLI-001-01..`; `-05`/`-06` assert `pytest.raises(SystemExit)`; `-32`/`-33` pin the AR10 typed-failure contract at the **real** site | `-33`'s design (the real renderer at the real call site, not a stand-in). `-05`/`-06` are updated **deliberately** (AC8/AC9.1) |
| `tests/test_invocation_contract.py` (968) | `derive_arguments` (a closure over **every** sub-command since 12.7), `-35`/`-37`/`-38`/`-39`/`-40` | The **derived-not-transcribed** principle and `-39`'s non-vacuity. ⚠️ 232 lines of NFR-M1 headroom |
| `tests/invocation_sources.py` (319) | `_INVOCATION_SOURCES`, `executable_line_numbers`, `parse_failure` — re-exported so `from tests.test_invocation_contract import executable_line_numbers` still resolves | That re-export (12.7 §4) and `SECURITY-001-30`'s repository-scoped single-resolver claim |
| `tests/test_cli_flag_contract.py` (317) | Story 10.3's behavioural criteria for the blessed flags | **`:22` forbids help-text assertions here.** Obey it |
| `tests/test_release_surface_honesty.py` (549) | `_RELEASE_SURFACES`, `_RELEASE_SURFACE_PATTERNS`, `_NOTE_SECTIONS` (order pinned by `-16`), `_OVER_CLAIMS` | Registry **and** pattern, both |
| `tests/test_outcome_next_action_contract.py` (241) | 12.4's `TERMINAL_OUTCOMES` enumeration + the AUDIT_FAILED renderer's only test | Extend; do not fork |
| `tests/test_instrument_disclosure.py` (1131) | Two `monkeypatch.setattr(cli, "run_audit", …)` sites; `-49`'s registered-surface closure | ⚠️ **1131 / 1200.** If AC7 takes the `run_audit_detailed` route these break (DN-4) |
| `.github/workflows/argus-student-audit.yml` | Requests a report type that does not exist (`vacuous-tests`) | It is in `-28`'s corpus — it must parse after AC3 |
| `action.yml` (160) | The complete exit-code map + its reasoning comment | The Story 9.2 / `DF-8-4-A` design: the catch-all is a **failure** token, never a guess |
| `README.md` (426) / `CHANGELOG.md` (972) | Consumer surfaces in `_RELEASE_SURFACES`; the *one measurement, one place* rule at `:152-162` | The **strike-not-delete** amendment form |
| `docs/README.md` | A BMad project-knowledge stub claiming the folder is empty | AC1 |
| `_bmad-output/.../architecture.md`, `deferred-work.md` | §3.4 immutability; append-only ledger | Strike, never delete. Close `DF-8-4-D` + `DF-10-4-C`; **cite** `DF-3-4-A` / `DF-10-5-C` / `DF-12-7-A` |

### Locked decisions this story must cite rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **AR3 exit-code wire contract** — exactly `0`/`2`/`3`/`1`; `1` is the reserved *no verdict produced* code | `argus/cli.py:5-6`, `action.yml:110-124` | AC8 **reuses** `1`. **No fifth code** |
| **FR16 decision table + verdict enum are UNTOUCHED** — no outcome reworded, upgraded or hedged | `epics.md:2312-2314`; 12.4's AC4 | This story explains; it never classifies |
| **`--deep-audit` is THE ONLY OPT-IN TO EGRESS** | `argus/cli.py:113-128` (12.2) | No help text, doc page or diagnosis may suggest a second route to egress |
| **DN-8 (Story 10.3)** — `--coverage-scope` CLI default `application` vs `AuditRequest` default `repository`; both shipped, pinned both ways by `CLI-001-37b` | `argus/cli.py:129-135` | The help text must state the **CLI's** default. Do not "fix" the divergence |
| **12.6 / DN-7** — six `cli.py` helpers PROMOTED to public rather than copied | 12-6 Dev Agent Record | Need a helper? **Promote it**; never copy, never reach through `_`-prefixed API |
| **12.6 / DN-8** — a false registry entry is worse than a coy docstring (the `-49` MCP-token ruling) | 12-6/12-7 | Apply verbatim if a `-49` hit appears |
| **12.7 / DN-12** — *"no host detected" exits 1*, reusing existing wording, **because authoring new diagnosis prose was 12.8's fence** | 12-7 Debug Log §3 | That fence is now **open to you** — and `install-commands`' messages are in AC3's population |
| **10.4 / DN-5 + `DF-10-4-C`** — the exception **type/class only, never the message**; nothing persisted | `grammar_status.py` docstring | AC5/AC6/AC7 |
| **`DF-10-4-E`'s lesson (12.5)** — an exhaustive dispatch **raises** on an unregistered member rather than rendering a neighbour's remedy | 12-5 Dev Agent Record; `_downgrade_sentence` | AC4's per-cause dispatch takes the same shape |
| **AI-E11-1** (Epic-11 retro §3.1) — a guard is adequate only if (i) its observable is named, (ii) the defect is demonstrated to move it **at the real seam**, (iii) at least one adversarial variant is **generated** from the grammar/registry it closes over | Epic-11 retro | Every new guard here meets it |
| **AI-E9-7 / single-source** — never publish a prose copy of a pinned constant | architecture §Enforcement | Why AC1 derives the verdict/exit-code table and AC2 derives the defaults |
| **`DF-8-5-B` / `DF-10-4-D` bootstrap** — commit the `argus/` delta **first**, then regenerate dogfood artifacts, then commit those **separately**; the script **refuses by design** otherwise | 12-5/12-6/12-7 Debug Logs | Applies if AC5 adds an `argus/**` module. Tasks §6 |
| **§3.4 evidence immutability** — supersede, strike, never erase | architecture §3.4 | Every correction in AC1/AC5/AC8/AC9 |

### Decisions taken by this story (record these in the Dev Agent Record; do not re-litigate silently)

- **DN-1 — The first-run page is `docs/first-run.md`, and the `docs/` co-tenancy is stated, not
  hidden.** Three homes were weighed. *(a) Root `FIRST-RUN.md`* competes with `README.md` for the
  first thing a reader sees and splits the integrator surface in two. *(b) A packaged asset under
  `argus/assets/`* would ship in the wheel, but 12.7 established that tree as **command assets with
  no execution authority**, and a prose page there would blur a boundary a whole story was spent
  drawing. *(c) `docs/first-run.md`* is what `epics.md:2421` names, is linkable from the README on
  both GitHub and PyPI, and costs nothing at build time. **Accepted tradeoff, stated rather than
  buried:** `docs/` is BMad's `project_knowledge` root (`_bmad/bmm/config.yaml:15`), so one
  consumer-facing page now co-tenants with a tooling directory. That is recorded in `docs/README.md`
  (AC1) so a later reader does not "tidy" it away, and it is why **reachability is an AC** — an
  unlinked page in a tooling folder is not a first-run surface.
- **DN-2 — Defaults in `--help` are DERIVED from the parser, never typed into prose.** A hand-typed
  default is a transcription of a pinned value, which is the exact class AI-E9-7 forbids and which
  `-35`/`-37` were built to close one layer in. Either `argparse.ArgumentDefaultsHelpFormatter` or an
  explicit `%(default)s` in each help string is acceptable — **state which and why**; the binding
  outcome is that the guard compares rendered help against the **live** `action.default`, so the two
  cannot drift. Rejected: a registry of expected default sentences (a second hand-list — the
  instrument that has been wrong three stories running).
- **DN-3 — CLOSED vocabularies are REFUSED; OPEN ones are DISCLOSED.** `--passes`, `--skip-pass` and
  `--reports` name members of finite, code-defined sets, so an unmatched token is unambiguously a
  mistake and refusal is the honest answer — it is also the only answer that prevents the measured
  false-green. `--critical-subsystem` / `--exclude-critical` take **paths**, which are an open
  vocabulary: refusing a path that matches nothing would break the legitimate case of designating a
  subtree that is absent from this partition, so those are **disclosed on stderr** instead. The
  precedent is this project's own: `_emit_suppression_disclosure` (Story 10.3 / AC4.3) prints on
  **every** run, including when the count is zero, and its docstring records the reason —
  *"a disclosure that only appears when something was hidden is one an operator learns nothing
  from."* `--reports` without `--report-dir` is likewise **disclosed**, not refused: the combination
  is legal, it is simply inert, and refusing it would break a caller who sets the flag conditionally.
- **DN-4 — The grammar diagnosis travels on `AuditResult`, not on `AuditVerdict`.** `AuditVerdict` is
  the **frozen, persisted** FR18/AR3 contract; a field there means a schema bump, an NFR-A1/NFR-M2
  additive review and `test_verdict_schema_bump.py`. `AuditResult` is explicitly *"a thin value
  holder (NOT a persisted model)"* and already carries three optional additive fields added by
  Stories 3.3, 4.1 and 4.3 by exactly this reasoning. **Measured cost, paid deliberately:** `cli.main`
  must call `run_audit_detailed`, which breaks **four** `monkeypatch.setattr(cli, "run_audit", …)`
  sites — `tests/test_cli.py:130`, `:176`, `tests/test_instrument_disclosure.py:938`, `:954` (the
  fifth, `tests/test_mcp_server.py:722`, patches `server.run_audit` and is untouched). `run_audit` is
  a thin wrapper that returns `run_audit_detailed(...).verdict`, so the pipeline call itself is
  byte-identical. **If measurement shows a blocker, the fallback is an optional one-argument sink
  callable handed down like 12.2's `disclose` — but state the reason; do not switch silently.**
- **DN-5 — AC8's usage-error mapping lives in `main()`, never in the parser.** A parser subclass
  overriding `error()` would change `build_parser().parse_args` for every guard that drives it —
  `-28`, `-35`..`-40`, `test_cli_flag_contract.py`, `invocation_sources.py:314` and
  `argus/mcp/server.py:107`, which deliberately catches the parser's `SystemExit` as a
  **non-verdict**. Handling it in `main()` leaves all six untouched. `SystemExit(0)` from `--help`
  is re-raised unchanged; only a usage exit is mapped.
- **DN-6 — No new flag, no new sub-command.** This story adds **explanation**, not surface. Every
  addition to the accepted surface costs a registry entry, a findable contract-site anchor, a help
  string, an MCP-schema check and a README row. If one proves unavoidable, it needs a **recorded
  reason** and all five — and it is not `--resume`, `--verbose`, or `evidence-bundle` (all fenced).
- **DN-7 — One diagnosis vocabulary, three surfaces.** The CLI's audit arm, the CLI's ship-readiness
  arm and `argus/mcp/server.py`'s failure arm say the **same words**; 12.6 made that the contract
  (*"the wording is the CLI's, character for character, so the two surfaces cannot describe one
  failure differently"*) and this story does not weaken it. A message added on one and not the others
  is a fork.

### Testing requirements

- **Framework:** `pytest`, offline, deterministic, no network, no sleeps, no real `$HOME`, no LLM.
  Every test names its `TC-ArgusAgent-<AREA>-001-<n>` id in the docstring alongside the AC it serves.
- **Verification areas — DECIDED: open NO new area.** Each concern has an existing home, and Story
  12.5's rejection of an invented area (`PACKAGING-001`) applies directly: a new area is warranted
  only when **no existing home covers the fact**. It does here:
  - **parser↔help parity → `tests/test_invocation_contract.py`**, `CLI-001` from `-52`. The epic
    says *"alongside 10.3's parser-vs-contract test"*, which is `-35`, and it lives there.
    `tests/test_cli_flag_contract.py:22` forbids it in the other file **by name**.
  - **operator-error diagnosis behaviour → `tests/test_cli.py`**, `CLI-001` continuing. That file's
    own docstring already claims *"a bad repo → exit 1 with a secret-safe stderr line"* — this is
    that claim's home, and it has 845 lines of headroom.
  - **next-action enumeration → `tests/test_outcome_next_action_contract.py`**, `REPORT-003` from
    `-08`, extending 12.4's `TERMINAL_OUTCOMES` device.
  - **grammar downgrade at the CLI → `tests/test_grammar_diagnosis.py`**, which already owns the
    `importlib.import_module` seam and the `INDEX-001` / `REPORT-002` ids. ⚠️ **It is 1203 lines and
    sits in `_EXEMPT_BY_DESIGN` under `DF-12-1-C`, whose `target_story` is `12-5-…` — a story that
    is `done` and did not split it.** So the exemption is **stale**: adding to this file grows an
    exemption nobody now owns. **Decide and record**: either home the new guard here and re-record
    `DF-12-1-C` with a live owner and reason, or split by cohesion (12.7 §4 is the worked
    precedent), or home it in `tests/test_cli.py` beside the other diagnosis guards. Do **not**
    enlarge a stale exemption silently.
  - **first-run page honesty → `tests/test_release_surface_honesty.py`** (`DOCS-001` from `-62`) plus
    the `-28` corpus in `tests/invocation_sources.py`.
- **Every guard meets AI-E11-1.** For each new test state the **observable**, demonstrate the defect
  **moving** it (a RED at the **real seam**, not against a reconstruction), and **generate** at least
  one adversarial variant from the registry/grammar the guard closes over. The five this story most
  needs, with their reds already located for you:
  - **help parity (AC2)** — red by adding a parser argument with no default in its help; the
    adversarial variant is generated from `derive_arguments`' closure, so a **second sub-command's**
    flag must move it too;
  - **unknown-token refusal (AC3)** — red on `--passes securty` **and** on the **real** committed
    line `.github/workflows/argus-student-audit.yml:48`, which is a live instance, not a synthetic;
  - **internal-vs-typed split (AC5)** — **both directions**: a `RepoIntakeError` must not print the
    internal-defect token, an injected `pydantic.ValidationError` must. One direction is half a guard;
  - **no absolute path (AC6)** — red by driving the real failure with a `tmp_path` whose absolute
    string is then searched for in **both** streams;
  - **usage-error exit code (AC8)** — red is already committed: `tests/test_cli.py:295-304`.
- **Non-vacuity floors** on everything that passes by finding nothing (E.3): `> 0` on arguments
  walked, `>= 2` sub-commands reached, `> 0` invocations extracted from `docs/first-run.md`, `> 0`
  typed classes enumerated, `> 0` verdict members compared — so a rename or a move turns the guard
  **RED** rather than silently green.
- **Full suite + static gates:** `python -m pytest -q`; `python -m mypy argus`; `python -m bandit -r
  argus -q` **with a stashed-`argus/` control run proving no NEW finding** — the raw count alone does
  not show that (12.5 §4, repeated by 12.6 and 12.7, is the pattern). A suppression must be justified
  in the Dev Agent Record, never applied quietly.

---

## Tasks & Subtasks

- [x] **Task 1: Re-measure §0 and §0.1 before writing code, and record every divergence (AC1-AC9)**
  - [x] Re-run every §0 and §0.1 measurement on the implementation baseline **by executing the real
        CLI**, and record the figures in the Dev Agent Record — **including confirmations**, not only
        divergences (Epic-11 retro §3.2.2). Confirm the baseline commit in the story frontmatter.
  - [x] Capture the **RED evidence** for every guard this story adds, **before** any `argus/` edit.
  - [x] Confirm by execution: (a) `render_audit_failed_next_action` still has zero production
        callers; (b) argparse usage errors still exit `2` and `action.yml` still maps 2 to a verdict;
        (c) `--passes <typo>` still disables every pass silently; (d) `argus-student-audit.yml:48`'s
        `vacuous-tests` is still unrendered; (e) `str(OSError)` still carries the absolute path
        through `source_state.py:122`.
  - [x] Measure `tests/test_grammar_diagnosis.py` against the NFR-M1 swept population **before**
        adding to it (§Testing flags it at 1203).

- [x] **Task 2: `--help` parity (AC2, DN-2)**
  - [x] Make every argument's default **derived** into its rendered help; add the three
        operator-consequence clauses (`--reports` inert, `--ignore-*` bare-substring + live-key).
  - [x] Parity guard beside `-35`, reusing `derive_arguments(build_parser())`; floors: `> 0`
        arguments, `>= 2` sub-commands.
  - [x] Correct `derive_arguments`' docstring sentence about `--help` prose being 12.8's.

- [x] **Task 3: Operator errors name cause and fix (AC3, AC6, DN-3, DN-7)**
  - [x] Refuse unknown `--passes` / `--skip-pass` / `--reports` tokens **inside `parse_args`**, with
        the accepted set derived from **one** definition each; introduce the single report-token
        constant in `generator.py` (there is none today) and derive both the default and the message.
  - [x] Disclose the open-vocabulary cases: `--critical-subsystem` / `--exclude-critical` matching
        nothing; `--reports` with no `--report-dir`.
  - [x] Give every cause-only message its fix; split `repo path does not exist` from `is not a
        directory` so the two causes reach the user distinctly.
  - [x] Remove the absolute-path leak at `source_state.py:122` and decide the other three raw-`{exc}`
        sites; assert the property over **both** streams.
  - [x] Fix `.github/workflows/argus-student-audit.yml:48` in the same change; confirm it parses.

- [x] **Task 4: Wire FR37's next action and split the typed arms (AC4, AC5, DN-7)**
  - [x] Render the **existing** `render_audit_failed_next_action` on the failure path — per-cause,
        dispatched by typed class, **raising** on an unregistered class (12.5's `_downgrade_sentence`
        shape). One vocabulary across the CLI's two arms and the MCP arm.
  - [x] Make an internal defect distinguishable from an expected degradation — **including the
        `pipeline.py` stage-wrap sites**, which pre-disguise it. Type name only, never `str(exc)`.
        Exit stays `1`. Pin **both** directions.
  - [x] Strike-and-correct `argus/cli.py`'s typed-`ValueError` docstring paragraph.

- [x] **Task 5: Grammar downgrade + first-run page + usage-error honesty (AC1, AC7, AC8, DN-1/4/5)**
  - [x] Route the grammar downgrade to the default run's stderr from the **same** renderer, via an
        additive optional `AuditResult` field; update the four `run_audit` monkeypatch sites
        deliberately. Prove it at the real `importlib` seam with **no `--report-dir`**.
  - [x] Write `docs/first-run.md` (four sections, no tutorial prose); link it from `README.md`;
        derive its verdict/exit-code/command claims by test; register it in `_RELEASE_SURFACES` **and**
        a pattern, and in `-28`'s corpus by glob; assert no diagnosis points the user to it.
  - [x] Map a usage error to exit `1` **in `main()`**; keep `--help` at `0`; update
        `tests/test_cli.py` `-05`/`-06` deliberately with the reason recorded; correct `action.yml`'s
        map comment.

- [x] **Task 6: Correct every gate and document this story falsifies (AC9)**
  - [x] Work AC9's twelve numbered items; record a decision for each, including any left unchanged.
  - [x] `deferred-work.md`: **close `DF-8-4-D` and `DF-10-4-C`** (or re-record remaining scope with a
        reason); **cite** `DF-3-4-A` / `DF-10-5-C` / `DF-12-7-A` without re-filing them.
  - [x] README/CHANGELOG/architecture corrections — **struck, not deleted**; the CHANGELOG section
        registered in `_NOTE_SECTIONS` with a reasoned placement comment.

- [x] **Task 7: Verification gates and the dogfood two-step (AC9.14)**
  - [x] `python -m pytest -q` — green, or every non-green named with its reason.
  - [x] `python -m mypy argus` clean; `python -m bandit -r argus -q` with a stashed-`argus/` control
        proving **no new** finding; any suppression justified in writing.
  - [x] Re-measure every `.py` file against the NFR-M1 1200 ceiling and record the counts.
  - [x] ⚠️ **If this story adds or renames an `argus/**` module the committed-artifact currency
        guards WILL go red.** Follow the `DF-10-4-D` bootstrap in order: (1) commit the `argus/`
        delta, (2) `python scripts/regenerate_dogfood_artifacts.py`, (3) commit the regenerated
        artifacts as a **separate** commit. The script **refuses by design** if run before (1).
        **Do not loosen an assertion to make them green.**
  - [x] **Publish nothing** (12.9): no tag, no index upload, no marketplace listing, no release, and
        no release-status claim anywhere.

---

## Dev Agent Record

### Agent Model Used

Claude Opus 5 (1M context) — `claude-opus-5[1m]`, via the BMAD `bmad-dev-story` workflow.

### Debug Log

**§1 — Task 1: §0 / §0.1 RE-MEASURED on the implementation baseline `2f84a0b`, BY EXECUTION.**
Confirmations are recorded as well as divergences (Epic-11 retro §3.2.2). The real CLI was driven
against a staged fixture repository; `baseline_commit` in the frontmatter is unchanged and correct.

| Premise | Re-measured | Verdict |
|---|---|---|
| `--passes securty` disables every pass silently, exit 0 | `verdict=RELEASE_READY … blocking_findings=0`, **exit 0**, **zero** stderr about the token | ✅ **CONFIRMED — the story's centre of gravity** |
| `--skip-pass securty` silent | exit 0, no message | ✅ CONFIRMED |
| `--reports vacuous-tests` silent | exit 0, no message; `argus-student-audit.yml:48` still ships the token | ✅ CONFIRMED |
| argparse usage errors exit `2` | `--budget 1.5` → 2, `argus bogus` → 2, bare `argus` → 2, `--help` → 0 | ✅ CONFIRMED |
| `action.yml` maps 2 → `NOT_READY_FOR_RELEASE assessed=true` | read at `:129-132` | ✅ CONFIRMED |
| `render_audit_failed_next_action` has zero production callers | grep over `argus/**`: its own `__all__` and nothing else | ✅ CONFIRMED |
| `render_grammar_downgrade_summary` reachable only via `--report-dir` | one caller, `generator.py:516`, inside `if request.report_dir:` | ✅ CONFIRMED |
| `str(OSError)` carries the absolute host path | `"[Errno 2] No such file or directory: '/…/x.py'"` | ✅ CONFIRMED |
| two bad-path causes render one message | `/no/such/path` and `README.md` both → *"repo path is not a directory"* | ✅ CONFIRMED |
| `README.md` contains zero `docs/` occurrences | `grep -c 'docs/' README.md` → **0** | ✅ CONFIRMED |
| `docs/README.md` is a BMad stub ending *"Currently empty apart from this file"* | read, 642 B | ✅ CONFIRMED |
| `test_grammar_diagnosis.py` at 1203 lines, exempt under `DF-12-1-C` | 1203; exemption's `target_story` is 12-5, which is **done** | ✅ CONFIRMED **and orphaned** |
| CLI-001 high-water `-51` | **CORRECTION:** `-49` (`test_cli_flag_contract.py:292`), `-50`/`-51` (`test_instrument_disclosure.py`) are taken. New ids start at **`-52`** |
| `DF-8-4-D`'s arm coordinates | audit arm at `cli.py:758`; three arms in `cli.py`, fourth in the second surface | ✅ CONFIRMED |

**RED evidence captured BEFORE any `argus/` edit** — every guard this story adds was demonstrated
failing against `2f84a0b`'s behaviour: the six exit codes above, the three silent tokens, the two
identical bad-path lines, the absent grammar sentence on a default run, and the eight `--help`
strings with no default. `tests/test_cli.py:295-304` (`-05`/`-06`) was already-committed RED for AC8.

**§2 — DECISIONS taken, with the alternative stated (the story's DN-1..DN-7 honoured; new ones numbered D8+).**

- **DN-2, resolved: `ArgumentDefaultsHelpFormatter`, not per-flag `%(default)s`.** One line per
  sub-parser versus 19 hand-edited help strings; more importantly a THIRD sub-command's flags inherit
  it with **no edit anywhere**, which is the property that makes the parity guard a closure rather
  than a list. `%(default)s` would have been 19 opportunities to forget one.
- **AC2's three "arguably implied" arguments, decided explicitly rather than by omission.**
  `--dry-run` and `--remove` are **not** exempt: a `store_true` has a real default (`False`) and
  stating it is what tells an operator that omitting the flag is a live choice. Positional `repo`
  **is** exempt, with the reason in `_HELP_DEFAULT_EXEMPT`: it is required, there is no fallback
  value, and `(default: None)` would state a falsehood. The registry is asserted to shrink only.
- **D8 — `ClosedVocabulary` is a CLASS with a public `accepted` attribute, not a closure.** The
  refusal had to fire inside `parse_args` (AC3), so it is an argparse `type=`. That broke
  `TC-ArgusAgent-CLI-001-36`, which drives every registered spelling through the real parser with the
  fixed placeholder `"x"` — no longer a legal value. The alternative was a hand-list of *"a valid
  `--passes` value"* in the guard, i.e. the second hand-list AR7 forbids and the `_CONSOLE_SCRIPTS`
  defect class this project has recorded four times. Exposing the live accepted set means `-36`
  derives its sample and a future closed-vocabulary flag is covered with no edit.
- **AC5 mechanism — a TYPED SUBCLASS at the wrap site, and the alternative is stated (AC5 requires
  this).** Chosen: `pipeline.UnexpectedStageError(PipelineError)` raised by the four stage wraps.
  Rejected: a boolean/flag attribute on `PipelineError` set at the same sites — it needs no new class,
  but an attribute is invisible to `except`, so every consumer would have to remember to read it, and
  a distinction a caller can forget to check is the one that goes back to being silent. A type is
  checked by the language. Also rejected: a fifth exit code (AR3 is frozen; AR7 reuse-never-fork).
- **D9 — `UnexpectedStageError` is deliberately ABSENT from `argus.pipeline.__all__`.**
  `tests/test_pipeline_split_surface.py` holds that list against the IMMUTABLE pre-split blob
  `ca37283:argus/pipeline.py` (`-15`), so it cannot accommodate an addition without being re-anchored
  — a second, unrelated published-surface change inside a story whose DN-6 says it adds explanation
  and not surface. The class is fully importable (`__all__` governs only `import *`), documented at
  its definition and in `cli.py`'s contract block, and enumerated where the enumeration is
  load-bearing (`plain_english.TYPED_FAILURE_CLASSES`, closed over the real classes by
  `TC-ArgusAgent-REPORT-003-08`). **The guard was NOT loosened; the surface was left alone.**
- **D10 — the next-action dispatch is keyed by class NAME, and `ValueError` is a REGISTERED member.**
  `plain_english` is PURE and is imported BY `pipeline.py`, so importing the pipeline's or the
  intake's exception classes would invert that arrow (AR8) and create a cycle. Names it is, with
  `TC-ArgusAgent-REPORT-003-08` closing the registry over the real `ast`-walked classes so a phantom
  entry fails. Registering base `ValueError` is what makes the dispatch **total** over everything
  `except ValueError` can catch — without it the "raise on unregistered" arm would fire INSIDE an
  exception handler and put a traceback in front of a user (NFR-R1). It is not a fallthrough: the
  internal-defect remedy is the correct and only honest answer for an unregistered typed failure, and
  `-09` asserts that split in both directions.
- **D11 — `argus/commands/**`'s three typed errors are enumerated too.** Without their own arms
  `UnknownHostError` would have inherited the base-`ValueError` remedy and an unregistered `--host`
  would have been reported to the operator as a bug in Argus. Found by writing `-09`'s both-direction
  assertion, not by inspection.
- **AC6 — each raw-`{exc}` site decided, including the two left alone.**
  `intake/source_state.py:122` **fixed** (type name only — this was the measured NFR-S1 leak).
  `intake/repo_loader.py:122-124` **fixed**: git's stderr routinely carries absolute paths
  (`fatal: not a git repository … : /home/<name>/…`), so the exit code plus the sub-command is the
  typed reason and the fix names the command the operator can run themselves.
  `pipeline.py:886` and `:979` **left as-is, with the reason**: both interpolate Argus-AUTHORED
  exceptions (`StoreIntegrityError`, `CanonicalSerializationError`, `ResumeError`) whose own contracts
  are relative-locator-only — verified by reading their raise sites — so they carry no host path, and
  both sit on the resume path, which has no CLI entrance at all today (`DF-3-4-A`, cited not built).
  Changing them would have been churn on unreachable code.
- **D12 — `INTERNAL_DEFECT_MARKER` / `ALL_REPORTS_SELECTOR` are named `…_MARKER` / `…_SELECTOR`
  rather than the house `…_TOKEN`.** `bandit`'s `B105` fires on any constant whose NAME contains
  `token`; a first draft named them `…_TOKEN` and the stashed-`argus/` control run showed **19 → 21**,
  i.e. two NEW findings. Rejected: this repository's first `# nosec` — a suppression mechanism is easy
  to reach for the second time, and the count would still have grown. Recorded because it IS a
  deliberate departure from the naming used elsewhere in the tree (`CORE_RUNTIME_TOKEN`), whose own
  B105 hits predate this story. After the rename the control diff is **empty**.
- **D13 — `parse_failure` read `SystemExit(0)` as a rejection, and that is CORRECTED, not worked
  around.** `docs/first-run.md` documents `argus audit --help`, which argparse ACCEPTS and answers
  with exit `0`; `-28` reported it as *"argparse rejected the documented command line"* — a guard
  asserting the opposite of what happened, and one structurally unable to admit a documented `--help`
  anywhere in the corpus. Exit `2` is still a failure there. The alternative (excluding `--help` lines
  from the corpus) would have narrowed the population, which this project files as a defect.
- **D14 — the CLI-level grammar guard is homed in `tests/test_cli.py`, not in
  `tests/test_grammar_diagnosis.py`.** §Testing named the choice. That file is 1203 lines under an
  ORPHANED exemption (`DF-12-1-C`'s target story is `done` and did not split it), so adding to it
  would grow an exemption nobody owns. The exemption's reason and target are **re-recorded in place**
  with a live date and a `NONE — unscheduled` target that the ledger now carries verbatim
  (`TC-ArgusAgent-MAINT-001-04` requires the two strings to agree).

**§3 — Two guards found unable to fail as written, and CORRECTED with the new form proven to bite.**
This repository treats an unfailable guard as a defect; both were found while writing this story's own
guards and neither was loosened.
1. **`-63`'s verdict-shape probe** matched `[A-Z][A-Z_]{5,}` and flagged the word `README` on the
   first-run page — a guard failing on the wrong observable. Narrowed to SCREAMING_SNAKE_CASE
   (`\b[A-Z]+(?:_[A-Z]+)+\b`), which is what a verdict token actually is, **with an inline positive
   control** proving it still matches `PROBABLY_FINE` and no longer matches `README`.
2. **`-65`'s pointer probe** searched for the bare phrase `first-run` and flagged `argus/pipeline.py`,
   which says *"a first-run / no-prior-state signal"* about the resume seam. Narrowed to the PATH
   `docs/first-run.md` — what a citation actually carries — **with a positive control** asserting the
   narrowed form still recognises a real citation, so it cannot pass merely because nobody wrote one.
Also corrected, and recorded as a re-derivation rather than a lowering:
3. **`TC-ArgusAgent-REPORT-002-31`'s `_MIN_WRITE_TEXT_CALLS = 4`.** Counting `write_text` calls was a
   proxy for *"the four reports are still written here"*, valid only while they were four copy-pasted
   branches. AC3 required ONE constant naming the report types, and a constant BESIDE four
   hand-written branches is a parallel list that drifts. The branches became one loop over
   `RENDERED_REPORT_TYPES`, so the floor is now asserted against **that constant's length** plus a
   check that the loop still iterates it. The guard is STRONGER — a fifth report type is routed
   through `_with_instrument_disclosure` by construction, which is that guard's own remedy sentence
   (*"route it, do not enumerate it"*) — and `-32`'s positive control is untouched.

**§4 — NFR-M1: the split, taken by the remedy rather than by shaving.** Adding AC2's parity guards put
`tests/test_invocation_contract.py` at **1277 / 1200**. Applied 12.7's remedy exactly: a COHESION
split into `tests/test_help_contract.py` — *does `--help` DESCRIBE the parser?* closes over the
argparse FORMATTER; *does the REGISTRY equal the parser?* closes over contract sites — with no
function split across the boundary, `live_actions` imported rather than re-implemented, and **no line
shaved and no population narrowed**. Final counts: `test_invocation_contract.py` **1036**,
`test_help_contract.py` **286**, `cli.py` **1139**, `pipeline.py` **1111**, `plain_english.py` **758**,
`generator.py` **940**, `test_cli.py` **853**, `test_release_surface_honesty.py` **794**,
`test_outcome_next_action_contract.py` **467**, `test_instrument_disclosure.py` **1179**,
`invocation_sources.py` **344**. ⚠️ **`cli.py` now has 61 lines of headroom and
`test_instrument_disclosure.py` 21** — recorded so the next story does not discover it.

**§5 — Gates.**
- `python -m pytest -q` → **1524 passed, 3 failed**. All three are the known `DF-10-4-D`
  artifact-currency class and nothing else:
  `tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`,
  `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`,
  `tests/test_dogfood_proof.py::test_red_first_vacuously_satisfied_critical_gate_is_named`.
  They move because `argus/**` composition moved (`git ls-files` reports the INDEX). **Not loosened,
  not xfailed, not skipped, and the artifacts were not hand-edited**; the regeneration script refuses
  by design until the `argus/` delta is committed, and this story does not commit.
- `python -m mypy argus` → **Success: no issues found in 83 source files.**
- `python -m bandit -r argus -q` → **21 Low / 0 Medium / 0 High**, and the STASHED-`argus/` control run
  is **19 Low**. The two-finding delta was the `…_TOKEN` naming above; after the rename the CSV diff
  between control and current is **empty — zero new findings**. No suppression was applied anywhere.
- **Published nothing** (12.9's fence): no tag, no index upload, no marketplace listing, no release,
  no release-status claim. `release.yml` and `git tag` were not touched.

**§6 — AC9's items, each with its disposition.**
1. `tests/test_cli.py` `-05`/`-06` — updated deliberately, reason in both docstrings, plus `-55`
   proving `--help` is not over-caught. 2. `tests/test_help_contract.py` `-52`/`-53`/`-54`;
   `derive_arguments`' *"its prose is Story 12.8's"* sentence struck-and-corrected in place.
3. `tests/invocation_sources.py` gains `docs/*.md` by glob with a `> 0` floor in `-39`.
4. `_RELEASE_SURFACES` + `_RELEASE_SURFACE_PATTERNS` both gain the docs pages; the CHANGELOG section
   is registered FIRST in `_NOTE_SECTIONS` with a reasoned placement comment (it is the only entry in
   the note that can break an existing pipeline on an unchanged repository). 5. `REPORT-003` extended
   from `-08`, not forked. 6. `cli.py`'s docstring: the typed-`ValueError` paragraph struck and
   corrected, the `--help`/refusal/usage-error contracts added; **no flag added** (DN-6 held).
7. `argus-student-audit.yml:48` corrected to `architecture-review` and re-verified through the real
   parser by `-28`. 8. `action.yml:110-124` comment corrected to state what `2` now cannot mean.
9. README (first-run link) + CHANGELOG (the behaviour-change note) — struck, never deleted. **README's
   exit-code statements were CHECKED and do not diverge**: it makes no numeric exit-code claim.
10. `docs/README.md`'s *"Currently empty"* struck-and-corrected, with DN-1's co-tenancy named.
11. `architecture.md`: the AR3 exit-code row, the CLI entry-point row, the invocation-contract
    enforcement block and a new **Operator-diagnosis enforcement** block — struck/appended, never
    deleted. 12. `deferred-work.md`: `DF-8-4-D` **CLOSED**, `DF-10-4-C` **partially closed with its
    remaining scope re-recorded and a reason**; `DF-3-4-A`, `DF-10-5-C`, `DF-12-7-A` cited and **not**
    re-filed. Append-only, `+n / -0`. 13. `test_instrument_disclosure.py`'s two `run_audit`
    monkeypatch sites updated deliberately (DN-4), as were `test_cli.py`'s two. 14. NFR-M1 swept and
    recorded in §4. 15. `DF-12-1-C`'s exemption re-recorded with a live date and an honest target
    rather than grown.

**§7 — Review fix iteration 1 (2026-08-15): the one Low finding, resolved by NARROWING THE PROSE.**
The finding is the story's own subject matter turned on the story: `docs/first-run.md:10-11` claimed
*"Everything on it is checked by a test against the code, not transcribed from it"* — a published
claim no test backs, in the epic whose purpose is eliminating exactly that, and contradicted twenty
lines later by the page's own install caveat (*"the documented shape, not an exercised capability"*).

**Two shapes were available and the choice is recorded rather than assumed.**
- **(b) Widen the derivation until the sentence becomes true — REJECTED, and not on cost grounds: it
  is unachievable in principle here.** The unchecked claim is the `pip install "argus-agent @
  git+…@v0.1.0"` line, and it is unexercisable BY DESIGN in this story: tag `v0.1.0` does not exist,
  and creating or publishing one is **Story 12.9's fence** (`epics.md:2446-2473`), which this story
  may not cross. Exercising it would also require network egress, which the test contract forbids
  (*offline, deterministic, no network*). A guard that "checked" it could therefore only check the
  string's SHAPE, which is transcription wearing a test's clothes — the `_CONSOLE_SCRIPTS` defect
  class again. Verified by execution that `extract_documented_invocations()` extracts exactly the
  three fenced `argus …` lines from this page (`argus audit .`, `argus audit --help`,
  `argus audit . --report-dir ./argus-reports`) and correctly does NOT touch the `pip` line.
- **(a) Name precisely what is derived — TAKEN.** The opening now reads *"The verdict vocabulary, the
  exit codes and every `argus …` command line on this page are checked by a test against the code,
  not transcribed from it."* Those three are **exactly** AC1's enumerated checkable claims and
  **exactly** what the shipped guards enforce: `TC-ArgusAgent-DOCS-001-63` (verdict vocabulary vs the
  live `Verdict` enum), `-64` (the exit column vs `exit_code_for_verdict` + the reserved `1`), and
  `-28`/`-39` (every fenced `argus …` line through the real `build_parser().parse_args`, with a
  `> 0` floor from the `docs/*.md` glob). A following sentence resolves the self-contradiction the
  reviewer found rather than leaving it: the rest is prose, and where a documented command is not an
  exercised capability the page says so **at that command** — which is what the install caveat
  already does, so the opening and the caveat now agree instead of contradicting.

**Considered and rejected: a guard pinning the new sentence's wording.** It would assert prose
against prose — no code observable — and would go RED on a rewording rather than on a falsehood,
which is the unfailable/wrong-observable class §3 records twice already. The sentence's honesty is
enforced where it can be: the three named facts each have a guard that turns RED if the page drifts
from the code, which is the property the claim now asserts and nothing more.

**Scope held.** Docs-only, four lines of prose on one page. No `argus/**` composition change, so the
`DF-10-4-D` artifact-currency guards stay green and no dogfood regeneration is needed. No locked
decision reopened, no test loosened, xfailed or skipped, no gate touched. Gates re-run after the
edit: `python -m pytest -q` → **1527 passed, 0 failed, 0 errors, 0 skipped** (junit-xml:
`tests="1527" failures="0" errors="0" skipped="0"`); `python -m mypy argus` → **Success: no issues
found in 83 source files**; `python -m bandit -r argus -q` → **19 Low / 0 Medium / 0 High**,
identical to the review's independently measured control count.

### Completion Notes

**What shipped, in one line each.**

- **AC1** — `docs/first-run.md` (four sections, no tutorial prose), linked from `README.md` with the
  link target asserted to resolve; the verdict vocabulary, the AR3 exit-code column and every `argus …`
  line on it are DERIVED by test; it is in `-28`'s corpus by glob and in both release-surface
  registries; and `TC-ArgusAgent-DOCS-001-65` asserts **no diagnosis, help string or report line
  points the user at it** — the page orients a first run and is never where the answer lives (FR37).
- **AC2** — every argument's rendered `--help` now states the default the parser actually holds,
  derived by formatter; parity asserted over `derive_arguments`' closure with `> 0` arguments and
  `>= 2` sub-commands; three operator-consequence facts pinned by exact substring.
- **AC3 — the centre of gravity.** `--passes` / `--skip-pass` / `--reports` refuse an unknown token
  INSIDE `parse_args`, against the one definition of each (`_ALL_PASSES + LLM_DEEP_PASSES`;
  `generator.ACCEPTED_REPORT_TOKENS`, a constant this story had to introduce because there was none —
  which is exactly why nothing could validate a report token). **The measured false-green is closed:
  `--passes securty` no longer returns `RELEASE_READY` exit 0 over a run that examined nothing.** The
  open vocabularies are disclosed instead, and every cause-only message gained its fix.
- **AC4** — `render_audit_failed_next_action` has production callers for the first time: both CLI arms
  and the second invocation surface, per-cause by typed class, raising on an unregistered type.
- **AC5** — `DF-8-4-D` closed at the WRAP SITE, not only at the CLI arm; both directions pinned.
- **AC6** — the NFR-S1 leak at `source_state.py:122` is gone, asserted as a property over both streams
  in every spelling a path can wear (the `repr`-escaped form is the one a naive check misses).
- **AC7** — 12.5's handover wired: the downgrade sentence reaches the DEFAULT run from the same
  renderer, via an additive `AuditResult` field; nothing new persisted.
- **AC8** — a usage error returns `1`, in `main()` only; `--help` still `0`; `action.yml` corrected.
- **AC9** — every falsified gate and document corrected, never loosened; two unfailable guards found
  and fixed with their new forms proven to bite.

**Honest residuals, stated rather than left to be found.** (a) ~~The three `DF-10-4-D` dogfood
artifact-currency guards are RED and stay RED until the commit → regenerate → commit bootstrap, which
this story may not perform.~~ **SUPERSEDED 2026-08-15 (§3.4 strike-not-delete): the bootstrap was
performed as recorded — `argus/` delta committed (`2826c51`), artifacts regenerated and committed
separately (`6efa306`) — and all three guards are GREEN. Re-confirmed in fix iteration 1: the full
suite is 1527 passed / 0 failed with no artifact regenerated, because this iteration changed no
`argus/**` composition.** (b) `DF-10-4-C`'s exception-CLASS payload is NOT delivered and is
re-recorded as unscheduled with its reason. (c) `cli.py` has 61 lines of NFR-M1 headroom and
`test_instrument_disclosure.py` has 21. (d) `--critical-subsystem`'s unmatched-path disclosure probes
the filesystem from `cli.py`, which is a (small) deliberate exception to *no business logic in the
entry point*: it is a disclosure detail rather than audit logic, the pure sentence lives in
`plain_english`, and the probe FAILS OPEN so a resolution quirk can never turn into a false accusation
about the operator's input.

### File List

**NEW**
- `docs/first-run.md`
- `tests/test_help_contract.py`

**MODIFIED — `argus/`**
- `argus/cli.py`
- `argus/pipeline.py`
- `argus/reports/plain_english.py`
- `argus/reports/generator.py`
- `argus/intake/source_state.py`
- `argus/intake/repo_loader.py`
- `argus/shared/grammar_status.py`
- `argus/mcp/server.py`

**MODIFIED — `tests/`**
- `tests/test_cli.py`
- `tests/test_invocation_contract.py`
- `tests/invocation_sources.py`
- `tests/test_release_surface_honesty.py`
- `tests/test_outcome_next_action_contract.py`
- `tests/test_instrument_disclosure.py`
- `tests/test_cli_flag_contract.py`
- `tests/test_module_size_ceiling.py`

**MODIFIED — consumer surfaces and artifacts**
- `README.md`
- `CHANGELOG.md`
- `action.yml`
- `docs/README.md`
- `.github/workflows/argus-student-audit.yml`
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md`
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`
- `_bmad-output/design-artifacts/ArgusAgent/stories/12-8-the-tool-explains-itself.md`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`

### Review Findings

**Review performed 2026-08-15** (adversarial code review, `bmad-code-review` workflow) against
`git diff 2f84a0b..HEAD` (commits `2826c51` + `6efa306`). Independently re-verified by execution:
`pytest -q` → **1527 passed, 0 failed** (junit-xml confirmed: `errors="0" failures="0" tests="1527"`,
including the three `DF-10-4-D` dogfood-currency tests, now green after the `6efa306` regeneration
commit); `mypy argus` → **clean, 83 files**; `bandit -r argus -q` → **19 Low / 0 Medium / 0 High**,
matching the Dev Agent Record's claimed stashed-control count, confirming the `…_MARKER`/`…_SELECTOR`
rename genuinely cleared B105 with no `# nosec` added. All nine ACs were independently verified by
reading the diff and, for the highest-risk claims, by running the real CLI (`--passes securty`,
`--skip-pass securty`, `--reports vacuous-tests`, `audit . --budget 1.5`, `--help` rendering) and
confirming the measured behavior matches what the story claims. The false-green channel (AC3) is
closed on every reachable path (CLI, MCP `audit_repository` — verified it drives the same
`build_parser().parse_args`, shipped command assets, `action.yml`, the workflow file); the exit-code
contract change (AC8) is isolated to `main()` as `build_parser().parse_args` is untouched; the new
`pipeline.UnexpectedStageError` (AC5) is correctly excluded from the two genuinely-typed `except`
clauses ahead of the wrap sites so it cannot misclassify a real `RepoIntakeError`/`SourceStateError`/
`WorkspaceContainmentError`; the four `run_audit_detailed` monkeypatch sites (DN-4) are all updated
correctly; the NFR-M1 split (`tests/test_help_contract.py`) drops no assertion and narrows no
population (verified: positive control `-53` proves the guard bites, `-54`'s exact-substring
assertions render live via `argus audit --help`); the `DF-12-1-C` exemption re-record and the
`DF-8-4-D`/`DF-10-4-C` ledger closures are append-only and cross-consistent with the test registry.

- [x] [Review][Patch] **RESOLVED 2026-08-15 (fix iteration 1) — see Debug Log §7.** `docs/first-run.md`'s opening claim overclaims what AC1 actually derives
  [docs/first-run.md:10-11]. The page states *"Everything on it is checked by a test against the
  code, not transcribed from it"* — but the page's own install section, twenty lines below, admits
  the opposite of its own leading claim: *"⚠️ This command does not resolve today... It is the
  documented shape, not an exercised capability"* (docs/first-run.md:30-33). Verified by execution
  that `tests/invocation_sources.py::extract_documented_invocations()` only extracts the three
  `argus …` command lines from this page (`argus audit .`, `argus audit --help`,
  `argus audit . --report-dir ./argus-reports`) — the `pip install` line is correctly NOT parsed
  or checked by any test, exactly as the page's own caveat says. AC1 itself only commits to three
  specific checkable facts being derived (verdict vocabulary, exit codes, `argus …` command lines) —
  not literally "everything" — so this is the page's own prose overclaiming its own certainty, which
  is a minor irony in a story about the tool not overclaiming. Low severity: no functional or
  security impact, and the enumerated AC1 facts are genuinely all derived by test as verified above.
  Suggested fix: reword the opening sentence to name what is actually checked, e.g. *"The verdict
  vocabulary, the exit codes and every `argus …` command line on this page are checked by a test
  against the code, not transcribed from it."*

  **RE-REVIEW CONFIRMATION 2026-08-15 (code review, iteration 2, final).** Resolution verified
  genuine, not a reword that still overclaims: every claim the new sentence makes is independently
  re-derived as actually enforced (`-63`/`-64` for the verdict vocabulary and exit codes; the
  `docs/*.md` glob + `_CONSOLE_SCRIPTS` filter in `tests/invocation_sources.py` for "every
  `argus …` command line" — the `pip install` line's first token is `pip`, correctly excluded);
  "the rest is prose" is accurate (no other guard touches this page); the opening and the install
  caveat at `:32-35` now agree. Both rejected alternatives (widening the derivation to the
  pip-install line; pinning the new sentence's prose in a guard) judged sound under this repo's own
  conventions (Story 12.9 owns the tag; this repo's tests are established network-free; DN-2 already
  rejected pinning prose for the identical reason). No regression: full suite green
  (`tests="1527" errors="0" failures="0" skipped="0"`), `mypy` clean, `bandit` byte-identical
  (19 Low / 0 Medium / 0 High). See Change Log for the full record.

## Change Log

| Date | Change |
|---|---|
| 2026-08-15 | **Code review, iteration 2 — RE-REVIEW of the fix (`bmad-code-review`, Sonnet 5). VERDICT: PASS. Status `review` → `done`.** Scope was narrowed to the single Low finding from iteration 1 and a no-regression sweep, per the orchestrator's fix-cap instructions (this is the final iteration). **The finding is genuinely resolved, not reworded away.** Read `git diff 6efa306..de05dec` in full (3 files, docs-only). Verified by execution that every claim the new opening sentence makes is actually enforced: `test_TC_ArgusAgent_DOCS_001_63_the_verdict_vocabulary_on_the_page_is_derived` and `-64_the_exit_codes_on_the_page_are_the_AR3_mapping` both pass and genuinely check the verdict vocabulary and exit-code table against the live `Verdict` enum / `exit_code_for_verdict`; `tests/invocation_sources.py::extract_documented_invocations()` genuinely extracts and parses all three (and only the three) `argus …` lines on the page via the `docs/*.md` glob and `_CONSOLE_SCRIPTS` filter — the `pip install …` line's first token is `pip`, not a console script, so it is correctly EXCLUDED from "every `argus …` command line", never overclaimed. Confirmed the new second sentence ("the rest is prose … flagged at that command") makes no claim the page's own content contradicts: grepped `test_release_surface_honesty.py` and found no guard checks anything else on the page besides the four DOCS-001-62/63/64/65/66 properties, so "the rest is prose" is accurate, and the `pip install` caveat at `docs/first-run.md:32-35` states plainly, at that command, that it "does not resolve today … is the documented shape, not an exercised capability" — the opening and the install caveat now AGREE where they contradicted before. **Both rejections judged sound, not rationalised avoidance:** widening the derivation to check the pip-install line would need to resolve a real `git+https://…@v0.1.0` ref, and (a) that tag is explicitly Story 12.9's fence per this story's own "What it is NOT" table (`epics.md:2446-2473`, cited above), not 12.8's to create, and (b) this repo's own test corpus is independently established as network-free (`tests/test_mcp_server.py`: "Offline, deterministic, no network"; `tests/test_workflow_input_containment.py`: "no network"), so a guard could only pattern-match the URL's shape, which would be exactly the transcription-not-derivation AI-E9-7 forbids. Pinning the new sentence's exact prose in a guard was also correctly rejected: it would compare prose against prose and go RED on a rewording rather than a falsehood, the identical reasoning this story's own DN-2 already used to reject "a registry of expected default sentences (a second hand-list — the instrument that has been wrong three stories running)". **No regression:** re-ran the full suite with `--junit-xml`: `tests="1527" errors="0" failures="0" skipped="0"` (junit-xml parsed directly, not read off the terminal), including the three `DF-10-4-D` dogfood-currency tests, still green and unmoved — correct, since this change touched no `argus/**` composition; `mypy argus` → clean, 83 source files; `bandit -r argus -q` → 19 Low / 0 Medium / 0 High, byte-identical to iteration 1's count. The story's own `[Review][Patch]` item is checked off with a dated resolution note, and `sprint-status.yaml` carries the fix-iteration record with the STATUS DEFINITIONS block and full prior-round history intact (verified by direct read). No unresolved `decision-needed` or `patch` item remains; no new finding raised. All nine ACs independently re-confirmed as still met (no code outside `docs/first-run.md` moved in this round). |
| 2026-08-15 | **Code-review findings addressed (`bmad-dev-story`, fix iteration 1) — 1 of 1 resolved. Status `in-progress` → `review`.** The single Low `[Review][Patch]` finding was the story's own subject turned on the story: `docs/first-run.md:10-11` published *"Everything on it is checked by a test against the code, not transcribed from it"* — a claim no test backs, contradicted twenty lines later by the page's own install caveat. **Resolved by narrowing the prose to what the guards actually enforce** (Debug Log §7): the opening now names the verdict vocabulary, the exit codes and every `argus …` command line — exactly AC1's three enumerated checkable claims and exactly what `TC-ArgusAgent-DOCS-001-63`, `-64` and `-28`/`-39` derive from the live `Verdict` enum, `exit_code_for_verdict` and the real `build_parser().parse_args` — and a following sentence states that the rest is prose and that a documented-but-unexercised command is flagged **at that command**, so the opening and the install caveat now agree instead of contradicting. **Widening the derivation instead was rejected on principle, not cost:** the unchecked claim is the `pip install …@v0.1.0` line, whose tag is **Story 12.9's fence** to create and whose resolution needs network egress the test contract forbids — a guard could only have checked its SHAPE, which is transcription wearing a test's clothes. A guard pinning the new sentence was also rejected: it would assert prose against prose and go RED on a rewording rather than on a falsehood. Docs-only, four lines, one page; no `argus/**` composition change, so the `DF-10-4-D` artifact-currency guards stayed green with no regeneration. Gates: `pytest -q` **1527 passed / 0 failed / 0 errors / 0 skipped**; `mypy argus` clean (83 files); `bandit -r argus -q` **19 Low / 0 Medium / 0 High**, control-matched. Nothing loosened, xfailed or skipped; **published nothing** (12.9's fence). |
| 2026-08-15 | **Story 12.8 implemented (`bmad-dev-story`). Status `ready-for-dev` → `review`.** The load-bearing delivery is AC3's: `--passes` / `--skip-pass` / `--reports` now REFUSE an unknown token inside `parse_args` against the one definition of each, so `--passes securty` — measured on `2f84a0b` returning `RELEASE_READY` **exit 0** over a run in which **every detector pass was silently disabled** — is a typed refusal instead of a false green. `generator.py` gained the single `RENDERED_REPORT_TYPES` constant AC3 requires (there was none, which is why nothing could validate a report token, and why this repository's own `argus-student-audit.yml:48` shipped `vacuous-tests`), and the four copy-pasted render branches became one loop over it. **AC8:** an argparse usage error now returns the reserved `1` in `main()` only, so a typo no longer publishes `verdict=NOT_READY_FOR_RELEASE assessed=true` through `action.yml`; `--help` still exits `0` and `build_parser().parse_args` is byte-identical. **AC4/AC5:** FR37's `render_audit_failed_next_action` has production callers for the first time — both CLI arms and the second invocation surface — dispatching per typed class and raising on an unregistered one; `DF-8-4-D` is **CLOSED at the wrap site** by `pipeline.UnexpectedStageError`, because `pipeline.py` was pre-disguising internal defects as expected `PipelineError`s and a CLI-only split could not have told them apart. **AC6:** the NFR-S1 absolute-host-path leak at `source_state.py:122` is gone, pinned as a property over both streams in every spelling a path can wear. **AC7:** 12.5's handover is wired — the grammar downgrade reaches the DEFAULT run from the SAME renderer via an additive `AuditResult` field, nothing new persisted; `DF-10-4-C`'s surface half is closed and its class-payload half re-recorded with a reason. **AC1/AC2:** `docs/first-run.md` ships, linked and with every checkable claim derived by test, and every argument's `--help` states its live default. **Two guards that could not fail as written were corrected with their new forms proven to bite**, and `TC-ArgusAgent-REPORT-002-31`'s floor was re-derived (not lowered) after the render loop. NFR-M1 forced 12.7's cohesion-split remedy: `tests/test_help_contract.py`, no line shaved, no population narrowed. Gates: `pytest` 1524 passed / **3 failed, all three the known `DF-10-4-D` artifact-currency class** awaiting the commit-then-regenerate bootstrap; `mypy argus` clean (83 files); `bandit` control-matched with **zero new findings** after two constants were renamed off the `…_TOKEN` suffix rather than suppressed. **Published nothing** (12.9's fence). |
| 2026-08-15 | **Code review complete (`bmad-code-review`). Status `review` → `in-progress`.** Verdict: **concerns**. Independently re-verified: `pytest -q` 1527 passed / 0 failed (the three `DF-10-4-D` dogfood-currency tests are green post-`6efa306`); `mypy argus` clean; `bandit -r argus -q` 19 Low / 0 Medium / 0 High, matching the claimed stashed-control count with no `# nosec`. The false-green closure (AC3), the exit-code contract change (AC8, confirmed `main()`-only via `build_parser().parse_args` byte-identity), `pipeline.UnexpectedStageError`'s wrap-site placement (AC5), the NFR-S1 property (AC6), the four DN-4 monkeypatch-site updates, and the NFR-M1 cohesion split were all independently verified by reading the diff and by execution (`--passes securty`, `--reports vacuous-tests`, `--budget 1.5`, `--help`) — no loosened gate, no fifth exit code, no re-merged split found anywhere hunted. One Low finding: `docs/first-run.md`'s opening line claims *"everything on it is checked by a test"*, which the page's own install-command caveat twenty lines later contradicts (that command is explicitly NOT exercised). No functional, security or AC impact — a one-line reword. Written to Review Findings as `[Review][Patch]`. |
| 2026-08-15 | Story 12.8 created (`bmad-create-story`). Scope: **the operator-facing explanation surface** — a first-run page, `--help` parity, and operator-error diagnosis — measured by **executing the real CLI** on `2f84a0b` rather than from the epic's prose. **Four of the epic's premises were found false and one partly false.** `docs/` holds a **BMad tooling stub**, not an integrator README, and nothing links to it. Two of the four operator errors the epic names are **already handled well** (`--deep-audit` with no provider, `--strict` refusals) and must not be rebuilt; *missing grammar* renders only into a report that needs `--report-dir`, which is precisely what 12.5 handed over by name. **Eight operator-error surfaces are entirely SILENT**, and one of them is a false-green channel: `--passes securty` disables every detector pass, prints nothing, and returns `RELEASE_READY` exit 0. **`render_audit_failed_next_action`, shipped by 12.4 for FR37, has ZERO production callers** — the CLI's two failure arms print a cause and stop. **`source_state.py:122` leaks the absolute host path** into the stderr line whose own docstring promises it never will. **`DF-8-4-D`'s arm has moved to `cli.py:758` and there are now THREE such arms, not two**, and the split alone cannot close it because `pipeline.py` already pre-disguises internal defects as typed `PipelineError`s. **Absorbed with a recorded reason (AC8): an argparse usage error exits `2`, which `action.yml:129` publishes as `verdict=NOT_READY_FOR_RELEASE assessed=true` — a typo fabricates an assessment for a run that never happened**, at the one surface whose sibling (`mcp/server.py:107`) already rules a parse rejection is not a verdict. Owns `DF-8-4-D` and `DF-10-4-C`; **cites and does not build** `DF-3-4-A` (resume), `DF-10-5-C` (evidence export) and `DF-12-7-A` (more hosts), all unscheduled. Status → `ready-for-dev`. |
