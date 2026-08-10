---
baseline_commit: 00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0
baseline_note: >-
  HEAD is `00c8d1b`. **Story 10.1's AND Story 10.2's deltas are in the working tree, NOT
  committed** — `tests/test_evidence_citation.py` and `tests/test_spec_claim_scope.py` are
  staged (`A `), and `E-PRD/prd.md`, `E-PRD/addendum.md`, `E-PRD/.memlog.md`,
  `architecture.md`, `epics.md`, `deferred-work.md`,
  `sprint-change-proposal-2026-07-28.md`, `README.md`, `CHANGELOG.md`,
  `argus/index/ast_index.py`, `argus/cache/key.py`, `argus/audit/deep_audit.py` and five
  test files carry their unstaged edits. **You are building ON TOP of that uncommitted
  delta.** Do not revert it, do not re-do it, and do not assume `git diff HEAD` isolates
  YOUR work — it does not. Measure your own delta against the tree as you found it and say
  so in the Dev Agent Record.
  ⚠️ **`bmad-dev-loop-pack/`, `.bmad-drift-audit/` and `_bmad-output/audit-reports/*`
  belong to the orchestrator — do not add, move or delete them.**
  `sprint-change-proposal-2026-08-10b.md` is untracked and is the AUTHORITY for the Epic
  10–13 text you are implementing: read it, do not rewrite it.
  THIS FILE is untracked and IS yours: `git add` it with your delta or you repeat AI-E8-1,
  in which Epic 8 shipped with its own story file untracked because `git diff` cannot see
  an untracked path.
  **Every line number in this document was measured on 2026-08-10 against the working
  tree** (i.e. *after* 10.1's and 10.2's edits). `epics.md`'s own Story 10.3 AC cites
  "architecture L226", which has drifted to **`:303-304`** — see §B. Line numbers in this
  project drift under the amendment cascade; **locate every site by its ANCHOR TEXT, and
  treat the line number as a hint that must be re-verified.**
story_key: 10-3-invocation-contract-says-what-the-cli-accepts
epic: 10
---

# Story 10.3: The invocation contract says what the CLI accepts

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

As a downstream integrator,
I want every accepted CLI flag to appear in the invocation contract,
so that the contract Story 1.7 declares LOCKED is the contract the tool actually honours.

**Why this story is third in Epic 10.** 10.1 established the *control* — a status claim cites an executed
gate or is recorded `NOT ESTABLISHED`. 10.2 made the first artifact correction *under* that control and
proved the instrument: a hand-counted site list fails, a **closure guard** holds. 10.3 is the same
instrument pointed at a different surface — the **parser**, which unlike a prose corpus is
*programmatically enumerable* (§C), so its closure guard can be exact rather than heuristic. It is also a
**hard dependency of Story 12.8**, whose AC reads *"given every CLI flag Story 10.3 blessed, `--help`
states what it does and its default, and a test asserts parser-vs-help parity **alongside 10.3's
parser-vs-contract test**"* ([epics.md:2397-2399](../epics.md)) — 12.8 cannot be written until this story
has ruled.

---

## Story Context

### Method statement — everything below was MEASURED on this tree on 2026-08-10

Every flag, every default, every line number and every suppression result in §A–§C came from `grep`, from
reading the file, or from **executing the real parser and the real suppression engine** on this host.
**Three of the measurements contradict the story's own epic text and its ledger entry.** Re-derive them;
do not transcribe them. §A.1 and §A.2 change what this story is allowed to decide.

---

### A. The five findings that change this story

#### A.1 — 🚩 The enumeration is FOUR in the ledger. Measurement finds **SIX**.

`DF-AUD-APAA-E` and the epic AC both name four flags: `--passes`, `--skip-pass`, `--ignore-path`,
`--ignore-pattern`. Measured against the **binding contract corpus** — `E-PRD/prd.md`,
`E-PRD/addendum.md`, `architecture.md`, `epics.md`, `CHANGELOG.md`, `README.md` — **two more flags have
zero occurrences anywhere in it.**

Mechanical derivation (run it yourself — this is the whole method):

```bash
cd d:/ProjectX/XAgents/XAgents/ArgusAgent
for f in commit strict budget materiality-bar critical-subsystem exclude-critical \
         passes skip-pass reports report-dir ignore-path ignore-pattern coverage-scope; do
  echo "--$f"; grep -c -- "--$f" \
    _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md \
    _bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md \
    _bmad-output/design-artifacts/ArgusAgent/architecture.md \
    _bmad-output/design-artifacts/ArgusAgent/epics.md CHANGELOG.md README.md
done
```

| Flag | Hits in the binding corpus | Specified? | Entered in |
|---|---|---|---|
| `repo` (positional) | — | ✅ FR30 names `repo` | 1.7 |
| `--commit` | 0 by spelling | ✅ FR30 parameter + Story 1.7's LOCKED spelling | 1.7 |
| `--budget` | `README:195` (and that line is broken — §A.3) | ✅ FR30 parameter + Story 1.7 | 1.7 |
| `--materiality-bar` | 0 by spelling | ✅ FR30 parameter + Story 1.7 | 1.7 |
| `--critical-subsystem` | `prd:463` ×1, `epics` ×6 | ✅ FR4 + Story 2.3 | 2.3 |
| `--exclude-critical` | `epics` ×7 | ✅ FR4 + Story 2.3 | 2.3 |
| `--coverage-scope` | `addendum` ×2, `epics` ×5, `CHANGELOG` ×6 | ✅ CHANGELOG §Defaults | `ae5f00c` (Epic 8) |
| `--report-dir` | `README:134` ×1 (+ `action.yml:80`) | 🟡 thin, but present and consumer-facing | `084c6a7` → `506bb73` |
| **`--strict`** | **0** | ❌ **NOT SPECIFIED — 🆕 missed by the audit** | `ae5f00c` (Epic 8) |
| **`--reports`** | **0** | ❌ **NOT SPECIFIED — 🆕 missed by the audit** | **`084c6a7`** (the separation seed) |
| `--passes` | `epics` ×1, and that one hit **is this story's own AC** | ❌ NOT SPECIFIED | `084c6a7` |
| `--skip-pass` | `epics` ×1, same | ❌ NOT SPECIFIED | `084c6a7` |
| `--ignore-path` | `epics` ×2, same | ❌ NOT SPECIFIED | `b05fa4c` |
| `--ignore-pattern` | `epics` ×2, same | ❌ NOT SPECIFIED | `b05fa4c` |

Provenance measured with `git log -S"--<flag>" -- argus/cli.py`.

**`--reports` is the same defect class as the four, from the same commit.** It entered in `084c6a7`, the
426-file separation seed, and no gate ever saw it. Worse than the four in one respect: **a committed
workflow depends on it.** [`.github/workflows/argus-student-audit.yml:48`](../../../../.github/workflows/argus-student-audit.yml)
runs `--reports "final-verdict,coverage-ledger,security-review,vacuous-tests"`. Removal is therefore *not*
free for `--reports` the way it is for the other five.

**`--strict` is a milder instance** — it entered through the story-gated Epic 8 commit `ae5f00c`
alongside `--coverage-scope`, but only `--coverage-scope` got a CHANGELOG entry. `--strict` is
load-bearing: `cli.py:31-41` names it as the **binding statement of the FR1 determinism pin** ("the pin is
enforced by `--strict`"), and Story 8.5 uses it as an existing fact. It is under-specified, not unwanted.

**The lesson, and it is the same one 10.2 drew a third time:** a hand-counted list is the wrong
instrument. **AC6 — the parser-vs-contract closure guard — is the load-bearing AC of this story, not
AC5.** Unlike 10.2's prose corpus, the parser here is *exactly* enumerable (§C), so there is no excuse
for a seventh instance.

#### A.2 — 🚩🚩 THE FINDING THAT DECIDES AC3/AC4: `--ignore-pattern` defeats the Live-Key Safeguard

`argus/detectors/secret_suppression.py:1-9` states the engine's own designed layering:

> *"4. Live-Key Safeguard: High-confidence live production key signatures **override folder glob
> exemptions** unless annotated with an explicit inline line comment."*

`evaluate_suppression` (`:112-147`) implements the order **1 inline annotation → 2 public sentinel → 3
`ignore_patterns` → 4 live-key safeguard → 5 `ignore_paths` glob**. Step **3 runs before step 4**, so the
CLI-supplied `--ignore-pattern` sits *above* the safeguard the module docstring promises, and its match
test is a **bare substring** (`if pat in snippet`, `:136`).

Measured on this host — run it yourself:

```python
from argus.detectors.secret_suppression import SecretSuppressionEngine as E
live = "AKIAABCDEFGHIJKLMNOP"                       # matches LIVE_KEY_PATTERNS[0]
E.evaluate_suppression(file_path="argus/prod.py", snippet=live)                             # (False, None)
E.evaluate_suppression(file_path="argus/prod.py", snippet=live, ignore_paths=("argus/**",)) # (False, None)  ← safeguard HOLDS
E.evaluate_suppression(file_path="argus/prod.py", snippet=live, ignore_patterns=("AKIA",))  # (True, 'custom_ignore_pattern')
E.evaluate_suppression(file_path="argus/prod.py", snippet=live, ignore_patterns=("A",))     # (True, 'custom_ignore_pattern')  ← ONE CHARACTER
```

**Read the last two lines again.** `--ignore-pattern A` silently suppresses every live AWS key, GitHub
PAT, Slack token and `BEGIN RSA PRIVATE KEY` block in the repository. `--ignore-path 'argus/**'`
suppresses none of them.

**The two flags are therefore NOT the same risk and must not take the same decision.** `--ignore-path`
is bounded by a safeguard that measurably holds; `--ignore-pattern` is an unbounded substring channel
that measurably does not. The epic AC treats them as a pair; measurement separates them, and DN-5/DN-6
record the split.

**And nothing at all is recorded.** `secret_scan.py:426-434` calls `evaluate_suppression`, binds the
reason to **`_reason`** and `continue`s — the reason token is discarded, no count is kept, no finding is
emitted. `AuditRequest.to_provenance_payload()` (`models.py:159-171`) persists the operator's *inputs*
(`ignore_paths`, `ignore_patterns`) into run-state, but the *effect* — that a secret was found and
suppressed — leaves no trace anywhere. That is the exact shape of unevidenced green this epic exists to
end, on the security surface, in a tool whose report (`argus/reports/generator.py:592`) actively tells
users to use it.

#### A.3 — The reverse direction: the contract names a flag the parser **rejects**

Parser-vs-contract equality has two directions, and the ledger only looked at one. Measured:

`README.md:192-196` documents the terminal invocation as:

```bash
argus --budget 500 --materiality critical
```

Executed on this tree:

```
usage: argus [-h] {audit} ...
argus: error: argument command: invalid choice: '500' (choose from 'audit')
SystemExit 2
```

Two defects in one line: the required `audit` sub-command is missing, and **`--materiality` is not a flag
this parser has ever accepted** (the flag is `--materiality-bar`). The first documented command a new user
copies fails.

⛔ **This is not Story 12.7.** 12.7 owns the **slash-command** block above it (`README.md:178-190`, seven
`/audit …` commands with no registration mechanism) and the console aliases. `:192-196` is a **terminal
flag invocation** and is squarely this story's direction-two defect. Fix the invocation; leave the
slash-command block untouched (DN-9).

#### A.4 — One measured default divergence between the parser and the model

Every parser default was compared against `AuditRequest`'s (`argus/models.py:88-147`). Thirteen of
fourteen agree — `_ALL_PASSES` matches `enabled_passes`, `_DEFAULT_REPORTS` matches `enabled_reports`,
`strict`/`report_dir`/`ignore_*` all match. **Exactly one diverges:**

| | parser (`cli.py:196`) | model (`models.py:125`) |
|---|---|---|
| `coverage_scope` default | **`"application"`** | **`"repository"`** |

Both are *documented in their own place* and they disagree: `CHANGELOG.md:286-290` announces the CLI
default as `application`; `models.py:128` describes `repository` as *"the V1 fold"*; and
`tests/test_sequential_portability.py:570-573` repeats the model's wording. A library consumer
constructing an `AuditRequest` directly gets a different assessed population than a CLI consumer running
the same audit. **DN-8 rules on this by name** — it is not silently swept into the guard's exemption list.

#### A.5 — 🆕 A finding to FILE, not to fix: argparse's usage error collides with the BLOCKED exit code

Measured in §A.3: an argparse usage error exits **`2`**. `architecture.md:306-307` and `CHANGELOG.md:187+`
define the wire contract as `0`=RELEASE_READY · **`2`=BLOCKED** · `3`=INSUFFICIENT_COVERAGE · `1`=crash,
and the CHANGELOG's decision table states *"`1` is not in this table because no verdict produces it"* —
usage errors are named nowhere. **A CI step branching on exit `2` reads a typo in its own workflow as
"Argus found a blocking defect."**

⛔ **Do NOT fix this here.** Changing an exit code is a change to the published AR3/FR18 wire contract
with a blast radius across `action.yml`, both workflows and every integrator — the definition of
high-blast-radius. **AC8.3 files it** with an id, a named owner and a `target_story`, so it is recorded
rather than discovered a third time.

---

### B. Where the contract actually lives — re-measured, because the epic's citation has drifted

The epic AC cites *"FR30 and architecture L226"*. **`architecture.md:226` is now inside a Story-7.1 risk
closure note about dogfood partitioning** — the amendment cascade moved it. Measured coordinates:

| Contract site | Measured at | Anchor text (locate by THIS) |
|---|---|---|
| **FR30** — the binding capability contract | [`E-PRD/prd.md:541`](../E-PRD/prd.md) | *"An integrator can invoke APAA headlessly with `repo + commit + budget + materiality_bar`…"* |
| The capability-contract preamble that makes FR30 binding | `E-PRD/prd.md:457` | *"This is binding: a capability not listed here will not exist in V1 unless explicitly added."* |
| **Architecture §A "Invocation contract"** (the epic's "L226") | [`architecture.md:303-304`](../architecture.md) | *"**Invocation contract:** `repo + commit + budget + materiality_bar → verdict artifact + exit code` (FR30)"* |
| Architecture §A heading / exit-code wire contract | `architecture.md:300` / `:306-307` | *"### A. Execution & Invocation"* / *"**Exit-code wire contract:**"* |
| **Story 1.7's LOCKED list** | [`stories/1-7-…-cartridge.md:168-182`](1-7-cli-invocation-contract-pipeline-signature-demo-vacuous-test-cartridge.md) | *"AC3 — `cli.py` thin `argparse` entrypoint…"* / *"the exact flag names/sub-command shape are LOCKED + documented by the dev"* |
| The in-code contract narrative | [`argus/cli.py:26-56`](../../../../argus/cli.py) | *"The LOCKED CLI contract (frozen + documented per the story)"* — lists **7 of 13** flags |
| CHANGELOG `## Unreleased` | [`CHANGELOG.md:41`](../../../../CHANGELOG.md) | the heading 10.2 already appended under |
| README terminal invocation | [`README.md:192-196`](../../../../README.md) | *"From terminal CLI:"* |
| §Enforcement (where guards are registered) | `architecture.md:639-651` | *"**Governance enforcement** *(added 2026-08-10 by Story 10.1)*…"* |

**`cli.py:26-56` is itself an under-count and a live trap.** Its "LOCKED CLI contract" block documents
`audit`, `<repo>`, `--commit`, `--budget`, `--materiality-bar`, `--critical-subsystem`,
`--exclude-critical` — **seven** — and stops. The six flags of §A.1 are absent from the module's own
statement of its contract. Commit `230bf5c` ("correct in-code statements that contradicted the shipped
behaviour") repaired the `--commit` paragraph in that same block and **left the omission**. Amending this
docstring is in scope; it is the contract statement closest to the code.

---

### C. The parser is programmatically enumerable — this is the instrument

10.2's guard had to infer a claim shape from prose with a hand-tuned regex. **This story does not.**
`build_parser()` yields the exact accepted surface:

```python
from argus import cli
p = cli.build_parser()
audit = p._subparsers._group_actions[0].choices["audit"]
for a in audit._actions:
    print(a.option_strings, a.dest, repr(a.default), a.nargs, a.type, a.choices)
```

Measured output — **15 actions: `-h/--help`, the `repo` positional, and 13 optional flags:**

| Flag | dest | default | shape |
|---|---|---|---|
| `--commit` | `commit` | `'HEAD'` | value |
| `--strict` | `strict` | `False` | `store_true` |
| `--budget` | `budget` | `0` | `type=int` |
| `--materiality-bar` | `materiality_bar` | `''` | value |
| `--critical-subsystem` | `critical_subsystem` | `None` | `append` |
| `--exclude-critical` | `exclude_critical` | `None` | `append` |
| `--passes` | `passes` | `None` | CSV value |
| `--skip-pass` | `skip_pass` | `None` | `append` |
| `--reports` | `reports` | `None` | CSV value |
| `--report-dir` | `report_dir` | `''` | value |
| `--ignore-path` | `ignore_paths` | `[]` | `append` |
| `--ignore-pattern` | `ignore_patterns` | `[]` | `append` |
| `--coverage-scope` | `coverage_scope` | `'application'` | `choices=('repository','application')` |

**"13 flags", as the epic says — confirmed exactly.** This is what makes AC6 an *equality* assertion
rather than a heuristic: the guard derives the left-hand side from the live parser and compares it to a
registry that must be edited deliberately.

⚠️ **`_subparsers`, `_group_actions` and `_actions` are argparse private API.** That is acceptable inside
a test but it is the guard's own failure mode: if a future argparse changes them, a naive walk returns an
empty list and the guard passes vacuously. **AC6.5's non-vacuity assertion is not optional.**

**What is measurably CONSUMED, so nobody argues about it later:**

| Flag | Consumed at | Note |
|---|---|---|
| `--passes` / `--skip-pass` | `cli.py:269-279` → `pipeline.py:494, 530, 546, 579, 814` | fully live; also passed to `render_ship_readiness(enabled_passes=…)`, so the narrowing is already disclosed in the human register |
| `--reports` | `cli.py:298` → `reports/generator.py:655` | **conditionally inert**: `pipeline.py:848` only calls `generate_reports` when `report_dir` is set, so `--reports` without `--report-dir` is a no-op |
| `--ignore-path` / `--ignore-pattern` | `pipeline.py:530-538` → `secret_scan.py:426` → `secret_suppression.py:112` | live since 2026-08-09; §A.2 |
| `--strict` | `models.py:116` → `intake/source_state.py` | the FR1 determinism enforcement lever |
| `--coverage-scope` | `pipeline.py:718-742` | §A.4 |

---

### D. ⛔ FENCES — what this story must NOT touch

| Fence | Owner | Why |
|---|---|---|
| **`argus/pipeline.py`** | **Story 12.1** | 1331 lines vs. the NFR-M1 cap of 1200 — already breaching. **Every AC in this story is reachable without editing it**: the flags are parsed in `cli.py`, consumed through an unchanged `AuditRequest`, and suppression is decided inside `detectors/`. **Do not add a line to this file.** If your design needs one, you have widened the interface — narrow it (AC4.4). |
| **`--help` text quality / parser-vs-help parity** | **Story 12.8** | 12.8's AC names 10.3 explicitly: it asserts help parity *alongside* your parser-vs-contract test. You produce the **contract**; 12.8 produces the **help prose**. Do not write 12.8's test. |
| **`argus/cli.py:368-372` / `:337` `except ValueError` split** | **Story 12.8** (DF-8-4-D) | You are editing `cli.py`. Leave both `except ValueError` arms structurally as you found them; if your edit moves their line numbers, say so in the Dev Agent Record so 12.8 re-locates by anchor. |
| **The exit-code wire contract (AR3/FR18), incl. the argparse-`2` collision** | **FILE it (AC8.3)** | §A.5. Changing a published exit code is high-blast-radius across `action.yml` + both workflows + every integrator. Record, do not repair. |
| **`README.md:178-190` (the seven slash commands) + `pyproject.toml:59-62` aliases** | **Story 12.7** (and 11.5's interim marker) | §A.3. Your README write is confined to the *terminal invocation* block at `:192-196`. |
| **A `--deep` flag (FR36) or an MCP surface (FR35)** | **Stories 12.2 / 12.6** | Not in the parser today. Your guard must **fail** when they are added until they are registered — that is the guard working, not a defect. Say so in the guard's docstring. |
| **`argus/index/ast_index.py`'s `except (ImportError, Exception)`** | **Story 10.4** | Untouched by this story; listed so the fence is not lost between siblings. |
| **Grammar/packaging decisions, `[languages]` promotion** | **Stories 10.4 / 11.4 / 12.5** | Out of scope entirely. |
| **The precision gate / `protocol_cleared`** | **Epic 13** | Out of scope entirely. |
| **Publishing, tagging, `workflow_dispatch`** | **Story 12.9** | 10.1's DN-7 is binding: do not manufacture a citation (AC8.4). |
| **`epics.md`** | 10.1 (fenced) / 2026-08-10b | Not in this story's write set. Its stale `L226` citation is **recorded here** (§B), not corrected there. |
| **`.github/workflows/audit-ci.yml`** | — | Green and correct. Editing a green workflow here is unjustified regression risk (10.1's DN-6). |
| **Epics 1-9 artifacts, all retrospectives, the preserved 7.2 record** | signed | Editing them now would falsify the record. |

---

### E. Traps previous stories already paid for — the five that apply here

1. **AI-E3-1 (Epic 3) — a keystone test can be green over its own keystone bug.** Story 3.4's resume test
   passed while resume silently dropped coverage. **Every new assertion in this story runs RED first**:
   the equality guard against the *unamended* contract (must fail naming all six flags), the live-key
   test against the *unfixed* ordering (must fail showing the AKIA key suppressed), the README
   invocation test against the *unfixed* line (must fail). A guard first run after the fix has proven
   nothing.
2. **AI-E8-6 (Epic 8) — all five Epic-8 stories shipped a guard narrower than their own AC.** AC6's
   closure over the *live parser* is the direct countermeasure. **Do not** hand-type the thirteen flags
   into the guard's left-hand side; derive them.
3. **`-17b` (Epic 9) — the denial filter that swallowed what it looked for.** Found by review, not by the
   author. AC6 needs a **positive control in both directions**: a synthetic parser with an unregistered
   flag **fires**; a synthetic parser matching its registry **does not**.
4. **The near-miss already in the tree.** `tests/test_sequential_portability.py:568-593` asserts
   `set(AuditRequest.model_fields) == {…}` — a **model**-field inventory, explicitly described in its own
   docstring as *"a DELIBERATE INVENTORY, not a freeze"*. It is green right now while six parser flags
   are unspecified, because **it pins the model and nobody pinned the parser**. That is exactly how §A.1
   survived two audits. Your AC6 guard pins the *parser* against the *contract*; do not weaken, delete or
   duplicate the existing model inventory (AC8.5).
5. **AI-E9-7 / R1 (Epic 9) — a prose copy of a pinned figure drifted at five sites.** If your amended
   prose states a flag **count**, derive it or pin it. A hand-typed "13" in FR30 is the next instance of
   that class; phrase it so no count is asserted, or make the guard assert the number you wrote.

---

## Acceptance Criteria

### AC1 — The enumeration is DERIVED, and it is six

**Given** `DF-AUD-APAA-E` and the epic AC name four flags,
**When** the parser surface is derived mechanically (§C) and differenced against the binding contract
corpus (§A.1),
**Then** the story records **six** unspecified flags — `--passes`, `--skip-pass`, `--reports`,
`--strict`, `--ignore-path`, `--ignore-pattern` — and:

1. `--reports` and `--strict` are named as **new instances the 2026-08-09 audit missed**, with their
   provenance (`084c6a7` and `ae5f00c` respectively, measured by `git log -S`).
2. `--report-dir`'s thin-but-present status (`README:134`, `action.yml:80`) is stated, so its exclusion
   from the six is a reasoned disposition rather than an oversight.
3. The count is **re-derived by the dev before any edit** and any divergence from this document is
   recorded, with the tree winning (§Method statement).

### AC2 — Each of the six takes a recorded ruling: blessed with acceptance criteria and a CHANGELOG entry, or removed

**Given** the epic's *"both outcomes are acceptable; leaving them unspecified is not"*,
**Then** each flag carries the disposition LOCKED in **DN-3 … DN-7**, and each blessed flag gets:

1. **A behavioural acceptance criterion pinned by test** — not merely a sentence. Minimum set:
   - `--passes` — an explicit CSV selects exactly those passes; a trailing comma is not a selection; an
     explicit flag selecting nothing stays empty rather than silently reverting to the default
     (`cli.py:257-266`).
   - `--skip-pass` — repeatable, and **composes in one direction only**: a skip can never re-add a pass
     `--passes` excluded (`cli.py:269-279`).
   - `--reports` — selects rendered report types, **and its conditional inertness is stated**: with no
     `--report-dir` it renders nothing (§C). Blessing a flag while concealing that it does nothing
     half the time would be this epic's own defect.
   - `--strict` — refuses a non-git tree, a dirty tree, or `HEAD != --commit`; **off by default**.
   - `--ignore-path` — extends `DEFAULT_TEST_PATH_PATTERNS`, and **cannot suppress a live production
     key** (the measured §A.2 property, asserted in both directions).
   - `--ignore-pattern` — per DN-6 / AC4.
2. **A CHANGELOG entry** under the existing `## Unreleased` heading (`CHANGELOG.md:41`), in that file's
   established honesty register, recording these as *documented-not-new* — the 10.2 precedent
   (*"Documented — the `[languages]` extra, which shipped undocumented"*). It states plainly that the
   flags shipped in `0.1.0` unspecified and that this release specifies them.
3. **No behaviour change is smuggled in under "blessing"**, other than the changes AC4 explicitly
   requires. A blessed flag behaves exactly as measured unless an AC says otherwise, and the dogfood
   verdict is unchanged (AC8.6).

### AC3 — 🔑 The threat model exists, and it gates the suppression flags

**Given** the epic: *"absent that model, the flags are removed rather than blessed"*,
**When** `--ignore-path` or `--ignore-pattern` is blessed,
**Then** a **written threat model** is committed — as a dated section of `architecture.md` §G (Security &
Governance) — that answers, in these terms:

1. **Who may suppress a secret finding.** The audit runs with the invoker's authority under the existing
   work-manifest permission boundary (NFR-S4); there is no second principal. State that plainly, and
   state its consequence: **suppression is not an access-control question, it is an evidence question** —
   which is why the answer is recording, not permission.
2. **What is recorded when they do** — AC4's mechanism, named.
3. **What each flag can and cannot reach**, from the §A.2 measurement: the Live-Key Safeguard
   (`LIVE_KEY_PATTERNS`, `secret_suppression.py:41-46`) holds against `--ignore-path` and, after AC4.1,
   against `--ignore-pattern`.
4. **The residual risk that is accepted and not engineered away**: `--ignore-pattern` matches by bare
   substring (`pat in snippet`), so a short pattern is a wide net. ⛔ Redesigning the *matching* semantics
   is **not** in scope — state the residual risk, and file it if you judge it material (AC8.3).
5. **The threat model is referenced from the CHANGELOG entry**, so a consumer reading about the flags can
   reach it.

⛔ The threat model is a **specification artifact**, not a security review of Argus at large. Two to four
paragraphs in §G. It does not enumerate attacker personas or rate anything CVSS.

### AC4 — A suppressed security finding is recorded and disclosed — never silently dropped

**This is the condition on which AC2's bless of the suppression flags stands.** Measured: today the
reason token is bound to `_reason` and discarded, and the finding vanishes (§A.2).

1. **The layering defect is fixed, and it is fixed first.** `evaluate_suppression` evaluates
   `ignore_patterns` **after** `is_live_production_key`, so the CLI can no longer defeat the safeguard the
   module's own docstring (`:1-9`) promises. Inline annotation (step 1) keeps its top precedence — that
   is the documented, in-diff, reviewable override and it is deliberately preserved.
   - **RED first**: assert `--ignore-pattern "AKIA"` and `--ignore-pattern "A"` currently suppress
     `AKIAABCDEFGHIJKLMNOP` at `argus/prod.py`; record the RED output; then assert they do not.
   - Assert the same for `ghp_…`, a `-----BEGIN RSA PRIVATE KEY-----` block and an `xoxb-…` token — the
     enumerated `LIVE_KEY_PATTERNS` space, not one sample (trap E.2).
2. **An operator-attributable suppression is recorded.** A suppression caused by a flag the operator
   passed (`custom_ignore_pattern`, or `test_fixture_glob` matching a **custom** `--ignore-path` rather
   than a built-in default) is **recorded with its reason token, its locator, and nothing else** —
   producer-side redaction is absolute: **no secret bytes, no source bytes, no absolute host path**
   (NFR-S1/NFR-S2/AR8).
3. **It is disclosed where the operator will see it**, in the register the project already uses for a
   narrowing: `--coverage-scope` is the precedent — a narrowing is *permitted, disclosed, and never
   allowed to lower a bar* (`CHANGELOG.md:298-303`). Minimum: the run states that N security findings
   were suppressed by operator-supplied rules, or that none were.
4. **Fence-compatible by construction.** `argus/pipeline.py` must be **byte-unchanged** (fence D). Two
   designs are known to satisfy that; **pick one and record the choice with its reason**:
   - **(a) record-as-finding** — emit a non-blocking, redacted record through the existing findings fold
     instead of `continue`. Requires proving **zero verdict drift** (it must not become verdict-eligible).
   - **(b) record-on-DetectorResult** — carry the suppression on the frozen `DetectorResult` the detector
     already returns, alongside `degraded`, surfaced by a consumer that is not `pipeline.py`.
5. **Built-in suppressions are OUT of scope** and that is deliberate, not an omission: the public
   sentinels, the inline annotation, and `DEFAULT_TEST_PATH_PATTERNS` are pre-existing blessed behaviour
   that no operator flag caused. Disclosing them is a *reporting* enhancement — file it if you want it
   (AC8.3); do not build it here.
6. **The fallback, so this cannot stall.** If AC4.2-AC4.3 provably cannot land inside fence D, then
   **`--ignore-pattern` is REMOVED from the parser** per DN-6's second branch and `--ignore-path` keeps
   its bless (the Live-Key Safeguard bounds it, and the tool's own report recommends it —
   `generator.py:592`). Record which branch you took and why. **Do not bless an unrecorded suppression
   channel; that is the defect this epic exists to close.**

### AC5 — The contract documents say what the parser accepts, exactly

Each site in the §B table is amended so the contract and the parser agree. Every amendment is **dated**,
**attributed to Story 10.3 / `DF-AUD-APAA-E`**, and uses the project's §3.4 form: **strike replaced
wording (`~~…~~`), never delete it.**

1. **FR30** (`prd.md:541`) — the binding capability contract. Amended so the invocation contract covers
   the whole accepted surface, not four parameters. **Per trap E.5, do not hand-type a flag list or a
   count into the PRD**: name `argus/cli.py::build_parser` as the source of truth and state the
   *categories* the contract commits to (the pin, the ceiling, the materiality bar, operator
   designation, pass/report selection, security suppression, assessment scope, release-gate mode) —
   the `source_languages.py` precedent FR7 set on 2026-08-10.
2. **Architecture §A** (`:303-304`) — the *"Invocation contract"* bullet, amended the same way, in the
   same section that already carries the exit-code wire contract and the FR35 entry-point table.
3. **Story 1.7's LOCKED list** (`stories/1-7-…:168-182`) — ⚠️ **append-only.** Story 1.7 is `done` and
   its record is signed. Add a **dated amendment note** under AC3 recording that the LOCKED surface has
   grown from four flags to the current set, by which stories, and that 10.3 is the correction. **Do not
   rewrite 1.7's original AC text** (§3.4; the same append-only rule 10.2 applied to `deferred-work.md`).
4. **`argus/cli.py:26-56`** — the in-code *"LOCKED CLI contract"* block, which documents 7 of 13 (§B).
   Every accepted flag appears with its default and its owning story/FR. This is the contract statement
   closest to the code and the one a maintainer reads first.
5. **README.md:192-196** — the broken terminal invocation (§A.3) is replaced by one that **actually
   runs**, and the replacement is asserted by AC6.4. ⛔ `:178-190` is Story 12.7's and is untouched.
6. **CHANGELOG.md** — AC2.2's entry.

> **Locate by anchor text.** Every number above was measured 2026-08-10 on a tree carrying 10.1's and
> 10.2's uncommitted edits; re-verify each before editing and record any that moved.

### AC6 — 🔑 A committed guard asserts parser-vs-contract equality, in both directions, and cannot be escaped

**This is the AC that makes the story stick** (DN-2). A new committed test derives the accepted surface
from the **live parser** and asserts it equals a declared contract registry.

1. **Derived, never transcribed.** The left-hand side comes from `cli.build_parser()` walked at runtime
   (§C). A hand-typed flag list on that side is a breach of this AC.
2. **Direction one — nothing accepted is unspecified.** Every flag the parser accepts appears in the
   registry, and each registry entry names the contract site(s) that specify it (FR / architecture /
   story / CHANGELOG). Adding a flag to the parser without registering it **fails**. This is what makes
   `--deep` (FR36) and any MCP-era flag land as a red test rather than as a seventh instance (fence D).
3. **Direction two — nothing specified is unaccepted.** Every flag spelling the registry claims is
   parseable by the live parser, so `README:195`'s `--materiality` class of defect fails the guard rather
   than reaching a user. **This direction is why §A.3 is in scope.**
4. **The documented invocations are executable.** Each `argus audit …` command line committed in
   `README.md`, `action.yml` and `.github/workflows/argus-student-audit.yml` parses through
   `build_parser().parse_args(...)` without `SystemExit`. Extracted by pattern, not by a fixed list, so a
   newly documented command line is covered.
5. **Non-vacuity — mandatory (§C warning).** The guard fails if it enumerated zero flags, zero registry
   entries or zero documented invocations. An argparse-internals change must turn this test **red**, not
   silently green.
6. **Positive control, both directions** (trap E.3): a synthetic parser carrying an unregistered flag
   **fires**; a synthetic parser matching a synthetic registry **does not**. Pure-function checks over
   synthetic parsers — never by mutating the real one.
7. **Defaults and shape are compared, not just names.** Each registry entry records the flag's default
   and its shape (`store_true` / `append` / `type=int` / `choices`), and a change to either fails until
   the registry is updated deliberately. Divergences are **exemptions with reasons** (DN-8, AC7), never
   silence — the `_PRESERVED_RECORD` anti-pattern 10.1's DN-5 ruled on.
8. **RED first** (trap E.1): run it against the **unamended** contract and record the failure naming all
   six flags of §A.1, before AC5's edits land. Restore any touched document byte-identically (sha256
   round-trip, 10.1's D4).
9. **Registered in `architecture.md` §Enforcement** (`:639-651`) beside 10.1's and 10.2's guards. *A rule
   that lives only in a test is not a rule, and a rule that lives only in prose is not enforced* — the
   guard asserts its own §Enforcement paragraph is still present, as `-23` does.

### AC7 — The known divergences are ruled on by name

1. **The `coverage_scope` default divergence (§A.4) takes the DN-8 ruling**, recorded in the guard's
   exemption list **with its reason**, and stated once in the contract so a library consumer and a CLI
   consumer can both discover which default applies to them. ⛔ Neither default is changed — see DN-8.
2. **`--reports`' conditional inertness (§C) is stated in the contract**, not just in this story file.
3. **`--report-dir`'s thin specification is thickened** to the same standard as the other blessed flags
   while it is in your hand — one line in the same amendment, not a separate campaign.

### AC8 — The ledger closes honestly, the gates run, and the fences hold

1. **`DF-AUD-APAA-E` (`deferred-work.md:1511-1527`) is closed APPEND-ONLY.** The original entry stays
   **byte-intact**; the closure note is appended and **must include the new findings** — §A.1 (the
   enumeration was four and is six, with `--reports` and `--strict` named and their provenance measured),
   §A.2 (the Live-Key Safeguard bypass and the discarded reason token), §A.3 (the reverse direction), and
   the disposition each flag took. `git diff --numstat` on `deferred-work.md` is **`+n / -0`** (10.1's
   DN-8 / §3.4).
2. **`AUDIT_REQUEST_SCHEMA_VERSION` is NOT bumped** unless a field actually changes; if DN-6's removal
   branch is taken, `AuditRequest.ignore_patterns` is **RETAINED defaulted-empty** (DN-6) so the
   additive-only schema-evolution policy (`prd.md:393`) is not breached, and the now-unreachable field is
   **recorded by name for Story 10.5's FR-sweep** rather than left for it to discover.
3. **New deferrals are filed with an id, an owner and a `target_story`** — never `target_story: NONE`
   without a named human (AI-E9-8). **At minimum §A.5 (the argparse-`2` / BLOCKED collision) is filed.**
   File any residual from AC3.4 or AC4.5 you judge material.
4. **Gates re-run and LABELLED LOCAL** (10.1's AC6): `mypy argus` · `bandit -r argus --severity-level
   medium` · `pytest tests/ --cov=argus --cov-fail-under=80`. **Measured baseline on this tree,
   2026-08-10: 1272 collected, all passing under `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; `mypy` clean on 71
   source files.** The count grows by **exactly** the new cases; **no test removed, skipped or weakened.**
5. **Evidence-citation compliance** — 10.1's binding rule (`architecture.md:490` + `:639-651`, enforced by
   `tests/test_evidence_citation.py`). Local gates are **necessary, not sufficient**: CI runs 3.10/3.11/
   3.12 on ubuntu and this host is Windows/3.11.15. Run `31341363300` covers `00c8d1b` **and cannot
   evidence your tree.** Either cite the `audit-ci.yml` run covering your **own** HEAD *with the sha it
   covers*, or record the status **NOT ESTABLISHED** and name the command a human runs.
   ⛔ **Do not push, tag, or `workflow_dispatch`** to manufacture a citation (10.1's DN-7).
6. **Write set — the fence, checked with `git status --porcelain` AND `git diff --stat`** (AI-E8-2: a
   plain `git diff` cannot see an untracked path):

   | Permitted | |
   |---|---|
   | `E-PRD/prd.md` · `architecture.md` · `deferred-work.md` | AC3, AC5.1, AC5.2, AC6.9, AC8.1, AC8.3 |
   | `stories/1-7-…-cartridge.md` (**append-only**) | AC5.3 |
   | `README.md` (**`:192-196` only**) · `CHANGELOG.md` | AC2.2, AC5.5, AC5.6 |
   | `argus/cli.py` | AC5.4, and the parser edit if DN-6's removal branch is taken |
   | `argus/detectors/secret_suppression.py` · `argus/detectors/secret_scan.py` | AC4 |
   | new + existing tests under `tests/` | AC2.1, AC4, AC6 |
   | this story file · `sprint-status.yaml` | process |

   **`argus/pipeline.py` must be byte-unchanged** (fence D, NFR-M1 at 1331/1200), and so must
   **`argus/models.py` in BOTH DN-6 branches** — the bless branch changes no field, and the removal
   branch retains `ignore_patterns` defaulted-empty by design (AC8.2), so a `models.py` diff means you
   breached the additive-only policy. Likewise unchanged: `epics.md`, `audit-ci.yml`, `action.yml`,
   `pyproject.toml`, `README.md:178-190`, and every Epic 1-9 artifact and retrospective. A diff outside
   the table above means scope has leaked — **stop and record why** rather than widening.
7. **Whole-system, not just the ACs.** The full suite is green and the **dogfood verdict is IDENTICAL**.
   A changed dogfood verdict is a stop-and-report, not a figure to update.

---

## Tasks / Subtasks

- [x] **T1 — Re-measure before you edit anything (AC1) — FIRST**
  - [x] Run the §A.1 `grep -c` loop; confirm the six-flag difference and reconcile every row of the table.
  - [x] Run the §C parser walk; confirm **15 actions / 13 optional flags** and every default.
  - [x] Run the §A.2 suppression probe; confirm `--ignore-pattern "A"` suppresses `AKIAABCDEFGHIJKLMNOP`
        and `--ignore-path 'argus/**'` does not. **Record the raw output — it is AC4.1's RED evidence.**
  - [x] Run the §A.3 README invocation; confirm the argparse error and `SystemExit 2` (AC8.3's finding).
  - [x] Re-verify every §B line number against the working tree; record every one that moved.
- [x] **T2 — Rule on each flag and write the ruling down (AC1, AC2)**
  - [x] Confirm or, with a recorded reason, revise DN-3 … DN-7 against your own measurement.
  - [x] Draft the CHANGELOG `## Unreleased` entry in the 10.2 documented-not-new register.
- [x] **T3 — RED first, before any fix (traps E.1/E.3; AC4.1, AC6.8)**
  - [x] Write the AC6 equality guard; run it against the **unamended** contract; capture the failure
        naming all six flags.
  - [x] Write the AC4.1 live-key assertions; run them against the **unfixed** ordering; capture the
        suppression of each `LIVE_KEY_PATTERNS` member.
  - [x] Write the AC6.4 documented-invocation test; run it against the **unfixed** `README:195`; capture
        the `SystemExit`.
  - [x] Verify every document you opened is byte-identical afterwards (sha256 round-trip).
- [x] **T4 — The threat model (AC3)**
  - [x] Write it into `architecture.md` §G, dated and attributed, answering AC3.1-AC3.4.
  - [x] Link it from the CHANGELOG entry (AC3.5).
- [x] **T5 — Suppression: fix the layering, record the effect (AC4)**
  - [x] Move the `ignore_patterns` arm below `is_live_production_key`; keep the inline annotation on top.
  - [x] Choose design (a) or (b) from AC4.4, record the choice and its reason, and implement it **without
        touching `pipeline.py`**.
  - [x] Distinguish a **custom** `--ignore-path` match from a `DEFAULT_TEST_PATH_PATTERNS` match so
        AC4.2's attribution is real (`secret_suppression.py:97-110` merges them today).
  - [x] Prove zero verdict drift; if design (a) moved a count, stop and report.
  - [x] If AC4.6's fallback is taken, apply DN-6's removal branch and record it. *(NOT taken — the
        condition was met, so DN-6's bless branch stands. Recorded in the Dev Agent Record.)*
- [x] **T6 — Amend the contract (AC5, AC7)**
  - [x] FR30 · architecture §A `:303-304` · `cli.py:26-56` · Story 1.7 (append-only) · `README:192-196` ·
        CHANGELOG — each dated, attributed, striking rather than deleting.
  - [x] Record the DN-8 `coverage_scope` ruling, `--reports`' conditional inertness, and `--report-dir`'s
        thickened line.
- [x] **T7 — Green the guard and register it (AC6)**
  - [x] Re-run the AC6 guard; it passes only once the contract matches the parser.
  - [x] Add the §Enforcement paragraph (`architecture.md:639-651`) and the assertion that it is present.
  - [x] Confirm non-vacuity and both positive controls.
- [x] **T8 — Close honestly (AC8)**
  - [x] Append the `DF-AUD-APAA-E` closure note; verify `git diff --numstat` is `+n / -0`.
  - [x] File the §A.5 exit-code collision (and any AC3.4/AC4.5 residual) with id, owner, `target_story`.
  - [x] Run the three gates; label them LOCAL; state the citation or **NOT ESTABLISHED**.
  - [x] Check the write set with `git status --porcelain` **and** `git diff --stat`; `git add` this file.

### Review Findings

**Code review 2026-08-10, iteration 1 — VERDICT: PASS. No unresolved findings.**

Adversarial verification performed by EXECUTION, not by reading, per the review brief:

- **Live-Key Safeguard, fuzzed adversarially.** Ran `evaluate_suppression` over 4 live-key samples
  (one per `LIVE_KEY_PATTERNS` member) × 12 hostile `--ignore-pattern` values (incl. `""`, `"*"`,
  `"?"`, single chars, case variants) = 84 combinations, × 7 hostile `--ignore-path` globs = 49
  combinations, plus 7 combined-flag invocations and 16 case-variant probes. **0 escapes in every
  sweep.** The safeguard measurably holds in both directions and under combination, confirming AC4.1
  independently of the story's own recorded probes.
- **AC6 guard bites on a live rogue flag.** Monkeypatched `cli.build_parser` in a throwaway process to
  add `--totally-new-rogue-flag` (not in `CONTRACT_REGISTRY`) and ran `derive_arguments` /
  `unregistered_and_unaccepted` from `tests/test_invocation_contract.py` against it directly (not the
  synthetic-parser unit test, an independent injection into the real `build_parser`). The guard named
  the rogue flag in `unregistered` as designed. Confirms AC6.1/AC6.2 are load-bearing, not vacuous.
- **Fence D (pipeline.py / models.py byte-unchanged).** `git diff --quiet HEAD -- argus/pipeline.py
  argus/models.py` — both clean. `epics.md` confirmed unchanged by mtime (11:39, predates this
  story's 19:01 session start) rather than by trusting the sha claim. `action.yml`,
  `audit-ci.yml`, `pyproject.toml`, `.github/workflows/argus-student-audit.yml` all `git diff --quiet`
  clean. README `:178-190` (the slash-command block) confirmed untouched in the actual diff hunk —
  only `:192-196` changed, honoring DN-9.
- **Story 1.7 amendment — genuinely append-only, not a scope breach.** Read the full diff: the
  original AC3 text is byte-preserved; a single dated, attributed, reasoned amendment block is
  appended below it, consistent with this project's own correction protocol (dated, reasoned,
  appended, never silent — the standard Story 10.1 established). Not a rewrite of the signed record.
- **`deferred-work.md` append-only, +404/-0.** `git diff --numstat` confirms. `DF-AUD-APAA-E`'s
  original entry read byte-intact above its closure note; `DF-10-3-A/B/C` filed with named owners
  (none `target_story: NONE` without a human named).
- **README invocations parse for real.** Ran all three `README.md:192-196` command lines through
  `cli.build_parser().parse_args(...)` directly — all three parse without `SystemExit`.
- **Dogfood verdict reproduced independently.** Ran `python -m argus.cli audit .` fresh:
  `RELEASE_READY`, exit `0`, `blocking_findings=0`, `deep_ratio=60/161`,
  `assessed_deep_ratio=15/19 scope=application held_out=85` — byte-identical to the story's recorded
  figures. The `operator_suppressed_secret` disclosure line printed correctly ("none were") and leaked
  nothing.
- **Full suite run twice, independently, to completion.** `PYTHONIOENCODING=utf-8
  ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 python -m pytest tests/ -q` (once plain, once with `-x
  --tb=short`, once with `-u --no-header`) — all three runs produced **exactly 1297 dots and zero
  `F`/`E`/`x`/`s` markers anywhere in the captured output** (verified by counting, since the Windows
  redirect in this shell truncates pytest's final summary line on this host — a shell/host quirk, not
  a test failure; every individual test result character was captured and all were passes). Matches
  the claimed 1297 passed / 0 failed / 0 skipped exactly.
- **`mypy argus` and `bandit -r argus --severity-level medium` re-run by the reviewer**: mypy clean on
  71 files; bandit 0 Medium / 0 High (19 Low, unchanged) — both match the dev's figures exactly.
- **No push/tag/dispatch found**: `git tag -l` empty, no unexpected branches, remote unchanged —
  consistent with the claimed `NOT ESTABLISHED` CI status.
- **New test files read in full** (`tests/test_invocation_contract.py`,
  `tests/test_cli_flag_contract.py`, `tests/test_secret_suppression_recording.py`): the AC6 registry
  is derived from the live parser (never hand-typed), the non-vacuity guard (`-39`) and positive
  control (`-40`) are real, the documented-invocation extractor is correctly scoped to
  README.md/action.yml/workflows (not story files or epics.md, honoring the 10.2 D2 lesson), and the
  suppression-recording tests assert redaction is absolute (secret, operator pattern, and absolute
  path all confirmed absent from the serialized record).
- **Architecture in `secret_suppression.py`**: the new evaluation order (inline → sentinel →
  live-key → operator pattern → operator path) is a minimal, correctly-scoped reordering with no new
  coupling to `cli.py` beyond the existing `AuditRequest` fields; `secret_scan.py`'s addition
  (`operator_suppression_rule_id`, the `Recording` fold) stays inside the existing pure/impure
  boundary and adds zero lines to the fenced `pipeline.py`. Design (a) over (b) is justified by a
  measured fact (the fence), not asserted as a preference — reviewed and accepted.

No High or Medium findings. No Low findings rose to the level of an actionable item — the two
"judgement calls" the dev flagged (conservative attribution; disclosure placement after the
ship-readiness block) are correct engineering judgements, not defects, and are already recorded in
the Dev Agent Record. AC1-AC8 all independently confirmed against the files, not the story's prose.
Status → `done`.

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

| # | Decision | Why |
|---|---|---|
| **DN-1** | The unspecified set is **six**, not the ledger's four | §A.1, measured. `--reports` shares the four's provenance (`084c6a7`, the separation seed) and is *depended on* by `argus-student-audit.yml:48`; `--strict` is the FR1 determinism lever specified nowhere in the binding corpus. Closing four and leaving two would leave the ledger entry honestly closed and the defect alive. |
| **DN-2** | **AC6 (the equality guard), not AC5 (the amendments), is the load-bearing AC** | 10.2's third-wrong-enumeration lesson, one story later. Here the parser is *exactly* enumerable (§C), so a heuristic is not even needed — there is no defensible reason for a seventh instance. If time is short, AC6 ships before AC5's last site. |
| **DN-3** | `--passes` and `--skip-pass` — **BLESSED** | Fully consumed (`pipeline.py:494,530,546,579,814`), recorded in run-state provenance, and the narrowing is **already disclosed** to the operator: `cli.py:375` passes `enabled_passes` into `render_ship_readiness`. This is the project's own permitted-and-disclosed pattern (the `--coverage-scope` precedent). They need specification, not removal. |
| **DN-4** | `--reports` — **BLESSED**, with its conditional inertness stated | A committed workflow depends on it (`argus-student-audit.yml:48`), so removal has a real in-repo cost the other five do not. But blessing it silently would hide that `--reports` without `--report-dir` renders nothing (§C) — concealing that is this epic's own defect, so AC2.1/AC7.2 make it explicit. |
| **DN-5** | `--strict` and `--ignore-path` — **BLESSED** | `--strict` is the enforcement of the FR1 determinism pin, named as the binding statement in `cli.py:31-41`; removing it would delete the only lever that refuses a drifted tree. `--ignore-path` is bounded by the Live-Key Safeguard **measurably** (§A.2: it cannot suppress an `AKIA` key), mirrors `DEFAULT_TEST_PATH_PATTERNS`, and is the remedy Argus's **own report** recommends (`generator.py:592`). Its bless is conditional on AC4. |
| **DN-6** | `--ignore-pattern` — **BLESSED ONLY IF AC4 lands; otherwise REMOVED from the parser** | §A.2 is decisive: it sits **above** the Live-Key Safeguard the module's own docstring promises, matches by bare substring, and `--ignore-pattern "A"` suppresses every live key in the repository with **nothing recorded**. Blessing that unchanged would be exactly the unevidenced green Epic 10 exists to end. Inert until 2026-08-09 ⇒ neither outcome is a behavioural break (ledger). **Removal branch, if taken:** remove the *parser flag* only; **retain `AuditRequest.ignore_patterns` defaulted-empty** because `prd.md:393`'s additive-only schema-evolution policy binds the persisted `to_provenance_payload()` shape and forbids deleting a field — and **record the retained field by name for Story 10.5's no-reachable-call-site sweep** so a known seam is not left to be "discovered" (the FR23/DF-6-7-A lesson, one story early). |
| **DN-7** | The **fix order inside AC4 is fixed**: layering first, recording second | The layering defect makes the flag unsafe; the missing record makes it unaccountable. A recording built on the current order would faithfully record a safeguard bypass. |
| **DN-8** | The `coverage_scope` default divergence (§A.4) is **RULED AS DELIBERATE, documented and pinned — neither default is changed** | Both are shipped and announced surfaces: `CHANGELOG.md:286-290` announced `application` to CLI consumers; `models.py:128` and `test_sequential_portability.py:570` describe `repository` as the library/V1 fold. Changing either is a **behavioural** change to a published default — beyond a specification-correction story, and the same fence 10.2 respected. What this story owes is that the divergence stops being an accident: stated once in the contract, exempted **by name with the reason** in AC6's registry, pinned in both directions so it cannot drift silently. |
| **DN-9** | `README.md:192-196` is **in scope**; `README.md:178-190` is **not** | `:192-196` is a terminal *flag* invocation and is direction-two of parser-vs-contract equality (§A.3). `:178-190` is the slash-command claim, explicitly owned by **Story 12.7** (`epics.md:2360-2381`) with an interim marker from 11.5. Two adjacent blocks, two owners; say so in the diff. |
| **DN-10** | `epics.md` is **not in the write set** | 10.1's AC5 fenced it to two locations; Epics 11-13 are 2026-08-10b's. Its stale *"architecture L226"* citation (§B) is **recorded here**, not corrected there — DN-9 of Story 10.2, applied identically. |
| **DN-11** | The exit-`2` collision (§A.5) is **FILED, not fixed** | Changing a published exit code touches `action.yml`, both workflows and every integrator — irreversible for consumers already branching on it, and it contradicts nothing in this story's scope. This is the one item that would exceed a story-level ruling; AC8.3 records it for a named owner. |
| **DN-12** | New test ids: **`TC-ArgusAgent-CLI-001-35…`** (parser-vs-contract equality, flag behaviour), **`TC-ArgusAgent-SECRET-001-15…`** (live-key layering, suppression recording), **`TC-ArgusAgent-DOCS-001-28…`** (documented-invocation executability) | Measured maxima on this tree: CLI-001 = `-34`, SECRET-001 = `-14`, DOCS-001 = `-27`. |

### Architecture patterns & constraints a reviewer will check

- **AR2 — stdlib `argparse` only.** Zero new dependency. A CLI library added here is a review rejection.
- **AR8 pure/impure separation.** `cli.py` is the impure shell: argv parsing + request construction +
  pipeline call + stdout/stderr/exit. **No audit logic in the entrypoint** (NFR-M1). The suppression
  engine stays a **pure** decision function — no I/O, no clock, no logging side effect.
- **AR3 / FR18 exit-code wire contract** — `0`/`2`/`3` verdicts, `1` reserved for a typed crash. **Do not
  touch it** (DN-11).
- **AR10 honest degradation + NFR-R1 no-crash** — a typed failure prints a secret-safe stderr line and
  returns `1`, never a traceback. Your changes must not introduce a new uncaught path through `main()`.
- **NFR-S1 / NFR-S2 producer-side redaction** — the suppression record carries a reason token and a
  locator, **never** the secret, never source bytes, never an absolute host path. This is the keystone
  Story 4.4's CI-blocking property suite guards; a leak here fails a merge-blocking job.
- **NFR-P1 host-invariance** — `fnmatchcase`, never `fnmatch` (`secret_suppression.py:17-25` explains why
  at length: `fnmatch` lower-cases on Windows, so the same repo would hide a credential on one host and
  report it on another). Any new matching you write follows that rule.
- **§3.4 evidence immutability** — strike, never delete; append, never rewrite. Exemplars at
  `prd.md:471` (FR7, 10.2's amendment), `architecture.md:492-498`, `deferred-work.md`'s closure notes.
- **Additive-only schema evolution** (`prd.md:393`) — new fields only, `schema_version` bumped,
  content-hash determinism preserved. This is the constraint behind DN-6's removal branch.
- **NFR-M1 ≤1200 lines/module** — applies to your new test files too. `cli.py` is 383,
  `secret_suppression.py` 147, `secret_scan.py` ~500 — all have room. Breached **only** by
  `argus/pipeline.py` at 1331 — **Story 12.1's, fenced, do not add a line.**
- **No `print()` in library code; typed exceptions at the impure shell; no bare `except: pass`** (AR10 /
  Story 4.3).

### Runtime & toolchain, verified on this machine 2026-08-10

| | |
|---|---|
| Python | **3.11.15** (CI matrix: 3.10 / 3.11 / 3.12, ubuntu) |
| Tests collected | **1272**, all passing under `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` (re-measured for this story) |
| `mypy` | **clean, 71 source files** (re-measured) |
| Parser surface | **15 actions on `audit`** — `-h`, `repo`, 13 optional flags (§C) |
| Local vs. CI | `mypy` local 2.3.0 vs. CI `>=1.0`; **if they disagree the EXECUTED CI RUN is the evidence** |

**No new dependency.** Everything this story touches is stdlib `argparse`, `re`, `fnmatch` and `pathlib`.

### Testing standards — the house form your new files must match

```bash
PYTHONIOENCODING=utf-8 ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 python -m pytest tests/ -q   # whole suite
python -m pytest tests/test_cli.py tests/test_secret_suppression.py -v
python -m pytest tests/test_sequential_portability.py -v                              # the near-miss (trap E.4)
python -m mypy argus
python -m pytest --cov=argus --cov-report=term-missing --cov-fail-under=80
```

- **`PYTHONIOENCODING=utf-8` is not optional on this Windows host,** and every markdown file you read in
  a test must be opened `encoding="utf-8"` **explicitly**. The artifact tree contains `~~`, `⚠️`, `🚩`,
  `café` and Cyrillic; `Path.read_text()` without it inherits the host locale — the exact class behind
  commits `d0e0a5c`/`ebdca75` that turned CI run `31322881580` red while every local run was green.
- **Naming:** `test_TC_ArgusAgent_<AREA>_<NNN>_<nn>_<snake_case_claim>()`, with the `TC-…` id on the
  docstring's first line and the story + AC on the second (see `tests/test_spec_claim_scope.py:299`).
- **Every assertion carries a failure message naming the offending flag / document / pattern.** A guard
  whose failure reads `assert derived == registry` costs the next reader an hour; print the symmetric
  difference.
- **The equality guard is pure `argparse` introspection + `pathlib`/`re` over committed files** — no
  network, no subprocess, no LLM, no `.argus/` write, so it runs identically on all three CI legs
  (10.1/10.2 precedent).
- **The live-key tests use synthetic, obviously-fake key material** that nonetheless matches
  `LIVE_KEY_PATTERNS`, and they assert on the `(bool, reason)` tuple — never on a secret value.
- **Never plant a real-looking credential in a committed fixture file**; build the string in the test.

### Previous story intelligence — Stories 10.1 and 10.2 (both `done`, both PASS iteration 1)

- **10.1's binding output is a STANDARD, not a number.** `architecture.md:490` + `:639-651`, guarded by
  `tests/test_evidence_citation.py` (`TC-ArgusAgent-DOCS-001-20..-23`). Run `31341363300` covers
  `00c8d1b` **only** and cannot evidence your tree (AC8.5).
- **10.2's guard shape is the template for AC6**: registry + glob/enumeration closure + positive control
  in both directions + non-vacuity + exemptions-as-data-with-reasons. Read
  `tests/test_spec_claim_scope.py:1-49` — its module docstring enumerates *"four known ways a guard like
  this lies, and what stops each"*. Your guard has the same four failure modes and one extra: argparse
  private API (§C).
- **10.2's D2 lesson**: it measured its corpus *before* writing the detector, because a too-wide pattern
  fires on the project's own meta-discussion and produces a guard that cries wolf and gets deleted. Your
  AC6.4 invocation-extractor will see `argus audit …` strings **inside this story file and inside
  `epics.md`**. Scope it to `README.md`, `action.yml` and `.github/workflows/*.yml` and say why.
- **10.2 filed `DF-10-2-A` rather than folding a new finding into a fenced AC.** Do the same with §A.5
  and with any AC3.4/AC4.5 residual (AC8.3).
- **10.1's and 10.2's deltas are uncommitted** — see the frontmatter. Your `git diff HEAD` includes them.

### Recent git context

`00c8d1b` is a merge of `fix/honest-verdict-reporting`; the six commits behind it (`d0e0a5c`, `ebdca75`,
`f7c666e`, `266bb28`, `f85fe76`, `40c0727`) are all **host-portability** defects — non-ASCII paths,
POSIX-vs-Windows containment, surrogate repair — **invisible on this Windows host and fatal on the ubuntu
runner.** Your AC4 work edits `fnmatchcase`-based path matching in exactly that neighbourhood, and
`secret_suppression.py:17-25` is a comment written by that very lesson. Anything you assert from a local
run inherits that blind spot, which is why AC8.4 makes you label local results as local.

Also relevant: `230bf5c` ("docs(cli,cost): correct in-code statements that contradicted the shipped
behaviour") repaired `cli.py`'s `--commit` paragraph and left the six-flag omission in the very same
docstring block (§B). AC5.4 finishes what that commit started.

### Project structure notes

- Tests are **flat under `tests/`**; `tests/apaa/` no longer exists (Epic 9). Architecture prose still
  saying `tests/apaa/` or `minions_core/apaa/` is stale — read it as `tests/` and `argus/`.
- Planning artifacts: `_bmad-output/design-artifacts/ArgusAgent/`; the PRD is under `E-PRD/prd.md`
  (**not** at the artifact root — the workflow's default `{planning_artifacts}/prd.md` does not exist).
- Stories live in `stories/`, **not** at the artifact root.
- `_bmad/bmm/config.yaml` and `_bmad/custom/config.toml` now agree on both artifact paths (corrected
  2026-08-10b); do not "fix" either.

### Open questions for the operator — saved for the end, as the workflow requires

1. **§A.1 makes the enumeration six, not the ledger's four.** The story treats `--reports` and `--strict`
   as in scope (DN-1) because closing the ledger entry over a known-incomplete list is the defect this
   epic exists to close. If you want the ledger entry closed at exactly four and the other two filed as a
   successor, say so **before dev starts**; note that a frozen hand-list is what failed three times in
   10.2.
2. **DN-6 makes `--ignore-pattern`'s bless conditional on AC4 and names removal as the fallback.** The
   epic's AC sanctions removal explicitly, and §A.2 shows a one-character pattern defeating the Live-Key
   Safeguard. If you would rather remove it outright without attempting AC4, that is a smaller story and
   DN-6's second branch is already written.
3. **AC4 changes behaviour on a security path** (suppression ordering, plus a recorded suppression). It
   is the *condition* of an honest bless, not decoration — but it is the largest code change here.
   Flagged rather than assumed.
4. **DN-8 leaves the `coverage_scope` default divergence in place, documented and pinned.** If you want
   the two aligned, that is a behavioural change to a published default and belongs in its own story with
   a migration note.

### References

- Epic + ACs — [epics.md:1873-1896](../epics.md) (Story 10.3) · [epics.md:1738-1790](../epics.md)
  (Epic 10 preamble, dependency flow, the 2026-08-10 citation audit)
- Ledger entry — [deferred-work.md:1511-1527](../deferred-work.md) (`DF-AUD-APAA-E`)
- Source of the finding — [sprint-change-proposal-2026-08-09.md](../sprint-change-proposal-2026-08-09.md)
- The binding contract — [E-PRD/prd.md:457](../E-PRD/prd.md) (capability contract) ·
  [E-PRD/prd.md:541](../E-PRD/prd.md) (**FR30**) · [E-PRD/prd.md:393](../E-PRD/prd.md) (additive-only
  schema policy)
- Architecture — [architecture.md:300-307](../architecture.md) (§A Execution & Invocation, the epic's
  drifted "L226") · [architecture.md:460-466](../architecture.md) (§G Security & Governance — AC3's home)
  · [architecture.md:639-651](../architecture.md) (§Enforcement — AC6.9's home)
- The LOCKED list this story corrects —
  [stories/1-7-cli-invocation-contract-pipeline-signature-demo-vacuous-test-cartridge.md:168-182](1-7-cli-invocation-contract-pipeline-signature-demo-vacuous-test-cartridge.md)
- Sibling stories (house style, both `done`) —
  [stories/10-1-release-status-must-cite-evidence.md](10-1-release-status-must-cite-evidence.md) ·
  [stories/10-2-multi-language-grounding-is-v1-in-the-specs.md](10-2-multi-language-grounding-is-v1-in-the-specs.md)
- Guard templates — [tests/test_evidence_citation.py](../../../../tests/test_evidence_citation.py) ·
  [tests/test_spec_claim_scope.py](../../../../tests/test_spec_claim_scope.py)
- Code under change — [argus/cli.py](../../../../argus/cli.py) ·
  [argus/detectors/secret_suppression.py](../../../../argus/detectors/secret_suppression.py) ·
  [argus/detectors/secret_scan.py](../../../../argus/detectors/secret_scan.py)
- The near-miss test (trap E.4) —
  [tests/test_sequential_portability.py:568-593](../../../../tests/test_sequential_portability.py)
- Consumer-facing invocations — [README.md:192-196](../../../../README.md) ·
  [action.yml:74-80](../../../../action.yml) ·
  [.github/workflows/argus-student-audit.yml:45-49](../../../../.github/workflows/argus-student-audit.yml)
- Downstream dependants — [epics.md:2397-2399](../epics.md) (Story 12.8 help parity, cites 10.3 by name) ·
  [epics.md:1951-1962](../epics.md) (Story 10.5's no-reachable-call-site sweep — AC8.2 feeds it)
- Sibling defect class — `DF-AUD-APAA-D` / Story 10.2 (a capability with no spec) · `DF-AUD-APAA-F` /
  Story 10.4 (grammar diagnosis) · `DF-6-7-A` / FR23 (a spec with no reachable call site)

---

## Dev Agent Record

### Context Reference

This story file. Every figure in it was measured on this tree on 2026-08-10 and is re-derivable by the
commands in §A, §C and T1 — **re-derive, do not transcribe.** Where a measurement disagrees with this
document, **the tree wins**: record the divergence and proceed from the measurement.

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context) — `bmad-dev-story`, unattended loop worker, single pass.

### Debug Log References

**T1 — every figure re-derived before any edit. The tree agreed with the story on all of it.**

| Measurement | Story says | Measured | Verdict |
|---|---|---|---|
| Parser walk (§C) | 15 actions / 13 optional flags | **15 / 13**, every default + shape + `choices` matching the §C table exactly | ✅ confirmed |
| Corpus difference (§A.1) | six unspecified | **six** — `--strict` 0, `--reports` 0, `--passes` 1, `--skip-pass` 1, `--ignore-path` 2, `--ignore-pattern` 2 (all epics.md hits are this story's own AC text) | ✅ confirmed |
| `--report-dir` (AC1.2) | thin but present | `README.md:134` ×1 + `action.yml:80` | ✅ excluded from the six, reasoned |
| `--budget` | `README:195`, and that line is broken | 1 hit, at `README.md:195` | ✅ confirmed |
| §A.2 suppression probe | `--ignore-pattern "A"` suppresses, `--ignore-path 'argus/**'` does not | reproduced **verbatim**, all four tuples | ✅ confirmed |
| §A.3 README invocation | `SystemExit 2` | `argus: error: argument command: invalid choice: '500'` → `SystemExit 2` | ✅ confirmed |

**§B line numbers re-verified by anchor text.** All confirmed on the nose — FR30 `prd.md:541`, the
capability preamble `:457`, architecture §A heading `:300`, the invocation-contract bullet `:303`,
Story 1.7's `AC3 —` at `:168` / `are LOCKED` at `:171`, `CHANGELOG.md:41`, `DF-AUD-APAA-E` at
`deferred-work.md:1511`, README `:134` / `:178-190` / `:192-196`. **Two moved:**

- **`architecture.md`'s exit-code wire contract is at `:305-306`, not `:306-307`** (the story's own
  §B cite). Immaterial — it is fenced (DN-11) and was not touched.
- **`secret_scan.py`'s `evaluate_suppression` call site is at `:422-430`, not `:426-434`.** The
  `_reason` / `continue` shape was exactly as described.

**T3 — RED demonstrations, all captured against the pre-change tree.**

1. **AC6 equality guard, unamended contract** — `TC-ArgusAgent-CLI-001-38` failed with **16 findings
   across 8 flags**, a strict superset of §A.1's six. All six of the ledger's expanded set were named
   on the contract-corpus half (`--passes`, `--skip-pass`, `--reports`, `--strict`, `--ignore-path`,
   `--ignore-pattern` — each *"anchor … is absent from CHANGELOG.md"*). Two more —
   **`--report-dir` and `--coverage-scope`** — were named on the *other* half of the same assertion,
   *"absent from cli.py's own 'LOCKED CLI contract' docstring block"*: they are specified elsewhere
   (README/action.yml and the CHANGELOG respectively) but were missing from the in-code statement,
   which is §B's measured 7-of-13 under-count showing up mechanically. `-41` also RED (no
   §Enforcement paragraph, no `build_parser` in §A or FR30). `-35`, `-36`, `-37`, `-37b`, `-39` and
   `-40` were **GREEN from the first run by design** — the registry was authored to match the live
   parser, so the redness is concentrated where the defect actually was: the documents.
2. **AC4.1 live-key layering, unfixed ordering** — **11 of 24** (live-key × hostile-pattern)
   combinations escaped the safeguard, including `--ignore-pattern 'A'` against **all four**
   `LIVE_KEY_PATTERNS` members and `--ignore-pattern '*'` against all four. `--ignore-path` escaped
   **0 of 4**. This is the measured basis on which DN-5 and DN-6 split the two flags.
3. **AC6.4 documented invocation, unfixed `README:195`** —
   `README.md:195: 'argus --budget 500 --materiality critical' -> ArgumentError: argument command:
   invalid choice: '500' (choose from 'audit')`. The extractor found it because it matches any
   console-script line in an executable block, **not** only `argus audit …` lines — had it been
   scoped to `argus audit`, the one broken invocation in the repository would have escaped the guard
   written to catch it.

**sha256 round-trip (10.1's D4).** The guards write nothing. Proven forward rather than asserted:
snapshot → execute all 25 new tests → snapshot, over the 11 documents they read
(`prd.md`, `addendum.md`, `architecture.md`, `epics.md`, `deferred-work.md`, `CHANGELOG.md`,
`README.md`, `action.yml`, `cli.py`, `argus-student-audit.yml`, story 1.7). **0 of 11 mutated.**

**Gates — ALL LOCAL, on Windows / Python 3.11.15 (AC8.4).**

| Gate | Result |
|---|---|
| `pytest tests/` (`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`) | **1297 passed, 0 failed, 0 skipped** (baseline 1272 → **+25**, exactly the new cases) |
| `mypy argus` | **Success: no issues found in 71 source files** |
| `bandit -r argus --severity-level medium` | **0 Medium, 0 High** (19 Low, unchanged) |
| `pytest --cov=argus --cov-fail-under=80` | **95.16%** |
| Dogfood `argus audit .` | **RELEASE_READY, exit 0, blocking_findings=0, deep_ratio=60/161, assessed 15/19 scope=application** — identical to the recorded baseline |

**+25 accounted for exactly:** 9 (`test_invocation_contract.py`) + 8 (`test_cli_flag_contract.py`) +
8 (`test_secret_suppression_recording.py`). **No test was removed, skipped, weakened or xfailed.**

**Write-set fence (AC8.6), checked with `git status --porcelain` AND `git diff --stat`, plus an
mtime partition** — this session begins at `19:01`, and every file modified at `19:01` or later is
in the permitted table with nothing else in it. **`argus/pipeline.py` and `argus/models.py` are
byte-unchanged** (`git diff --quiet` clean, both DN-6 branches' requirement satisfied by the bless
branch changing no field). Also byte-unchanged: `epics.md` (sha `3c1621ce…` identical to the
pre-edit snapshot; mtime `11:39`, i.e. 10.2's), `.github/workflows/audit-ci.yml`, `action.yml`,
`pyproject.toml`, `README.md:178-190`. `deferred-work.md` `git diff --numstat` = **`+404 / -0`**
(includes 10.2's uncommitted 257 — the load-bearing figure is the **`-0`**).

**Evidence-citation status (AC8.5, 10.1's binding rule): NOT ESTABLISHED.**
No CI run covers this tree. Run `31341363300` is sha-scoped to `00c8d1b` and cannot evidence a tree
carrying 10.1's, 10.2's and this story's uncommitted deltas. All results above are **LOCAL**, on
Windows / CPython 3.11.15, against a CI matrix of ubuntu × 3.10/3.11/3.12 — and the six commits
behind `00c8d1b` are *all* host-portability defects invisible on this host, which is precisely why a
local run is necessary and not sufficient. **Nothing was pushed, tagged or `workflow_dispatch`ed to
manufacture a citation (10.1's DN-7 / AC8.4).** The command a human runs to establish it:
`gh run list --workflow=audit-ci.yml --branch <branch>` after committing, then cite the run id
**together with the sha it covers**.

### Completion Notes List

**The enumeration is six, and the tree confirmed every claim (AC1).** No divergence to record beyond
the two drifted line numbers above. `--reports`' provenance (`084c6a7`, the separation seed) and
`--strict`'s (`ae5f00c`, Epic 8) both re-measured; `--report-dir`'s exclusion from the six is a
reasoned disposition, not an oversight, and AC7.3 thickened it anyway while it was in hand.

**DN-6's condition was MET, so `--ignore-pattern` was BLESSED, not removed.** The fallback branch was
not taken. Consequence recorded deliberately: `AuditRequest.ignore_patterns` is untouched,
`argus/models.py` is byte-unchanged, `AUDIT_REQUEST_SCHEMA_VERSION` is **not** bumped (no field
changed), and there is **no now-unreachable field to hand to Story 10.5's sweep** — AC8.2's
obligation is discharged by the branch not being taken, not skipped.

**AC4.4 design decision: (a) record-as-finding. Chosen, with its reason.** Design (b)
(record-on-`DetectorResult`) is *unreachable* under fence D, and that is a fact about the code rather
than a preference: a new `DetectorResult` field must be read by whoever folds the result, and the
only folder is `argus/pipeline.py:539` — which is byte-fenced to Story 12.1 at 1331 lines against the
NFR-M1 cap of 1200. Design (a) needs **zero** lines there, because `findings.extend(secret_result
.findings)` already carries it. The record is a non-blocking, redacted
`operator_suppressed_secret:<reason>` `Recording`; the reason travels **in the `rule_id`** because
`Recording` is frozen `extra="forbid"` with no free-text slot, and widening it would be a schema
change a specification-correction story has no licence to make.

**Zero verdict drift, proven three ways** (AC4.4, AC8.7): `depth_supported=None` makes the record
ineligible by construction (`is_verdict_blocking`), pinned by `TC-ArgusAgent-SECRET-001-22`; the
blocking count is asserted equal with and without the flag; and `reports/generator.py:556` filters
the security report to `("secret_scan", "hardcoded_secret")`, so no rendered report byte moves
either. Above all, **the record only ever fires on an operator-supplied rule**, and the dogfood run
passes none — so its verdict cannot drift, and measured, it did not.

**Two judgement calls worth a reviewer's attention.**

1. **Attribution is conservative on purpose.** `path_glob_reason` tests the **built-in**
   `DEFAULT_TEST_PATH_PATTERNS` *first*, so an `--ignore-path 'tests/**'` that merely restates a
   default is **not** credited with a suppression that would have happened without it. Crediting the
   operator there would inflate the disclosed count, and over-attributing a suppression is as
   dishonest as recording none. Pinned in all three directions by `TC-ArgusAgent-SECRET-001-19`.
2. **The disclosure prints AFTER the ship-readiness block, not before.** The first placement broke
   `tests/test_cli.py::test_cli_summary_line_is_unchanged_for_a_non_blocking_verdict`, which pins
   `Ship-readiness:` as the first line on stderr. **The existing test was not weakened** — the new
   line moved. It is also deliberately *not* emitted on the `ShipReadinessError` → exit `1` path:
   that exit means no verdict reached the consumer, and a suppression count printed beside a verdict
   we just refused to vouch for would dress a non-result as a result.

**One pre-existing closure guard fired, and it was right to.**
`TC-ArgusAgent-DOCS-001-16` (`test_release_surface_honesty.py`) refused the three new
`## Unreleased` sections until they were registered in `_NOTE_SECTIONS` — *"an unenumerated section
is a consumer claim nobody reviewed."* Registered deliberately, with a comment saying what each
claims. This is a sibling guard behaving exactly as AC6's is designed to behave for flags, and it is
the second piece of evidence in this story that the registry-plus-closure idiom works.

**Fences held, and one was tested against.** `pipeline.py` byte-unchanged — AC4's design was chosen
*because* of that fence, not merely checked against it afterwards. `--help` prose untouched (12.8);
the `cli.py` `except ValueError` arms are **structurally unchanged** but have **moved down by ~60
lines** — the docstring amendment (AC5.4) is above them — so **Story 12.8 must re-locate them by
anchor text**: `except ShipReadinessError as exc:` in `_emit_ship_readiness`, and the
`except ValueError as exc:` immediately following it (previously `:337`), plus the
`except ValueError as exc:` in `main`'s `run_audit` block (previously `:368-372`). `epics.md` not in
the write set — its stale *"architecture L226"* citation is recorded here (§B), not corrected there
(DN-10). `README.md:178-190` untouched (DN-9). The exit-`2` collision filed, not fixed (DN-11).

**Trap E.4 respected**: `tests/test_sequential_portability.py:568-593`'s `AuditRequest.model_fields`
inventory is untouched, un-weakened and not duplicated. It pins the **model**; AC6's guard pins the
**parser** — the exact gap through which §A.1 survived two audits.

**Three new deferrals filed with an id, an owner and a disposition** (AC8.3, AI-E9-8): `DF-10-3-A`
(the argparse-`2` / BLOCKED collision, §A.5 — owner Engineering Lead, target `12-9`), `DF-10-3-B`
(built-in suppressions undisclosed, AC4.5's boundary), `DF-10-3-C` (`--ignore-pattern`'s bare
substring matching, AC3.4's residual risk). **None carries `target_story: NONE` without a named
human** — where no story id is safe to assert, the owner is named and the reason for not asserting
one is written down rather than a wrong id being invented.

**AC-by-AC:** AC1 ✅ (six, re-derived) · AC2 ✅ (all six blessed, each with a behavioural test + a
CHANGELOG entry; no behaviour smuggled in beyond AC4's) · AC3 ✅ (threat model in architecture §G,
four questions answered, linked from the CHANGELOG) · AC4 ✅ (layering first per DN-7, then the
record; design (a); attribution real; zero drift proven) · AC5 ✅ (all six sites, dated, attributed,
struck-not-deleted; Story 1.7 append-only) · AC6 ✅ (both directions, defaults+shapes, findable
contract sites, non-vacuity, both positive controls, RED-first, registered in §Enforcement) ·
AC7 ✅ (DN-8 pinned both ways, `--reports`' inertness stated in the contract, `--report-dir`
thickened) · AC8 ✅ (ledger closed `+n/-0` with the new findings named, three deferrals filed, gates
run and labelled LOCAL, citation **NOT ESTABLISHED**, write set clean, dogfood verdict identical).

### File List

**Modified — code**
- `argus/detectors/secret_suppression.py` — Live-Key Safeguard moved above both operator arms;
  `path_glob_reason` splits built-in from custom path matches; `OPERATOR_ATTRIBUTABLE_REASONS`;
  module docstring records the order as the security property.
- `argus/detectors/secret_scan.py` — `RULE_OPERATOR_SUPPRESSED_SECRET`,
  `operator_suppression_rule_id`; the discarded `_reason` now mints a non-blocking redacted record,
  de-duplicated by content id; `SecretSuppressionEngine` import lifted to module scope.
- `argus/cli.py` — `_emit_suppression_disclosure` (AC4.3); the "LOCKED CLI contract" docstring block
  extended from 7 arguments to all 14 with defaults and owning stories (AC5.4).

**Modified — specifications**
- `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` — FR30 amended (AC5.1).
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §A invocation contract amended
  (AC5.2); §G *"Suppression threat model"* added (AC3); §Enforcement *"Invocation-contract
  enforcement"* added (AC6.9).
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — `DF-AUD-APAA-E` closure +
  `DF-10-3-A/B/C`, **append-only** (AC8.1, AC8.3).
- `_bmad-output/design-artifacts/ArgusAgent/stories/1-7-cli-invocation-contract-pipeline-signature-demo-vacuous-test-cartridge.md`
  — dated amendment note under AC3, **append-only** (AC5.3).
- `CHANGELOG.md` — three `## Unreleased` sections (AC2.2, AC5.6).
- `README.md` — the terminal invocation block at `:192-196` replaced with three that run (AC5.5).

**Modified — tests**
- `tests/test_release_surface_honesty.py` — the three new CHANGELOG sections registered in
  `_NOTE_SECTIONS` (the pre-existing closure guard's intended deliberate edit).

**Added — tests**
- `tests/test_invocation_contract.py` — `TC-ArgusAgent-CLI-001-35`..`-41` + `-37b`,
  `TC-ArgusAgent-DOCS-001-28` (AC6).
- `tests/test_cli_flag_contract.py` — `TC-ArgusAgent-CLI-001-42`..`-49` (AC2.1, AC4.3).
- `tests/test_secret_suppression_recording.py` — `TC-ArgusAgent-SECRET-001-15`..`-22` (AC4).

**Process**
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — this key + `last_updated`.
- `_bmad-output/design-artifacts/ArgusAgent/stories/10-3-invocation-contract-says-what-the-cli-accepts.md`
  — this file (`git add`ed with the delta, per AI-E8-1).

**Byte-unchanged, verified:** `argus/pipeline.py` · `argus/models.py` · `epics.md` ·
`.github/workflows/audit-ci.yml` · `action.yml` · `pyproject.toml` · `README.md:178-190` ·
`tests/test_sequential_portability.py`.

### Change Log

| Date | Version | Description |
|---|---|---|
| 2026-08-10 | 0.1 | Story contexted (`bmad-create-story`, unattended loop worker). Enumeration re-derived from the live parser: **six** unspecified flags, not the ledger's four (`--reports`, `--strict` newly found). Live-Key Safeguard bypass by `--ignore-pattern` measured. DN-1…DN-12 locked. Status → `ready-for-dev`. |
| 2026-08-10 | 1.0 | **Implemented (`bmad-dev-story`, unattended loop worker). All 8 ACs met; status → `review`.** T1 re-measured every figure before any edit — all confirmed (15 actions / 13 flags; six unspecified; the `--ignore-pattern "A"` bypass; `SystemExit 2` on `README:195`); two §B line numbers had drifted and are recorded. **RED-first demonstrated for all three keystones** (trap E.1): the equality guard failed naming 8 flags — §A.1's six on the contract-corpus half plus `--report-dir` and `--coverage-scope` on the in-code half, i.e. §B's 7-of-13 under-count showing up mechanically; the live-key assertions failed on **11 of 24** combinations; the documented-invocation test failed on `README:195`. **AC4 landed, so DN-6's bless branch stands and `--ignore-pattern` was NOT removed**: the Live-Key Safeguard now sits above both operator arms (inline annotation deliberately keeps top precedence), an operator-caused suppression is recorded as a non-blocking redacted `operator_suppressed_secret:<reason>` finding and disclosed on stderr on every run, and attribution is conservative so a redundant `--ignore-path` is not credited. **Design (a) of AC4.4 chosen because design (b) is unreachable under fence D** — `argus/pipeline.py` is byte-unchanged, as is `argus/models.py`. Six contract sites amended (FR30, architecture §A, `cli.py`'s LOCKED block 7→14 arguments, Story 1.7 append-only, `README:192-196`, CHANGELOG), threat model written into architecture §G, guard registered in §Enforcement. `DF-AUD-APAA-E` closed append-only (`-0`) with all three of its own errors named; `DF-10-3-A/B/C` filed with owners. **Gates (LOCAL): 1297 passed / 0 failed / 0 skipped (+25, exactly the new cases), mypy clean on 71 files, bandit 0 Med/High, coverage 95.16%, dogfood `RELEASE_READY` exit 0 — identical.** CI evidence **NOT ESTABLISHED** (10.1's rule; nothing pushed or dispatched to manufacture a citation). |
