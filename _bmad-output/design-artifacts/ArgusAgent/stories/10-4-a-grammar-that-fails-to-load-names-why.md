---
baseline_commit: 00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0
baseline_note: >-
  HEAD is `00c8d1b`. **Stories 10.1, 10.2 AND 10.3 are all `done` but their deltas are in the
  WORKING TREE, not committed.** `git status --porcelain` on 2026-08-10 shows `argus/cli.py`,
  `argus/cache/key.py`, `argus/audit/deep_audit.py`, `argus/detectors/secret_scan.py`,
  `argus/detectors/secret_suppression.py` and — **the file you are here to change** —
  `argus/index/ast_index.py` all `M`, plus five staged (`A`) test files
  (`test_evidence_citation.py`, `test_spec_claim_scope.py`, `test_invocation_contract.py`,
  `test_cli_flag_contract.py`, `test_secret_suppression_recording.py`).
  **You are building ON TOP of that uncommitted delta.** Do not revert it, do not re-do it, and
  do not assume `git diff HEAD` isolates YOUR work — it does not. Measure your own delta against
  the tree as you found it (mtime partition + `git diff` taken before your first edit) and say so
  in the Dev Agent Record.
  ⚠️ **`bmad-dev-loop-pack/`, `.bmad-drift-audit/` and `_bmad-output/audit-reports/*` belong to the
  orchestrator — do not add, move or delete them.**
  THIS FILE is untracked and IS yours: `git add` it with your delta or you repeat AI-E8-1, in which
  Epic 8 shipped with its own story file untracked because `git diff` cannot see an untracked path.
  **Every line number below was measured on 2026-08-10 against the working tree** (i.e. *after*
  10.1's, 10.2's and 10.3's edits). The ledger and the epic both cite `ast_index.py:266`; 10.2's own
  Dev Agent Record says it moved to `:294`; **it is at `:350` on this tree.** That is three
  coordinates for one clause in two days. **Locate every site by its ANCHOR TEXT and treat every
  line number in this document as a hint you must re-verify.**
story_key: 10-4-a-grammar-that-fails-to-load-names-why
epic: 10
---

# Story 10.4: A grammar that fails to load names why

Status: review

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

As an operator auditing a polyglot repository,
I want a grammar failure to say whether the package is missing or broken,
so that the remedy the report gives me is the remedy that works.

**Why this story is independent, and why it is still Epic 10's.** `sprint-status.yaml:364` and
[epics.md:1750](../epics.md) both say *"10.4 is independent and may land at any point"* — it corrects
no specification and touches no contract document. It is in Epic 10 because it is the fourth face of
the same defect: **a recorded statement that names a cause which is not the cause.** 10.1 fixed a
status claim that cited no gate. 10.2 fixed a spec claim that named the wrong scope. 10.3 fixed a
contract that named the wrong flag set. 10.4 fixes a **degradation record that names the wrong
reason**. The coverage grade it produces is honest — that is why `DF-AUD-APAA-F` is 🟢 — but the
*evidence attached to it* is wrong, and by 10.1's own rule an evidence artifact that misnames its
cause is not evidence. **Do not oversell this as a correctness defect** (see §A.5): overselling is the
exact class Stories 10.2 and 10.5 exist to close, and manufacturing it inside this story would be the
same joke 10.2 nearly told.

---

## Story Context

### Method statement — everything below was MEASURED on this tree on 2026-08-10

Every failure mode, exception type, line number, coverage figure and token in §A–§D was produced by
`grep`, by reading the file, by **executing `build_ast_index` against simulated failure modes on this
host**, by running `pytest --cov`, or by extracting string literals from the **shipped
`tree_sitter/_binding.cp311-win_amd64.pyd`**. **Four of the measurements change the story as the epic
and the ledger wrote it.** Re-derive them; do not transcribe them.

---

### A. The five findings that change this story

#### A.1 — 🚩 The ledger says TWO causes. Measurement finds **FOUR**, and all four emit the same token

`DF-AUD-APAA-F` ([deferred-work.md:1529-1543](../deferred-work.md)) and the epic AC
([epics.md:1906-1912](../epics.md)) both describe **two** states: *missing* vs *installed-but-broken*.
The function is `argus/index/ast_index.py::_get_parser_for_lang` (**measured at `:336-352`**):

```python
    try:
        from tree_sitter import Language, Parser          # ← cause 4 lives here
        module_name = f"tree_sitter_{lang}"
        mod = importlib.import_module(module_name)        # ← cause 1 lives here
        lang_func = getattr(mod, entry_point, None)
        if lang_func is not None:                         # ← cause 2 is this fall-through
            return Parser(Language(lang_func()))          # ← cause 3 lives here
    except (ImportError, Exception):
        pass
    return None
```

Executed on this host against a `.go` fixture, monkeypatching only `ast_index.importlib.import_module`
(the raw run is reproducible in three lines — reproduce it, it is AC5's RED evidence):

| # | Cause | What the operator actually has | **Recorded today** | Correct remedy |
|---|---|---|---|---|
| 0 | baseline, grammar installed | — | `ast_eligible=True`, reason `None` | — |
| 1 | `ModuleNotFoundError` on `tree_sitter_go` | the package is not installed | **`grammar_missing_go`** | `pip install tree-sitter-go` |
| 2 | module imports, `getattr(mod, "language")` → `None` | the package IS installed; **Argus** does not know its entry point | **`grammar_missing_go`** | *nothing the operator can do* — an **Argus** defect |
| 3 | entry point raises, or `Language()` rejects the capsule | the package is installed and **broken** for this runtime (ABI mismatch, corrupt build) | **`grammar_missing_go`** | reinstall / rebuild; check the core–grammar version pair |
| 4 | `from tree_sitter import …` raises | the **core** runtime is broken, not the grammar | **`grammar_missing_go`** | `pip install tree-sitter` — and *every* language is affected, not this one |

**All four collapse to one token, and in three of the four the token's implied remedy is wrong.**
Cause 2 is the worst of them: it tells an operator to install a package they already have — the exact
sentence the ledger uses to describe the defect — and it is the cause the ledger's own repair
(splitting the `except`) **does not catch, because nothing raises**. Story 10.2 measured this
independently and wrote it down for you: *"splitting `except (ImportError, Exception)` does nothing
here, because nothing raises. `getattr` returns `None`"*
([10-2 story:169-170](10-2-multi-language-grounding-is-v1-in-the-specs.md)). 10.2 fixed the two
**instances** it had (TypeScript, PHP) with `_ENTRY_POINT_BY_LANGUAGE` and explicitly left the
**class** — the silent `None` fall-through — to this story. Cause 4 is not in any prior document.

> **The tuple is redundant, and the redundancy is the tell.** `ImportError` is a subclass of
> `Exception`, so `except (ImportError, Exception)` is `except Exception` written in a way that looks
> like it discriminates. It is the only *catch-everything-then-`pass`* in `argus/` (verified: the
> other five broad catches at `secret_scan.py:428`, `tool_runner.py:265/273/335` and
> `ast_index.py:358` each carry a `# noqa: BLE001` **and record a typed outcome**). AR10 and
> `architecture.md:698` forbid this shape by name.

#### A.2 — 🚩🚩 THE FINDING THAT DECIDES AC6: the only surface that shows the token is **untested**, and it is **all-or-nothing**

`parse_failure_reason` has exactly **three** consumers in `argus/` (measured, whole-tree grep):

| Consumer | What it does | Reaches an operator? |
|---|---|---|
| `argus/detectors/vacuous_test.py:400` | copies it into `DegradedCondition.reason` | **NO — see A.3** |
| `argus/reports/generator.py:322-336` | `_render_readability_warning` — the CAUTION callout naming the pip command | **YES, and only here** |
| `argus/reports/generator.py:325` | reads the field via `getattr` duck-typing | (same site) |

Two measured facts about that single surface:

1. **It is dead code under test.** `pytest --cov=argus.reports.generator` over **every** test file that
   imports the generator (`test_report_generator`, `test_report_honesty`,
   `test_report_surface_consistency`, `test_release_note`, `test_release_preflight`,
   `test_critical_eligibility_pipeline`, `test_secret_scan_precision`) reports
   **`Missing … 322-336`** — the entire `grammar_missing_` counting block, the package lookup and the
   callout body have **never executed in this suite**. Line 316 (`if not entries`) is also missed;
   `318-320` are covered, i.e. every test reaches the function and returns at
   `if eligible: return []`.
   **Consequence: if you rename the token and forget this file, no test in the repo turns red.** The
   guard you are asked to write would pass, the ledger entry would close, and the one message an
   operator ever sees would have gone silent. That is the story eating its own tail, and it is why
   AC6 exists.
2. **It fires only when NOTHING parsed.** `if eligible: return []` at `:318-320`. In the persona's own
   repository — *"an operator auditing a polyglot repository"* — the Python files parse, so
   `eligible > 0`, so **the callout never fires and the Go/Rust grammar failure is invisible.**
   ⛔ **Fixing the partial case is Story 12.5's** (*"its absence and the reason appear in the tool's
   own output at the point the file is downgraded"*, [epics.md:2328-2330](../epics.md)) — see §D. It
   is **filed**, not fixed, here.

> **The trap inside the fix.** `:322-327` recovers the language by **string arithmetic**:
> `prefix = "grammar_missing_"` … `reason[len(prefix):]`. `grammar_entrypoint_missing_go` does **not**
> start with that prefix, so it is silently skipped; a naive widening to `startswith("grammar_")`
> would slice `grammar_entrypoint_missing_go` into the language `"entrypoint_missing_go"` and hand the
> operator `pip install tree-sitter-entrypoint_missing_go`. **Classification must move to one shared
> definition both sides import** (DN-3), never a second prefix guess.

#### A.3 — `DetectorResult.degraded` has **zero production readers**. File it; do not fix it

`grep -rn "\.degraded" argus/` (excluding `degraded=` constructions) returns **0 hits**. Three
detectors (`vacuous_test`, `orphan_code`, `tool_runner`) build `DegradedCondition` tuples, `base.py`
declares the field, **21 tests assert on it — and no code in `argus/` ever reads it.** So
`vacuous_test.py:400`'s careful `ast_entry.parse_failure_reason or "not_ast_eligible"` is written into
a structure nothing consumes: the reason is recorded and then dropped.

This is `DF-6-7-A`'s class exactly — *a delivered seam with no reachable production call site* — and
**Story 10.5's fourth AC is the sweep for it** ([epics.md:1951-1958](../epics.md)), while
**Story 12.4** owns making outcomes name their next action. ⛔ **Out of scope here** (AC7.3 files it
with a named owner and a `target_story`, per AI-E9-8: never `target_story: NONE`). It is recorded so
10.5 inherits a measurement instead of a rediscovery — the courtesy 10.2 paid this story in §A.1.

#### A.4 — The exception types, measured — and why the arm must never match on the message

Executed on this host (`tree-sitter 0.25.2`, CPython 3.11.15):

| Probe | Raises |
|---|---|
| `importlib.import_module("tree_sitter_nosuchlang")` | `ModuleNotFoundError` *(subclass of `ImportError`)* |
| `Language(42)` | `ValueError: invalid language ID` |
| `Language(object())` / `Language(None)` / `Language(tsp.language)` *(forgot the `()`)* | `TypeError: an integer is required` |
| entry point raises (`OSError("cannot open shared object file")`) | `OSError` |
| `KeyboardInterrupt` inside the entry point | **propagates today** — `BaseException` is not caught, and that is correct (AR10 degrades *errors*, never signals). **Keep it that way.** |

The real ABI-mismatch message was not reproducible on this host (no out-of-bound grammar is
installed), so it was recovered from the shipped binding instead — the literal
`Incompatible Language version %u. Must be between %u and %u` is present in
`.venv/Lib/site-packages/tree_sitter/_binding.cp311-win_amd64.pyd`, alongside `invalid language ID`,
which we measured as a `ValueError`. **Do not encode that string, or any other message text, in a
condition.** Classify by **arm position** — *which call raised* — not by exception message and not by
exception type: cause 3 is "the parser could not be constructed", whether that surfaces as
`ValueError`, `TypeError`, `OSError` or something the next tree-sitter release invents.

#### A.5 — The severity is 🟢 and the story must keep it there

Verified: `pipeline.py:391` and `:426`, `audit/grounding.py:88` and `vacuous_test.py:228/399` branch on
**`parse_failed` / `ast_eligible` booleans only** — **never on the token**. So the token split cannot
move a coverage grade, a deep ratio or a verdict, and a grammar failure pushes the verdict *away* from
green (fewer deep files → toward `INSUFFICIENT_COVERAGE`), not toward it.

**State this precisely and do not inflate it.** The false-green risk in this story is **not** in the
verdict; it is (a) in the **evidence**, which names a cause that is not the cause, and (b) in the
**operator's reading** of an ordinary-looking `INSUFFICIENT_COVERAGE` — *"your repo needs more tests"*
when the truth is *"I could not read your code"*, which is the harm `generator.py:300-311`'s own
docstring already describes. `parse_failed` **stays `False`** for a load failure: the flag means *a
parse was attempted and failed*, and no parse is attempted when no parser exists — the same convention
`non_python` already follows. Changing it would move the ledger denominator, which AC4 forbids.

---

### B. Where the code actually is — re-measured, because three documents disagree

| Site | Coordinate **on this tree** | Anchor to locate by |
|---|---|---|
| the blanket catch | **`argus/index/ast_index.py:350`** *(ledger says `:266`; 10.2's record says `:294`)* | `except (ImportError, Exception):` |
| the loader | `argus/index/ast_index.py:336-352` | `def _get_parser_for_lang(` |
| its only caller | `argus/index/ast_index.py:420-439` | `entry_point = _entry_point_for(` |
| the token emission | `argus/index/ast_index.py:432-438` | `parse_failure_reason=f"grammar_missing_{lang}"` |
| entry-point maps (10.2's) | `argus/index/ast_index.py:100-130` | `_ENTRY_POINT_BY_LANGUAGE` |
| the operator surface | `argus/reports/generator.py:297-346` | `def _render_readability_warning(` |
| its package table | `argus/reports/generator.py:283-294` | `_GRAMMAR_PACKAGE_BY_LANGUAGE` |
| the existing token pin | `tests/test_ast_index.py:90-116` | `TC-ArgusAgent-INDEX-001-73` |
| 10.2's grounding matrix | `tests/test_multilanguage_audit.py:293-330` | `TC-ArgusAgent-INTAKE-003-07/-08` |
| AR10's no-bare-except rule | `architecture.md:698` | `no bare \`except: pass\`` |
| the degradation rule | `architecture.md:694-699` | `### Error / Degradation Patterns` |
| §Enforcement (register your guard here) | `architecture.md:701-728` | `### Enforcement` |
| the ledger entry to close | `deferred-work.md:1529-1543` | `- **DF-AUD-APAA-F**` |
| PRD's binding sentence | `E-PRD/prd.md:473` | `a named reason token — never a silent drop` |

`prd.md:473` is the sentence this story makes true: *"It degrades to `ast_eligible=False` with **a
named reason token** — never a silent drop, never a false deep claim (AR10)."* A token that names the
wrong cause is a named token in form only.

---

### C. The instrument — reuse the idiom, do not invent one

10.1, 10.2 and 10.3 each landed a guard of the same shape, and all three survived code review on
iteration 1: **registry + closure + both-direction positive control + non-vacuity**. Use it. The
closure device differs per surface, and picking the right one is the only design decision here:

| Story | Closure device | Why |
|---|---|---|
| 10.1 `test_evidence_citation.py` | **glob** over `sprint-change-proposal-*.md` | a new document cannot escape by being new |
| 10.2 `test_spec_claim_scope.py` | **glob + claim-shape pattern** | a new spec sentence cannot escape |
| 10.3 `test_invocation_contract.py` | **live `argparse` walk** | the parser is *exactly* enumerable, so the guard can be exact |
| **10.4 (this story)** | **the module's own source, parsed with `ast`** | the failure modes are *exactly* enumerable **from the code**, so a fifth arm cannot be added unregistered |

**This is the point.** A hand-written table of four failure modes closes today's four instances; only a
closure over the function's own control flow closes the class — which is precisely the lesson 10.2
recorded when its hand-list was wrong for the third time (*"the closure GUARD, not the site list, is
the load-bearing AC"*). `ast.parse(Path(ast_index.__file__).read_text())` → locate
`_get_parser_for_lang` → walk it. That is stdlib only; **add no dependency** (10.1's guard is pure
`pathlib` + `re`, 10.3's is pure `argparse` introspection).

⚠️ **Non-vacuity is mandatory, for the same reason it was in 10.3.** A source-walking guard goes green
by finding nothing. If the function is renamed or moved, the walk must **fail loudly**, never pass on
an empty node set.

---

### D. ⛔ FENCES — what this story must NOT touch

| Fenced | Owner | Why, and where the line sits |
|---|---|---|
| **The `tree-sitter <0.26` runtime version bound; any verdict withholding** | **Story 11.4** | **The adjacent boundary — state it in your Dev Notes.** 11.4's danger is the *silent* case: on `0.26.0` the grammar **loads fine** and AST corroboration merely stops firing, flipping `NOT_READY_FOR_RELEASE → RELEASE_READY` ([epics.md:2089-2091](../epics.md)). **Nothing raises, so this story's loader never sees it** — which is exactly why 11.4 needs a *runtime version assertion* and why 10.4 cannot substitute for one. Where they touch: an out-of-bound core that makes `Language()` **raise** now records `grammar_load_failed_<lang>`, a signal 11.4 may key on. ⛔ **10.4 adds no version comparison, no typed finding, and never changes a verdict.** 10.4 records; 11.4 decides what a record may vouch for. |
| **Which grammars ship by default; `pyproject.toml`'s `[languages]` extra; any NEW per-file point-of-downgrade output** | **Story 12.5** | **The other adjacent boundary.** 12.5 owns the packaging decision (NFR-P3) and the *point-of-downgrade* surface ([epics.md:2328-2330](../epics.md)). 10.4's **only** report-layer obligation is that the **already-existing** whole-report callout does not go **silent** or **misdirect** under the new token set (AC6) — a regression this story would otherwise introduce itself (§A.2). The measured **partial-failure blind spot** (`if eligible: return []`) is **filed for 12.5** (AC7.3), not fixed here. |
| **Operator-facing cause-and-fix messages; `--help` prose; the `cli.py` `except ValueError` split** | **Story 12.8** | 12.8 explicitly *"extends 10.4's diagnosis principle to the user surface"* and names *"missing grammar"* among the errors it must make actionable ([epics.md:2405](../epics.md)). The **exception type/detail** an operator might want is 12.8's (DN-5). |
| **`argus/pipeline.py` — must be BYTE-UNCHANGED** | **Story 12.1** | NFR-M1: 1331 lines vs a 1200 cap. Every AC here is reachable without touching it (verified: `pipeline.py` branches on booleans only, §A.5). |
| **`DetectorResult.degraded`'s missing production reader** | **Stories 10.5 / 12.4** | §A.3 — filed with an owner (AC7.3), not fixed. |
| **`DF-10-2-A`** (C/C++/Ruby/Rust ground but extract zero definitions) | already filed, open | A *different* failure: those grammars **load and parse**. Do not conflate. |
| **`epics.md`, `E-PRD/*`, `README.md`, `CHANGELOG.md`, `action.yml`, `audit-ci.yml`, `pyproject.toml`** | — | This story corrects **no specification**. If you find yourself editing a contract document, scope has leaked — stop and record why. `architecture.md` is the **one** exception, and only §Enforcement + §Error/Degradation (AC5.7). |
| **Publishing, tagging, `workflow_dispatch`** | 12.9 / operator | 10.1's DN-7: triggering a run to manufacture a citation is manufacturing evidence. |
| **The Epic 13 precision gate** | Epic 13 | Nothing here clears it. |

---

### E. Traps previous stories already paid for — the four that apply

| # | Trap | What it costs you here |
|---|---|---|
| **E.1** | **AI-E3-1 — a keystone test that was green over its own keystone bug** (Story 3.4). | **RED-first is MANDATORY** for AC5 *and* AC6. Capture the failure against the **pre-change** tree and paste it into the Dev Agent Record. §A.2 makes this non-optional: AC6's target lines have **never executed**, so a test written after the fix proves nothing. |
| **E.2** | **10.2's hand-list was wrong three times.** | Do not close this with a four-row table. AC5's closure over the function's own arms is the load-bearing half (§C). |
| **E.3** | **Positive control, both directions** (10.1/10.3). | A synthetic failure mode with no registered token must **fire**; a registered mode must **not**. Pure functions over synthetic inputs — **never** by uninstalling a real grammar or mutating the shared registry at runtime. |
| **E.4** | **A guard that passes vacuously** (10.3's `-39`). | Assert non-zero arms walked, non-zero modes exercised, non-zero tokens registered. |
| **E.5** | **AI-E8-1 / -E8-2 — `git diff` cannot see an untracked path.** | `git add` this story file **and** every new test/module before you claim a write-set fence. Verify with `git status --porcelain` **and** `git diff --stat`. |

---

## Acceptance Criteria

### AC1 — The four causes are distinguished, and every token implies a remedy that works

1. **Four distinct outcomes** replace the single token, one per §A.1 cause. The token set is
   **exactly** (DN-1 — these spellings are locked, and AC5 pins them):

   | Cause | Token | Remedy it implies |
   |---|---|---|
   | 1 — package not importable | **`grammar_missing_<lang>`** *(UNCHANGED)* | `pip install tree-sitter-<lang>` |
   | 2 — imported, entry point absent | **`grammar_entrypoint_missing_<lang>`** | an **Argus** defect: the entry-point map has no entry for this package version |
   | 3 — entry point present, parser construction failed | **`grammar_load_failed_<lang>`** | the installed grammar is broken for this runtime — reinstall/rebuild |
   | 4 — the `tree_sitter` **core** is not importable | **`tree_sitter_runtime_missing`** *(no `<lang>` suffix — it is not language-specific)* | `pip install tree-sitter`; **every** language is affected |

2. **`grammar_missing_<lang>` keeps its exact spelling and its exact meaning** — the epic requires it
   (*"a missing package keeps `grammar_missing_<lang>`"*, [epics.md:1910-1911](../epics.md)) and
   `TC-ArgusAgent-INDEX-001-73` pins it. That test must still pass **unmodified**; if you need to edit
   it, you have changed the missing-package contract and must say why.
3. **Classification is by ARM POSITION, never by message and never by exception type** (§A.4). No
   condition anywhere may test for `"Incompatible Language version"`, `"invalid language ID"` or any
   other message substring.
4. **Cause 2 is in scope and is not optional.** It is the cause the ledger's stated repair misses
   (§A.1) and the one 10.2 handed forward by name. A story that splits the `except` and leaves the
   silent `getattr` → `None` fall-through has closed the instance and left the class.

### AC2 — The blanket catch is gone, and nothing is swallowed

1. **`except (ImportError, Exception):` … `pass` is deleted** and replaced by explicit arms, each of
   which **returns a recorded outcome**. The redundancy is named in the code comment so the next
   reader learns why the tuple was a tell, not a discriminator (§A.1).
2. **No handler body in `_get_parser_for_lang` is a lone `pass`.** Every caught exception produces a
   token. This is `architecture.md:698` / AR10 / Story 4.3, and it is the ledger's stated close
   condition.
3. **Broad catches keep the house form**: the cause-3 arm may catch `Exception` — it must, because
   §A.4 shows the type varies — but it carries `# noqa: BLE001` **and a comment naming the degraded
   outcome**, matching `ast_index.py:358`, `secret_scan.py:428` and `tool_runner.py:265/273/335`.
4. **`BaseException` is still NOT caught.** `KeyboardInterrupt` must keep propagating (§A.4).
   ⛔ A guard assertion, not a hope.
5. **No exception message, `repr`, traceback or host path is persisted anywhere** (NFR-S1). Recording
   `str(exc)` would put a host filesystem path into the index — the containment rule Stories 2.5 and
   4.4 are built on. **Pin it**: a simulated failure raising
   `OSError("/home/operator/secret/lib/libfoo.so: cannot open shared object file")` must produce a
   record in which **neither the path nor any fragment of the message appears** (assert against the
   serialized `model_dump_json()` of the whole `AstIndex`, not just the one field).

### AC3 — One definition of the token set, imported by both sides

1. **The tokens and their remedy classification live in ONE pure module**, and both the producer
   (`argus/index/ast_index.py`) and the consumer (`argus/reports/generator.py`) import them from it
   (DN-3). **`argus/shared/grammar_status.py`** is the locked location and
   `argus/shared/source_languages.py` is the precedent — `ast_index.py:59-66` and `:77-78` already
   record what this project paid when *"the same mapping lived in four places"*.
2. **It is PURE** (AR8): frozen data + pure functions, no I/O, no `importlib.metadata`, no tree-sitter
   import. The dependency arrow is impure-shell → pure-contract, the sanctioned one.
3. **It exposes a classifier, not a prefix**: given a reason token, callers get back *(is this a
   grammar-load failure? / which class? / which language, if any?)*. ⛔ **No second
   `startswith`/slice parse anywhere** — §A.2's trap.
4. ⛔ **No new field on `AstIndexEntry` / `AstIndex`, and `schema_version` stays `"2"`** (DN-5).
   `tests/test_ast_index.py:257` pins `"2"` as 10.2's deliberate bump; `CACHE_KEY_SCHEMA_VERSION`
   stays `"3"` (verified: `argus/cache/key.py` folds `grammar_versions`, **never** entries, so no key
   moves). **Assert both are unchanged** — a silent schema bump is the invalidation class `DF-5-1-A`
   files.
5. **Record the module count move.** `mypy argus` reports **71 source files** on this tree; a new
   module makes it **72**. Say so in the Dev Agent Record so a reviewer does not read it as drift.

### AC4 — The degradation is unchanged, provably

The epic's second AC: *"the degradation itself is unchanged: a file whose grammar cannot load is still
recorded `ast_eligible=False`, never a false deep claim"* ([epics.md:1914-1917](../epics.md)).

1. For **every** one of the four causes: `ast_eligible is False`, `parse_failed is False` (§A.5 — no
   parse was attempted), `definitions == ()` and `edges == ()`. **Asserted per cause, not once.**
2. **The coverage grade and the verdict are identical before and after.** Assert equality on the
   graded outcome for a fixture repository under a simulated failure, comparing the pre-change and
   post-change behaviour — not merely that a verdict was produced.
3. **A grammar that fails to load contributes NO `GrammarProvenance` row** — it never parsed, so
   10.2's *"a function of the audit, not of the host"* rule holds. Assert `grammar_versions` is
   unchanged under each simulated failure.
4. **The dogfood verdict is byte-identical** to the recorded baseline: `argus audit .` →
   `RELEASE_READY`, exit 0, `blocking_findings=0`, `deep_ratio=60/161`, assessed 15/19,
   `scope=application`. A changed dogfood verdict is a **stop-and-report**, not a figure to update.
5. **`tests/test_ast_index.py` `-73`/`-74` and `tests/test_multilanguage_audit.py`
   `INTAKE-003-07`/`-08` (10.2's 10/10 grounding matrix) stay green, unmodified, unskipped.**

### AC5 — 🔑 A committed guard pins every cause, closes over the code's own arms, and cannot go vacuous

**This is the AC that makes the story stick** (DN-2). New file `tests/test_grammar_diagnosis.py`,
ids **`TC-ArgusAgent-INDEX-001-108`..** (measured maximum in use: `-107`).

1. **Behavioural matrix — every cause, its exact token.** Parametrized over the four causes of §A.1
   **plus the success baseline**, each simulated at the **`importlib.import_module` seam inside
   `ast_index`** (monkeypatch), driving the real `build_ast_index` and asserting the exact token.
   ⛔ Never by uninstalling a grammar; never by editing `_ENTRY_POINT_BY_LANGUAGE`.
2. **Closure over the code, not over a list (§C).** Parse `argus/index/ast_index.py` with the stdlib
   `ast` module, locate `_get_parser_for_lang`, and assert:
   - **no `ExceptHandler` has `type is None`** (no bare `except:`);
   - **no `ExceptHandler` body is a lone `pass`/`...`** — AC2.2 mechanically;
   - **no handler catches a redundant tuple** in which one member subclasses another — this is the
     `(ImportError, Exception)` shape itself, and the assertion is what stops it coming back;
   - **`BaseException`, `KeyboardInterrupt` and `SystemExit` appear in no handler** (AC2.4);
   - **every `return`/failure path in the function is accounted for by a registered token**, so a
     **fifth** arm added later fails this test until it is registered. *This is the closure.*
3. **Registry closure, both directions.** The token registry in `argus/shared/grammar_status.py` and
   the modes the matrix exercises are **the same set**: a registered token no test drives **fails**,
   and an observed token that is not registered **fails**.
4. **Positive control, both directions (E.3).** A synthetic failure mode carrying an unregistered
   token **fires**; a synthetic mode matching its registered token **does not**. Pure functions over
   synthetic inputs.
5. **Non-vacuity (E.4).** Fail if zero arms were walked, zero causes exercised, zero tokens
   registered, or if `_get_parser_for_lang` could not be located in the parsed module — a rename must
   turn this **red**, not silently green.
6. **NFR-S1 containment is asserted here** (AC2.5), on the serialized index.
7. **Registered in `architecture.md` §Enforcement** beside 10.1's, 10.2's and 10.3's guards, and the
   §Error/Degradation section gains the **one-line rule** this story establishes: *a degraded outcome
   records the cause it actually had, and a recorded reason token names a remedy that works.* The
   guard asserts **both** paragraphs are still present — *a rule that lives only in a test is not a
   rule, and a rule that lives only in prose is not enforced* (10.1's `-23`, 10.3's precedent).
8. **RED first (E.1).** Run the matrix against the **unamended** loader and record the failure showing
   **causes 2, 3 and 4 all reporting `grammar_missing_go`**, before any `argus/` edit. Restore any
   touched file byte-identically (sha256 round-trip, 10.1's D4).

### AC6 — The one surface an operator sees does not go silent, and does not misdirect

**Forced by §A.2** — without this AC, the token split *disables* the only message that ever reaches an
operator, and no existing test notices.

1. **`_render_readability_warning` classifies via the AC3 shared classifier**, never by prefix
   arithmetic. ⛔ The `reason[len(prefix):]` slice at `generator.py:327` is removed, not widened.
2. **Every one of the four causes produces a callout, and the remedy is per class**: `pip install
   tree-sitter-<lang>` **only** for cause 1; cause 4 names the **core** package; causes 2 and 3 do
   **not** tell the operator to install something they already have. **This is the story's whole
   point, delivered at the surface the story's user story describes.**
3. **The mixed case is pinned**: an index containing more than one failure class produces a callout
   naming **each** class with **its own** remedy — never a single blended sentence.
4. **RED first, mandatory (§A.2.1).** These lines have **never executed**. Demonstrate the pre-change
   failure: with the new tokens in place and `generator.py` untouched, the callout for causes 2/3/4
   is **absent or wrong**. Record the raw output.
5. ⛔ **The all-or-nothing trigger (`if eligible: return []`) is NOT changed** — that is Story 12.5's
   (§D), and it is filed under AC7.3. Do not widen the trigger; widen only the classification inside
   it.
6. **`_GRAMMAR_PACKAGE_BY_LANGUAGE` (`generator.py:283-294`) may move into the AC3 pure module** if
   that removes the duplication — but it is a **move**, not an edit: the same ten languages, the same
   ten package names, asserted equal to `LANGUAGE_BY_SUFFIX`'s value set so an eleventh language
   cannot be added to one and not the other. If you judge the move out of scope, say so and leave it
   byte-unchanged. Both outcomes are acceptable; silence is not.

### AC7 — The ledger closes honestly, the gates run, and the fences hold

1. **`DF-AUD-APAA-F` (`deferred-work.md:1529-1543`) is closed APPEND-ONLY.** The original entry stays
   **byte-intact**; the closure note is appended and **must name the findings the entry did not
   have**: §A.1 (two causes in the ledger, **four** measured, with the entry-point fall-through and
   the core-runtime arm named and their provenance given), §A.2 (the only operator surface was
   **untested and all-or-nothing**), §A.3 (`DetectorResult.degraded` has no production reader), and
   the exact token each cause now records. `git diff --numstat` on `deferred-work.md` is **`+n / -0`**
   (10.1's DN-8 / §3.4).
2. **Story 10.2's fence note is honoured in writing.** 10.2 recorded *"leave the except clause
   structurally as you found it … 10.4 should re-locate by anchor"*. Confirm in the Dev Agent Record
   which coordinate you actually found it at (**measured `:350`**, not the `:266` the ledger names nor
   the `:294` 10.2 recorded) — three coordinates in two days is itself the argument for anchors
   over line numbers.
3. **New deferrals are filed with an id, an owner and a `target_story`** — never `target_story: NONE`
   without a named human (AI-E9-8). **At minimum:**
   - **§A.2.2 — the partial-failure blind spot** (`if eligible: return []`; a polyglot repo whose
     Python parses is told nothing about its failed Go grammar) → `target_story: 12-5-…`;
   - **§A.3 — `DetectorResult.degraded` has zero production readers** → `target_story: 10-5-…` (its
     reverse-sweep AC), owner Governance Owner;
   - **the exception detail an operator might want** (type/class, never the message) → 12.8, which
     already inherits this story's diagnosis principle by name.
4. **Gates re-run and LABELLED LOCAL** (10.1's AC6): `mypy argus` · `bandit -r argus --severity-level
   medium` · `pytest tests/ --cov=argus --cov-fail-under=80`. **Baseline RE-MEASURED on this tree,
   2026-08-10: 1297 collected under `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; `mypy` clean on 71 source
   files; coverage 95.16%.** The count grows by **exactly** your new cases; **no test removed,
   skipped, weakened or `xfail`ed.**
5. **Evidence-citation compliance** — 10.1's binding rule (`architecture.md` §H + §Enforcement,
   enforced by `tests/test_evidence_citation.py`). Local gates are **necessary, not sufficient**: CI
   runs 3.10/3.11/3.12 on ubuntu, this host is Windows/CPython 3.11.15, and the six commits behind
   `00c8d1b` were **all** host-portability defects invisible here. Run `31341363300` is sha-scoped to
   `00c8d1b` and **cannot** evidence a tree carrying 10.1's, 10.2's, 10.3's and your deltas. Either
   cite the `audit-ci.yml` run covering your **own** HEAD *with the sha it covers*, or record the
   status **NOT ESTABLISHED** and name the command a human runs.
   ⛔ **Do not push, tag or `workflow_dispatch`** (10.1's DN-7).
6. **Write set — the fence, checked with `git status --porcelain` AND `git diff --stat`** (E.5):

   | Permitted | For |
   |---|---|
   | `argus/index/ast_index.py` | AC1, AC2, AC4 |
   | `argus/shared/grammar_status.py` (**NEW**) | AC3 |
   | `argus/reports/generator.py` | AC6 |
   | `tests/test_grammar_diagnosis.py` (**NEW**) | AC5 |
   | `architecture.md` (**§Error/Degradation + §Enforcement ONLY**) | AC5.7 |
   | `deferred-work.md` (**append-only**) | AC7.1, AC7.3 |
   | this story file · `sprint-status.yaml` | process |

   **Byte-unchanged, verified with `git diff --quiet`:** `argus/pipeline.py` (fence, NFR-M1
   1331/1200) · `argus/models.py` · `argus/cache/key.py` · `argus/cli.py` · `pyproject.toml` ·
   `epics.md` · `E-PRD/**` · `README.md` · `CHANGELOG.md` · `action.yml` · `audit-ci.yml` · every
   Epic 1–9 artifact and retrospective. **A diff outside the table means scope has leaked — stop and
   record why rather than widening.**
7. **Whole-system, not just the ACs.** Full suite green; dogfood verdict identical (AC4.4); the story
   leaves the system working end-to-end, not merely satisfying its own ACs.

---

## Tasks / Subtasks

- [x] **T1 — Re-measure before you edit anything (AC1, AC2) — FIRST**
  - [x] Locate `except (ImportError, Exception)` **by anchor** and record the coordinate you actually
        found (expected `:350`; the ledger says `:266`, 10.2 says `:294`). (AC7.2) — **found at `:350`,
        confirming the story's re-measurement and making it the third coordinate in two days.**
  - [x] Reproduce the §A.1 five-mode probe on this host; confirm all four causes emit
        `grammar_missing_go`. **Keep the raw output — it is AC5.8's RED evidence.** (AC1) — **confirmed
        verbatim; raw output in Debug Log §1.**
  - [x] Reproduce the §A.4 exception-type probes, including that `KeyboardInterrupt` propagates.
        (AC2.4) — **confirmed verbatim; Debug Log §2.**
  - [x] Re-run the §A.2 coverage measurement and confirm `generator.py:322-336` is **missing**.
        (AC6.4) — **confirmed: `Missing … 94, 278, 316, 322-336, …`.**
  - [x] Re-verify the baseline: **1297 collected** under `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, mypy
        clean on **71** files. Record any divergence rather than adopting the story's figure. (AC7.4)
        — **1297 and 71 both confirmed. One divergence found and NOT adopted: the dogfood figures
        (Debug Log §7).**
- [x] **T2 — Write the guard RED, against the unamended tree (AC5) — BEFORE any `argus/` edit**
  - [x] `tests/test_grammar_diagnosis.py`, ids `INDEX-001-108..`; behavioural matrix, `ast`-based
        closure, both-direction registry closure, positive control both ways, non-vacuity,
        containment. — **27 tests: `INDEX-001-108..-119`, `REPORT-002-25..-29`, `DOCS-001-29`.**
  - [x] Run it. **Record the failure showing causes 2/3/4 all reporting `grammar_missing_go`** and the
        `(ImportError, Exception)` redundancy assertion firing. (AC5.8) — **15 of 27 RED; Debug Log §3.**
  - [x] sha256 round-trip any file you touched to produce the RED state. (AC5.8) — **`ast_index.py`
        and `generator.py` verified byte-identical at RED capture (`sha256sum -c`: both OK).**
- [x] **T3 — The pure token module (AC3)**
  - [x] `argus/shared/grammar_status.py`: four tokens, remedy class per token, a classifier that
        returns class + language. No I/O, no tree-sitter import. — **purity asserted by `-119`.**
  - [x] Assert `schema_version == "2"` and `CACHE_KEY_SCHEMA_VERSION == "3"` are **unchanged**.
        (AC3.4) — **`-111`, plus the whole `AstIndexEntry` field set.**
- [x] **T4 — Split the loader (AC1, AC2)**
  - [x] Explicit arms: core-import → cause 4; grammar-import `ImportError` → cause 1; `getattr` →
        `None` → cause 2; construction raises → cause 3 (`# noqa: BLE001` + comment).
  - [x] Carry the cause back to the caller (`:420-439`) so the emitted token is the arm's, not a
        constant. Keep the parser cache keyed `(lang, entry_point)` — 10.2's `.tsx` fix depends on it.
        — **cache key unchanged; it now caches the whole `_ParserLoad` outcome.**
  - [x] Comment **why** the tuple was redundant, so the shape does not return. (AC2.1)
- [x] **T5 — Prove the degradation did not move (AC4)**
  - [x] Per-cause assertions on `ast_eligible` / `parse_failed` / `definitions` / `edges`. — **`-110`.**
  - [x] Grade-and-verdict equality under simulated failure; `grammar_versions` unchanged. — **`-114`
        runs a real `run_audit` under each of the four causes and requires one distinct outcome.**
  - [x] `-73`/`-74` and `INTAKE-003-07`/`-08` green and unmodified. — **all four green; neither test
        file touched (`tests/test_ast_index.py` / `test_multilanguage_audit.py` are not in my delta).**
- [x] **T6 — Keep the operator surface honest (AC6)**
  - [x] Demonstrate the pre-change RED (callout absent/wrong for causes 2/3/4). (AC6.4) — **Debug Log
        §4: cause 2 produced NO callout; the mixed case silently counted 2 of 4 files.**
  - [x] Route `_render_readability_warning` through the shared classifier; per-class remedies; pin the
        mixed case; ⛔ do not change the `if eligible` trigger. — **trigger pinned unchanged by `-29`.**
  - [x] Rule on the `_GRAMMAR_PACKAGE_BY_LANGUAGE` move — either way, **record the decision**.
        (AC6.6) — **ruled MOVE (DEV-2, below).**
- [x] **T7 — Architecture (AC5.7)**
  - [x] One-line rule into §Error/Degradation; guard registered in §Enforcement; guard asserts both
        are present. — **`DOCS-001-29`; it went RED first (the anchors were absent) and then green.**
- [x] **T8 — Close the ledger and file forward (AC7.1, AC7.3)**
  - [x] `DF-AUD-APAA-F` closed append-only, naming all four causes and the §A.2/§A.3 findings.
        — **`git diff --numstat` on `deferred-work.md`: `+540 / -0`, and append-only additionally
        verified programmatically (`after.startswith(before)`).**
  - [x] File the three deferrals, each with an id, an owner and a real `target_story`. — **`DF-10-4-A`
        → 12-5, `DF-10-4-B` → 10-5 (Governance Owner), `DF-10-4-C` → 12-8. No `target_story: NONE`.**
- [x] **T9 — Gates, fences, write set (AC7.4-7.7)** — ✅ **UNBLOCKED by operator decision 2026-08-10; see §Operator decisions below**
  - [x] mypy (expect **72** files — record the move) · bandit · full suite · coverage · dogfood.
        — **mypy clean on 72 (71→72 exactly as AC3.5 predicted); bandit 0 High / 0 Medium (19 Low,
        baseline); coverage 95.51% (from 95.16%); dogfood verdict UNCHANGED by this delta (Debug Log
        §7, §10). Full suite after the fix round: **1324 collected, 1324 pass, 0 fail, 0 error,
        0 skip** (Debug Log §10).**
  - [x] `git status --porcelain` + `git diff --stat` + `git diff --quiet` on every byte-unchanged
        path; `git add` the new module, the new test and this story file. — **write set clean
        (Debug Log §6); all three paths staged `A`.**
  - [x] Record the CI evidence status per AC7.5 — cite a run covering your own HEAD, or
        **NOT ESTABLISHED**. — **NOT ESTABLISHED (below), and re-affirmed after the commits: HEAD has
        moved to a sha no CI run has ever seen, and run `31341363300` is still scoped to `00c8d1b`.
        Nothing pushed, tagged or dispatched.**
  - [x] ✅ **Full suite green** — the five red `test_dogfood_*` guards are resolved as the operator
        directed: the 10.1–10.4 deltas are committed, the three committed Epic-7 artifacts are
        regenerated **through their own renderers** at a HEAD that genuinely contains those deltas,
        and the suite is **1324/1324**. See §Operator decisions and Debug Log §10.
- [x] **T10 — Fix round: execute the operator's two decisions (2026-08-10)**
  - [x] **D1** — commit 10.1–10.4's deltas (commit only; no push, no tag, no dispatch), then
        regenerate `minions-dogfood-partition-plan.md`, `-budget-plan.md` and `-proof.md` via
        `partition_plan.render_partition_plan_markdown` / `render_budget_plan_markdown` /
        `proof_render.render_proof_markdown`, then re-run `test_dogfood_plan.py` +
        `test_dogfood_proof.py` to green. — **done; 48/48 dogfood tests green.**
  - [x] **D1 sub-decision (delegated to dev)** — branch vs. `master`. — **ruled `master`, on measured
        evidence; see DEV-6.**
  - [x] **D2** — file the systemic sub-finding append-only in `deferred-work.md` with a named owner
        and a real `target_story`. — **`DF-10-4-D` filed; `git diff --numstat` `+585 / -0`.**

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

| # | Decision | Rationale |
|---|---|---|
| **DN-1** | **Four causes, four tokens, spellings fixed by AC1.1.** `grammar_missing_<lang>` keeps its exact spelling. | The epic requires the missing case keep its token; `-73` and `generator.py` both depend on it. Four rather than the ledger's two because measurement found four (§A.1) — the same "the enumeration is wrong" correction 10.2 and 10.3 each made, made once here **before** implementation instead of after. |
| **DN-2** | **AC5 (the guard) is load-bearing, not AC1 (the tokens).** | 10.2's own conclusion after its hand-list was wrong three times: a list closes instances, a closure closes the class. Here the closure can be **exact**, because the failure modes are enumerable from the function's own AST (§C). |
| **DN-3** | **The token set lives in ONE new pure module, `argus/shared/grammar_status.py`; both producer and report import it.** | `ast_index.py:59-66` / `:77-78` record what this project paid when one mapping lived in four places; `source_languages.py` is the sanctioned precedent. The alternative — `reports/` importing the impure `index/` for a constant — inverts the layering (AR8). Cost is one module (mypy 71→72), recorded in AC3.5. |
| **DN-4** | **Classification by ARM POSITION; never by exception message; never by exception type.** | §A.4: the same cause surfaces as `ValueError`, `TypeError` or `OSError` depending on how the grammar is broken, and the ABI message is a C format string (`Incompatible Language version %u…`) that a tree-sitter release may change. Matching on it would be a new instance of the fragility this story removes. |
| **DN-5** | **NO new field on `AstIndexEntry`; `schema_version` stays `"2"`; the exception detail is DEFERRED to 12.8.** | The epic asks for a *distinct token*, not a *detail payload*. A field would (a) spend a second schema bump inside one epic on a 🟢 diagnosis defect, (b) edit `test_ast_index.py:257`, a pin 10.2 deliberately placed, and (c) create a persisted free-text slot whose only natural filler is `str(exc)` — a host path, breaching NFR-S1. `argus/` has **no logging facility** (measured: one file mentions `logging`), so there is nowhere else to put it; 12.8 owns the operator message and inherits this principle by name. **Do not manufacture an unread seam** — §A.3 is this repo's third instance of that class. |
| **DN-6** | **`parse_failed` stays `False` for all four causes.** | §A.5: the flag means *a parse was attempted and failed*; no parse is attempted with no parser. `non_python` already follows this convention, and `pipeline.py:391/426` branches on it — flipping it would move the coverage denominator, which AC4 forbids and which would turn a 🟢 diagnosis fix into a verdict change. |
| **DN-7** | **AC6 (the report) is IN scope; the partial-failure trigger is OUT.** | Without AC6 the story silently disables the only operator-facing message (§A.2) — a regression it introduces itself, and no existing test would catch it. But *widening* the trigger to fire when some files parsed is a new surface, and 12.5 owns the point-of-downgrade output by name. **In: do not go silent. Out: do not add a surface.** |
| **DN-8** | **Cause 4 (`tree_sitter_runtime_missing`) is in scope even though the core is a base dependency.** | It is one arm, and it produces the maximally wrong message today: *"install `tree-sitter-go`"* when the core is broken and **every** language is down. `pyproject.toml:26` pins `tree-sitter>=0.25.0,<0.26` in base deps, so this state means a broken install — precisely a remedy-that-cannot-work. |
| **DN-9** | **⛔ No verdict, gate or version comparison changes.** | Fence to 11.4 (§D). 10.4 records; 11.4 decides what a record may vouch for. Crossing this line converts a 🟢 independent story into a release-integrity change that Epic 11 has not yet reasoned about. |

### Architecture patterns & constraints a reviewer will check

- **AR8 pure/impure**: the loader is impure shell; the token module is pure contract; the arrow is
  shell → contract, never the reverse.
- **AR10 / `architecture.md:694-699`**: failure → recorded degraded outcome, never an uncaught raise,
  never a bare `except: pass`. This story is the last instance of that shape in `argus/`.
- **AR11**: entries stay sorted; you are not changing ordering.
- **NFR-S1**: no absolute host path persisted — AC2.5 pins it on the serialized index.
- **NFR-P2**: the language conditional stays confined to `index/` (+ the new pure token module);
  `ledger/` and `verdict/` gain no language field.
- **NFR-M1**: every touched file stays ≤1200 lines (`ast_index.py` 471, `generator.py` 685 today).
- **PRD `:473`**: *"a named reason token — never a silent drop"* — the sentence this story makes true.

### Testing standards — the house form your new file must match

- `pytest`, one verification-area id per test in the **docstring first line**:
  `"""TC-ArgusAgent-INDEX-001-108 — <what it pins>."""` Measured maxima in use: `INDEX-001-107`,
  `INTAKE-003-09`, `DOCS-001-28`, `REPORT-002-24`.
- Pure functions over synthetic inputs for controls; `monkeypatch` for the import seam; `tmp_path`
  for fixtures. **Never** uninstall a grammar, **never** mutate a module-level registry without
  restoring it.
- Failure messages state **what broke and what to do** — every guard in `test_evidence_citation.py`,
  `test_spec_claim_scope.py` and `test_invocation_contract.py` does this; match it.
- `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` turns optional-grammar skips into hard failures
  (`test_multilanguage_audit.py:38-41`). **Run the suite with it set**, as CI does
  (`audit-ci.yml:75`).

### Previous story intelligence — 10.1, 10.2, 10.3 (all `done`, all PASS on review iteration 1)

- **10.1** — established the citation standard (run id **plus** the sha it covers, or **NOT
  ESTABLISHED**) in `architecture.md` §H + §Enforcement, enforced by `tests/test_evidence_citation.py`
  (`DOCS-001-20..-23`). **AC7.5 is this rule applied to you.** Its DN-7 (never manufacture a citation)
  and DN-8 (ledger corrections are append-only) both bind here.
- **10.2** — took grammar grounding 8/10 → 10/10 with the declarative entry-point map; bumped
  `AstIndex.schema_version` 1→2 and `CACHE_KEY_SCHEMA_VERSION` 2→3; filed `DF-10-2-A`. **It left
  `except (ImportError, Exception)` structurally intact for you, on purpose, and told you the class
  its map did not close (§A.1).** Its lesson — *the closure guard, not the site list, is
  load-bearing* — is DN-2.
- **10.3** — parser-derived equality guard; blessed `--ignore-pattern` behind the Live-Key Safeguard
  with a recorded, redacted `operator_suppressed_secret` finding. **Its central finding is your
  precedent**: `secret_scan.py` bound a reason to `_reason` and `continue`d, so *"the operator's
  INPUTS are persisted while the EFFECT leaves no trace"*. `except …: pass` is the same defect with
  the exception instead of the reason — and §A.3 shows a third instance still open.
- **Shared review posture across all three**: reviewers **re-derived every mechanical figure by
  execution** rather than reading it off the story. Expect that. Do not hand in a number you did not
  run.

### Runtime & toolchain, verified on this machine 2026-08-10

CPython **3.11.15** (Windows) vs CI's ubuntu × 3.10/3.11/3.12 · `tree-sitter` **0.25.2**
(`LANGUAGE_VERSION 15`, `MIN_COMPATIBLE 13`) · grammars installed and their measured versions:
python 0.25.0, javascript 0.25.0, go 0.25.0, typescript 0.23.2, rust 0.24.2, java 0.23.5, c 0.24.2,
cpp 0.23.4, ruby 0.23.1, php 0.24.1 — **the version spread is real**, which is 10.2's per-grammar
provenance and 11.4's version bound, not yours. `mypy` clean on 71 files; suite 1297 collected.

**No web research was required and none was used.** Every external fact this story depends on —
exception types, the ABI message, the entry-point exports, the version spread — was measured against
the **installed** toolchain on this host, which is stronger evidence than release notes for a story
about what the runtime actually does. The one string that could not be produced by execution
(`Incompatible Language version %u. Must be between %u and %u`) was extracted from the shipped
`_binding.cp311-win_amd64.pyd` and is recorded in §A.4 **as a string not to match on**.

### Project structure notes

New files land as `argus/shared/grammar_status.py` (pure, beside `source_languages.py`) and
`tests/test_grammar_diagnosis.py` (flat under `tests/`, the house layout). No new package, no new
dependency, no `__init__.py` export change beyond what `argus/shared/__init__.py` already does.

### Open questions for the operator — saved for the end, as the workflow requires

1. **`_GRAMMAR_PACKAGE_BY_LANGUAGE` (AC6.6)** — move into the shared module or leave in `generator.py`?
   Ruled **dev's call, with the decision recorded**; the duplication is real but the move is cosmetic
   and AC6 works either way.
2. **Cause 2's remedy wording** — it is an *Argus* defect, and the callout will say so to an operator.
   Ruled **say it plainly**: the tool telling the truth about its own gap is this epic's whole thesis
   (10.1 §Enforcement, `FR34`). If the wording needs softening for a public audience, that is 12.8's
   surface, not this one.
3. **The partial-failure blind spot (§A.2.2)** is filed for 12.5. If 12.5 slips, an operator auditing
   a mixed Python/Go repository still learns nothing about the failed Go grammar. **Flagged as the
   residual this story knowingly leaves open**, with an owner.

### References

- [epics.md#Story 10.4](../epics.md) — the three ACs this story implements (`:1898-1920`)
- [epics.md#Story 11.4](../epics.md) `:2081-2101` · [#Story 12.5](../epics.md) `:2314-2335` ·
  [#Story 12.8](../epics.md) `:2383-2405` — the three adjacent fences
- [deferred-work.md](../deferred-work.md) `:1529-1543` — `DF-AUD-APAA-F` (close append-only) ·
  `:1481-1508` — `DF-10-2-A` (different defect, do not conflate)
- [architecture.md](../architecture.md) `:694-699` §Error/Degradation · `:701-728` §Enforcement
- [E-PRD/prd.md](../E-PRD/prd.md) `:473` — *"a named reason token — never a silent drop"*
- [Story 10.2](10-2-multi-language-grounding-is-v1-in-the-specs.md) `:167-172`, `:297`, `:387` — the
  fence handed to this story and the third cause it names
- [Story 10.3](10-3-invocation-contract-says-what-the-cli-accepts.md) `:318-319` — the fence restated;
  §A.2 — the discarded-reason precedent
- `argus/index/ast_index.py:336-352`, `:420-439`, `:100-130` · `argus/reports/generator.py:283-346` ·
  `argus/detectors/vacuous_test.py:399-402` · `tests/test_ast_index.py:90-116` ·
  `tests/test_multilanguage_audit.py:293-330`

---

## Dev Agent Record

### Context Reference

- This story file (self-contained; §A–§E carry every measurement).

### Agent Model Used

`claude-opus-5[1m]` (BMAD `dev-story`, 2026-08-10).

---

## ✅ Operator decisions — 2026-08-10 — the HALT below is RESOLVED

**Recorded verbatim as operator decisions, not as dev judgement.** The HALT block that follows is
preserved **unedited** as the record of why the first round stopped; everything it says about the two
root causes still holds and was re-verified. What changed is that the operator (**XAgent007**) ruled on
it on **2026-08-10**, and this section records the ruling, the authority limits attached to it, and what
was actually done under it.

### DECISION 1 (operator) — take the prior round's recommended option 1

> Commit the 10.1–10.4 deltas so HEAD genuinely contains them, **then** regenerate the Epic-7 dogfood
> artifacts via their **own** renderers (`partition_plan.render_partition_plan_markdown`,
> `render_budget_plan_markdown`, `proof_render.render_proof_markdown` — do **not** hand-edit them),
> **then** re-run `test_dogfood_plan.py` + `test_dogfood_proof.py` until green.

**AC7.6's write set is widened by exactly those artifacts**, for the recorded reason that *their
provenance sha is now truthful rather than stale*. It is recorded **here**, in the Dev Agent Record,
rather than by editing AC7.6 itself: the workflow permits a dev to modify only the frontmatter,
Tasks/Subtasks checkboxes, Dev Agent Record, File List, Change Log and Status, and an acceptance
criterion edited by the person it constrains is not an acceptance criterion. The three added paths are:

| Added to the permitted write set | For | Renderer that produced it |
|---|---|---|
| `_bmad-output/…/minions-dogfood-partition-plan.md` | AC7.7 (whole-system green) | `render_partition_plan_markdown` |
| `_bmad-output/…/minions-dogfood-budget-plan.md` | AC7.7 | `render_budget_plan_markdown` |
| `_bmad-output/…/minions-dogfood-proof.md` | AC7.7 | `render_proof_markdown` |

⛔ `minions-dogfood-proof-story-7-2-superseded.md` is the **preserved historical record** (Story 8.5's
AC5) and was **not** touched. `_bmad-output/audit-reports/*` were **not** regenerated: no test guards
them, they are outside this story's fence, and regenerating them is scope this decision did not
authorise.

**Authority limits attached to the decision, and how each was honoured:**

| Limit | Honoured |
|---|---|
| **Git is authorised for this story: COMMIT ONLY** | ✅ six commits, all local |
| ⛔ **Do NOT push** | ✅ `git reflog` shows no push; no remote ref moved |
| ⛔ **Do NOT tag** | ✅ `git tag -l` still empty |
| ⛔ **Do NOT `workflow_dispatch`** | ✅ nothing dispatched. 10.1's **DN-7** still binds |
| **CI status stays NOT ESTABLISHED** | ✅ re-affirmed below and in Debug Log §11 |

### DECISION 2 (operator) — file the systemic sub-finding the prior round left open

The prior round observed, and deliberately did not file on its own authority, that *"these five guards
fire on **any** story that adds a module to `argus/`, and Epics 11–13 add several."* Filed as
**`DF-10-4-D`**, append-only, owner **Engineering Lead**, `target_story:
12-1-pipeline-stops-breaching-its-own-limit`, category `developer-experience`, severity 🟡.
⛔ **FILED ONLY** — the guard's coupling to `git ls-files`-including-the-index is **not** fixed here.
The entry also records that `DF-8-5-B` is the same class measured **one trigger short**, and that 12.1
(which already absorbs `DF-8-5-B`) carries a bootstrap ordering hazard: it is simultaneously the story
that owns the remedy and the story most certain to trip the defect before the remedy exists.

### DEV-6 — the branch-vs-`master` call, which the operator delegated to this dev under §7

**Ruled: commit on `master`.** The countervailing standard the operator named — *a provenance sha cited
by a committed artifact must stay valid* — is not hypothetical in this repository, and the deciding
input is a measurement, not a preference:

```
$ grep 'Commit descriptor' minions-dogfood-partition-plan.md      # the artifact as committed
- Commit descriptor (HEAD at generation): `7be90f7788c66d040a887b6b68f1358856961d4c`

$ git merge-base --is-ancestor 7be90f77 HEAD   →  NOT an ancestor of HEAD
$ git branch -a --contains 7be90f77            →  backup/pre-rebase-fix
                                                  release/epics-8-9
                                                  remotes/origin/release/epics-8-9
```

**The artifact I am replacing already cited a sha that is not in this branch's history.** It survives
only on a side branch and on one literally named `backup/pre-rebase-fix` — i.e. the exact failure this
decision exists to prevent has already happened once here, by rebase. Ordinary hygiene (*branch before
committing on the default branch*) is a real standard and I am not dismissing it; it is **outbid by an
explicit project constraint**, which is the conflict-resolution rule §7 states. Reinforcing inputs:

1. I am **forbidden to push**, so a branch would be purely local — it buys none of branching's actual
   benefit (review, CI, isolation) while carrying all of its rewrite risk.
2. The repo's own flow merges PRs; a platform default of *Squash and merge* would collapse four commits
   into one new sha and orphan the cited one. On `master` there is no rewrite step between generation
   and forever.
3. The BMAD loop's review gate (`bmad-code-review`) runs on the story, not on a PR, so branching would
   not add the review that branching is normally for.

**Recorded tradeoff:** committing to the default branch bypasses pre-merge review. Mitigations actually
in place: six small, individually-messaged commits; nothing pushed, so nothing is published and any of
this is still revertible; and the story goes to `review` with the whole delta on disk for the gate.

### What was done, in order

1. `DF-10-4-D` appended to `deferred-work.md` (**Decision 2**), verified append-only
   (`after.startswith(before)`, `+585 / -0`).
2. Six commits on `master`, in dependency order, each with a body in the repo's existing style and the
   required `Co-Authored-By` trailer:

   | sha | Subject | Carries |
   |---|---|---|
   | `e59c2e1` | `docs(planning): replan Epics 11-13 from the 2026-08-10 repository audit` | the two sprint-change proposals + the readiness report — the change signal 10.1–10.4 cite, which was sitting **untracked** (AI-E8-1 in documentary form) |
   | `ce2cc7e` | `docs(planning): release status must cite the run AND the sha it covers` | Story 10.1 |
   | `ae5c6a3` | `fix(index,cache): ground ten grammars per grammar, and say V1 in the specs` | Story 10.2 |
   | `58821c3` | `fix(cli,detectors): the invocation contract says what the CLI accepts` | Story 10.3 |
   | **`a9cc933`** | `fix(index,reports): a grammar that fails to load names why` | **Story 10.4 — the provenance sha the three artifacts now cite** |
   | *(final)* | `chore(dogfood): regenerate the plan and proof artifacts at a truthful sha` | the three regenerated artifacts + this story file + `sprint-status.yaml` |

   **Attribution honesty.** Four stories were implemented against **one uncommitted working tree**, so
   eight documents (`architecture.md`, `deferred-work.md`, `prd.md`, `README.md`, `CHANGELOG.md`,
   `epics.md`, `ast_index.py`, `test_release_surface_honesty.py`) carry hunks from more than one story
   and cannot be split without inventing hunks nobody authored. Rule applied and stated in the messages:
   **a co-edited file is carried by the LAST story that touched it.** The consequence is stated rather
   than hidden — the four story commits are individually attributable but **only the set is complete**;
   an intermediate commit is not expected to pass its own suite.
   **Deliberately NOT committed** (outside the authorised set, and not a story delta):
   `_bmad/**/config.yaml`, `_bmad/config.user.toml`, `E-PRD/.memlog.md` and `E-PRD/addendum.md` — all
   six are the workspace's `Varin → XAgent007` operator rename, tooling state, not Epic 10 work. The
   orchestrator-owned `bmad-dev-loop-pack/`, `.bmad-drift-audit/` and `_bmad-output/audit-reports/*`
   were not added, moved or deleted, per the frontmatter.
3. **Regenerated the three artifacts at `a9cc933`**, by calling the renderers and writing their return
   value verbatim — never by editing a file to match. Verified three ways (**AI-E3-1**):
   - the script printed a unified diff of *committed vs live render* **before** writing, and every
     changed line is a **derived figure** (population, LOC, `$X`, `partition_id`, bundle hash), never an
     assertion or a narration;
   - after writing, each file was re-read and asserted **equal to the renderer's string**;
   - `plan.commit_descriptor == proof.commit_descriptor == git rev-parse HEAD == a9cc933`, asserted in
     the script — so the sha each artifact cites is a sha that **contains the deltas it describes**.
   **No test was edited to match output.** `git diff HEAD -- tests/` after the regeneration is empty,
   and the suite grew by zero cases (1324 before the fix round, 1324 after).
4. Gates re-run; suite **1324/1324**; verdict re-measured (Debug Log §10).

### CI evidence — still **NOT ESTABLISHED** (AC7.5, 10.1's DN-7)

Committing is **not** evidence. HEAD is now a sha no CI run has ever seen, and run `31341363300` remains
scoped to `00c8d1b`. Every figure in this story is **LOCAL** (Windows / CPython 3.11.15; CI is
ubuntu × 3.10/3.11/3.12 — and the six commits behind `00c8d1b` were **all** host-portability defects
invisible on this host). **The command a human runs:** push this branch and cite the `audit-ci.yml` run
**with the sha it covers**. Committing has made that command *possible*, which it was not before; it has
not made its answer known.

---

## ⛔ HALT — PRESERVED UNEDITED as the record of round 1 (RESOLVED above on 2026-08-10)

**Status was `in-progress`, NOT `review`.** All seven ACs are satisfied and **1319 of 1324 tests pass**.
Five tests are RED. They are **not** defects in this story's code — every one of them says *"a committed
AUTO-GENERATED dogfood artifact no longer matches what the generator now derives"*, and the two facts
that made them stale are both **mandated by this story**. I did not fix them because the remedy is to
rewrite files AC7.6 fences byte-unchanged by name, and doing so *at this moment* would stamp a **false
provenance sha** on evidence artifacts — the exact defect class this epic exists to close.

**The five red tests, and the artifact each one guards:**

| Test | Guards |
|---|---|
| `test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation` | `minions-dogfood-partition-plan.md` |
| `test_dogfood_plan.py::test_plan_artifacts_name_the_tree_they_actually_planned` | same, its Provenance block |
| `test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork` | `minions-dogfood-budget-plan.md` |
| `test_dogfood_proof.py::test_artifact_states_the_ceiling_honesty_pair` | `minions-dogfood-proof.md` |
| `test_dogfood_proof.py::test_red_first_vacuously_satisfied_critical_gate_is_named` | same |

### Root cause 1 — this story's added LOC tips an NFR-SC1 bin-packing boundary

The partition artifact records three `partition_id`s, each a **sha256 over its unit's sorted member
paths** (`index/partitioner.py:395-401`), and the test re-derives the plan from the working tree so
that *"the artifact cannot silently rot away from the generator"*. This story adds ~700 physical lines
to two tracked files (most of it the explanatory comment this codebase's house style requires), pushing
the largest unit past the soft target of ≤40 files / ≤15000 LOC:

| | committed artifact | live |
|---|---|---|
| unit A | 10 files / 2993 LOC | **12 files / 3660 LOC** |
| unit B | 21 files / 1325 LOC | 21 files / 1330 LOC *(id unchanged)* |
| unit C | **40** files / 14100 LOC | **39** files / **14793** LOC |

Unit C's 40th file no longer fits under 15000, so it moves, so the member-path sets change, so the ids
change (`085854c90586` → `ed6d08f25ce3`, `bde14bbf3bcf` → `82a3d605e61e`).

**Proved to be this delta and only this delta.** I reconstructed the tree *as this story found it* (my
five edits to `ast_index.py`/`generator.py` reverse-applied) and re-derived: it reproduced
`085854c90586 · 477ef77d7b65 · bde14bbf3bcf` — the committed ids, exactly. I then restored both files
and verified the round-trip by sha256 (`a248633692113c2e…` / `f881dd56332951f8…`), so the tree is
byte-identical to the state I measured in.

### Root cause 2 — the MANDATED `git add` moves the audited population 71 → 72

`enumerate_minions_source_files` reads **`git ls-files`**, which includes the **index**, not just
`HEAD`. E.5 / AC7.6 and AI-E8-1 require me to `git add` the new module ("`git diff` cannot see an
untracked path" — Epic 8 shipped with its own story file untracked for exactly this reason). Staging
`argus/shared/grammar_status.py` therefore makes it *tracked*, and the planned/audited population moves
from **71 to 72** source files. That in turn moves the total LOC, the budget `$X` (`450`/`843` in the
committed artifacts), and the critical-set size (`51`) — which is what the other four tests assert.

**This is verifiable at a glance:** before the `git add` the suite had **one** failure (root cause 1
alone); after it, five. **Both halves are required by the story**, so neither is something I can undo:
un-staging the module would re-open AI-E8-1, and shrinking the comments to hold a sha256 stable is
tail-wagging-dog.

### Why I did not regenerate the four artifacts

Two independent reasons, either sufficient:

1. **AC7.6 fences them by name.** Its byte-unchanged list ends *"every Epic 1–9 artifact and
   retrospective"*; all four are Story-7.1/7.2 generator artifacts. AC7.6's own instruction for this
   exact situation is *"a diff outside the table means scope has leaked — **stop and record why rather
   than widening**"*. Stopping and recording is the specified behaviour, not a judgement call I made
   against the story.
2. **Regenerating NOW would manufacture a false citation.** Each artifact's Provenance block records
   *"Commit descriptor (HEAD at generation)"*, and `_resolve_commit_descriptor` is a bare
   `git rev-parse HEAD` with **no dirty marker** (`partition_plan.py:438-450`). HEAD is `00c8d1b`,
   which contains **none** of 10.1's, 10.2's, 10.3's or 10.4's deltas. A regenerated artifact would
   assert it was derived at a sha whose content is not what was planned — a provenance claim citing a
   state it did not cover, which is Story 10.1's founding defect and its DN-7 ("triggering a run to
   manufacture a citation is manufacturing evidence") pointed at an artifact instead of a status line.
   **The regeneration is correct and necessary; it is only correct AFTER these four stories' deltas are
   committed.**

### Options for the orchestrator / Engineering Lead (I hold none of these open in code)

1. **Commit 10.1–10.4's deltas first, then regenerate, then re-run.** The renderers are the artifacts'
   own: `argus/dogfood/partition_plan.py::render_partition_plan_markdown` and
   `::render_budget_plan_markdown`, and `argus/dogfood/proof_render.py::render_proof_markdown`. Run
   them at a HEAD that actually contains the deltas, then `pytest tests/test_dogfood_plan.py
   tests/test_dogfood_proof.py`. This is the technically correct sequence and it makes each artifact's
   provenance true. **Recommended.**
2. **Widen this story's write set by four files** — add the four `minions-dogfood-*.md` artifacts to
   AC7.6's permitted table with a recorded reason, and accept that their Provenance sha is stale until
   the commit lands. Cheap, but knowingly writes a wrong sha into evidence artifacts.
3. **File it forward and accept five red tests** — e.g. `DF-10-4-D`, owner Engineering Lead. ⛔
   Recommend against: a red suite is precisely the false-green ground this epic is clearing, and the
   artifacts are *genuinely* stale rather than spuriously so.
4. **Un-stage the new module / shrink the added LOC** — ⛔ Recommend against both. The first re-opens
   AI-E8-1; the second shapes source layout to hold a sha256 stable, and the very next story that adds
   a module to `argus/` tips it again anyway. **The real finding here is that these five guards fire on
   *any* story that adds a module to `argus/`, and no story before this one had to.** That may itself
   deserve a ledger entry, which I have deliberately not filed on my own authority.

**A related pre-existing divergence, reported and NOT adopted (AC4.4).** The story records a dogfood
baseline of `deep_ratio=60/161`, assessed `15/19`. Measured on this tree today: `argus audit .` →
`verdict=RELEASE_READY deep_ratio=31/82 blocking_findings=0 assessed_deep_ratio=31/39
scope=application held_out=86`, exit `0`. I ran the **same** command against the reconstructed
pre-story tree and got **the identical line**, so **this story does not move the dogfood verdict** —
what AC4.4 actually asks is satisfied. The divergence from the *recorded figures* predates this story
(the tree already carries 10.1–10.3's uncommitted deltas, and `git ls-files` counts 161 source files
against the run's 82). Per AC4.4 this is a **stop-and-report, not a figure to update**: I have changed
no baseline number anywhere.

---

### Debug Log References

**§1 — RED evidence, the §A.1 five-mode probe, run against the tree AS FOUND** (`.go` fixture,
patching only `ast_index.importlib.import_module`; cause 4 via `sys.modules["tree_sitter"]`, because
the *pre-change* loader reached the core with a `from tree_sitter import …` statement that bypasses
`importlib`):

```
0 baseline (grammar installed)                 ast_eligible=True  parse_failed=False reason=None defs=1 edges=0 grammar_versions=['go']
1 ModuleNotFoundError (package not installed)  ast_eligible=False parse_failed=False reason='grammar_missing_go' defs=0 edges=0 grammar_versions=[]
2 entry point absent (getattr -> None)         ast_eligible=False parse_failed=False reason='grammar_missing_go' defs=0 edges=0 grammar_versions=[]
3a entry point raises OSError                  ast_eligible=False parse_failed=False reason='grammar_missing_go' defs=0 edges=0 grammar_versions=[]
3b Language(42) rejects capsule                ast_eligible=False parse_failed=False reason='grammar_missing_go' defs=0 edges=0 grammar_versions=[]
4 tree_sitter core broken (no Language/Parser) ast_eligible=False parse_failed=False reason='grammar_missing_go' defs=0 edges=0 grammar_versions=[]
```

**All four causes emitted `grammar_missing_go`, exactly as §A.1 measured.** Re-derived, not transcribed.

**§2 — the §A.4 exception types, re-measured on this host** (`tree-sitter 0.25.2`, CPython 3.11.15):

```
importlib.import_module('tree_sitter_nosuchlang') -> ModuleNotFoundError: No module named 'tree_sitter_nosuchlang'
Language(42)                                      -> ValueError: invalid language ID
Language(object())                                -> TypeError: an integer is required
Language(None)                                    -> TypeError: an integer is required
KeyboardInterrupt inside the entry point          -> PROPAGATES (correct)
```

Confirms DN-4: one cause, three exception types → classify by **arm position**. `KeyboardInterrupt`
propagating is now a guard (`-113`), not a hope.

**§3 — RED run of `tests/test_grammar_diagnosis.py` against the unamended `argus/`.** `sha256sum -c`
first: `argus/index/ast_index.py: OK`, `argus/reports/generator.py: OK` — i.e. the RED was captured
with both production files byte-identical to the tree as found. **15 of 27 tests failed**, including
every load-bearing one:

```
AssertionError: simulated mode 'entry_point_missing'    recorded parse_failure_reason='grammar_missing_go', expected 'grammar_entrypoint_missing_go'
AssertionError: simulated mode 'load_failed_entry_raises' recorded parse_failure_reason='grammar_missing_go', expected 'grammar_load_failed_go'
AssertionError: simulated mode 'load_failed_bad_capsule'  recorded parse_failure_reason='grammar_missing_go', expected 'grammar_load_failed_go'
AssertionError: simulated mode 'core_runtime_missing'     recorded parse_failure_reason=None,                expected 'tree_sitter_runtime_missing'
FAILED …::test_loader_has_no_unnamed_swallowed_or_redundant_arm
FAILED …::test_registry_and_behavioural_matrix_close_over_each_other
FAILED …::test_this_guard_cannot_pass_vacuously
FAILED …::test_degradation_rule_and_guard_are_registered_in_architecture
FAILED …::test_no_exception_detail_or_host_path_is_persisted
FAILED …::test_verdict_and_coverage_are_identical_across_all_four_causes
```

*(`core_runtime_missing` reads `None` rather than `grammar_missing_go` here purely because the guard
drives the `importlib` seam and the pre-change core import did not use it — §1 shows the same cause
producing `grammar_missing_go` when driven at the seam it did use. Both are RED; the guard's seam is
the one that survives, see DEV-1.)*

**§4 — RED evidence for AC6, the report.** With the tokens defined and `generator.py` untouched:

```
AssertionError: cause 2 produced NO callout. `grammar_entrypoint_missing_php` does not start with
`grammar_missing_`, so a prefix-arithmetic reader skips it silently — the exact regression AC6 exists to prevent.
```

and the mixed case rendered by the **pre-change** code, which is the harm in one line — four failed
files, only two counted, two classes silently dropped:

```
> **No file could be parsed …** Argus enumerated 4 file(s) (2 go) but has no installed grammar for them …
  Install: `pip install tree-sitter-go` and re-run.
```

**§5 — §A.2's coverage measurement, reproduced.** `pytest --cov=argus.reports.generator` over the seven
test files that import the generator:
`argus\reports\generator.py 254 40 84% Missing: 94, 278, 316, 322-336, 361-391, …` — **`322-336` and
`316` confirmed never executed**, exactly as measured at story-design time. After this story the same
seven files reach 89%, and the whole-suite figure for that module is higher again.

**§6 — write-set fence.** My delta was isolated by **mtime partition** against the session start (the
tree already carried 10.1/10.2/10.3's uncommitted work, so `git diff HEAD` cannot isolate it — the
frontmatter warns about exactly this). Files touched by me, and only these:

```
21:36 argus/reports/generator.py            21:34 argus/index/ast_index.py
21:32 tests/test_grammar_diagnosis.py       21:27 argus/shared/grammar_status.py
      _bmad-output/…/architecture.md              _bmad-output/…/deferred-work.md
      this story file                             _bmad-output/…/sprint-status.yaml
```

Everything else in `git status --porcelain` has an mtime **older than this session** — including every
fenced path. `git diff --quiet HEAD` additionally confirms `argus/pipeline.py` (the NFR-M1 fence),
`argus/models.py`, `pyproject.toml`, `action.yml` and `.github/workflows/audit-ci.yml` are byte-identical
to HEAD. `argus/cli.py`, `argus/cache/key.py`, `README.md`, `CHANGELOG.md`, `epics.md` and `E-PRD/**`
differ from HEAD but **not from me** — those are 10.1/10.2/10.3's deltas, confirmed by mtime.

**§7 — the dogfood divergence, and the proof it is not mine.** See the HALT block above. Both runs —
post-change and reconstructed-pre-change — produced the byte-identical line
`verdict=RELEASE_READY deep_ratio=31/82 blocking_findings=0 assessed_deep_ratio=31/39 scope=application held_out=86`.

**§8 — gates, all LOCAL (this host is Windows / CPython 3.11.15; CI is ubuntu × 3.10/3.11/3.12).**

| Gate | Baseline | After | |
|---|---|---|---|
| `mypy argus` | clean, **71** files | clean, **72** files | ✅ the one new module, AC3.5 |
| `bandit -r argus --severity-level medium` | 0 High / 0 Med | **0 High / 0 Med** (19 Low) | ✅ |
| `pytest tests/` (`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`) | 1297 collected | **1324 collected, 1319 pass, 5 FAIL** | ⛔ the HALT |
| coverage | 95.16% | **95.51%** (`--cov-fail-under=80` met) | ✅ |
| `argus audit .` | see §7 | unchanged by this delta | ✅ |

**No test was removed, skipped, weakened or `xfail`ed.** The count grew by exactly my 27 new cases.

**§9 — CI evidence status: NOT ESTABLISHED** (10.1's AC6 / architecture §H, enforced by
`tests/test_evidence_citation.py`). Every figure above is **LOCAL**. Run `31341363300` is sha-scoped to
`00c8d1b` and cannot evidence a tree carrying 10.1's, 10.2's, 10.3's and this story's deltas; no CI run
covers this tree because it is uncommitted. ⛔ I did not push, tag or `workflow_dispatch` anything
(10.1's DN-7). **The command a human runs:** commit these deltas, push the branch, and cite the
`audit-ci.yml` run **with the sha it covers**.

---

**§10 — FIX ROUND, 2026-08-10. Gates re-run after the commits + the regeneration.** All LOCAL.

| Gate | Round 1 | Fix round | |
|---|---|---|---|
| `pytest tests/` (`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`) | 1324 collected, **1319 pass / 5 FAIL** | **1324 collected · 1324 pass · 0 fail · 0 error · 0 skip**, exit `0` | ✅ |
| `pytest tests/test_dogfood_plan.py tests/test_dogfood_proof.py tests/test_dogfood_module_split.py` | 5 FAIL | **48 passed** | ✅ |
| `mypy argus` | clean, 72 files | **clean, 72 files** | ✅ unchanged |
| `bandit -r argus --severity-level medium` | 0 High / 0 Med (19 Low) | **0 High / 0 Med (19 Low)** | ✅ unchanged |
| `pytest --cov=argus --cov-fail-under=80` | 95.51% | **95.51%**, gate met | ✅ unchanged |

The whole-suite count was taken from `--junit-xml` rather than read off the terminal: this Windows shell
truncates pytest's final summary line, a host quirk 10.3's review already measured and recorded. The XML
attributes are `tests=1324 failures=0 errors=0 skipped=0`. **The suite did not grow in the fix round** —
1324 before and after — which is the mechanical statement that no test was added, and `git diff HEAD --
tests/` after the regeneration is **empty**, which is the mechanical statement that none was edited,
weakened, skipped or deleted (**AI-E3-1**).

**§10b — the dogfood verdict, re-measured after the commits, and the round-1 divergence RESOLVED.**

```
$ argus audit .
verdict=RELEASE_READY deep_ratio=61/163 blocking_findings=0 assessed_deep_ratio=61/77 scope=application held_out=86   exit 0
```

Round 1 reported this as an unexplained pre-existing divergence: the story's recorded baseline is
`deep_ratio=60/161`, assessed `15/19`, but the dirty tree measured `31/82` / `31/39`. **Committing
explains it, and the arithmetic closes exactly.** `15/19` is the *reduced* form of `60/76`, so the
recorded baseline is `60` deep of `76` assessed of `161` enumerated, i.e. `161 − 76 = 85` held out.
Today: `61` of `77` of `163`, i.e. `163 − 77 = 86` held out. The deltas are **+1 assessed-and-deep** and
**+1 held-out**, which are precisely this story's two new files — `argus/shared/grammar_status.py`
(a source module: assessed, and audited deep) and `tests/test_grammar_diagnosis.py` (a test file: held
out). Nothing else moved. So the round-1 `31/82` was an artefact of auditing a *drifted, half-untracked*
tree, not a real divergence, and the recorded `60/161` baseline **does** reproduce once the tree is
committed — off by exactly the two files this story adds.

**AC4.4 is satisfied in the form it asks for**: the *verdict* is byte-identical — `RELEASE_READY`, exit
`0`, `blocking_findings=0`, `scope=application`. ⛔ **I changed no baseline figure anywhere in any
document**; the ratio movement is reported here, per AC4.4's "stop-and-report, not a figure to update".

**§11 — the write set, re-fenced after the fix round.** `git diff --quiet HEAD` confirms byte-unchanged:
`argus/pipeline.py` (the NFR-M1 1331/1200 fence), `argus/models.py`, `argus/cache/key.py`, `argus/cli.py`,
`pyproject.toml`, `epics.md`, `E-PRD/**`, `README.md`, `CHANGELOG.md`, `action.yml`,
`.github/workflows/audit-ci.yml`, `tests/**`. The only paths written in the fix round are
`deferred-work.md` (append-only, `+585/−0`), the three regenerated `minions-dogfood-*.md` artifacts,
this story file and `sprint-status.yaml`. `git tag -l` is **empty**; the reflog shows no push and no
dispatch. One item of debris removed: `probe_tmp/main.go`, an untracked `.go` fixture left behind by
round 1's failure-mode probes — untracked, referenced by nothing (`grep -rn probe_tmp` returns zero
hits outside `.venv`), and outside every enumeration (`git ls-files argus`), so its removal moves no
figure.

### Completion Notes List

**What was built.** Four measurably different grammar-load failures now record four different reason
tokens, and the one operator-facing surface that shows them prints a different remedy for each. The
token vocabulary lives in one new pure module both sides import; the loader is four named arms instead
of one blanket catch; and an `ast`-closure guard over the loader's own control flow means a fifth arm
cannot be added without registering and driving it.

**Decisions I took, with the reasoning (none of DN-1..DN-9 was re-litigated):**

- **DEV-1 — the `tree_sitter` core is resolved through `importlib.import_module("tree_sitter")`, not a
  `from tree_sitter import Language, Parser` statement.** AC5.1 requires every cause to be simulated at
  *"the `importlib.import_module` seam inside `ast_index`"*, and a `from …` statement bypasses that seam
  entirely (it goes through `__import__`/`sys.modules`), so cause 4 could only have been driven by
  mutating `sys.modules` — a process-global the story's own testing standards warn against. Routing the
  core import through `importlib` puts **all four causes on one seam a test can drive**, which is the
  whole reason the arm is testable. Cost: the arm catches `(ImportError, AttributeError)` rather than
  `ImportError` alone, because `core.Language` raises `AttributeError` where `from … import Language`
  would have raised `ImportError`. That pair is **not** redundant — neither subclasses the other, which
  `-115` asserts structurally rather than by blocklist — and both mean the same thing here: the core is
  not usable. *Testability drove a design choice; the choice is also the more honest one, since it
  distinguishes "core absent" from "core present but not the 0.25-era API".*
- **DEV-2 — `_GRAMMAR_PACKAGE_BY_LANGUAGE` MOVED into `argus/shared/grammar_status.py`** (AC6.6 left
  this to the dev, requiring only that the decision be recorded). Moved, because after this story the
  table is no longer report-private: the remedy line for cause 3 names the same package the classifier
  identifies, so leaving it in `generator.py` would have recreated the two-copies shape
  `argus/shared/source_languages.py` exists to prevent — and this project has already paid for that
  mapping living in four places. It is a **move, not an edit**: the same ten languages, the same ten
  package names, now pinned equal to `LANGUAGE_BY_SUFFIX`'s value set by `REPORT-002-25`, so an
  eleventh language cannot be added to one and not the other. `-25` also asserts `generator.py` no
  longer carries a private copy.
- **DEV-3 — the pure module holds the FACTS, the report holds the PROSE.** `grammar_status.py` answers
  *which class / which language / which package*; the operator wording lives in
  `generator.py::_render_grammar_remedy`. Putting the sentences in the shared module would have pulled
  operator-facing message text — Story 12.8's surface by name — into a contract module, and would have
  coupled the CLI's future wording to the report's. Separation of concerns in the direction the fences
  already point.
- **DEV-4 — `_get_parser_for_lang` returns a `_ParserLoad(parser, failure)` NamedTuple rather than
  `object | None`.** This is what makes AC5.2's closure *exact*: every exit is a two-argument
  `_ParserLoad(...)` whose failure slot is either `None` (the single success) or a registered
  `GrammarFailure` member, so the guard can walk the function's AST and prove the arms are exhaustive
  and registered. Returning a bare `None` for four different reasons is the defect in miniature.
- **DEV-5 — cause 2's callout says plainly that it is an Argus defect** (the story's open question 2,
  ruled "say it plainly"). Implemented as written: *"the package IS installed, so there is nothing for
  you to install — this is an **Argus** defect. Please report it with the installed version of
  `tree-sitter-php`."*

**Where a principle met a project standard, the standard won.** Two places, both recorded:

1. The guard `-115`/`-118` reads `argus/index/ast_index.py`'s **source text** and walks its AST. That is
   ordinarily a smell (a test coupled to implementation shape). This project's DN-2 makes it the
   *load-bearing* assertion, because Story 10.2's hand-written list was wrong three times and a closure
   over the code is the only thing that closes the class. Mitigated as the standard requires: the walk
   **fails loudly** if the function moves or is renamed, and `-118` pins every count it depends on.
2. The blanket `except Exception` in arm 3 survives, deliberately. AR10 would normally push toward
   narrow types; §A.4's measurement shows the type genuinely varies and a future tree-sitter release may
   invent another. The house form (`# noqa: BLE001` + a comment naming the degraded outcome + a recorded
   return) is what makes it legitimate, and it now matches `_index_source_file`, `secret_scan.py:428`
   and `tool_runner.py`.

**Things I deliberately did NOT do:** `DetectorResult.degraded`'s missing reader (§A.3 — filed as
`DF-10-4-B`, not fixed); the partial-failure trigger (`DF-10-4-A`, 12.5's); exception detail on the
entry (`DF-10-4-C`, 12.8's); any version comparison, verdict change or typed finding (DN-9, 11.4's
fence); `pipeline.py` (byte-unchanged, verified). No new dependency: the guard is stdlib `ast` +
`builtins` + `pathlib`, and the new module imports only `__future__`, `enum` and `typing`.

**AC status (round 1):** AC1 ✅ · AC2 ✅ · AC3 ✅ · AC4 ✅ · AC5 ✅ · AC6 ✅ · AC7 — 7.1 ✅ 7.2 ✅ 7.3 ✅
7.4 ⛔ *(five red tests)* 7.5 ✅ *(NOT ESTABLISHED, recorded)* 7.6 ✅ 7.7 ⛔ *(same five)*.

---

### Fix round — 2026-08-10 — what changed, and the one decision that was mine

The grammar-diagnosis work above is untouched: **no `argus/**` source file, and no test, was edited in
the fix round.** The blocker was never in this story's code; it was that three committed
AUTO-GENERATED evidence artifacts had gone stale against a generator that re-derives them from the live
tree, and that regenerating them *before* the deltas were committed would have written a sha into an
evidence document that does not contain what the document describes. The operator ruled; §Operator
decisions above records the ruling and its authority limits.

- **DEV-6 — `master`, not a branch** (the one call delegated to me). Decided on a measurement, not a
  preference: the artifact I was replacing **already cited `7be90f77`, a sha that is not an ancestor of
  this history** — it survives only on `release/epics-8-9` and on a branch named `backup/pre-rebase-fix`.
  The failure mode the operator asked me to prevent has already occurred once in this repository, by
  rebase. Normal hygiene says branch first; the explicit project constraint (*a cited provenance sha
  must stay valid*) outbids it, which is precisely §7's conflict rule, and I am recording the tradeoff
  rather than pretending there is none: committing to the default branch skips pre-merge review, and the
  mitigations are that nothing was pushed, the commits are small and individually messaged, and the
  whole delta still faces this story's review gate.
- **DEV-7 — the artifacts were regenerated, never reconciled.** Each file on disk was asserted equal to
  its renderer's return value after writing, and the pre-write diff was printed and inspected: every
  changed line is a **derived figure**, not a claim, a narration or an assertion. `git diff HEAD --
  tests/` is empty and the suite count is unchanged at 1324, so no test was bent to fit output
  (**AI-E3-1**, which is why the check is mechanical rather than a promise).
- **DEV-8 — the write-set widening is recorded in the Dev Agent Record, not by editing AC7.6.** The
  operator authorised widening the fence by exactly the three artifacts; the dev-story workflow does not
  let a dev edit the Acceptance Criteria, and an AC amended by the party it constrains is not a
  constraint. Recorded, with its reason, where a reviewer will read it.
- **DEV-9 — `DF-10-4-D` records a mechanism strictly stronger than `DF-8-5-B`'s, and says so.**
  `DF-8-5-B` measured the trigger as *"any commit that changes `argus/**` composition"*. The measured
  trigger is *"any story that **stages** an `argus/**` source file"*, because
  `enumerate_minions_source_files` reads `git ls-files`, which reports the **index**. That fires
  mid-implementation, at the exact moment `AI-E8-1` requires the `git add` — so the two requirements
  are in direct mechanical conflict, and no story can satisfy one without tripping the other. Filed to
  12.1 (which already absorbs `DF-8-5-B`), **not fixed here**: the coupling lives in `argus/dogfood/`,
  outside this story's fence, and changing what the dogfood enumerates is verdict-adjacent, which DN-9
  fences to Epic 11/12.
- **Things the fix round deliberately did NOT do:** touch `minions-dogfood-proof-story-7-2-superseded.md`
  (Story 8.5's preserved historical record); regenerate `_bmad-output/audit-reports/*` (no test guards
  them, and it is scope the decision did not authorise); push, tag or dispatch anything (10.1's DN-7 —
  CI stays **NOT ESTABLISHED**); fix `DF-10-4-D`; commit the `_bmad/**` and `E-PRD` operator-rename
  churn, which is tooling state and not Epic 10 work.

**AC status (final):** AC1 ✅ · AC2 ✅ · AC3 ✅ · AC4 ✅ *(4.4 satisfied as verdict invariance; the ratio
movement is reported in Debug Log §10b and reconciles to exactly this story's two new files — no
recorded figure was edited)* · AC5 ✅ · AC6 ✅ · AC7 — 7.1 ✅ 7.2 ✅ 7.3 ✅ **7.4 ✅** 7.5 ✅ *(NOT
ESTABLISHED, recorded and re-affirmed)* **7.6 ✅** *(as widened by operator decision, recorded above)*
**7.7 ✅** *(full suite 1324/1324; dogfood verdict unchanged)*.

### File List

**Modified**
- `argus/index/ast_index.py` — the four-arm loader, `_ParserLoad`, the caller emits the arm's token
- `argus/reports/generator.py` — `_render_grammar_remedy` (new), `_render_readability_warning` routed
  through the shared classifier, `_GRAMMAR_PACKAGE_BY_LANGUAGE` removed (moved)
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §Error/Degradation rule + §Enforcement
  registration ONLY (AC5.7)
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **append-only**, `+585 / -0`
  (`+540` round 1; `+45` in the fix round for `DF-10-4-D`)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — this story's status value + annotation
- `_bmad-output/design-artifacts/ArgusAgent/stories/10-4-a-grammar-that-fails-to-load-names-why.md`

**Added** *(both `git add`ed — AI-E8-1: `git diff` cannot see an untracked path)*
- `argus/shared/grammar_status.py` — the pure token contract (AC3)
- `tests/test_grammar_diagnosis.py` — the guard, 27 tests (AC5, AC6)

**Regenerated in the fix round** *(write set widened by operator decision 2026-08-10 — see §Operator
decisions; every one is renderer output, verified equal to the renderer's return value after writing,
never hand-edited)*
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` —
  `partition_plan.render_partition_plan_markdown`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` —
  `partition_plan.render_budget_plan_markdown`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` —
  `proof_render.render_proof_markdown`

**Removed** — `probe_tmp/main.go`, untracked debris from round 1's failure-mode probes (referenced by
nothing; outside every enumeration).

**Deliberately NOT modified** — `argus/pipeline.py` · `argus/models.py` · `argus/cache/key.py` ·
`argus/cli.py` · `pyproject.toml` · `epics.md` · `E-PRD/**` · `README.md` · `CHANGELOG.md` ·
`action.yml` · `audit-ci.yml` · `tests/**` *(no test file was touched in either round beyond adding
`tests/test_grammar_diagnosis.py`)* · `minions-dogfood-proof-story-7-2-superseded.md` *(Story 8.5's
preserved historical record)* · `_bmad-output/audit-reports/**` · `_bmad/**` · `bmad-dev-loop-pack/` ·
`.bmad-drift-audit/`.

### Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-10 | 0.1 | **Story contexted.** Four measurements changed it: (1) the ledger's **two** causes are **four**, and all four emit `grammar_missing_<lang>` today — the entry-point fall-through 10.2 named and a core-runtime arm nobody had; (2) the **only** operator-facing consumer (`generator.py:322-336`) is **never executed by any test**, so a token rename would silently disable it, and it fires only when **zero** files parsed — invisible in the polyglot repo this story's persona owns; (3) `DetectorResult.degraded` has **zero production readers**, filed for 10.5's reverse sweep; (4) the blanket catch is at **`:350`**, not the `:266` the ledger cites nor the `:294` 10.2 recorded. 7 ACs; AC5 (an `ast`-closure guard over the loader's own arms) is load-bearing; DN-1..DN-9 locked, incl. **no new field / no schema bump** (DN-5) and **no verdict change** (DN-9, fence to 11.4). Baseline re-verified, not trusted: **1297 collected** under `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, mypy clean on **71** files. Status → `ready-for-dev`. | Scrum Master (`bmad-create-story`, `claude-opus-5[1m]`) |
| 2026-08-10 | 0.2 | **Implemented — T1..T8 complete, T9 blocked; status `ready-for-dev` → `in-progress`, NOT `review`.** Every §A measurement re-derived by execution before any edit, and all of them held: the anchor at **`:350`** (the ledger's `:266` and 10.2's `:294` both stale), all four causes emitting `grammar_missing_go`, `generator.py:322-336` never executed, `KeyboardInterrupt` propagating, baseline **1297 / 71 files**. RED captured first with `ast_index.py` and `generator.py` sha256-verified byte-identical (15 of 27 new tests failed, incl. the callout going **silent** on cause 2). Delivered: `argus/shared/grammar_status.py` (pure token contract, four tokens, one classifier — mypy 71→**72** as AC3.5 predicted); a four-arm `_get_parser_for_lang` returning `_ParserLoad(parser, failure)` so the emitted token is the arm's; `_render_readability_warning` routed through the shared classifier with a **per-class** remedy and the all-or-nothing trigger pinned unchanged; `tests/test_grammar_diagnosis.py` (27 tests) whose load-bearing half is an **`ast` closure over the loader's own control flow** — no bare/lone-`pass`/redundant-tuple/signal-catching handler, and every exit must return a **registered** `GrammarFailure`. `DF-AUD-APAA-F` closed **append-only (`+540/-0`)** correcting its enumeration from two causes to four; `DF-10-4-A/B/C` filed with named owners and real `target_story`s. Gates LOCAL: mypy clean 72, bandit 0 High/0 Med, coverage 95.16%→**95.51%**, dogfood verdict **unchanged by this delta** (proved by re-running it against a reconstructed pre-story tree). CI evidence **NOT ESTABLISHED**; nothing pushed, tagged or dispatched. ⛔ **HALT: 1319/1324 tests pass. FIVE `test_dogfood_*` guards are red**, each saying a committed AUTO-GENERATED Epic-7 artifact no longer matches what the generator derives. Two root causes, **both mandated by this story**: (a) the added LOC tips an NFR-SC1 bin-packing boundary (unit 40 files/14100 LOC → 39/14793), changing two of three `partition_id`s; (b) the **required** `git add` of the new module makes it tracked, so `git ls-files` moves the planned/audited population **71 → 72**, moving total LOC, the budget `$X` and the critical-set size. Proved: reverse-applying my edits reproduced the committed ids exactly, then I restored byte-identically (sha256 round-trip); and the suite had **one** failure before the `git add` and five after. **Not fixed**: AC7.6 fences all four artifacts by name (*"every Epic 1–9 artifact"*), and regenerating now would stamp HEAD `00c8d1b` — a sha containing none of 10.1–10.4's uncommitted deltas — as their provenance, manufacturing exactly the false-citation class Epic 10 exists to close. Four named options in the HALT block; option 1 (commit, then regenerate with the artifacts' own renderers, then re-run) recommended. | Developer (`bmad-dev-story`, `claude-opus-5[1m]`) |
| 2026-08-10 | 0.3 | **Fix round — HALT resolved by operator decision; status `in-progress` → `review`; suite 1319/1324 → 1324/1324.** No `argus/**` source file and no test was edited: the blocker was never in this story's code, it was three committed AUTO-GENERATED Epic-7 evidence artifacts that had gone stale against a generator which re-derives them from the live tree. **Operator (XAgent007) DECISION 1** — commit 10.1–10.4's deltas so HEAD genuinely contains them, then regenerate via the artifacts' OWN renderers, then re-run; git authorised COMMIT ONLY (no push, no tag, no dispatch — 10.1's DN-7 still binds, CI stays **NOT ESTABLISHED**). **DECISION 2** — file the systemic sub-finding round 1 left to the operator. Executed: `DF-10-4-D` filed **append-only** (`deferred-work.md` now `+585/−0`), owner **Engineering Lead**, `target_story: 12-1-pipeline-stops-breaching-its-own-limit`, 🟡, `developer-experience` — it records a mechanism **strictly stronger than `DF-8-5-B`'s**: `enumerate_minions_source_files` reads `git ls-files`, which reports the **INDEX**, so the guards break on `git add` **alone**, mid-implementation, at the exact moment AI-E8-1 *requires* the `git add` — two repo requirements in direct mechanical conflict, which no story can satisfy both of. **FILED ONLY, not fixed** (the coupling is in `argus/dogfood/`, outside the fence; changing what the dogfood enumerates is verdict-adjacent, DN-9's fence to Epic 11/12). Six local commits on `master`, each in the repo's message style with the `Co-Authored-By` trailer: `e59c2e1` (the untracked correct-course change signal — AI-E8-1 in documentary form), `ce2cc7e` (10.1), `ae5c6a3` (10.2), `58821c3` (10.3), **`a9cc933`** (10.4 — the provenance sha the artifacts now cite), and the regeneration commit. Co-edited documents are carried by the LAST story that touched them, stated in the messages rather than hidden, because four stories were implemented against ONE uncommitted tree and splitting eight files would invent hunks nobody authored. **DEV-6 — `master` over a branch, the one call the operator delegated**, decided on a measurement: the artifact being replaced already cited `7be90f77`, **not an ancestor of this history** — it survives only on `release/epics-8-9` and on a branch literally named `backup/pre-rebase-fix`, so the orphaned-provenance failure has already happened here once, by rebase. Ordinary branch-first hygiene is outbid by the explicit project constraint that a cited provenance sha must stay valid (§7's conflict rule); tradeoff recorded, not waved away. Three artifacts regenerated through `render_partition_plan_markdown` / `render_budget_plan_markdown` / `render_proof_markdown` and **asserted equal to the renderer's return value after writing**, with the pre-write diff printed and inspected — every changed line is a derived figure (population 71→72, LOC 18418→19783, `$X` 443→450, two `partition_id`s, bundle hash, critical set 50→51), never a claim or an assertion; `plan.commit_descriptor == proof.commit_descriptor == HEAD == a9cc933`, asserted in the script. **AI-E3-1 checked mechanically, not promised**: `git diff HEAD -- tests/` empty and the suite count unchanged at 1324, so nothing was bent to fit output; no test removed, skipped, weakened or `xfail`ed. Gates re-run LOCAL: **1324 collected / 1324 pass / 0 fail / 0 error / 0 skip** (counts from `--junit-xml`, since this shell truncates pytest's summary — 10.3's measured host quirk), mypy clean 72, bandit 0 High / 0 Med, coverage 95.51%. **Dogfood verdict byte-identical** — `RELEASE_READY`, exit 0, `blocking_findings=0`, `scope=application` — and round 1's unexplained divergence is now **resolved**: `15/19` is the reduced form of `60/76`, so the recorded `60/161` baseline **does** reproduce once the tree is committed, off by exactly **+1 assessed-and-deep** (`argus/shared/grammar_status.py`) and **+1 held-out** (`tests/test_grammar_diagnosis.py`) — this story's own two files. The round-1 `31/82` was an artefact of auditing a drifted, half-untracked tree. **No baseline figure was edited anywhere** (AC4.4 stop-and-report). AC7.6's write set widened by exactly the three artifacts, recorded in the Dev Agent Record rather than by editing the AC, because a dev may not amend the criterion that constrains them. All 7 ACs now ✅. | Developer (`bmad-dev-story` fix round, `claude-opus-5[1m]`) |
