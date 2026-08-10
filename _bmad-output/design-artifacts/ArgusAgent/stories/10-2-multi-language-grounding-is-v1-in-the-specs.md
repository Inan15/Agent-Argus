---
baseline_commit: 00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0
baseline_note: >-
  HEAD is `00c8d1b`. **Story 10.1's delta is in the working tree, NOT committed** —
  `tests/test_evidence_citation.py` is staged (`A `), and `architecture.md`, `epics.md`,
  `deferred-work.md` and `sprint-change-proposal-2026-07-28.md` carry 10.1's unstaged edits.
  You are building ON TOP of that uncommitted delta. Do not revert it, do not re-do it, and do
  not assume `git diff HEAD` isolates YOUR work — it does not. Measure your own delta with
  `git diff` against the tree as you found it, and say so in the Dev Agent Record.
  ⚠️ **`bmad-dev-loop-pack/` and `.bmad-drift-audit/` belong to the orchestrator — do not add,
  move or delete them.** `sprint-change-proposal-2026-08-10b.md` is untracked and is the
  AUTHORITY for the Epic 10-13 text you are implementing: read it, do not rewrite it.
  THIS FILE is untracked and IS yours: `git add` it with your delta or you repeat AI-E8-1, in
  which Epic 8 shipped with its own story file untracked because `git diff` cannot see an
  untracked path.
  **Every line number in this document was re-measured on 2026-08-10 against the working tree.**
  The line numbers in `epics.md`'s Story 10.2 AC1 are STALE — see §B.1. Line numbers in this
  project drift under the amendment cascade; **locate every site by its ANCHOR TEXT, and treat
  the line number as a hint that must be re-verified.**
story_key: 10-2-multi-language-grounding-is-v1-in-the-specs
epic: 10
---

# Story 10.2: Multi-language grounding is V1 in the specs, and its provenance is honest

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

As a downstream integrator auditing a non-Python repository,
I want the specs to state the languages ArgusAgent actually grounds and the provenance it records to
name the grammar that actually parsed,
so that a capability I depend on is specified, and a cached or replayed result cannot be keyed on the
wrong grammar.

**Why this story is second in Epic 10.** 10.1 established the *control* — a status claim must cite an
executed gate or be recorded `NOT ESTABLISHED`. 10.2 is the first artifact correction made *under* that
control, and it has the largest blast radius of the four, which is why the epic sequences it before
10.3. It is also a **hard dependency of Story 12.3** (memoization wiring): the architecture records the
10.2-before-12.3 order as load-bearing, because wiring a store over the current key persists a key that
is wrong for 9 of 10 languages.

---

## Story Context

### Method statement — everything below was MEASURED on this tree on 2026-08-10

Every line number, every version string and every eligibility result in §A-§C came from `grep`, from
reading the file, or from **executing `build_ast_index` over a ten-language fixture** on this host. Two
of the measurements contradict the story's own epic text. **Re-derive them; do not transcribe them.**
§A.2 in particular is a finding that changes what this story is allowed to write.

---

### A. The two findings that change this story

#### A.1 — 🚩 The site enumeration has now been wrong a THIRD time

The epic's own AC records that this list has been wrong twice (4 sites → 7 sites → 10 sites). Measured
on this tree, **the "measured 10-site list" is also incomplete, and its line numbers have all drifted.**

Mechanical derivation (run it yourself — this is the whole method):

```bash
cd _bmad-output/design-artifacts/ArgusAgent
grep -nE "multi-language|multi language|Python V1|Python in V1|V1 deep|AST-grounding = Python|Python AST in V1|deep AST-grounding" E-PRD/prd.md
grep -nE "multi-language|multi language|Python in V1|V1 deep|AST = Python|Python only|Python-only" architecture.md
```

**PRD — 8 sites. The epic's PRD enumeration is COMPLETE; only its line numbers are stale.**

| Epic says | Actually at | Anchor text (locate by THIS, not the number) |
|---|---|---|
| L23 | **`:23`** ✅ | `durableMoat: … AST-grounded depth [Python V1, multi-language V2]` |
| L116 | **`:121`** | *"`audited_deep` requires a grounded claim validated against the repo's AST (Python in V1; multi-language in V2)"* |
| L174 | **`:193`** | *"Python = impl #1 — so V2 multi-language is additive, not a core rewrite"* |
| L180 | **`:214`** | Growth Features (V2) list — *"· **multi-language** AST grounding ·"* |
| L317 | **`:364`** | Project-type overview — *"**Stack-agnostic** by construction (V1 deep AST-grounding = Python…)"* |
| L375 | **`:438`** | Risk mitigation — *"Python-only AST → stack-agnostic validator interface (V2 multi-language additive)"* |
| L398 | **`:469`** | **FR7 — the binding capability contract.** *"validate a deep claim against source structure (Python AST in V1)"* |
| L476 | **`:571`** | **NFR-P2.** *"deep AST-grounding = Python in V1; `claim_emitted` proxy elsewhere"* |

**Architecture — the epic names 2. Measurement finds 4 to amend and 2 to exempt.**

| Epic says | Actually at | Anchor text | Disposition |
|---|---|---|---|
| — | **`:89-90`** | *"**Stack:** Python 3.11+ … AST = Python in V1 (`claim_emitted` proxy elsewhere)"* | 🆕 **AMEND — missed by all three enumerations** |
| L220 | **`:267`** | *"**Deferred (post-V1):** multi-language AST, seam auditor…"* | AMEND |
| L237 | **`:317`** | *"Stack detection via `cloc`/`radon` + tree-sitter; V1 deep = Python only"* | AMEND |
| — | **`:800`** | *"**Future enhancement:** multi-language AST (V2), seam auditor (V2)…"* | 🆕 **AMEND — missed by all three enumerations** |
| — | `:471` | *"…so the default public install grounds **Python only** — which NFR-P3 classifies as a packaging defect"* | ⛔ **EXEMPT — TRUE, and Story 12.5's** |
| — | `:766` | *"…an optional extra, so the default install grounds **Python only** — the exact state NFR-P3 classifies as…"* | ⛔ **EXEMPT — TRUE, and Story 12.5's** |

**Measured total: 12 sites to amend (8 PRD + 4 architecture), 2 exempt by name.**

**Why the two exemptions are not a loophole.** `:471` and `:766` are not V1/V2 *scope* claims. They are
**true statements about the default install**: the nine non-Python grammars sit in the optional
`[languages]` extra, so `pip install argus-agent` really does ground Python only. Amending them would
replace a true sentence with a false one. They are **Story 12.5's** (NFR-P3, promote-to-base-deps vs.
document-the-extra) and are fenced out of this story — **but they must be named in the guard's
exemption list with that reason written down**, never silently skipped. Silent omission is the
`_PRESERVED_RECORD` anti-pattern 10.1's DN-5 already ruled on.

**The lesson the epic already drew, now confirmed a third time:** a hand-counted list is the wrong
instrument. **AC2 — the closure guard — is the load-bearing AC of this story, not AC1.** If you deliver
AC1 and skip AC2, this recurs, and the epic's own AC says so.

#### A.2 — 🚩🚩 THE FINDING THAT CONSTRAINS AC1: only **8 of 10** languages actually ground

Measured by running the real code path on this host:

```python
from argus.index.ast_index import build_ast_index
# ten one-function fixtures, one per language, into a tmp dir
idx = build_ast_index(tmpdir, ("a.c","a.cpp","a.go","a.java","a.js","a.php","a.py","a.rb","a.rs","a.ts"))
```

| File | `ast_eligible` | `parse_failure_reason` |
|---|---|---|
| `a.c` `a.cpp` `a.go` `a.java` `a.js` `a.py` `a.rb` `a.rs` | ✅ `True` | — |
| **`a.ts`** | ❌ `False` | **`grammar_missing_typescript`** |
| **`a.php`** | ❌ `False` | **`grammar_missing_php`** |

**Result: `eligible 8 / 10`. And the reason token is false.** Both grammars **are installed** and both
**are declared in the `[languages]` extra** (`pyproject.toml:47-56`). The cause is
`argus/index/ast_index.py:257-268`:

```python
mod = importlib.import_module(f"tree_sitter_{lang}")
lang_func = getattr(mod, "language", None)     # ← the whole defect
if lang_func is not None:
    return Parser(Language(lang_func()))
```

Two of the ten grammar packages do not export `language()`:

| Package | Version installed | Exports |
|---|---|---|
| `tree_sitter_typescript` | 0.23.2 | `language_typescript`, `language_tsx` — **no `language`** |
| `tree_sitter_php` | 0.24.1 | `language_php`, `language_php_only` — **no `language`** |

Verified that the alternates load and parse cleanly under the installed `tree-sitter` runtime:
`Parser(Language(tst.language_typescript()))`, `…language_tsx()`, `…tsp.language_php()` and
`…language_php_only()` all construct and parse their sample with `has_error=False`.

**Why this is not a footnote — it is the story's central constraint.**
AC1 amends **FR7, the binding capability contract**. Writing *"multi-language AST grounding, delivered
in V1, 10 languages"* into FR7 while two of them return `ast_eligible=False` would **replace one false
spec claim with another false spec claim** — and this one drifts in the *oversell* direction, which the
ledger explicitly notes the original did not. That is Story 10.5's defect class (*a spec with no
capability*) manufactured inside the story whose job is closing its inverse.

Second-order: the reason token **`grammar_missing_typescript` tells an operator to install a package
they already have**. `DF-AUD-APAA-F`/Story 10.4 files the *identical harm* — *"the remedy the report
gives an operator is wrong"* — for a different cause (broken grammar vs. missing grammar). This is a
**third** cause of the same harm, and 10.4's AC as written does not catch it: splitting
`except (ImportError, Exception)` does nothing here, because **nothing raises**. `getattr` returns
`None` and the code falls straight through. See **DN-3** for the disposition and **§F** for the fence.

#### A.3 — The provenance defect, measured rather than quoted

`AstIndex.grammar_version` is a single `str` (`ast_index.py:172-174`) filled by
`_grammar_version()` (`:180-189`) = `importlib.metadata.version("tree-sitter-python")`.

In the ten-language run above, the index recorded **`grammar_version = '0.25.0'`** — for a build in
which a Rust file was parsed by `tree-sitter-rust` **0.24.2**, a Java file by `tree-sitter-java`
**0.23.5**, a Ruby file by `tree-sitter-ruby` **0.23.1**, and so on. The versions genuinely differ:

| Grammar | Installed version |
|---|---|
| python | **0.25.0** |
| javascript | 0.25.0 |
| go | 0.25.0 |
| rust | 0.24.2 |
| c | 0.24.2 |
| php | 0.24.1 |
| java | 0.23.5 |
| cpp | 0.23.4 |
| typescript | 0.23.2 |
| ruby | 0.23.1 |

So the recorded provenance is **wrong for 7 of the 8 languages that actually ground**, and a Go, Rust,
Java, C, C++ or Ruby grammar upgrade **would not move the R3 cache key**. This is the
silent-cache-staleness class `DF-5-1-A` already files for `prompt_template_version`.

---

### B. What the specs say vs. what the code does — the disagreement, adjudicated

| Claim | Spec | Code | Which is wrong |
|---|---|---|---|
| Multi-language AST grounding is a **V2** capability | PRD ×8, architecture ×4 | 10-language index shipped since `084c6a7` | **The spec.** The capability exists; amend the spec. |
| **10** languages are grounded | *(the amendment about to be written)* | **8** ground; TS + PHP silently do not | **The code** — and it is a 2-line-shaped defect. Fix it, then the spec is true. |
| Provenance is one `grammar_version` | architecture R3 (`:83-88`, `:248`, `:327-328`) — *designed* for one grammar | one scalar, always `tree-sitter-python`'s | **Both**, in different ways: it is a **design change**, not a defect fix. Amend R3 *and* the code. |
| `[languages]` extra exists and is discoverable | *nothing* — `README.md` and `CHANGELOG.md` have **zero** occurrences of `[languages]` | `pyproject.toml:47-56` ships it; `audit-ci.yml` sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` | **The docs.** Confirmed by grep: README mentions `tree-sitter` twice, never the extra. |

#### B.1 — ⚠️ `epics.md`'s Story 10.2 AC1 line numbers are stale, and that is expected

The AC was written on 2026-08-10b against the *pre-amendment* PRD; the 2026-08-10b cascade then inserted
~95 lines into `prd.md` and ~90 into `architecture.md`. **You are not correcting `epics.md`.** Epics
1-9 are delivered, Epics 11-13 were written 2026-08-10b, and 10.1's AC5 fenced `epics.md` to two named
locations. **`epics.md` is NOT in this story's write set** (see AC8's fence). The drift is recorded here
so the dev locates by anchor text and does not conclude the epic is describing a different document.

---

### C. The R3 cache-key contract, read in place

Three architecture sites carry the single-grammar assumption. All three are AC5's targets:

| Site | Text |
|---|---|
| `architecture.md:83-88` | *"Key inputs: content-hash + model checkpoint + prompt-template version + **tool versions (tree-sitter grammar, radon)** + …"* — singular |
| `architecture.md:246-249` | *"`tree-sitter==0.25.2` … **The grammar version is pinned into the determinism cache key (R3).**"* |
| `architecture.md:327-328` | *"cache key = full recording-producing closure: … + **tree-sitter-grammar/tool versions** + …"* |

And `architecture.md:330-345` already states the wiring order this story must honour:

> *"**Story 10.2 first** — the cache key currently folds **one** `grammar_version` resolved from
> `tree-sitter-python` while the index parses **10 languages**… 10.2 makes provenance per-grammar and
> **explicitly declines to wire the store**."*

#### C.1 — 🟢 The bump is free TODAY, and that is measurable

```bash
grep -rn "derive_cache_key\|RecordingProducingClosure\|MemoStore" --include=*.py argus/
```

Measured: **no production caller derives a key.** `argus/pipeline.py` imports neither `cache.key` nor
`cache.memo_store`. `argus/cache/invalidation.py` and `argus/audit/deep_audit.py` reference them, and
both are themselves unwired (`DeepAuditSeam` is Story 12.2's). **There are no persisted cache entries
in the world to migrate.** Bumping `CACHE_KEY_SCHEMA_VERSION` (`argus/cache/key.py:90`, currently
`"2"`) costs exactly one constant today. After 12.3 wires the store it costs a migration. This is the
architecture's *"free now, expensive later"* in literal form — and it is why this story exists now
rather than after 12.3.

---

### D. The additive-only schema policy you must not breach

PRD `:393`: *"**'Migration guide' = the additive-only schema-evolution policy**: new fields only,
`schema_version` bumped, content-hash determinism preserved."*

**Consequence, and it is the trap in AC4:** you may **not** delete `AstIndex.grammar_version` or
`RecordingProducingClosure.grammar_version`. You **add** the per-grammar field beside it and bump the
schema version. What you *must* fix is the **docstring lie**: `ast_index.py:162-163` and
`key.py:216-217` both describe the scalar as if it were the index's provenance. After this story it is
what it has always actually been — *the `tree-sitter-python` package version* — and the per-grammar map
is the provenance. Say that in the field description, so the next reader is not misled the way the
architecture was.

---

### E. Traps previous stories already paid for — the five that apply here

1. **AI-E3-1 (Epic 3) — a keystone test can be green over its own keystone bug.** Story 3.4's resume
   test passed while resume silently dropped coverage. **Every new assertion in this story runs RED
   first**: the grounding-matrix test against the *unfixed* loader (must fail naming `typescript` and
   `php`), the closure guard against the *unamended* specs (must fail naming the sites), the cache-key
   test against the *unbumped* key (must fail). A guard first run after the fix has proven nothing.
2. **AI-E8-6 (Epic 8) — all five Epic-8 stories shipped a guard narrower than their own AC.** AC2's
   glob closure and AC3's ten-language enumeration are the direct countermeasures. **Do not** discharge
   an enumerated space with one sample, and **do not** replace the closure with a fixed file list.
3. **`-17b` (Epic 9) — the denial filter that swallowed what it looked for.** Found by review, not by
   the author. AC2's guard needs a **positive control in both directions**: plant an unamended claim
   (must fire) and plant a correctly-amended one (must not).
4. **`test_the_ten_claimed_languages_are_enumerable` (`tests/test_multilanguage_audit.py`,
   `TC-ArgusAgent-INTAKE-003-02`) is the near-miss.** It already exists, and it asserts
   `claimed <= set(LANGUAGE_BY_SUFFIX.values())` — **enumerability, not groundability**. It is green
   right now while two of the ten cannot ground. It is the *weaker* property, asserted where the
   *stronger* one was assumed. **This is exactly how §A.2 survived a full epic.** Your AC3 test asserts
   the stronger property.
5. **AI-E9-7 / R1 (Epic 9) — a prose copy of a pinned figure drifted at five sites.** If your amended
   spec prose states a language count or a language list, **derive it or pin it**. A hand-typed "10" in
   the PRD is the sixth site of that same class.

---

### F. ⛔ FENCES — what this story must NOT touch

| Fence | Owner | Why |
|---|---|---|
| **`argus/pipeline.py`** | **Story 12.1** | 1331 lines vs. the NFR-M1 cap of 1200 — already breaching. It calls `build_ast_index` at `:910` and `:1189` with an unchanged signature, so **no pipeline edit is required**. If your change needs one, you have widened the interface; narrow it instead. **Do not add a line to this file.** |
| **`except (ImportError, Exception)` at `ast_index.py:266`** | **Story 10.4** | 10.4's whole AC is splitting that tuple so MISSING and BROKEN report distinct tokens. You are editing the same function. **Add the entry-point map; leave the except clause structurally as you found it.** If your edit moves its line number, say so in the Dev Agent Record so 10.4 re-locates by anchor. |
| **Wiring `MemoStore` into the pipeline** | **Story 12.3** | The epic AC says so explicitly, and the architecture records the ordering as deliberate. **AC6 makes not-wiring a positive requirement**, not an omission. |
| **A runtime `tree-sitter` version assertion / degradation** | **Story 11.4** | 11.4 owns *"wrong grammar version cannot produce a false green."* You **record** the measured per-grammar versions (which is 11.4's input); you do **not** add a runtime bound, a version gate, or a degradation path. |
| **`architecture.md:471`, `architecture.md:766`** | **Story 12.5** | True statements about the default install (NFR-P3). Exempt **by name with the reason**, never silently. |
| **Promoting `[languages]` to base dependencies** | **Story 12.5** | AC7 *documents* the extra. Changing where the grammars live is 12.5's open decision. |
| **`epics.md`** | 10.1 (fenced) / 2026-08-10b | Not in this story's write set at all (§B.1). |
| **`.github/workflows/audit-ci.yml`** | — | Already correct and green, and already sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`. Editing a green workflow here is unjustified regression risk (10.1's DN-6, same reasoning). |
| **Epics 1-9 artifacts, all retrospectives, the preserved 7.2 record** | signed | Editing them now would falsify the record. |

---

## Acceptance Criteria

### AC1 — Every measured scope-claim site records multi-language grounding as delivered in V1

All **12** sites in the §A.1 tables — **PRD** `:23`, `:121`, `:193`, `:214`, `:364`, `:438`, `:469`
(**FR7**), `:571` (**NFR-P2**); **architecture** `:89-90`, `:267`, `:317`, `:800` — are amended so each
records multi-language AST grounding as **delivered in V1**, not deferred to V2.

1. Each amendment is **dated** and **attributed** to `sprint-change-proposal-2026-07-28.md` (the change
   that shipped the capability without a story), in the §3.4 form this project uses: **strike replaced
   wording (`~~…~~`), never delete it.**
2. **The V2 roadmap no longer lists it.** `prd.md:214`'s Growth Features (V2) list drops
   *"**multi-language** AST grounding"*, and `architecture.md:267` / `:800` drop it from
   *"Deferred (post-V1)"* / *"Future enhancement"* — so **V2 cannot re-scope delivered work**. The other
   V2 items on those lines are untouched; 2026-08-10b swept them and multi-language is the only leak.
3. **FR7 and NFR-P2 are the load-bearing two.** FR7 is the *binding* capability contract
   (`prd.md:455`: *"a capability not listed here will not exist in V1 unless explicitly added"*). Its
   amended text states the grounded language set and its **source of truth**
   (`argus/shared/source_languages.py`), not a hand-typed list (trap E.5).
4. `architecture.md:471` and `:766` are **NOT amended** and appear in the AC2 guard's exemption list
   with the recorded reason *"true statement about the default install; Story 12.5 (NFR-P3)."*
5. Any spec sentence stating a **count** either cites the pin or is phrased so no count is asserted.

> **Locate by anchor text.** Line numbers in this project drift (§B.1). Every number above was measured
> 2026-08-10; re-verify each before editing and record any that moved.

### AC2 — 🔑 A committed guard fails on the unamended claim shape, and cannot be escaped

**This is the AC that makes the story stick.** A new committed test greps the amendable artifact set for
the unamended claim shape and fails if any site survives, so the enumeration is **asserted, not
hand-counted a fourth time** (§A.1).

1. **Registry + glob closure.** The guard registers the artifacts it scans **and** globs
   `_bmad-output/design-artifacts/ArgusAgent/E-PRD/*.md` + `architecture.md`, failing if a scanned-class
   file exists on disk that is not registered. A fixed file list is a breach of this AC (trap E.2).
2. **The claim shape is a pattern, not a line list.** It fires on the V2-deferral shape
   (multi-language AST grounding co-occurring with a `V2` / `post-V1` / `Future enhancement` /
   `Deferred` marker in the same sentence), so a *newly written* V2 claim at a *new* line is caught.
3. **Positive control, both directions** (trap E.3): a planted unamended sentence **fires**; a planted
   correctly-amended sentence **does not**. Both are pure-function checks over planted strings, never
   over the real files.
4. **Non-vacuity**: the guard fails if it scanned zero files or matched zero exemptions.
5. **Exemptions are data with reasons**, enumerated by name (AC1.4). An exemption without a reason
   string fails the guard's own self-check.
6. **RED first** (trap E.1): run it against the **unamended** specs and record the failure naming the
   surviving sites, before AC1's edits land. Restore the documents byte-identically afterwards
   (sha256 round-trip, as 10.1's D4 did).

### AC3 — The specs claim only what the code can do: all ten languages actually ground

**Given** §A.2 measured `eligible 8 / 10` — TypeScript and PHP return `ast_eligible=False` with
`grammar_missing_<lang>` **while their grammars are installed and declared in `[languages]`** —
**When** AC1 writes the delivered-in-V1 claim into FR7,
**Then** the claim is **true at the moment it is written**:

1. `argus/index/ast_index.py`'s grammar loading resolves the **per-language entry point**, not only
   `language`. A declarative map (e.g. `typescript → language_typescript`, `php → language_php`) with
   `language` as the default — **data, not a chain of `if`s**, so adding a language stays a one-line
   edit in one place (the `source_languages.py` precedent).
2. **`.tsx` resolves to `language_tsx()`**, not `language_typescript()` — both are in
   `LANGUAGE_BY_SUFFIX` as `typescript`, and tsx-vs-ts is a *suffix*-level distinction the current
   language-level parser cache cannot express. Measured: both entry points construct and parse cleanly.
   If you cannot express it without widening scope, **record the shortfall explicitly** and file it;
   do not let `.tsx` silently regress.
3. **A ten-language grounding matrix test** builds an index over a minimal valid fixture in **each** of
   the ten languages and asserts `ast_eligible is True`, with a failure message naming the language and
   its `parse_failure_reason`. **Enumerated space** (trap E.2): a language in `LANGUAGE_BY_SUFFIX` with
   no fixture **fails the test** — it must not be possible to add language #11 and leave it unpinned.
4. **Grammar-availability honesty is preserved.** The matrix test follows the existing
   `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` convention in `tests/test_multilanguage_audit.py`: skip when the
   optional grammar is genuinely absent, **hard-fail in CI** where the extra is installed. A skip that
   could hide this regression is the false green the file exists to prevent.
5. **RED first**: against the unfixed loader the matrix test fails, naming exactly `typescript` and
   `php`. Record the RED output. A matrix test first run after the fix has proven nothing (trap E.1).
6. **Zero verdict drift on this repository, proven not assumed.** `git ls-files` matches **0** files
   with `.ts/.tsx/.mts/.cts/.php` suffixes, so the local suite and the dogfood verdict must be
   unchanged. **Any change to the dogfood verdict is a stop-and-report**, not a figure to update.

⛔ **Scope fence:** this is a *grammar-resolution* fix. It is **not** licence to touch the
`except (ImportError, Exception)` clause (Story 10.4), nor to add a runtime version bound (Story 11.4).

### AC4 — Provenance names the grammar that actually parsed, per grammar

1. `AstIndex` gains a **per-grammar provenance record**: for each language whose grammar was **actually
   loaded and used in this build**, the resolved package version. Deterministic and canonically
   serializable — **sorted, no dict-iteration-order reliance, no float** (AR4/AR11); a frozen tuple of
   frozen models, matching the `Definition`/`CodeEdge` house shape.
2. **Additive only** (§D): `grammar_version` is **retained**, `AstIndex.schema_version` is **bumped**,
   and the retained scalar's description is corrected to say what it actually is — *the resolved
   `tree-sitter-python` package version* — rather than implying it is the index's provenance.
3. **Only grammars that parsed are recorded.** A language present in `LANGUAGE_BY_SUFFIX` but absent
   from this repository, or whose grammar is not installed, does **not** appear. Recording every
   installed grammar would make the key depend on the *host*, not on the *audit* — a determinism
   regression, and the inverse defect. Assert both directions.
4. Existing `AstIndex` consumers keep working: `argus/dogfood/partition_plan.py:478`,
   `argus/pipeline.py:910`/`:1189` and every test constructing `AstIndex(grammar_version=…)` must not
   break — **the new field is defaulted**, and the ~10 existing test constructions are **not** rewritten.

### AC5 — The R3 cache key moves for a grammar that parsed, and only for one that parsed

1. `RecordingProducingClosure` (`argus/cache/key.py:196`) gains the same per-grammar provenance,
   `_closure_payload` folds it **sorted** (`:258-280`), and **`CACHE_KEY_SCHEMA_VERSION` is bumped
   `"2"` → `"3"`** (`:90`) — free today, per §C.1, and this is the moment the architecture reserved.
2. **The two-directional determinism property, pinned by test:**
   - a **change to a grammar version that parsed** ⇒ the key **MOVES** (the defect being closed: today
     a Go/Rust/JS grammar change does not move it);
   - a **change to a grammar that did not parse** ⇒ the key **DOES NOT MOVE** (the regression being
     prevented: the key must be a function of the audit, not of the host's installed packages).
3. **Architecture R3 is amended as a DESIGN CHANGE, dated, at all three sites** — `:83-88`, `:246-249`,
   `:327-328` — stating that provenance is per-grammar and that the key folds only the grammars that
   participated. The epic is explicit that this *"is a design change and not a defect fix"*; the
   amendment must say so in those words rather than reading as a typo correction.
4. The existing golden/canary coverage in `tests/test_cache_key.py` and
   `tests/test_cache_invalidation.py` is **extended, never weakened**. In particular the
   `("grammar_version", …)` input-sensitivity case at `test_cache_key.py:127` stays, and gains a
   per-grammar sibling. **No existing test is deleted, skipped or relaxed.**
5. `argus/audit/deep_audit.py::build_closure_from_recording` (`:54-88`) still constructs a valid closure
   after the change. It is unwired (Story 12.2's), so it is **updated for compatibility only** — no new
   behaviour, no wiring.

### AC6 — The memoization store is NOT wired, and the ordering is recorded as deliberate

A **positive requirement**, not an omission. `argus/pipeline.py` must still import neither
`argus.cache.key` nor `argus.cache.memo_store` when this story ends — verifiable by the same grep as
§C.1. The story records, in `architecture.md` beside the existing `:330-345` note, that the key was
corrected **before** anything depended on it, and that **Story 12.3 wires the store over the corrected
key**. Wiring here would persist a key that was wrong for 9 of 10 languages hours before it was fixed.

### AC7 — A consumer can discover the capability they are paying for

Measured: `README.md` mentions `tree-sitter` twice and the `[languages]` extra **zero** times;
`CHANGELOG.md` mentions grammars **zero** times.

1. **`README.md`** — the install section (`:28-40`, alongside the existing INTERIM VCS-pin block) names
   the `[languages]` extra, the install command, **the languages it enables**, and **what a missing
   grammar does to a file's coverage grade** (`ast_eligible=False` → shallow, never a silent drop,
   never a false deep claim).
2. **`CHANGELOG.md`** — an entry under the existing **`## Unreleased`** heading (`:41`) recording the
   extra as a consumer-visible capability, in the file's established honesty register.
3. Both state the honest boundary `source_languages.py:27-32` already draws: **enumerable ≠ deeply
   auditable.** A language without its grammar still enumerates and grades — it just cannot reach
   `audited_deep`.
4. **No claim exceeding AC3's measured matrix.** If AC3.2 (`.tsx`) is not fully delivered, the docs say
   so. ⛔ Do not describe promoting the grammars to base dependencies — that is Story 12.5's decision.

### AC8 — The ledger closes honestly, the gates run, and the fences hold

1. **`DF-AUD-APAA-D` (`deferred-work.md:1394-1414`) is closed APPEND-ONLY.** The original entry stays
   **byte-intact**; the closure note is appended and **must include both new findings** — §A.1 (the
   enumeration was wrong a third time; the real count is 12 with 2 exempt) and §A.2 (only 8 of 10
   grounded, and the reason token misdiagnosed it). `git diff --numstat` on `deferred-work.md` is
   **`+n / -0`** (10.1's DN-8 / §3.4).
2. **Any new deferral is filed with an id, an owner and a `target_story`** — never `target_story: NONE`
   without a named human (AI-E9-8). **If AC3.2 (`.tsx`) or any part of AC3 is not fully delivered, it
   is filed, not omitted.**
3. **Gates re-run and LABELLED LOCAL** (10.1's AC6, and the standard 10.1's AC5 hands to this story):
   `mypy argus` · `bandit -r argus --severity-level medium` · `pytest tests/ --cov=argus
   --cov-fail-under=80`. **Baseline is 1235 collected** (measured on this tree by summing per-file
   collection counts). The count grows by **exactly** the new cases; **no test removed, skipped or
   weakened.**
4. **Evidence-citation compliance (10.1's binding rule, `architecture.md:438-443` + `:599-602`,
   enforced by `tests/test_evidence_citation.py`).** Local gates are **necessary, not sufficient** — CI
   runs 3.10/3.11/3.12 on ubuntu and this host is Windows/3.11.15. Run `31341363300` covers `00c8d1b`
   **and cannot evidence your tree.** Either cite the `audit-ci.yml` run covering your **own** HEAD
   *with the sha it covers*, or record the status **NOT ESTABLISHED** and name the command a human runs.
   ⛔ **Do not push, tag, or `workflow_dispatch`** to manufacture a citation (10.1's DN-7).
5. **Write set — the fence, checked with `git status --porcelain` AND `git diff --stat`** (AI-E8-2: a
   plain `git diff` cannot see an untracked path):

   | Permitted | |
   |---|---|
   | `E-PRD/prd.md` · `architecture.md` · `deferred-work.md` | AC1, AC5.3, AC6, AC8.1 |
   | `README.md` · `CHANGELOG.md` | AC7 |
   | `argus/index/ast_index.py` · `argus/cache/key.py` · `argus/audit/deep_audit.py` | AC3, AC4, AC5 |
   | new + existing tests under `tests/` | AC2, AC3, AC4, AC5 |
   | this story file · `sprint-status.yaml` | process |

   **`argus/pipeline.py` must be byte-unchanged** (fence F, NFR-M1 at 1331/1200), and so must
   `epics.md`, `audit-ci.yml`, and every Epic 1-9 artifact and retrospective. A diff outside the table
   above means scope has leaked — **stop and record why** rather than widening.
6. **Whole-system, not just the ACs.** The full suite is green and the **dogfood verdict is
   IDENTICAL** (AC3.6). A changed dogfood verdict is a stop-and-report.

---

## Tasks / Subtasks

- [x] **T1 — Re-measure before you edit anything (AC1, AC3) — FIRST**
  - [x] Run both `grep -nE` commands from §A.1; confirm **8 PRD + 6 architecture** hits and reconcile
        every one against the §A.1 tables. Record any line that moved.
  - [x] Run the ten-language `build_ast_index` probe (§A.2). Confirm **8/10**, and that `a.ts`/`a.php`
        report `grammar_missing_typescript`/`grammar_missing_php` while both packages import.
  - [x] Record the per-grammar installed versions (§A.3) — they are AC4's fixture **and Story 11.4's
        input**.
  - [x] `grep -rn "derive_cache_key\|MemoStore" --include=*.py argus/` → confirm the store is unwired
        (§C.1), so the `CACHE_KEY_SCHEMA_VERSION` bump is free.
  - [x] `git ls-files | grep -Ei '\.(ts|tsx|mts|cts|php)$'` → expect **0** (AC3.6 blast radius).
  - [x] ⛔ **If any measurement disagrees with this document, the tree wins.** Record the divergence and
        proceed from the measurement.

- [x] **T2 — Read before writing**
  - [x] `tests/test_multilanguage_audit.py` in full — the near-miss (trap E.4), the
        `ARGUS_REQUIRE_LANGUAGE_GRAMMARS` convention, and the fixture style your matrix test extends
  - [x] `argus/index/ast_index.py` end-to-end (368 lines) — especially `:180-189`, `:257-268`, `:298-368`
  - [x] `argus/cache/key.py:196-304` — the closure model, `_closure_payload`, `derive_cache_key`
  - [x] `tests/test_cache_key.py` + `tests/test_cache_invalidation.py` — the golden/canary coverage you
        must extend and must not weaken
  - [x] `tests/test_evidence_citation.py` — 10.1's guard shape (registry + glob closure + positive
        control + non-vacuity); **AC2's guard is the same shape over a different corpus**
  - [x] `architecture.md:83-88`, `:246-249`, `:327-345`, `:438-443` · `argus/shared/source_languages.py`

- [x] **T3 — RED first, all three, before any fix (AC2.6, AC3.5, AC5.2) — trap E.1**
  - [x] Grounding-matrix test vs. the **unfixed** loader → must FAIL naming `typescript` and `php`
  - [x] Claim-shape guard vs. the **unamended** specs → must FAIL naming the surviving sites
  - [x] Per-grammar cache-key test vs. the **unbumped** key → must FAIL
  - [x] Record each RED output verbatim in the Debug Log; if the test code changes afterwards,
        **re-run RED with the final code** (10.1's D4 — otherwise the shipped assertions were never
        seen red)

- [x] **T4 — Make the claim true (AC3)**
  - [x] Per-language entry-point map in `ast_index.py`; `language` remains the default
  - [x] `.tsx` → `language_tsx()`, or the shortfall recorded and filed (AC3.2, AC8.2)
  - [x] Ten-language matrix test, enumerated over `LANGUAGE_BY_SUFFIX` so language #11 cannot escape
  - [x] ⛔ Leave `except (ImportError, Exception)` structurally alone (fence F / Story 10.4)
  - [x] Confirm **GREEN 10/10**, and re-run the dogfood verdict → **IDENTICAL** (AC3.6)

- [x] **T5 — Per-grammar provenance (AC4)**
  - [x] Add the sorted, frozen per-grammar record to `AstIndex`; bump its `schema_version`
  - [x] Retain `grammar_version`; **correct its description** (§D) — do not delete it
  - [x] Pin both directions: a grammar that parsed **is** recorded; one that did not **is not**
  - [x] Confirm the ~10 existing `AstIndex(grammar_version=…)` test constructions still pass unedited

- [x] **T6 — The key moves, correctly (AC5)**
  - [x] Add the field to `RecordingProducingClosure`; fold it **sorted** in `_closure_payload`
  - [x] Bump `CACHE_KEY_SCHEMA_VERSION` `"2"` → `"3"`
  - [x] Pin the two-directional property (AC5.2); extend `test_cache_key.py:127`'s sensitivity table
  - [x] Update `deep_audit.py::build_closure_from_recording` for **compatibility only** — no wiring
  - [x] Amend `architecture.md` R3 at all three sites, dated, **as a design change** (AC5.3)

- [x] **T7 — Amend the 12 sites + land the guard (AC1, AC2)**
  - [x] PRD ×8 and architecture ×4, each dated + attributed, replaced wording `~~struck~~`
  - [x] V2 roadmap / Deferred / Future-enhancement lists drop multi-language **only** (AC1.2)
  - [x] FR7 + NFR-P2 point at `source_languages.py` as the source of truth (AC1.3, trap E.5)
  - [x] Exempt `architecture.md:471`/`:766` **by name with the reason** (AC1.4)
  - [x] Guard: registry + **glob closure** + pattern claim-shape + positive control **both directions**
        + non-vacuity + reasoned exemptions (AC2.1-2.5)

- [x] **T8 — Not wiring, recorded (AC6)**
  - [x] Re-run the §C.1 grep → `argus/pipeline.py` imports neither module
  - [x] Record the ordering rationale beside `architecture.md:330-345`

- [x] **T9 — Consumer documentation (AC7)**
  - [x] `README.md` install section: the extra, the command, the languages, the coverage consequence
  - [x] `CHANGELOG.md` under `## Unreleased` (`:41`), in the file's honesty register
  - [x] Claim nothing beyond AC3's measured matrix

- [x] **T10 — Close, gate, fence (AC8)**
  - [x] `DF-AUD-APAA-D` closed **append-only**, including §A.1 and §A.2; verify numstat `+n 0`
  - [x] File any shortfall with id + owner + `target_story`
  - [x] `mypy argus` · `bandit -r argus --severity-level medium` · `pytest tests/ --cov=argus
        --cov-fail-under=80`; record figures **labelled LOCAL**; baseline **1235 collected**
  - [x] Evidence citation: run id **plus its sha**, or **NOT ESTABLISHED** + the command (AC8.4).
        ⛔ No push, no tag, no `workflow_dispatch`
  - [x] `git status --porcelain` **and** `git diff --stat` vs. the write-set table; confirm
        `argus/pipeline.py` and `epics.md` byte-unchanged; `git add` this story file
  - [x] Set Status to `review`; update `sprint-status.yaml` `10-2-…: review`

### Review Findings

**Code review 2026-08-10, iteration 1 — PASS. No unresolved findings.** Verified independently
against the files on disk, not read off this document.

1. **All 8 ACs checked against the actual files.** AC1: all 12 amendment sites confirmed by content
   at their measured anchors — PRD `:23 :121 :193 :214 :364 :438 :471(FR7) :576(NFR-P2)`, architecture
   `:104-108 :294-296 :347-351 :847-849` — each struck (`~~…~~`), dated `2026-08-10`, attributed to
   `sprint-change-proposal-2026-07-28.md`; the two default-install sentences at architecture `:517-518`
   / `:812-813` confirmed unamended and correctly outside the write set (DN-2 / Story 12.5). AC2:
   `tests/test_spec_claim_scope.py` read in full — registry + **measured** glob closure (`Path.glob`
   independently confirmed to include dotfiles, so `.memlog.md` is genuinely inside the closure), two
   claim rules (deferral-marker and Python-only-scope), heading-context for markers only, positive
   control in both directions, non-vacuity, and reasoned + exercised exemptions. AC3: FR7 and README
   independently confirmed to disclose the `DF-10-2-A` shortfall (C/C++/Ruby/Rust ground but extract
   zero definitions) **immediately beside** the delivered-in-V1 claim, not buried — the central
   question of this review (does the amended FR7 oversell in a subtler way) resolves **no**: "grounded"
   is explicitly scoped to `ast_eligible`/parses, distinguished in the same bullet from "reaches
   `audited_deep`", and the boundary is stated at the point of the claim in FR7, README and CHANGELOG
   alike. AC4/AC5: `GrammarProvenance` confirmed defined in the PURE `cache/key.py` and imported by the
   impure `ast_index.py` shell (no reverse import, no circularity); `_one_version_per_language`
   validator, sorted fold, and the two-directional cache-key tests (`CACHE-001-77`/`-78`) read and
   independently reasoned through. AC6: `argus/pipeline.py` git-diff confirmed empty. AC7: README/
   CHANGELOG read in full, cross-checked against FR7 and `deferred-work.md` for consistency — no claim
   exceeds the measured matrix. AC8: `DF-AUD-APAA-D` original text confirmed byte-intact before its
   closure note; `DF-10-2-A` filed with a named owner (Engineering Lead) and explicit non-folding
   rationale, satisfying AI-E9-8 despite `target_story: NONE`.

2. **Mechanical claims re-derived by the reviewer, not transcribed:**
   `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest tests/` → **1272 passed, 0 failed, 0 skipped** (exact
   match); `mypy argus` → **0 issues / 71 files** (match); `bandit -r argus --severity-level medium` →
   **0 Medium/High** (match); `pytest --cov=argus --cov-fail-under=80` → **95.06%**, gate satisfied
   (match). `git diff -- argus/pipeline.py` and `git diff -- .github/workflows/audit-ci.yml` both
   **empty** (byte-unchanged, confirmed). `git diff --numstat -- deferred-work.md` → **`257 0`**
   (append-only, confirmed). `sha256sum` on `E-PRD/.memlog.md` and `E-PRD/addendum.md` matches the
   story's recorded pre/post hashes exactly (unchanged by this story). File mtimes for every path in
   `git status --porcelain` partition cleanly at the session boundary (~13:53–16:25): everything
   outside the story's declared File List (`epics.md` 11:39, `_bmad/*` configs 08:17, `sprint-change-
   proposal-2026-07-28.md` 11:39, `tests/test_evidence_citation.py` 11:34, `stories/10-1-…md` 12:27)
   predates this session and belongs to 10.1 / the 2026-08-10b cascade, not to 10.2 — the write-set
   fence (AC8.5) holds with zero leakage. `git reflog` shows no commits, `git tag -l` is empty, and
   `origin` was not pushed to — DN-7 honored, CI status correctly recorded `NOT ESTABLISHED`.

3. **The three new guards read in full and adversarially probed**, not sampled: the grounding matrix
   (`tests/test_multilanguage_audit.py` `-07`..`-09`) enumerates over `LANGUAGE_BY_SUFFIX` so language
   #11 cannot escape unpinned, and its companion `_YIELDS_DEFINITIONS` table pins the `DF-10-2-A`
   shortfall in both directions (a language starting to extract definitions fails as loudly as one
   regressing) — both parametrized suites independently re-run and green. The spec-claim guard's glob
   behavior (dotfile inclusion) was independently verified in a separate Python invocation rather than
   trusted from the docstring. No existing test was found deleted, skipped, or `xfail`-marked anywhere
   in the diff (`git diff` searched for removed `def test_` lines and skip/xfail markers — none found).
   The golden cache key was regenerated (old/new hash both visible in the diff) with a documented
   rationale tied to the `CACHE_KEY_SCHEMA_VERSION` bump; the `("grammar_version", …)` sensitivity leg
   at the pre-existing line is confirmed still present, with a `grammar_versions` sibling added beside
   it, not in place of it.

4. **Engineering-principle check.** `except (ImportError, Exception)` confirmed structurally unchanged
   (moved `:266`→`:294` as the dev recorded) and correctly left to Story 10.4 — not touching it here is
   the right call, not a leaky hand-off: AC3's own §A.2 finding proves this codepath's failure mode
   (`getattr` returning `None`) never reaches that `except` at all, so splitting the tuple would not
   have closed this story's defect and widening scope to do it anyway would have been scope creep.
   `GrammarProvenance`'s placement in `cache/key.py` (pure) rather than a new `argus/shared/` module is
   a deliberate, justified trade against AC8.5's fenced write set, and avoids re-litigating the exact
   four-copies duplication `source_languages.py` was created to end — good SRP/DRY judgement, not
   premature abstraction. The declarative entry-point map (data, not an `if`-chain) is the right shape
   for the problem and matches the codebase's existing precedent.

No decision-needed, patch, or defer items are outstanding. Two pre-existing, correctly-out-of-scope
observations are noted for context, not filed as findings: the `except (ImportError, Exception)` tuple
redundancy (Story 10.4's, confirmed untouched) and `DF-10-2-A`'s `target_story: NONE` (compliant with
AI-E9-8 via its named owner and explicit rationale, but worth a human's attention when Engineering Lead
next triages the ledger).

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

| # | Decision | Why |
|---|---|---|
| **DN-1** | The site list is **12 to amend + 2 exempt**, measured on this tree — **not** the epic's 10, **not** the earlier 7 or 4 | §A.1. All three prior enumerations were hand-counted and all three were wrong. Architecture `:89-90` and `:800` are genuine V2/Python-only scope claims that every prior count missed. |
| **DN-2** | `architecture.md:471` and `:766` are **EXEMPT, named, with the reason in the guard** | They are **true** statements about the default install. Amending them would write a falsehood. NFR-P3 packaging is **Story 12.5's** open decision. Named-not-silent follows 10.1's DN-5. |
| **DN-3** | **This story fixes the TypeScript/PHP entry-point resolution** (AC3) rather than writing "8 of 10" into FR7 | §A.2. AC1 amends the **binding** capability contract. Writing an untrue capability claim into FR7 manufactures Story 10.5's defect class inside the story closing its inverse — and in the *oversell* direction, which the ledger notes the original defect was not. The fix is a declarative map; measured blast radius on this repo is **zero** (0 tracked `.ts/.tsx/.mts/.cts/.php` files). **Fallback if it proves non-trivial: record the measured 8/10 in the specs, name the two languages, and FILE them (AC8.2) — never a silent 10.** |
| **DN-4** | **AC2 (the closure guard), not AC1, is the load-bearing AC** | The epic's own second AC says the count has been wrong twice; measurement makes it three. A hand-list closes today's instance; only the guard closes the class. If time is short, AC2 ships before AC1's last site. |
| **DN-5** | Provenance is **ADDITIVE**: new per-grammar field, `grammar_version` retained, `schema_version` bumped | PRD `:393`'s additive-only schema-evolution policy. What gets fixed is the **description**, which currently implies the scalar is the index's provenance (§D). |
| **DN-6** | Only grammars **that actually parsed** are folded into the key | Folding every *installed* grammar makes the key a function of the **host**, not the **audit** — a determinism regression (NFR-D1/AR4) and the inverse defect. Pinned in both directions (AC5.2). |
| **DN-7** | `CACHE_KEY_SCHEMA_VERSION` **is bumped now**, `"2"` → `"3"` | Measured §C.1: no production caller derives a key; no persisted entry exists to migrate. The architecture reserved this exact moment. After 12.3 it costs a migration. |
| **DN-8** | The store is **NOT wired**, and that is a **positive AC** (AC6), not an omission | Epic AC + `architecture.md:330-345`. Wiring first persists a key wrong for 9 of 10 languages. |
| **DN-9** | `epics.md` is **not in the write set** | 10.1's AC5 fenced it to two locations; Epics 11-13 are 2026-08-10b's. Its stale 10.2 line numbers (§B.1) are **recorded here**, not corrected there. |
| **DN-10** | New test ids: **`TC-ArgusAgent-INTAKE-003-07…`** (grounding matrix — extends the file that already owns the multi-language end-to-end claim), **`TC-ArgusAgent-INDEX-001-105…`** (provenance), **`TC-ArgusAgent-CACHE-001-76…`** (key), **`TC-ArgusAgent-DOCS-001-24…`** (spec-claim guard) | Measured maxima on this tree: INTAKE-003 = `-06`, INDEX-001 = `-104`, CACHE-001 = `-75`, DOCS-001 = `-23` (`-17b`/`-21b` are suffixed variants, not free slots). |

### Architecture patterns & constraints a reviewer will check

- **AR4 / NFR-D1 determinism** — sorted, order-independent, no float, no dict-iteration reliance. The
  per-grammar record is a **sorted frozen tuple**, folded sorted into the closure payload.
- **AR8 purity** — `cache/key.py` is PURE (no I/O, no clock, no `importlib.metadata`). **Version
  resolution happens in the impure `ast_index` shell and is *passed in*.** Reading package metadata
  inside `key.py` would breach the module's stated contract and is a review rejection.
- **AR10 honest degradation** — a missing grammar stays `ast_eligible=False` with a reason token, never
  an exception and never a fabricated parse. AC3 makes *more* files eligible; it must not make any file
  eligible that did not genuinely parse.
- **AR11 sorted output** — index entries, definitions, edges, and now the provenance record.
- **§3.4 evidence immutability** — strike, never delete; append, never rewrite. Exemplars at
  `architecture.md:428-433` and `deferred-work.md:520`.
- **NFR-M1 ≤1200 lines/module** — applies to your new test files too. `ast_index.py` is 368 and
  `key.py` 304, so both have room. Breached **only** by `argus/pipeline.py` at 1331 — **Story 12.1's,
  fenced, do not add a line.**
- **Additive-only schema evolution** — new fields only, `schema_version` bumped, determinism preserved.
- **No `print()` in library code; typed exceptions at the impure shell.**

### Runtime & toolchain, verified on this machine 2026-08-10

| | |
|---|---|
| Python | **3.11.15** (CI matrix: 3.10 / 3.11 / 3.12, ubuntu) |
| Tests collected | **1235** (summed per-file, this tree) |
| `tree-sitter` runtime | pinned `>=0.25.0,<0.26` — the upper bound is **load-bearing** (Story 11.4) |
| Grammars installed | all 10; versions in §A.3 range **0.23.1 → 0.25.0** |
| `[languages]` extra | `pyproject.toml:47-56`, pinned `>=0.23.0,<0.26` |
| Local vs. CI | `mypy` local 2.3.0 vs. CI `>=1.0`; **if they disagree the EXECUTED CI RUN is the evidence** |

**No new dependency.** Every grammar this story reaches is already declared in `[languages]` and already
installed. Adding a package here would be rejected at review.

### Testing standards — the house form your new files must match

```bash
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q                  # whole suite
python -m pytest tests/test_multilanguage_audit.py -v              # matrix
python -m pytest tests/test_ast_index.py tests/test_cache_key.py -v
python -m mypy argus
python -m pytest --cov=argus --cov-report=term-missing --cov-fail-under=80
```

- **`PYTHONIOENCODING=utf-8` is not optional on this Windows host,** and every file you read must be
  opened `encoding="utf-8"` **explicitly**. The artifact tree contains `~~`, `⚠️`, `🚩`, `café` and
  Cyrillic. `Path.read_text()` without it inherits the host locale — the exact class behind commits
  `d0e0a5c`/`ebdca75` that turned CI run `31322881580` red while every local run was green.
- **Naming:** `test_TC_ArgusAgent_<AREA>_<NNN>_<nn>_<snake_case_claim>()`, with the `TC-…` id on the
  docstring's first line and the story + AC on the second.
- **Every assertion carries a failure message naming the offending language / file / sentence.** A
  matrix test whose failure reads `assert eligible` costs the next reader an hour.
- **The spec guard is pure `pathlib` + `re` over committed markdown** — no network, no subprocess, no
  YAML dependency (10.1's precedent). It must run identically on all three CI legs.
- **The grounding-matrix test writes only to `tmp_path`** and must not require `.argus/` state.

### Previous story intelligence — Story 10.1 (done, PASS iteration 1)

- **10.1's binding output is a STANDARD, not a number.** `architecture.md:438-443` + `:599-602`, guarded
  by `tests/test_evidence_citation.py` (`TC-ArgusAgent-DOCS-001-20..-23`). Run `31341363300` covers
  `00c8d1b` **only** and cannot evidence your tree (AC8.4).
- **Its guard shape is the template for AC2**: registry + glob closure + sentence-scoped scan + positive
  control both directions + non-vacuity. Copy the form; the corpus and the pattern differ.
- **Its D2 lesson matters for AC2.2**: 10.1 measured its corpus *before* writing the detector and
  narrowed the pattern, because a too-wide phrase list fires on the project's own meta-discussion (this
  story file is full of the phrase *"multi-language … V2"*) and produces a guard that cries wolf and
  gets deleted. **Story files and change proposals are not in AC2's corpus** — scan `E-PRD/*.md` and
  `architecture.md` only, and say so.
- **Its D3/D4 lesson is T3's shape**: the RED demonstration was repeated after the test code changed,
  and all documents were restored **byte-identically, verified by sha256 round-trip**.
- **10.1's delta is uncommitted** — see the frontmatter. Your `git diff HEAD` includes it.

### Recent git context

`00c8d1b` is a merge of `fix/honest-verdict-reporting`; the six commits behind it
(`d0e0a5c`, `ebdca75`, `f7c666e`, `266bb28`, `f85fe76`, `40c0727`) are all **host-portability**
defects — non-ASCII paths, POSIX-vs-Windows containment, surrogate repair — **invisible on this Windows
host and fatal on the ubuntu runner.** Your AC3 work touches file reading and `importlib` in exactly
that neighbourhood. Anything you assert from a local run inherits that blind spot, which is why AC8.3
makes you label local results as local.

### Project structure notes

- Tests are **flat under `tests/`**; `tests/apaa/` no longer exists (Epic 9). Architecture prose still
  saying `tests/apaa/` or `apaa/store/canonical.py` is stale — read it as `tests/` and `argus/`.
- Planning artifacts: `_bmad-output/design-artifacts/ArgusAgent/`; the PRD is under `E-PRD/prd.md`
  (**not** at the artifact root — the workflow's default `{planning_artifacts}/prd.md` does not exist).
- Stories live in `stories/`, **not** at the artifact root.

### Open questions for the operator — saved for the end, as the workflow requires

1. **§A.2 is a NEW finding and is not in the epic's AC as written.** It has been folded into **AC3**
   with **DN-3** because AC1 cannot be discharged truthfully without it. If you would rather the
   TypeScript/PHP loader fix were its own story — leaving 10.2 to write "8 of 10" into FR7 and file the
   remainder — say so **before dev starts**; the fallback path is written into DN-3.
2. **§A.1 makes the enumeration wrong for the third time.** The story treats AC2's guard as the real
   remedy (DN-4). If the intent was to freeze the 10-site list as an approved scope boundary rather
   than to correct every true instance, say so — but note that a frozen list is what failed twice.
3. **AC5 bumps `CACHE_KEY_SCHEMA_VERSION`.** Free today (§C.1) and sanctioned by the architecture, but
   it is a contract constant. Flagged rather than assumed.

### References

- Epic + ACs — [epics.md:1830-1871](../epics.md) (Story 10.2) · [epics.md:1738-1790](../epics.md)
  (Epic 10 preamble, dependency flow, the 2026-08-10 citation audit)
- Ledger entry — [deferred-work.md:1394-1414](../deferred-work.md) (`DF-AUD-APAA-D`)
- Corrected enumeration + the V2 sweep — [sprint-change-proposal-2026-08-10b.md §1.4(a), §1.5](../sprint-change-proposal-2026-08-10b.md)
- The change that shipped the capability — [sprint-change-proposal-2026-07-28.md:18](../sprint-change-proposal-2026-07-28.md)
- R3 cache-key contract — [architecture.md:83-88](../architecture.md) ·
  [architecture.md:246-249](../architecture.md) · [architecture.md:327-345](../architecture.md)
- 10.1's citation rule — [architecture.md:438-443](../architecture.md) ·
  [architecture.md:599-602](../architecture.md) · [tests/test_evidence_citation.py](../../../../tests/test_evidence_citation.py)
- Sibling story (house style, `done`) — [stories/10-1-release-status-must-cite-evidence.md](10-1-release-status-must-cite-evidence.md)
- Code under change — [argus/index/ast_index.py](../../../../argus/index/ast_index.py) ·
  [argus/cache/key.py](../../../../argus/cache/key.py) ·
  [argus/shared/source_languages.py](../../../../argus/shared/source_languages.py)
- The near-miss test (trap E.4) — [tests/test_multilanguage_audit.py](../../../../tests/test_multilanguage_audit.py)
- Sibling defect class — `DF-5-1-A` (silent cache staleness) · `DF-AUD-APAA-F` / Story 10.4 (grammar
  diagnosis) · Story 10.5 (the inverse: a spec with no capability)
- Downstream dependant — [epics.md:2240](../epics.md) (Story 12.3 memoization wiring)

---

## Dev Agent Record

### Context Reference

This story file. Every figure in it was measured on this tree on 2026-08-10 and is re-derivable by the
commands in §A and T1 — **re-derive, do not transcribe.** Where a measurement disagrees with this
document, **the tree wins**: record the divergence and proceed from the measurement.

### Agent Model Used

`claude-opus-5[1m]` (BMAD `dev-story`, unattended loop worker), 2026-08-10.

### Debug Log References

#### T1 — re-measurement (every §A figure re-derived; the tree agreed with the document everywhere)

| Measurement | Story says | Measured | Verdict |
|---|---|---|---|
| PRD claim sites | 8 at `:23 :121 :193 :214 :364 :438 :469 :571` | **identical, all 8, same lines** | ✅ no drift |
| Architecture claim sites | 6 hits → 4 amend + 2 exempt (`:89 :267 :317 :800`; `:471 :766`) | **identical** | ✅ no drift |
| Ten-language grounding | `eligible 8 / 10`, `a.ts`/`a.php` → `grammar_missing_*` | **8 / 10, same two, same tokens** | ✅ confirmed |
| Per-grammar versions | python/js/go 0.25.0 · rust/c 0.24.2 · php 0.24.1 · java 0.23.5 · cpp 0.23.4 · ts 0.23.2 · ruby 0.23.1 | **identical, all ten** | ✅ confirmed |
| Grammar exports | `tree_sitter_typescript` → `language_typescript`,`language_tsx`; `tree_sitter_php` → `language_php`,`language_php_only`; **neither exports `language`** | **identical** | ✅ confirmed |
| Store wiring | unwired; `pipeline.py` imports neither | **confirmed** — only `cache/invalidation.py` + `audit/deep_audit.py` reference them | ✅ bump is free |
| `.ts/.tsx/.mts/.cts/.php` tracked | 0 | **0** | ✅ zero blast radius |
| Tests collected | 1235 | **1235** | ✅ baseline confirmed |
| Runtime | py 3.11.15, tree-sitter 0.25.2 | **identical** | ✅ |

**No divergence to record.** Every number in §A–§C held. The one thing the document could not predict is
in the Completion Notes: a *further* finding one level below §A.2 (`DF-10-2-A`).

#### T3 — the three RED demonstrations, before any fix (trap E.1 / AI-E3-1)

**RED 1 — grounding matrix vs. the UNFIXED loader** (`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`):

```
FAILED tests/test_multilanguage_audit.py::test_every_claimed_language_actually_grounds[sample.php]
FAILED tests/test_multilanguage_audit.py::test_every_claimed_language_actually_grounds[sample.ts]
FAILED tests/test_multilanguage_audit.py::test_every_claimed_language_actually_grounds[sample.tsx]
E  AssertionError: php (sample.php) did NOT ground: ast_eligible=False,
   parse_failure_reason='grammar_missing_php'. The grammar package `tree_sitter_php` IS importable
   in this environment, so a `grammar_missing_php` token here is a MISDIAGNOSIS…
E  AssertionError: typescript (sample.ts) did NOT ground: ast_eligible=False,
   parse_failure_reason='grammar_missing_typescript'…
E  AssertionError: typescript (sample.tsx) did NOT ground: ast_eligible=False,
   parse_failure_reason='grammar_missing_typescript'…
```

Fails naming **exactly `typescript` and `php`** (AC3.5), with the other eight green.

**RED 2 — claim-shape guard vs. the UNAMENDED specs.** `-24` failed naming **all 12** surviving sites
and no others; `-26` (glob closure + reasoned, *exercised* exemptions) passed, proving the two
exemptions were live rather than decorative; `-27` failed because no amendment existed yet:

```
E  [deferral]          E-PRD/prd.md: durablemoat: '…ast-grounded depth [python v1, multi-language v2]…'
E  [deferral]          E-PRD/prd.md: `audited_deep` requires a **grounded claim … ast** (python in v1; multi-language in v2)…
E  [deferral]          E-PRD/prd.md: …python = impl #1 — so v2 multi-language is additive, not a core rewrite.
E  [deferral]          E-PRD/prd.md: …· **multi-language** ast grounding · **mutation-grade** vacuous-test detect…
E  [python-only-scope] E-PRD/prd.md: **stack-agnostic** by construction (v1 deep ast-grounding = python, …)
E  [deferral]          E-PRD/prd.md: …python-only ast → stack-agnostic validator interface (v2 multi-language additive)…
E  [python-only-scope] E-PRD/prd.md: - **fr7:** … validate a deep claim against source structure (python ast in v1)…
E  [python-only-scope] E-PRD/prd.md: - **nfr-p2:** … (deep ast-grounding = python in v1; `claim_emitted` proxy elsewhere)…
E  [python-only-scope] architecture.md: - **stack:** python 3.11+ …; ast = python in v1 (`claim_emitted` proxy elsewhere)…
E  [deferral]          architecture.md: **deferred (post-v1):** multi-language ast, seam auditor, …
E  [python-only-scope] architecture.md: - **stack detection** via `cloc`/`radon` + tree-sitter; v1 deep = python only, …
E  [deferral]          architecture.md: - **future enhancement:** multi-language ast (v2), seam auditor (v2), …
```

⚠️ **RED 2 was re-run after the test code changed (10.1's D4).** The FIRST RED found only **11** of the
12 — `architecture.md:317` escaped, because *"V1 deep = Python only"* contains no `ast` / `grounding`
word at all, only `deep` and `tree-sitter`. **The guard's own positive control (`-25`) caught the miss**,
since that line is planted there verbatim. `_GROUNDING_TERMS` gained `deep` and `tree-sitter`, and the
listing above is the re-run with the SHIPPED code. Worth recording plainly: the site enumeration was
about to be wrong a *fourth* time, inside the story written to stop that, and only the positive control
caught it — which is DN-4's whole argument, demonstrated live.

**RED 3 — the cache-key defect, reproduced against the SHIPPED code.** Writing the test first produced
only an `ImportError`, which proves nothing about the defect, so the defect itself was executed:

```
CACHE_KEY_SCHEMA_VERSION (unbumped) = '2'
AstIndex has per-grammar provenance field: False
Closure has per-grammar provenance field: False
parsed languages: python+go+rust; recorded grammar_version = '0.25.0'   <-- tree-sitter-python's
key with go 0.25.0 = 5e7d9351e8f0d4fd…
key with go 0.26.0 = 5e7d9351e8f0d4fd…
DEFECT REPRODUCED — key MOVED: False
```

A Go grammar upgrade is *unrepresentable* in the old closure, so the key cannot move. `-77` is now green
over exactly that, and `-78` pins the inverse.

#### RED-demonstration integrity: no document was mutated

AC2.6 anticipates mutating documents to force the RED and restoring them byte-identically. **That was
not necessary**: the specifications were *already* in the unamended state, so RED 2 was a read-only run
against the tree as found. The two corpus documents this story never amends are byte-identical to their
pre-work state, verified by sha256 round-trip:

| File | sha256 before | sha256 after | |
|---|---|---|---|
| `E-PRD/addendum.md` | `2dd50d85…4bb610` | `2dd50d85…4bb610` | ✅ unchanged |
| `E-PRD/.memlog.md` | `f2b3c3e4…dd0c9c` | `f2b3c3e4…dd0c9c` | ✅ unchanged |

(Both show `| 2 +-` under `git diff --stat` — that is 10.1's pre-existing uncommitted delta, not this
story's. The hash equality is the proof, exactly as the frontmatter warned `git diff HEAD` would not be.)

### Completion Notes List

**Baseline honesty.** Built on top of 10.1's uncommitted delta, as the frontmatter warned. `git diff` at
HEAD spans both; this story's own delta is the twelve files in the File List below, and mtimes plus
sha256 separate them where the diff cannot (`epics.md` last written 11:39, this session wrote from
14:3x onward).

**AC1 — 12 sites amended, 2 exempt.** Each amendment strikes the replaced wording (`~~…~~`) rather than
deleting it, is dated `2026-08-10`, and is attributed to `sprint-change-proposal-2026-07-28.md`. FR7 and
NFR-P2 point at `argus/shared/source_languages.py` as the source of truth instead of restating a
language list — trap E.5, where AI-E9-7/R1 watched a prose copy of a pinned figure drift at five sites.
No amended sentence asserts a count. The V2 roadmap, `Deferred (post-V1)` and `Future enhancement` lists
drop multi-language **only**; every sibling item is byte-untouched.

**AC2 is the one that will still be working next year.** `tests/test_spec_claim_scope.py`
(`TC-ArgusAgent-DOCS-001-24`..`-27`) resolves the corpus by glob (`E-PRD/*.md` + `architecture.md`),
matches the claim as a *pattern* over heading-scoped sentence units, and refuses to be quiet: it fails
if it scans nothing, if a glob finds an unregistered file, if an exemption lacks a ≥20-word reason, or
if an exemption stops matching anything real. Three design notes worth a reviewer's attention:

1. **Two rules, not one.** The AC describes the V2-deferral shape. Measurement showed half the sites
   carry **no V2 marker at all** (`AST = Python in V1`), so there is a second rule for the
   Python-only-scope shape. A guard written only to the AC's letter would have passed over five sites.
2. **Heading context.** `prd.md:214` sits under `### Growth Features (V2)` and the line itself never
   says "V2". Units therefore carry their nearest heading for *marker* lookup only — never for claim
   terms, which would manufacture hits.
3. **Line-aware unit splitting**, unlike 10.1's paragraph splitter. These documents are dense markdown
   tables; collapsing a ten-row table into one unit lets a grounding term in one row pair with a
   Python-only term in another and invent a claim no sentence makes.

The guard fired on my own first draft of the `prd.md:214` amendment note (a sentence naming
`test_multilanguage_audit.py` under a `(V2)` heading). That is the intended behaviour and the note was
reworded, not the guard. Its only escape hatch is the literal phrase AC1 requires — so an amendment that
quiets the guard is an amendment that satisfies the AC.

**AC3 — DN-3 taken, fallback not needed. 8/10 → 10/10, and `.tsx` delivered in full.** Grammar loading
resolves a per-language entry point from a declarative map (`_ENTRY_POINT_BY_LANGUAGE`) with a
suffix-level override (`_ENTRY_POINT_BY_SUFFIX`, `.tsx → language_tsx`), `language` remaining the
default so eight grammars need no entry at all. The parser cache is re-keyed `(language, entry_point)`,
which is what lets `.ts` and `.tsx` — one language, two dialects — coexist; AC3.2 anticipated this might
not be expressible without widening scope, and it was, in one tuple. `except (ImportError, Exception)`
is structurally **untouched** (fence F / Story 10.4); it moved from `:266` to `:294`, so 10.4 should
re-locate by anchor. `_get_parser_for_lang` gained a *defaulted* second parameter, so its signature is
source-compatible. Verified: **11/11 fixtures ground**, dogfood verdict byte-identical.

**🚩 NEW FINDING, one level below §A.2 — filed as `DF-10-2-A`, not fixed.** With the loader fixed, C,
C++, Ruby and Rust ground cleanly and extract **zero definitions**: C/C++ carry a `function_definition`'s
name under the `declarator` field rather than `name`; Ruby's method node is `method`, absent from
`_DEF_KIND_BY_NODE`; Rust's is `function_item` where the map says `fn_item`. A file in those four parses
and is graded but has no function or class for the depth gate to stand on, so it **cannot reach
`audited_deep`** — a real limit on what "multi-language grounding" buys a consumer, and the same
adjacent-capability gap as §A.2 one layer deeper. **Deliberately filed rather than fixed:** AC3's fence
says *"this is a grammar-resolution fix"*, and widening the definition vocabulary changes which files
reach `audited_deep` in any polyglot repo — a capability change owing its own ACs and cartridges, not a
line smuggled into a specification-correction story. I found it because an over-strong assertion in my
own first draft of the matrix test failed; rather than delete the signal, it is pinned **in both
directions** by `TC-ArgusAgent-INTAKE-003-09` (a language starting to extract definitions fails just as
loudly as one stopping), disclosed in FR7's measured-shortfall bullet and in the README limits
paragraph, and filed with an owner. FR7 therefore claims exactly what `-08` and `-09` measure.

**AC4/AC5 — additive, and the honest half of the design change.** `GrammarProvenance` is defined in the
**pure** `cache/key.py` and imported by the impure `index/ast_index.py` shell, never the reverse: version
resolution stays in the shell (`_package_version`) and resolved strings are passed in, so AR8 holds and
`key.py` still imports no `importlib.metadata`. *Rejected alternative:* a new `argus/shared/` module
would have been the tidier home, but AC8.5's write-set table forbids new files outside it, and
duplicating the model is the four-copies defect `source_languages.py` exists to prevent — so one
definition, imported, in the module that owns the determinism contract. Only grammars that **parsed**
are recorded (DN-6), including when the parse degraded, because a `syntax_error` is as much a function
of the grammar version as a clean parse. A duplicate language is a typed error at construction.
`grammar_version` is retained with its description corrected to what it always actually was;
`AstIndex.schema_version` `1→2`, `CACHE_KEY_SCHEMA_VERSION` `2→3`. **The golden key was regenerated** —
the one thing here a reviewer should check hardest — as the documented intentional invalidation the
constant's own comment reserves for a schema bump; the regeneration is recorded in the test docstring
and in `key.py`'s bump comment. No existing test was deleted, skipped or relaxed; the
`("grammar_version", …)` sensitivity leg stays and gained a `grammar_versions` sibling.

**AC6 — not wiring, as a positive act.** `argus/pipeline.py` is byte-unchanged (`git status` does not
list it), the §C.1 grep names only `cache/invalidation.py` and `audit/deep_audit.py`, and
`architecture.md` §C now records that step 1 is done, step 2 is 12.3's, and the grep is the fence.

**AC7 — no claim exceeds the matrix.** README gains an install section for the `[languages]` extra with
a two-column table of what a missing grammar does to a file's grade, the enumerable-≠-deeply-auditable
boundary, and the `DF-10-2-A` limits paragraph. CHANGELOG gains three `## Unreleased` entries. Registering
those three in `test_release_surface_honesty.py::_NOTE_SECTIONS` was required by an existing
enumerated-space guard (`DOCS-001-16`) — that guard doing its job, not a workaround.

**AC8 — and the part that is NOT established.** `DF-AUD-APAA-D` closed append-only (`+257 / −0`), with
both new findings recorded and its own wrong site-count left byte-intact as evidence. Gates re-run
**LOCALLY** — see below. **Release/CI status for this tree: NOT ESTABLISHED.** No `audit-ci.yml` run
covers it; run ids are sha-scoped and `31341363300` covers `00c8d1b` only, which is not this tree. No
push, no tag, no `workflow_dispatch` was performed (DN-7). The command a human runs to establish it:
push this branch and read the `audit-ci.yml` run for the resulting sha across all three legs
(3.10/3.11/3.12, ubuntu). **This host is Windows/3.11.15, and the six commits behind HEAD are all
host-portability defects invisible here and fatal on the runner** — so the local figures below are
necessary and explicitly not sufficient.

**LOCAL gate results (Windows, py 3.11.15, 2026-08-10) — necessary, NOT sufficient:**

| Gate | Result |
|---|---|
| `mypy argus` | **Success: no issues found in 71 source files** |
| `bandit -r argus --severity-level medium` | **0 Medium, 0 High** (18 Low, unchanged) |
| `pytest tests/` (`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`) | **1272 collected, 1272 passed, 0 failed, 0 skipped** |
| Coverage | **95.06%** (`--cov-fail-under=80` satisfied) |
| Collection delta | **1235 → 1272 = +37**, exactly the new cases; none removed, skipped or weakened |
| Dogfood verdict | `RELEASE_READY deep_ratio=30/79 blocking_findings=0 assessed_deep_ratio=15/19 scope=application held_out=82` — **byte-identical before and after** (AC3.6) |

The +37 reconciles exactly: 4 spec-guard · 23 multi-language (1 closure + 11 matrix + 11 structure pin) ·
3 provenance · 5 cache-key · 2 new parametrize legs on the existing sensitivity matrices.

**Fences verified, not assumed.** `argus/pipeline.py`, `epics.md`, `.github/workflows/audit-ci.yml` and
every Epic 1-9 artifact are unmodified (`git status` + mtimes: `epics.md` 11:39, `pipeline.py` and
`audit-ci.yml` 04:43, all pre-session). `architecture.md:471`/`:766` are unamended and named in the
guard's exemption table with the recorded reason. No new dependency.

**The three non-blocking operator questions, and the assumption taken on each:**

1. **§A.2 folded into AC3 (DN-3), not split into its own story.** Taken as written: FR7 is the binding
   contract and writing "delivered in V1" over an untrue 8/10 would manufacture Story 10.5's defect in
   the oversell direction. The fix was two data tables; the fallback ("record 8/10 and file the two")
   was not needed and is now moot.
2. **AC2's guard treated as the remedy, not a frozen 10-site list (DN-4).** Vindicated during the run —
   the enumeration was about to be wrong a fourth time and the guard's positive control caught it.
3. **`CACHE_KEY_SCHEMA_VERSION` bumped.** The §C.1 licensing measurement was re-verified before bumping:
   no production caller derives a key, so the cost was one constant plus a regenerated golden.

### File List

| Path | Why | AC |
|---|---|---|
| `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` | 8 scope-claim sites amended (incl. FR7, NFR-P2); V2 roadmap note | AC1 |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | 4 scope-claim sites amended; R3 design change at 3 sites; AC6 ordering note | AC1, AC5.3, AC6 |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | `DF-AUD-APAA-D` append-only closure (+257/−0); new `DF-10-2-A` | AC8.1, AC8.2 |
| `README.md` | `[languages]` extra: install, languages, coverage consequence, measured limits | AC7.1, AC7.3, AC7.4 |
| `CHANGELOG.md` | three `## Unreleased` entries in the file's honesty register | AC7.2 |
| `argus/index/ast_index.py` | per-language entry-point map + `.tsx` override; `(lang, entry_point)` parser cache; per-grammar provenance; `schema_version` 1→2 | AC3, AC4 |
| `argus/cache/key.py` | `GrammarProvenance`; closure field + sorted fold + duplicate validator; `CACHE_KEY_SCHEMA_VERSION` 2→3 | AC5 |
| `argus/audit/deep_audit.py` | defaulted `grammar_versions` passthrough — compatibility only, no wiring | AC5.5 |
| `tests/test_spec_claim_scope.py` | **NEW** — the closure guard, `TC-ArgusAgent-DOCS-001-24`..`-27` | AC2 |
| `tests/test_multilanguage_audit.py` | `TC-ArgusAgent-INTAKE-003-07`..`-09` — fixture closure, grounding matrix, structure pin | AC3 |
| `tests/test_ast_index.py` | `TC-ArgusAgent-INDEX-001-105`..`-107` — provenance, both directions, additive schema | AC4 |
| `tests/test_cache_key.py` | `TC-ArgusAgent-CACHE-001-76`..`-80`; perturbation matrix extended; golden regenerated | AC5 |
| `tests/test_release_surface_honesty.py` | registered the 3 new CHANGELOG sections in `_NOTE_SECTIONS` (existing enumerated-space guard) | AC7.2 |
| `_bmad-output/design-artifacts/ArgusAgent/stories/10-2-…md` | this file (untracked → `git add`ed, per the frontmatter's AI-E8-1 warning) | process |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | `10-2-… : review` + dated annotation | process |

**Not modified, deliberately:** `argus/pipeline.py` (fence F / 12.1 — AC6 makes this positive),
`epics.md` (DN-9), `.github/workflows/audit-ci.yml`, `architecture.md:471`/`:766` (12.5 / NFR-P3),
`E-PRD/addendum.md` and `E-PRD/.memlog.md` (sha256-verified above), every Epic 1-9 artifact.

### Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-10 | 0.1 | Story contexted from `epics.md` Story 10.2 + `DF-AUD-APAA-D`, with the site enumeration, the 8/10 grounding measurement and the per-grammar version spread measured live on this tree. Status → `ready-for-dev`. | Scrum Master (`bmad-create-story`) |
| 2026-08-10 | 1.0 | **Implemented.** All 10 tasks, all 8 ACs. §A re-measured and confirmed with zero divergence. **AC1:** 12 sites amended (PRD ×8, architecture ×4), struck-not-deleted, dated, attributed; `:471`/`:766` exempt by name. **AC2:** `tests/test_spec_claim_scope.py` (`DOCS-001-24`..`-27`) — registry + glob closure + two-rule pattern + heading context + positive control both ways + non-vacuity + exercised, reasoned exemptions; demonstrated RED naming all 12, re-run RED after the detector was widened (its own control caught a 12th-site miss — the enumeration was about to be wrong a fourth time). **AC3 (DN-3):** per-language entry-point map + `.tsx` suffix override; **8/10 → 10/10**, `.tsx` delivered in full; `except (ImportError, Exception)` structurally untouched (moved `:266`→`:294`). **AC4/AC5:** per-grammar provenance, additive (`grammar_version` retained + description corrected), `AstIndex.schema_version` 1→2, `CACHE_KEY_SCHEMA_VERSION` 2→3, golden regenerated as a documented intentional invalidation; only grammars that parsed are folded, pinned both directions. **AC6:** store NOT wired, `pipeline.py` byte-unchanged, ordering recorded. **AC7:** README + CHANGELOG document the extra and its measured limits. **AC8:** `DF-AUD-APAA-D` closed append-only (+257/−0); **new `DF-10-2-A` filed** — C/C++/Ruby/Rust ground but extract zero definitions, out of AC3's fence, pinned both directions by `INTAKE-003-09`. LOCAL gates: mypy 0/71, bandit 0 Med/0 High, **1235 → 1272 collected, all pass, 0 skipped**, coverage 95.06%; dogfood verdict byte-identical. **CI status NOT ESTABLISHED** — no run covers this tree and none was manufactured (DN-7). Status → `review`. | Dev Agent (`bmad-dev-story`, `claude-opus-5[1m]`) |
