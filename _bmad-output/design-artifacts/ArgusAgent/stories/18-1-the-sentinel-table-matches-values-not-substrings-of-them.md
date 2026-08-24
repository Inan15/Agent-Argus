---
baseline_commit: 7a3cc7c
---

# Story 18.1: The sentinel table matches values, not substrings of them

Status: review

<!-- Contexted 2026-08-24 at HEAD `7a3cc7c` (branch `docs/merge-strategy-decision`) by the
     create-story workflow (Opus 5).

     ⛔ EVERY FIGURE IN §0 WAS READ OFF THIS TREE BY EXECUTION, not copied from `epics.md`,
     from `sprint-change-proposal-2026-08-24.md`, from `DF-AUD-DETECT-A` or from the
     `sprint-status.yaml` comment. The three-line reproduction was re-run through the shipped
     `SecretScanDetector.run()`; the candidate repair was applied IN MEMORY and the whole
     secret-detector test population plus a 250-file sweep of this repository's own tracked
     Python was re-measured under it. Where an artifact and the tree disagree, §0 says so and
     THE TREE WINS.

     ⛔ NO `argus/`, `tests/`, `scripts/` OR ARTIFACT FILE WAS TOUCHED TO PRODUCE THIS STORY.
     Every simulation was monkeypatching of module attributes inside a throwaway interpreter
     driven from a scratch directory outside the repository. `git status --porcelain` was
     clean at contexting and is clean now, apart from this file.

     ⛔ THIS IS THE FIRST STORY OF EPIC 18 AND EPIC 18 RUNS BEFORE EPIC 17. Epic numbers are
     CREATION order in this repository; execution order is stated, never inferred from the
     number. Nothing in Epic 17 depends on this story and this story must not be used to
     delay it.

     ⛔ NOTHING HERE SPENDS `DF-13-5-A`. No member is ratified, no protocol row is added, no
     FR is amended, no third-party source is fetched. -->

## Story

As the **Engineering Lead**,
I want **the public-sentinel suppression to match a VALUE rather than appear anywhere inside one, and the Live-Key Safeguard to stop disabling itself on the same string**,
so that **a real credential is not silently dropped because its host happens to be named `localhost`.**

### What this story IS

The discharge of **`DF-AUD-DETECT-A`** — a **live security false negative** in shipped code, in
the **under-reporting → correct** direction.

Two lines of `argus/detectors/secret_suppression.py` decide it:

- `:120` — `if sentinel in snippet_clean` inside `is_public_sentinel`, over a table (`:61`) five
  of whose eight members are shorter than 20 characters (`localhost` 9, `127.0.0.1` 9,
  `example.com` / `.org` / `.net` 11).
- `:130–:132` — the identical `if sentinel in snippet: return False` short-circuit inside
  `is_live_production_key`, which makes the **Live-Key Safeguard disable itself on the same
  string** that step 2 already matched.

The story replaces containment with a **bounded match that cannot fire on a substring of a larger
secret**, removes the safeguard's short-circuit, commits the audit's own three-line reproduction
(**including the control**) as a guard proven RED before and GREEN after, and records the
falsification of `DF-10-3-B`'s safety claim as a dated append-only note.

### What it is NOT

- ⛔ **NOT a redesign of `--ignore-pattern`.** `pat in snippet` at `:222` is **`DF-10-3-C`**, it is
  OPEN, it is architecture §G's *accepted* residual risk, and this story does not touch it, narrow
  it, anchor it or disposition it.
- ⛔ **NOT a change to the evaluation ORDER.** Steps 1–5 in `evaluate_suppression` are the security
  property (Story 10.3 / AC4.1). The order is byte-unchanged and `TC-ArgusAgent-SECRET-001-15`..
  `-22` are re-run **unedited** to prove it.
- ⛔ **NOT a widening or narrowing of the sentinel TABLE.** All eight members stay. None is added.
  ⛔ In particular `AKIAIOSFODNN7EXAMPLE` is **NOT** added — see §0.8/(c), where the measured fact
  that `is_live_production_key`'s own docstring names a sentinel the table does not contain is
  recorded rather than "fixed" by widening suppression.
- ⛔ **NOT a change to `argus/detectors/secret_scan.py`.** The dead `self._evidence_for(match)` at
  `:506` is **`DF-AUD-DETECT-B` / Story 18.2**; the two regex precision defects are
  **`DF-AUD-DETECT-E` / Story 18.3**; the `Detector` Protocol is **`DF-AUD-DETECT-F` / Story 18.4**.
  Touching any of them here steals a later story's RED.
- ⛔ **NOT a disclosure feature.** `DF-10-3-B`'s actual subject — that built-in suppressions are not
  reported — is **untouched and stays OPEN**. Only its *safety claim* is falsified, by note.
- ⛔ **NOT a verdict move.** Every `hardcoded_secret` finding is built `advisory=True,
  depth_supported=None` (`secret_scan.py:509`, `:516`), so it is non-blocking **by construction**.
  The gate stays `BLOCKED`, the ≥80% precision keystone stays **NOT CLEARED**, and nothing in this
  story clears, softens or re-scopes it.
- ⛔ **NOT an epic-16-or-earlier reopening.** Epics 1–16 are `done`. `Story 6.2`'s closed record is
  not edited. `Story 2.5`'s and `Story 10.3`'s records are not edited.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `7a3cc7c`

⛔ **Task 0 re-derives every row below before a line is written.** Five consecutive epics in this
repository found a stated premise false by executing it. The figures here were true on
2026-08-24 on a Windows host; **they are a baseline to re-measure, not a fact to cite.**

### §0.0 The tree, the paths and the baseline

| fact | value at contexting |
|---|---|
| repo root | `d:/ProjectX/XAgents/XAgents/ArgusAgent` |
| HEAD | `7a3cc7c73f356f85444fd37c7c2d67880a86bfeb` (`7a3cc7c`) |
| branch | `docs/merge-strategy-decision` |
| last commit touching `argus/` | `3183e2a` — `feat(16-7): derive the silent test class…` |
| `git status --porcelain` | **empty** |
| python | 3.11.15 (MSC v.1944, 64-bit) |
| tests collected under `tests/` | **1,716** (without `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`) |
| full suite | **green, 0 failures** at contexting |
| `argus/detectors/secret_suppression.py` | **231** lines (NFR-M1 ceiling 1,200) |
| `argus/detectors/secret_scan.py` | **575** lines — ⛔ NOT touched by this story |
| `tests/test_secret_suppression.py` | 103 lines |
| `tests/test_secret_suppression_recording.py` | 276 lines |
| `tests/test_secret_scan.py` / `_precision.py` | 222 / 121 lines |
| the four secret test modules together | **53 passed** |

⚠️ **`tests/test_secret_containment.py` cannot be collected on its own** — `from _cartridge import
stage_cartridge` resolves only when the whole `tests/` directory is collected. Measured at HEAD,
**with and without this story's change**: it is a pre-existing property of the file, not something
you broke. Run it as `python -m pytest tests/ -q`, never as a single-file invocation.

⛔ **`AI-E13-1` — the local suite is Windows-only and CI runs an ubuntu matrix.** A green local run
is recorded as **LOCAL** and never on its own discharges a cross-platform claim. This project has
already shipped POSIX-only defects off a green Windows run.

### §0.1 ⛔ THE DEFECT REPRODUCES EXACTLY — 0 / 0 / 1, through the shipped `run()`

Re-executed at HEAD `7a3cc7c` on a **non-test path** (`argus/prod/settings.py`), each line audited
alone, through `SecretScanDetector().run(...)`:

```
DATABASE_URL  = "postgres://admin:Tr0ub4dor3@localhost:5432/prod"   -> 0 findings
SMTP_PASSWORD = "aBcD1234EfGh5678@example.com"                      -> 0 findings
DATABASE_URL  = "postgres://admin:Tr0ub4dor3@dbhost:5432/prod"      -> 1 hardcoded_secret   [CONTROL]
```

`DF-AUD-DETECT-A`'s three rows reproduce **exactly**. The control — the same value with the
sentinel substring removed — **is** reported, which is what makes the first two a false negative
rather than a policy.

The per-match detail, which the entry does not carry and the guard needs:

| line | pattern_id extracted | value length | `evaluate_suppression` |
|---|---|---:|---|
| `localhost` | `high_entropy_string` | 47 | `(True, 'known_sentinel')` |
| `example.com` | `generic_assigned_secret` | 28 | `(True, 'known_sentinel')` |
| `example.com` | `high_entropy_string` | 28 | `(True, 'known_sentinel')` |
| CONTROL | `high_entropy_string` | 44 | `(False, None)` |

⛔ **The `example.com` line yields TWO matches, not one.** `run()` de-duplicates on
`(start_line, end_line, pattern_id)` (`secret_scan.py:439`), and the two patterns differ, so after
the repair that line reports **2** findings. **Write the guard as `>= 1` per line, not `== 1`** —
see `DN-18-1-5`.

### §0.2 The mechanism, read against the source — every citation resolves

- `KNOWN_PUBLIC_SENTINELS` (`secret_suppression.py:61`) — eight members, **measured lengths**:
  `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` **40** · `0123456789abcdef0123456789abcdef01234567`
  **40** · `xoxb-123456789012-1234567890123-example` **39** · `example.com` / `example.org` /
  `example.net` **11** · `127.0.0.1` **9** · `localhost` **9**.
- `is_public_sentinel` (`:116`) strips, then tests `sentinel in snippet_clean` (`:120`).
- It is consulted at **step 2** (`:210`), **above** the Live-Key Safeguard at **step 3** (`:217`).
- `is_live_production_key` (`:125`) carries the same short-circuit at `:130–:132`, so the safeguard
  returns `False` on any snippet containing any sentinel — **it disables itself on the same string**.
- The only production caller is `secret_scan.py:451`, which passes `snippet=match.value` — the
  **extracted value**, never a source line.

⚠️ **Nothing pins the current behaviour.** A grep over `tests/` finds **no** `is_public_sentinel`
call and **no** `KNOWN_PUBLIC_SENTINELS` reference at all. The containment semantics are neither
asserted nor an accepted cost; they are **unexamined**. That is why this story's guard is the
deliverable and not a footnote.

### §0.3 ⛔ THE LIVE-KEY HALF — 7 of 7 today, 0 of 7 after. Structural, not probable.

Enumerating the values that **genuinely match a `LIVE_KEY_PATTERNS` member** *and* contain one of
the five short sentinels (a `ghp_` body is `[A-Za-z0-9_]{36}`, so it can carry `localhost` but not
`example.com`; a Slack token's tail is `[a-zA-Z0-9]{24,32}`; the PEM pattern is a `search`, so any
sentinel anywhere in the snippet reaches it; `AKIA[0-9A-Z]{16}` is upper-case-and-digits and can
carry none of them):

| | cells | safeguard DISABLED | `evaluate_suppression` says SUPPRESSED |
|---|---:|---:|---:|
| **shipped (`7a3cc7c`)** | 7 | **7** | **7** |
| **candidate repair** | 7 | **0** | **0** |

⛔ **This is `DF-10-3-B`'s falsification, executed.** That entry states *"no live production key can
be suppressed by any of these paths except an explicit inline annotation, which is reviewable in the
diff."* Measured here: **seven can**, and none of the seven involves an operator flag or an
annotation.

End-to-end through `run()` on `argus/prod/settings.py`, as `API_TOKEN = "<value>"`:

| value shape carrying `localhost` | shipped | repaired |
|---|---:|---:|
| `ghp_` + 36-char body | **0** | **1** |
| `xoxb-…-` + 24-char tail | **0** | **2** |
| `-----BEGIN RSA PRIVATE KEY-----localhost` | 1 | 2 |

⚠️ **State the probability rather than suppressing it, because it cuts both ways** (the entry's own
discipline). A GitHub PAT body is effectively random base62, so containing that exact nine-character
run is astronomically unlikely — **the live-key half is structural, not probable.** What IS probable
is the `generic_assigned_secret` / `high_entropy_string` half of §0.1, where the value is an
operator-authored connection string and `localhost` / `example.com` are among the commonest
substrings such a value can carry. **The story rests on the probable half; `DF-10-3-B`'s wording
rests on the improbable one, and that is exactly why the wording has to move.**

### §0.4 ⛔ THE BLAST RADIUS OVER THIS REPOSITORY'S OWN SOURCE — measured, not argued

`SecretScanDetector().run()` driven over **every file in `git ls-files -- '*.py'`** (250 files) at
HEAD, counting `hardcoded_secret` findings, shipped vs repaired:

| | findings | files |
|---|---:|---:|
| shipped | **86** | 36 |
| repaired | **87** | 36 |
| **LOST (a finding that disappears)** | **0** | — |
| **newly reported** | **1** | 1 |

⛔ **The one new finding is `tests/test_deep_pass_wiring.py:397`**, and it is worth reading:

```python
"https://user:sup3rs3cret@api.example.com/v1/chat?key=AKIAIOSFODNN7EXAMPLE",
```

Two patterns hit that span. The `aws_access_key_id` match (`AKIAIOSFODNN7EXAMPLE`, 20 chars)
**already reports today** — it contains no sentinel, and step 3 lets it through. The
`high_entropy_string` match is the **whole 73-character URL**, which contains `example.com`, so
today step 2 answers `(True, 'known_sentinel')` and the URL — embedded credential and all — is
dropped. After the repair the URL is no longer a sentinel by value, and because it now genuinely
matches `AKIA[0-9A-Z]{16}` the safeguard reports it at step 3.

⛔ **DO NOT MAKE THIS ONE GO AWAY.** It is a synthetic literal in a test file, the line is *already*
flagged today by the sibling pattern, and the finding is `advisory=True, depth_supported=None` — not
verdict-eligible. **Editing, annotating or relocating that line to keep the count at 86 is exactly
the assertion-loosening move `DF-8-5-B` forbids.** Disclose it in the completion notes with its
cause. If you believe it must be suppressed, that is **AC8**, an escalation.

### §0.5 ⛔ THREE CANDIDATE REPAIRS, ALL THREE EXECUTED — and one of them breaks a shipped test

Each variant was applied in memory and the four secret test modules (**53 tests**) re-run:

| variant | what it does | result |
|---|---|---|
| **A — length-gated match** ✅ SELECTED | sentinels **< 20 chars** matched by **exact equality** of `snippet.strip()`; sentinels **≥ 20 chars** keep containment; safeguard short-circuit **removed** | **53 passed** |
| **B — equality for ALL eight** | `snippet.strip() in frozenset(TABLE)`; short-circuit removed | ⛔ **1 FAILED** |
| **C — short-circuit removal ALONE** | `is_live_production_key` loses `:130–:132`; `is_public_sentinel` unchanged | 53 passed — but **does not fix §0.1**: the value still matches at step 2 and never reaches step 3 |

⛔ **VARIANT A WAS ALSO RUN OVER THE WHOLE SUITE, NOT JUST THE FOUR SECRET MODULES.**
`python -m pytest tests/ -q` with the repair applied in memory: **exit 0, zero failures**, over the
same 1,716-test population that is green at HEAD. **So the repair is not expected to cost you a
single existing assertion** — if one goes red, it is either yours or a genuine finding, and neither
is a licence to loosen it (AC4.4).

⛔ **Variant B's single failure is the crux of this story, so read it rather than route around it.**

```
tests/test_secret_suppression.py::test_public_sentinel_suppression
    snippet = 'MOCK_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
>   assert suppressed is True
E   assert False is True
```

That test passes a **whole assignment line** as `snippet`. The only production caller
(`secret_scan.py:451`) passes **`match.value`**. So the existing test asserts a *line*-shaped
semantic that the shipped pipeline never exercises — and pure equality would break it while fixing
nothing about the real defect.

⛔ **Variant A keeps that test valid ON ITS OWN TERMS** — a 39-to-40-character published credential
cannot be an *accidental* substring of anything — while removing the only mechanism the defect uses.
It is also literally what `DF-AUD-DETECT-A` proposes: *"exact comparison against a `frozenset` …
keeping containment — if wanted — only for the three full-length published keys, whose length makes
accidental containment impossible."* See `DN-18-1-1`.

⚠️ Variant A is also **O(1)** for the five short values instead of the present
O(table × snippet) scan. That is a side effect, not a justification, and **`DF-AUD-DETECT-C`
(detector cost) is NOT dispositioned by it.**

### §0.6 ⛔ ONE GUARD GOES RED THE MOMENT `argus/` MOVES, AND IT FORCES THE COMMIT ARC

**`TC-ArgusAgent-DOGFOOD-001-50`** (`tests/test_dogfood_artifact_currency.py:174`) fails as soon as
`argus/**` moves past the sha the three committed dogfood artifacts cite. This story changes
`argus/detectors/secret_suppression.py`, so **it will fire.** Story 16.6 spent a whole unplanned
commit on exactly this (`6304552`).

⛔ **`scripts/regenerate_dogfood_artifacts.py` REFUSES to run on a dirty `argus/` tree** (exit **2**,
`:73`, `:118`). So the ordering is forced: **commit `argus/` + `tests/` FIRST, then regenerate, then
commit the three artifacts separately.** A commit cannot cite itself. That is why AC7.2's arc is
**four** commits.

The three registered artifacts (`_CURRENT_ARTIFACTS`, `:84`): `minions-dogfood-partition-plan.md`,
`minions-dogfood-budget-plan.md`, `minions-dogfood-proof.md`. ⛔
`minions-dogfood-proof-story-7-2-superseded.md` is a **`_PRESERVED_RECORD`** and must never be
regenerated.

⛔ **`TC-ArgusAgent-DOCS-001-78` (`tests/test_governance_record_integrity.py:196`) WILL FIRE ON
YOUR OWN COMPLETION NOTES IF YOU GET THE COMMIT ORDER WRONG — measured, by this story reddening it.**
It extracts every `DF-*` id a **committed story file** claims to have CLOSED (line-scoped;
`_CLOSURE_VERB` matches `CLOSED` / `Closes` / `closes` / `Closed by this story`, and `_NEGATED`
exempts *"not closed"* and friends) and cross-checks `deferred-work.md`. **The moment this file
records a closure disposition for the entry, the ledger must already carry it.** AC7.2's
`docs` commit therefore carries **the ledger append and the story record together, ledger first in
the diff** — or you split them and take a RED between two commits.
⚠️ This story file was deliberately written to make **no** closure claim, so contexting leaves the
guard green. Verify that before you start: `python -m pytest
tests/test_governance_record_integrity.py -q`.

**Guards that do NOT fire, verified so you do not chase them:**

- `TC-ArgusAgent-RELEASE-001-11` (import-reach registry) and `-20` (built-distribution import) fire
  on **adding a file under `argus/`**. This story adds none — it edits one existing module.
- `tests/test_status_document_registry.py::_STATUS_DOCUMENTS` — `stories/` is in
  **`_EXCLUDED_BY_DESIGN`** (`:349`–`:350`). ⛔ **This story file must NOT be registered there**, and
  neither must the new test module: that registry governs planning records, not code.
- `tests/test_dogfood_proof.py:908`'s `| 2289 |` pins the **preserved Story-7.2 Minions** record,
  read from a committed artifact. It is not a live re-derivation and this change cannot move it.
- `tests/test_gate_seal.py::_ADJUDICATION_SETS` — this story produces no adjudication set. Leave it
  at two.
- `tests/test_command_assets.py`'s markdown publishing corpus (`-06`, `-11`) closes over
  `git ls-files`, but **`_bmad-output/` and `tests/` are both declared `_NON_PUBLISHING_PREFIXES`**
  (`:95`), so neither this story file nor the new test module enters it. Verified at HEAD.

### §0.7 The ledger's byte state, and the next free ids — both measured

- `deferred-work.md` is **537,063 bytes**, **LF-only**: 0 CRLF, 6,945 lone LF, and **exactly ONE
  lone `\r`, at byte 407,906 (line 5,371)**, which is *content* — a literal `` `\r` `` inside a
  backtick span discussing line endings. ⛔ **Edit it in BINARY MODE.** A Windows text-mode write
  rewrites all 6,945 newlines to CRLF *and* eats that CR, producing a 7,000-line diff over a
  three-line append.
- ⚠️ **This story file, `epics.md` and `sprint-status.yaml` are CRLF.** They are not the same
  file class as the ledger. Do not "normalise" either direction.
- **Next free verification id: `TC-ArgusAgent-SECRET-001-23`.** Measured — the SECRET index is
  continuous `-03`..`-22` and `-22` is the maximum. **CONTINUE it; renumbering anything invalidates
  citations in `architecture.md` and `deferred-work.md`.**
- **No new `DF-*` entry is expected.** ⛔ **Grep the ledger before filing anything** — 124 declared
  entries, and it already knows about the sentinel table (`DF-AUD-DETECT-A`), the disclosure gap
  (`DF-10-3-B`), the `--ignore-pattern` semantics (`DF-10-3-C`) and the detector cost
  (`DF-AUD-DETECT-C`). Cite prior art rather than re-file. `DF-INV-LEDGER-A` exists because someone
  filed as new what this ledger had recorded the day before.

### §0.8 What is already true and must NOT be re-done — plus one thing found while measuring

**(a)** The evaluation order was already repaired by **Story 10.3 / AC4.1**, and
`TC-ArgusAgent-SECRET-001-15`..`-22` already pin it, including the whole `LIVE_KEY_PATTERNS` space
against the whole hostile-pattern space. **Re-run them; do not rewrite them.**

**(b)** `fnmatchcase` (never bare `fnmatch`) is already the host-invariance discipline, with the
reason recorded at `secret_suppression.py:50`–`:58`. It is `--ignore-path`'s business, not this
story's, and it stays.

**(c)** ⛔ **FOUND WHILE MEASURING, RECORDED, NOT FIXED HERE.** `is_live_production_key`'s docstring
(`:128`) says *"Excludes known public sentinels (e.g. `AKIAIOSFODNN7EXAMPLE`)"*. **Measured:
`AKIAIOSFODNN7EXAMPLE` is not in `KNOWN_PUBLIC_SENTINELS` and never has been** — the table holds the
AWS *secret* key `wJalrXUt…`, not the AWS *access-key id*. So the docstring names an exclusion the
code does not implement, and this repository reports the canonical AWS documentation key as a live
key today (that is the `aws_access_key_id` half of §0.4's `test_deep_pass_wiring.py:397` line).
⛔ **The remedy is to CORRECT THE DOCSTRING when the short-circuit it describes is deleted — NOT to
add `AKIAIOSFODNN7EXAMPLE` to the table.** Adding it widens suppression, which is the opposite of
this story's direction. Greped: `deferred-work.md` contains **zero** occurrences of that string, so
if you judge the false positive worth an entry, it is genuinely new — but it is `AI-E9-8`-owned by
the Engineering Lead, not by this story, and 18.3 is the precision story.

---

## §1 — WHY THIS STORY EXISTS

### §1.1 A real credential is dropped today, with no disclosure

This is the only one of Epic 18's four stories where something real is lost right now. `run()`
returns **zero findings** for a production connection string carrying a live password, and the
report that follows says nothing at all — not "suppressed", not "known sentinel". A reader cannot
distinguish *clean* from *quiet*, which architecture §G names as precisely the threat the
suppression model exists to address.

### §1.2 The safeguard that was supposed to be the backstop is disabled by the same string

Story 10.3 moved the Live-Key Safeguard above both operator flags and made that the module's stated
security property. §0.3 measures the hole it does not cover: the safeguard's own body short-circuits
on the same sentinel table, so for **7 of 7** enumerable live-key-shaped values carrying a short
sentinel, the backstop is not merely bypassed — **it declines to fire.**

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **Built-in suppressions are still not disclosed.** `DF-10-3-B`'s real subject survives this story
  and stays OPEN. A repaired sentinel test is still a *silent* test.
- **`--ignore-pattern` is still a bare substring** (`DF-10-3-C`, OPEN, accepted in architecture §G).
- **`run()` still discards the evidence it computes** (`DF-AUD-DETECT-B` → Story 18.2).
- **The two regex precision defects are still there** (`DF-AUD-DETECT-E` → Story 18.3).
- **The ≥80% precision keystone is still NOT CLEARED and the gate is still `BLOCKED`.**

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ The existing test asserts a semantic the production caller never uses

`tests/test_secret_suppression.py::test_public_sentinel_suppression` passes a **line**;
`secret_scan.py:451` passes a **value**. §0.5 measured that pure equality breaks the first and
nothing else. **Do not resolve this by editing that test.** Variant A satisfies both, and the story
additionally pins the value-shaped call so the ambiguity is asserted rather than inherited.

### §2.2 ⛔ The order is the security property. Do not touch it.

Steps 1–5 of `evaluate_suppression` (`:205`–`:230`) and the module docstring that states them stay
**byte-unchanged in their ordering**. This story changes what step 2 *decides*, never *where it
sits*, and deletes the self-disabling short-circuit *inside* step 3's predicate. `-15`..`-22` are the
proof and they are re-run unedited.

### §2.3 ⛔ Guard vacuity — this project's signature defect, and this story's version

`AI-E14-1` / trap E.1: Story 3.4's keystone test was green over its own keystone bug, and 16.3's own
mutation run caught one of its guards unreal. **This story's specific version:** a guard that asserts
"the localhost line is reported" but builds its input in a way that never reaches the suppression
engine — e.g. running it on a `tests/**` path, where step 5's `DEFAULT_TEST_PATH_PATTERNS` suppresses
it for an entirely different reason and the assertion says nothing.

⛔ **Every case runs on a NON-TEST path** (`argus/prod/settings.py`), and `AI-E11-1` applies: assert
the population is non-empty before asserting anything about it.

### §2.4 ⛔ Host invariance — never `lower()`, never `casefold()`

`NFR-P1` requires byte-identical output across hosts, and `secret_suppression.py:50`–`:58` records
why: a host-dependent match means the same repository at the same commit reports a credential on
Linux and hides it on Windows. The equality compare must be plain `str.__eq__`. ⛔ **Case-insensitive
matching WIDENS suppression** and is an escalation, not a convenience.

### §2.5 ⛔ The commit arc is FORCED, and it is four commits

Because of §0.6: `chore` (this story file + `in-progress`) → `feat` (`argus/` + `tests/`) → `chore`
(regenerate the three dogfood artifacts on a **clean** `argus/` tree) → `docs` (ledger + this
story's record). ⛔ **A commit cannot cite itself**, and the regeneration script exits 2 on a dirty
`argus/`.

⛔ **`DF-INV-MERGE-A` (OPEN, DECIDED-NOT-YET-APPLIED).** Squash and rebase merging orphan the
provenance sha a regenerated dogfood artifact cites, and `TC-ArgusAgent-DOGFOOD-001-49` then reddens
**`master`, after the merge, where no PR check can see it coming**. This story regenerates dogfood
artifacts on a branch, which is the exact hazard shape. **If the PR lands sha-rewritten, re-run
`python scripts/regenerate_dogfood_artifacts.py` on `master` and commit the result.**

### §2.6 ⛔ The working tree is SHARED, and one artifact file has a byte invariant

- **A concurrent session commits to this same branch.** ⛔ **Stage by EXPLICIT PATH. Never
  `git add -A`, never `git add .`.** Verify the write set with `git status --porcelain` — **not**
  `git diff --name-only`, which cannot see the new untracked test module.
- **`deferred-work.md` is LF-only with one content `\r`** (§0.7). ⛔ **Binary-mode edits only.**

### §2.7 The idioms the guard needs, so you do not go looking for them

- ⛔ **`run()` is PURE and never opens the file.** `file_path` is a *string used for path-glob
  matching and locators only*. **`argus/prod/settings.py` does not exist and must not be created** —
  it is chosen because it is a plausible non-test path that `DEFAULT_TEST_PATH_PATTERNS` does not
  match, which is precisely what §2.3 requires.
- The entry the detector needs is constructed directly, no tree-sitter:
  `AstIndexEntry(file_path=<same string>, ast_eligible=True, definitions=())`
  (`argus.index.ast_index`). This is the `tests/test_secret_scan.py::_entry` precedent.
- Findings are counted as `[f for f in result.findings if f.rule_id == RULE_HARDCODED_SECRET]`;
  locators are `f.locators[0].start_line`. ⛔ **De-duplication is on
  `(start_line, end_line, pattern_id)`**, so one source line can legitimately yield more than one
  finding (`DN-18-1-5`).
- Test function names follow the area convention exactly:
  `def test_TC_ArgusAgent_SECRET_001_23_<snake_case_claim>() -> None:` — the id is *in the function
  name*, which is how `tests/conftest.py`'s guard-fire recorder attributes a RED.
- Non-blocking-ness is proven with `blocking_finding_count` / `is_verdict_blocking` from
  `argus.verdict.verdict_gate` (the `-22` precedent).

---

## §3 — AC ↔ TASK MAP

*(There to be checked, not trusted. Every AC is named by at least one task; every task cites the AC
it discharges. Stories 16.5 and 16.6 each failed a readiness validation where an AC was repaired on
one side of the file and its mirror left defective in the task list.)*

| AC | discharged by |
|---|---|
| AC1 — bounded sentinel match | Task 2, Task 3 |
| AC2 — safeguard stops disabling itself | Task 2, Task 3, Task 5 |
| AC3 — three-line reproduction, RED→GREEN, control included | Task 3, Task 4 |
| AC4 — nothing is lost; direction is under-report→correct | Task 1, Task 5 |
| AC5.6 — `architecture.md` is not edited | Task 6, Task 8 |
| AC5 — the ledger records closure + falsification | Task 6 |
| AC6 — scope, paths, portability, ceilings | Tasks 2, 3, 7 |
| AC7 — gates, dogfood regeneration, commit arc | Task 7, Task 8 |
| AC8 — escalate, do not decide | all tasks |

---

## Acceptance Criteria

### AC1 — THE SENTINEL TEST CANNOT FIRE ON A SUBSTRING OF A LARGER SECRET

- **AC1.1** — `is_public_sentinel` no longer answers `True` for a snippet that merely **contains** a
  sentinel shorter than `MIN_CONTAINMENT_SENTINEL_LENGTH` (**20**). Short sentinels match by
  **exact equality of `snippet.strip()`**; the three published full-length credentials (39–40 chars)
  keep containment, because a value that long cannot be an accidental substring.
- **AC1.2** — the table is expressed as **two named, non-overlapping constants** whose union is
  **byte-equal, and order-equal, to today's `KNOWN_PUBLIC_SENTINELS`**, and
  `KNOWN_PUBLIC_SENTINELS` **remains exported** as that union (NFR-M2, additive-only: it is a
  module-level public name and something may read it).
- **AC1.3** — ⛔ **AN INVARIANT GUARD MAKES THE DEFECT UNABLE TO RECUR BY A TABLE EDIT:** every
  member of the containment table is `>= MIN_CONTAINMENT_SENTINEL_LENGTH`, every member of the
  equality table is `<` it, the two are disjoint, and their union equals `KNOWN_PUBLIC_SENTINELS`.
  A future contributor who adds a short sentinel to the wrong table gets a RED, not a silent
  reopening of `DF-AUD-DETECT-A`.
- **AC1.4** — ⛔ **NO SUPPRESSION IS LOST.** All **eight** members, passed **alone**, still return
  `(True, 'known_sentinel')` from `evaluate_suppression`. Measured true today and required after.
- **AC1.5** — the signature, name, purity and return type of `is_public_sentinel` are unchanged; it
  stays a `@staticmethod` on `SecretSuppressionEngine` (AR8: no I/O, no clock, no network).

### AC2 — THE LIVE-KEY SAFEGUARD CAN NO LONGER DISABLE ITSELF

- **AC2.1** — the `for sentinel in KNOWN_PUBLIC_SENTINELS: if sentinel in snippet: return False`
  short-circuit at `secret_suppression.py:130`–`:132` is **REMOVED**.
- **AC2.2** — its docstring (`:126`–`:129`) is **corrected, not merely trimmed**: §0.8/(c) measured
  that its example `AKIAIOSFODNN7EXAMPLE` is **not in the table**. The replacement text must state
  what the function now does — match `LIVE_KEY_PATTERNS`, full stop — and must not claim an
  exclusion that does not exist.
- **AC2.3** — for the enumerated set of values that genuinely match a `LIVE_KEY_PATTERNS` member and
  carry a short sentinel (**7 cells** at HEAD, §0.3), `is_live_production_key` returns `True` for
  **all** of them and `evaluate_suppression` suppresses **none** of them. The guard **enumerates the
  space**, mirroring `-15`'s discipline (trap E.2: every Epic-8 guard was narrower than its own AC).
- **AC2.4** — the three published full-length sentinels are still answered at **step 2** and never
  reach step 3, so removing the short-circuit does not start reporting a documented non-secret.
- **AC2.5** — ⛔ **THE ORDER IS UNCHANGED.** Steps 1–5 keep their positions and their reason tokens.
  `TC-ArgusAgent-SECRET-001-15`..`-22` are re-run **with no edit to any assertion, docstring or
  fixture in `tests/test_secret_suppression_recording.py`**, and pass.

### AC3 — THE AUDIT'S THREE-LINE REPRODUCTION IS A COMMITTED GUARD, RED BEFORE AND GREEN AFTER

- **AC3.1** — a new module `tests/test_secret_sentinel_matching.py` opens
  **`TC-ArgusAgent-SECRET-001-23`** and continues upward. ⛔ **CONTINUE the index; renumber nothing.**
  Its module docstring states the defect, the measurement and the RED evidence, in the register of
  `tests/test_secret_suppression_recording.py`.
- **AC3.2** — it carries **all three** audit lines verbatim, run through the shipped
  `SecretScanDetector.run()` on the **non-test path** `argus/prod/settings.py`, **each line alone**,
  and asserts `>= 1` `hardcoded_secret` finding for each — **including the CONTROL**, which must
  still be reported. ⛔ A repair that reports nothing, or that reports the two defect lines while
  losing the control, fails this AC.
- **AC3.3** — ⛔ **THE RED IS OBSERVED AND ITS EXACT TEXT RECORDED.** Drive it by reverting **only**
  the `argus/detectors/secret_suppression.py` change (`git stash` the source hunk, or run the guard
  against the pre-fix module) — **never** by weakening an assertion. Record the failure text and the
  restoration proof in the Dev Agent Record. Per the guard-fire rule (architecture, 2026-08-23) an
  author-driven RED is **vacuity evidence**, not "caught a real defect"; record it as such.
- **AC3.4** — `AI-E11-1`: every guard asserts its population is non-empty **before** asserting
  anything about it.
- **AC3.5** — every key value is **built in the module**; ⛔ **no secret is planted in a committed
  fixture file**, and no assertion is on a value — only on counts, rule ids and `(bool, reason)`
  tuples (the `-15`..`-22` precedent, NFR-S1/NFR-S2).
- **AC3.6** — the module additionally pins §0.5's crux: `is_public_sentinel` is asserted for **both**
  the value-shaped call (what `run()` makes) and the line-shaped call (what
  `test_public_sentinel_suppression` makes), so the two semantics are on the record instead of being
  inherited.

### AC4 — NOTHING IS LOST: THE CHANGE MOVES ONLY UNDER-REPORTING → CORRECT

- **AC4.1** — ⛔ **NO PRE-FIX FINDING DISAPPEARS.** Re-derive §0.4's sweep over
  `git ls-files -- '*.py'` at the story's own HEAD and record the pair. **The LOST set must be
  empty.** Baseline at `7a3cc7c`: **86 findings / 36 files → 87 / 36, LOST = 0, NEW = 1.**
- **AC4.2** — the newly reported finding(s) are **disclosed by path and cause** in the completion
  notes, and proven **not verdict-eligible** by running `blocking_finding_count` /
  `is_verdict_blocking` over them — proven, not asserted.
- **AC4.3** — ⛔ `tests/test_deep_pass_wiring.py:397` is **NOT edited, annotated, or relocated** to
  keep a count stable (§0.4, `DF-8-5-B`).
- **AC4.4** — the full suite is green at or above its baseline, with **no test's assertion
  loosened** to accommodate the change. If an existing test genuinely encodes the defect, that is
  **AC8**.

### AC5 — THE LEDGER RECORDS THE CLOSURE AND THE FALSIFICATION, APPEND-ONLY

- **AC5.1** — **`DF-AUD-DETECT-A`** gains a **dated append-only closure note** naming this story,
  the fix sha, the new guard ids and the measured before/after (§0.1, §0.3, §0.4). ⛔ **The original
  entry above it is NOT rewritten** (§3.4 evidence immutability — the `DF-1-3-A` note is the
  template).
- **AC5.2** — **`DF-10-3-B`** gains a **dated append-only FALSIFICATION note** quoting the falsified
  clause verbatim — *"no live production key can be suppressed by any of these paths except an
  explicit inline annotation"* — with §0.3's 7-of-7 measurement and the fact that the repair
  repairs it. ⛔ Its `id` / `owner` / `target_story` / `category` / `severity` lines are **not edited**, and
  the entry **stays OPEN**: its actual subject (built-in suppressions are not disclosed) is untouched
  by this story.
- **AC5.3** — ⛔ **`DF-10-3-C` is NOT dispositioned**, and neither are `DF-AUD-DETECT-B` / `-C` /
  `-D` / `-E` / `-F`. Naming one in prose without doing its work is the `AI-E12-3` defect.
- **AC5.4** — ⛔ **Binary-mode edit only.** Verify after writing: `deferred-work.md` still has **0**
  CRLF pairs and **exactly one** lone `\r`, and `git diff --stat` shows only the appended lines.
- **AC5.5** — ⛔ **Grep before filing.** Nothing new is filed unless the ledger provably does not
  already carry it; cite prior art instead (`DF-INV-LEDGER-A`).
- **AC5.6** — ⛔ **`architecture.md` is NOT edited.** Measured: §G's stated property — *"the
  Live-Key Safeguard … is now evaluated above both flags, so neither can suppress a high-confidence
  live production key"* — is a claim about the two **flags**, and it is true before and after. This
  change makes §G's promise *more* true, not different, and `sprint-change-proposal-2026-08-24.md`
  §2 records `architecture.md: None`. If you judge §G must move, that is **AC8**.

### AC6 — SCOPE, PATHS, PORTABILITY AND CEILINGS

- **AC6.1** — ⛔ **THE WRITE SET IS EXACTLY:**
  1. `argus/detectors/secret_suppression.py` — UPDATE
  2. `tests/test_secret_sentinel_matching.py` — NEW
  3. `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — APPEND-ONLY
  4. the three regenerated dogfood artifacts (`minions-dogfood-partition-plan.md`,
     `minions-dogfood-budget-plan.md`, `minions-dogfood-proof.md`) — by their own renderer only
  5. this story file
  6. `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — status transitions only

  ⛔ **`argus/detectors/secret_scan.py` is NOT in it.** ⛔ Neither is any file under
  `minions_core/apaa/` — that tree is dead; `argus/` is the only live one.
- **AC6.2** — NFR-M1: `secret_suppression.py` is 231 lines and must stay ≤ **1,200**; the new test
  module likewise. **Split, never shave, never exempt.**
- **AC6.3** — no new dependency, no new import beyond the standard library already in the module.
  AR8 purity preserved: no I/O, no clock, no randomness, no network on any decision path.
- **AC6.4** — NFR-P1 host invariance: plain `str.__eq__`. ⛔ **No `lower()` / `casefold()` /
  `re.IGNORECASE` anywhere in the sentinel path.**
- **AC6.5** — `AI-E13-1`: the local run is Windows-only and is recorded as **LOCAL**. The
  cross-platform claim is the CI ubuntu matrix's, and only after it is green at the pushed sha.
- **AC6.6** — ⛔ stage by **explicit path**; never `git add -A` / `git add .` (§2.6). Verify with
  `git status --porcelain`.

### AC7 — GATES, DOGFOOD REGENERATION AND THE COMMIT ARC

- **AC7.1** — green at the end, **every exit code recorded**: the full suite (`python -m pytest
  tests/ -q`, and again with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`), coverage
  `--cov-fail-under=80`, `mypy argus`, `bandit -r argus --severity-level medium`,
  `tests/test_module_size_ceiling.py`, `tests/test_release_preflight.py`,
  `tests/test_dogfood_artifact_currency.py`, `tests/test_governance_record_integrity.py`,
  `tests/test_gate_*.py`. ⛔ Run with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared — Story
  16.5's dev lost a commit to a **false RED from stale bytecode**.
- **AC7.2** — the commit arc is **four** commits, in this order, for §0.6's forced reason:
  **`chore`** (this story file + `sprint-status` → `in-progress`) → **`feat`** (`argus/` + `tests/`)
  → **`chore`** (regenerate the three dogfood artifacts on a clean `argus/`) → **`docs`** (ledger +
  this story's record). ⛔ Commit messages **pure ASCII** (`DF-16-6-F`).
- **AC7.3** — ⛔ `DF-INV-MERGE-A`: if the PR lands squashed or rebased, re-run
  `python scripts/regenerate_dogfood_artifacts.py` on `master` and commit, or
  `TC-ArgusAgent-DOGFOOD-001-49` reddens `master` after the fact.
- **AC7.4** — the final write set equals AC6.1 exactly, verified with `git status --porcelain`
  (**not** `git diff --name-only` — the new test module is untracked and `git diff` is blind to it).

### AC8 — ESCALATE, DO NOT DECIDE

⛔ **STOP and escalate — do not decide — if any of these becomes necessary:**

- a member must be **added to** or **removed from** `KNOWN_PUBLIC_SENTINELS` (including
  `AKIAIOSFODNN7EXAMPLE`, §0.8/(c));
- the match must become **case-insensitive**, or `MIN_CONTAINMENT_SENTINEL_LENGTH` must move off
  **20**;
- the **step order** in `evaluate_suppression` must change;
- any assertion in `tests/test_secret_suppression_recording.py` (`-15`..`-22`) must be edited;
- `argus/detectors/secret_scan.py` must be touched;
- `--ignore-pattern`'s matching semantics must change (`DF-10-3-C`);
- the `tests/test_deep_pass_wiring.py:397` finding must be suppressed, or **any** pre-fix finding
  disappears (AC4.1's LOST set is non-empty);
- the CONTROL line stops being reported;
- `architecture.md`, `E-PRD/prd.md`, `epics.md` or any `done` story's record must be edited;
- `DF-13-5-A` must be spent, a member ratified, a protocol row added, or an FR amended;
- a finding must become **verdict-eligible**, or a threshold must move;
- any `DN-*` must be reopened. ⛔ **A `DN-*` you disagree with is an escalation, not a story
  decision.**

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

- **`DN-18-1-1` — LENGTH-GATED MATCHING, NOT UNIFORM EQUALITY.** Sentinels `< 20` chars match by
  equality; `>= 20` keep containment.
  *Rejected: uniform equality for all eight.* Measured (§0.5, variant B): it breaks
  `test_public_sentinel_suppression`, which passes a whole assignment line, and fixing that would
  mean editing a shipped test to accommodate a change — the move this project forbids. It is also
  exactly the repair `DF-AUD-DETECT-A` itself proposes.
  *Rejected: removing the short sentinels from the table.* That is a behaviour change nobody asked
  for; `HOST = "localhost"` should still be suppressed, and AC1.4 requires it.
  *Rejected: a regex with word boundaries.* A third matching semantics in a module that already has
  two (`in`, `fnmatchcase`) is the AR7 fork this project has recorded four times.
- **`DN-18-1-2` — `KNOWN_PUBLIC_SENTINELS` SURVIVES AS THE UNION.** The two new tables are additive;
  the old public name keeps its exact value and order.
  *Rejected: renaming or deleting it.* NFR-M2 is additive-only, and a module-level public tuple is a
  contract even when the current reader count is one.
- **`DN-18-1-3` — THE INVARIANT GUARD IS PART OF THE DELIVERABLE (AC1.3).** Without it the repair is
  one careless table edit away from being undone silently — and §0.2 measured that **nothing** pins
  this behaviour today.
  *Rejected: a comment saying "keep short sentinels out of the containment table".* `AI-E14-1`: a
  rule that depends on someone reading a comment is a rule that will not run.
- **`DN-18-1-4` — A NEW TEST MODULE, NOT A SIXTH FUNCTION IN `test_secret_suppression.py`.** That
  file is 103 lines of un-numbered legacy cases with no verification ids; a `TC-`numbered guard
  belongs in a module that carries the measurement and the RED evidence, as `-15`..`-22` do.
  *Rejected: appending to `test_secret_suppression_recording.py`.* That module's subject is **Story
  10.3 / AC4 — an operator cannot defeat the safeguard from the command line.** This story's subject
  is the built-in table. One module, one subject.
- **`DN-18-1-5` — THE GUARD ASSERTS `>= 1` PER LINE, NOT AN EXACT COUNT.** Measured post-repair:
  **1 / 2 / 1** (§0.1 — the `example.com` line matches two patterns at one span). Exact counts are
  the honest thing to *record*; they are the brittle thing to *assert*, because **Story 18.3 is
  chartered to narrow these very regexes** and would redden this guard for the right reason.
  Record 1/2/1 in the completion notes; assert `>= 1`.
- **`DN-18-1-6` — THE NEW `test_deep_pass_wiring.py:397` FINDING IS DISCLOSED, NOT REMOVED**
  (§0.4, AC4.3). Suppressing an honest new finding to keep an arithmetic stable is `DF-8-5-B`'s
  forbidden move.
- **`DN-18-1-7` — `architecture.md` IS NOT EDITED** (AC5.6). §G's claim is about the two operator
  flags and stays true; the ledger is where a falsification is recorded, and this repository already
  carries three sites where an identical paragraph was duplicated into `architecture.md` and then
  had to be kept in sync.

### Locked decisions this story CITES rather than reopens

- **Story 10.3 / DN-5, DN-6, DN-7** — the two flags are not the same risk and do not take the same
  ruling; layering first, recording second.
- **Story 10.3 / AC4.5** — built-in suppressions emit **no** `operator_suppressed_secret` record.
  ⛔ This story must not start emitting one: that would move the finding count on runs that passed
  no flag, and it is `DF-10-3-B`'s scope, not this story's.
- **Story 2.5** — producer-side redaction is structural (no value field on `Recording` / `Locator` /
  `FindingDraft`). It holds regardless of this change.
- **architecture §G** — the suppression threat model, and `DF-10-3-C` as accepted residual risk.

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| entry | bearing |
|---|---|
| **`DF-AUD-DETECT-A`** | **THE SUBJECT.** This story is chartered to discharge it (AC5.1). Independently re-verified by execution before scheduling; §0.1/§0.3 reproduce it again. |
| **`DF-10-3-B`** | Its **safety claim** is falsified (AC5.2). ⛔ The entry itself **stays OPEN** — its subject is disclosure, which this story does not deliver. |
| **`DF-10-3-C`** | ⛔ OPEN, untouched, out of scope (AC5.3). |
| **`DF-AUD-DETECT-B` / `-E` / `-F`** | Stories 18.2 / 18.3 / 18.4. Do not pre-empt them. |
| **`DF-AUD-DETECT-C`** | ⛔ OPEN as **context only**, named on Story 17.3, **not** dispositioned by variant A's incidental O(1) improvement. |
| **`DF-AUD-DETECT-D`** | Story 17.3. Not this story. |
| **`DF-INV-MERGE-A`** | OPEN, DECIDED-NOT-YET-APPLIED. Governs how this PR may land (§2.5, AC7.3). |
| **`DF-INV-WHEEL-A`** | OPEN. The wheel packages gitignored `.argus/` output, so running Argus inside its own repo reddens `TC-ArgusAgent-DOCS-001-54`. If you hit that red, it is **not yours**. |
| **`DF-INV-REFS-A`** | OPEN. Six referenced ids do not resolve. Do not "fix" one in passing. |
| **`DF-13-5-A`** | ⛔ **OPEN and UNSPENT.** No member ratified, no protocol re-version, no FR amended. Nothing here spends it. |
| **`DF-8-5-B`** | *"Do not close it by loosening an assertion."* The standing rule over AC4.3 and AC8. |

### Dependencies — none are added, and that is a requirement

The change is inside a module whose imports are `re`, `pathlib.Path`, `typing.Sequence` and
`fnmatch.fnmatchcase`. **No new third-party package. No version pin moves.** ⛔ Nothing in this story
requires web research: there is no library API surface involved, the regexes are the repository's
own, and the credential shapes (`AKIA…`, `ghp_…`, `xox[baprs]-…`, PEM headers) are already
enumerated in `LIVE_KEY_PATTERNS` and pinned by `-15`.

### Standing rules (non-negotiable)

- **AR7** — one arithmetic, one vocabulary, never forked. Two spellings of "is this a known
  sentinel" is the same fork class this project has recorded four times.
- **AR8** — pure/impure separation. `secret_suppression.py` is PURE and stays PURE.
- **NFR-P1** — no clock, randomness, network or host-dependent comparison on any decision path.
- **NFR-S1 / NFR-S2** — no source byte, no secret value, no absolute host path in any artifact,
  message or test assertion.
- **NFR-M1** — 1,200 physical lines per module. **Split, never shave, never exempt.**
- **NFR-M2** — frozen, additive-only contracts.
- **`AI-E11-1`** — every guard asserts its population is non-empty **before** asserting anything
  about it.
- **`AI-E13-1`** — the local suite is Windows-only; CI runs an ubuntu matrix.
- **`AI-E12-3` / `AI-E12-6`** — *a disposition recorded in prose and not in the ledger is not a
  disposition.*
- **`AI-E14-1`** — an author-driven RED is vacuity evidence, not "this guard caught a defect".

### Previous-story intelligence

⛔ **This is story 1 of Epic 18; there is no previous story in this epic.** The relevant inheritance
is from the two stories that built what this one repairs, and from the Epic 16 arc that ran
immediately before.

1. **Story 2.5** (`2-5-hardcoded-secret-detector-producer-side-redaction.md`) built the detector and
   the redaction keystone. ⚠️ Its record at `:349` and `:613` describes `_evidence_for` as part of
   the `run()` flow — **which is `DF-AUD-DETECT-B`'s trap**: a reader checking the AC against the
   code finds a call that appears to satisfy it and does not. **That is Story 18.2's, not yours.**
2. **Story 10.3** built the order, the Live-Key Safeguard's promotion and `-15`..`-22`. Its own
   lesson, recorded in the test module's docstring: *"Every assertion here was run RED against the
   unfixed engine (trap E.1) … `-15` enumerates the whole `LIVE_KEY_PATTERNS` space rather than one
   sample (trap E.2)."* **Do both.**
3. **Epic 16's stories each found a stated premise false by executing it** — 16.4 found three, 16.6
   found two. §0 already carries one (§0.8/(c): a docstring naming a sentinel the table lacks).
   **Expect a second.**
4. **16.5's dev found the baseline RED when the story claimed GREEN**, costing a commit, and hit a
   **false RED from stale bytecode**. Task 0 exists for that.
5. **16.6 spent an entire unplanned commit on the dogfood regeneration.** §0.6 and §2.5 plan for it.
   **Four commits, not three.**
6. **Two commits, not one, when a sha must be cited** — a commit cannot cite itself.
7. **16.5 and 16.6 each failed an independent readiness validation, and every blocking defect was in
   the STORY TEXT** — most often an AC repaired on one side of the file with its mirror left live in
   the task list. **§3 is the map; check it rather than trust it.**

### Git intelligence

Recent arc (last 12 commits) is entirely **governance and planning** — `docs(gov)` and `docs(plan)`
— with the last `argus/` change at `3183e2a` (Story 16.7). So:

- **`argus/` is quiet.** Nothing is mid-flight in the detector tree; the three dogfood artifacts were
  last regenerated for 16.7 and cite a sha this story will move past.
- **The last four commits are the 2026-08-24 self-audit correcting its own record** — `9ae9d0e`
  withdrew three claims, `f5700f2` withdrew an attribution, `932cec9` filed `DF-INV-LEDGER-A`
  against a duplicate filing, `7a3cc7c` filed `DF-INV-MERGE-A`. **The culture this week is: measure,
  then withdraw what the measurement does not support.** Do that in your completion notes.
- Epic 16's commit shape is `chore(story + in-progress) → feat → chore(regenerate artifacts) →
  docs`. **This story's arc is identical** (§2.5), minus a split step (nothing needs splitting).
- ⚠️ `3a9e100` had to re-cite provenance *after a rebase-merge orphaned the old sha* — the lived
  instance of `DF-INV-MERGE-A`. AC7.3 is not theoretical.

### References

- [epics.md](../epics.md) — `## Epic 18` (line ~3609) and `### Story 18.1` (line ~3648). ⛔ Its
  *"AWAITING OPERATOR APPROVAL"* paragraph is **deliberately left as written** with the append-only
  approval note beneath it (§3.4 / the Epic 16 precedent). **It is not a blocker and must not be
  edited.**
- [sprint-change-proposal-2026-08-24.md](../sprint-change-proposal-2026-08-24.md) — §1 (the audit),
  §2 (impact: `prd.md` None, `architecture.md` None), §4 (Epic 18's four stories and the sequencing).
  **APPROVED 2026-08-24 by XAgent007 (Engineering Lead).**
- [deferred-work.md](../deferred-work.md) — `DF-AUD-DETECT-A` (§6270+), `DF-AUD-DETECT-B` (§6321+),
  `DF-10-3-B` / `DF-10-3-C` (§1772+), the Epic 17/18 scheduling table (§6479+), `DF-INV-MERGE-A`
  (tail). ⛔ **Line numbers drift; grep by id.**
- [architecture.md](../architecture.md) — §G *Security & Governance* (line ~570), the **Suppression
  threat model** and its `DF-10-3-B` / `DF-10-3-C` paragraph (~617). ⛔ **Read, do not edit**
  (AC5.6).
- [E-PRD/prd.md](../E-PRD/prd.md) — **FR11** (`:528`, detect hardcoded secrets and report them with
  the value redacted) and **FR28** (`:573`, redaction / no secret bytes in ledgers, evidence, logs,
  traces). ⛔ Neither is amended.
- `argus/detectors/secret_suppression.py` — the module under change. **Read the whole docstring
  (`:1`–`:42`) before touching a line**; it states the order as the security property.
- `argus/detectors/secret_scan.py:399`–`:520` — the only production caller. **Read; do not edit.**
- `tests/test_secret_suppression_recording.py` — `-15`..`-22`, and the register the new module
  should be written in. **Read; do not edit.**

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC3.4, AC4.1, AC7.1)

- [x] `git status --porcelain` — confirm clean (a peer session shares this branch). Record HEAD.
- [x] Clear `__pycache__`; export `PYTHONDONTWRITEBYTECODE=1`. **Story 16.5 lost a commit to a false
      RED from stale bytecode.**
- [x] Re-run §0.1's three lines through `SecretScanDetector().run()` on `argus/prod/settings.py`.
      **Expect 0 / 0 / 1.** If it does not reproduce, **STOP and report** — the premise is false.
- [x] Re-run §0.3's live-key × short-sentinel enumeration. **Expect 7 cells, 7 disabled.**
- [x] Re-run §0.4's 250-file sweep and record the baseline pair (**86 / 36**).
- [x] Re-run the four secret test modules (**expect 53 passed**) and the full suite (**expect
      green**). Record both.
- [x] Re-measure §0.7's ledger byte state and the max `TC-ArgusAgent-SECRET-001-NN` (**expect
      `-22`**).
- [x] Record every figure that came out different. **Expect at least one.**

### Task 1 — THE BLAST-RADIUS INSTRUMENT, BUILT BEFORE THE FIX (AC4.1, AC4.2)

- [x] Write the sweep as a throwaway script **outside the repository** (scratch dir), driving
      `run()` over `git ls-files -- '*.py'` and reporting `{total, per-file, LOST, NEW}`.
- [x] Capture the **pre-fix** result. ⛔ It is the only baseline you will ever be able to take.

### Task 2 — THE FIX, IN ONE MODULE (AC1, AC2, AC6.1–AC6.4)

- [x] Split the table into two named constants + `MIN_CONTAINMENT_SENTINEL_LENGTH = 20`; keep
      `KNOWN_PUBLIC_SENTINELS` as their **order-preserving union** (AC1.2).
- [x] Rewrite `is_public_sentinel`: exact equality of `snippet.strip()` against the short table;
      containment against the long table. Same name, same signature, same purity (AC1.1, AC1.5).
- [x] Delete `is_live_production_key`'s sentinel short-circuit (`:130`–`:132`) and **correct its
      docstring** — §0.8/(c): its `AKIAIOSFODNN7EXAMPLE` example was never in the table (AC2.1,
      AC2.2).
- [x] Extend the module docstring's step-2 bullet to say what step 2 now *decides*. ⛔ **Do not
      renumber or reorder the steps** (AC2.5). Leave the `DF-10-3-C` paragraph (`:36`–`:39`) intact.
- [x] ⛔ No `lower()`, no `casefold()`, no `re.IGNORECASE` (AC6.4).

### Task 3 — THE GUARD (AC1.3, AC1.4, AC2.3, AC2.4, AC3, AC6.2)

- [x] Create `tests/test_secret_sentinel_matching.py`, opening `TC-ArgusAgent-SECRET-001-23` and
      continuing upward. Docstring in the `-15`..`-22` register: the defect, the measurement, the
      RED evidence, and *"key material is synthetic and built in the module"*.
- [x] `-23` — the audit's **three lines** through `run()` on a non-test path, each alone, each
      `>= 1` `hardcoded_secret`, **CONTROL included** (AC3.2, `DN-18-1-5`).
- [x] `-24` — the **table invariant**: long table all `>= 20`, short table all `< 20`, disjoint,
      union `== KNOWN_PUBLIC_SENTINELS` (AC1.3).
- [x] `-25` — **no suppression lost**: all eight members alone still give
      `(True, 'known_sentinel')`; and each of the three long sentinels embedded in a larger line is
      still suppressed (AC1.4, AC2.4).
- [x] `-26` — the **enumerated live-key × short-sentinel space**: `is_live_production_key` True for
      every regex-valid cell, `evaluate_suppression` suppresses none (AC2.3).
- [x] `-27` — the **two call shapes** of `is_public_sentinel`, value-shaped and line-shaped, both
      pinned (AC3.6).
- [x] Every case asserts its population non-empty first (AC3.4); no assertion on a value (AC3.5).

### Task 4 — DRIVE IT RED (AC3.3)

- [x] Revert **only** the `secret_suppression.py` change and run the new module. **Record the exact
      failure text of every case that goes RED, and which do not.**
- [x] ⛔ **Two safe mechanisms, and one unsafe one.** SAFE: (a) keep a pre-fix copy of the module
      outside the repository and monkeypatch `SecretSuppressionEngine.is_public_sentinel` /
      `.is_live_production_key` back to their shipped bodies inside a throwaway interpreter; or
      (b) `git stash push -- argus/detectors/secret_suppression.py` — **explicit path**, and only
      after `git status --porcelain -- argus/detectors/secret_suppression.py` confirms the only
      change there is yours (§2.6: a peer session shares this branch). ⛔ UNSAFE: `git stash` with
      no pathspec.
- [x] ⛔ A case that stays GREEN against the unfixed engine is **not a guard** — fix the case, not
      the assertion, and record that you found it (`AI-E14-1`, and 16.3 found one of its own).
- [x] Restore, re-run, record GREEN.

### Task 5 — PROVE THE DIRECTION (AC4)

- [x] Re-run Task 1's sweep post-fix. **LOST must be empty.** Record `{86 → 87, LOST 0, NEW 1}` or
      whatever this tree actually gives.
- [x] Prove the new finding(s) non-blocking via `blocking_finding_count` / `is_verdict_blocking`.
- [x] Re-run `tests/test_secret_suppression_recording.py` (`-15`..`-22`) **with no edit to any
      assertion, docstring or fixture in it** — that is AC2.5's whole discharge, and the proof the
      evaluation ORDER did not move.
- [x] Full suite, green, **no assertion loosened**. ⛔ `tests/test_secret_containment.py` must be run
      as part of the whole-directory collection (§0.0).
- [x] ⛔ Confirm `tests/test_deep_pass_wiring.py` is **unmodified** (AC4.3) — `git status --porcelain`
      must not list it.

### Task 6 — THE LEDGER (AC5)

- [x] ⛔ **Grep first.** Then append, **in binary mode**: the `DF-AUD-DETECT-A` closure note and the
      `DF-10-3-B` falsification note, both dated, both leaving the original entries unrewritten.
- [x] Verify afterwards: 0 CRLF pairs, exactly one lone `\r`, and a `git diff` confined to the
      appended lines.
- [x] ⛔ Confirm `architecture.md`, `E-PRD/prd.md` and `epics.md` are **unmodified** (AC5.6) —
      `git status --porcelain` must not list any of them.

### Task 7 — GATES AND THE DOGFOOD REGENERATION (AC6.6, AC7.1, AC7.2)

- [x] Commit `argus/` + `tests/` **by explicit path**. ⛔ Never `git add -A`.
- [x] `python scripts/regenerate_dogfood_artifacts.py` on the now-clean `argus/` tree; commit the
      three artifacts separately. ⛔ Exit 2 means the tree is dirty — fix the tree, never pass
      `--allow-dirty-argus`.
- [x] Run the full AC7.1 gate list. **Record every exit code.** Mark the run **LOCAL / Windows-only**
      (AC6.5).

### Task 8 — HAND-OFF (AC7.3, AC7.4)

- [x] `git status --porcelain` — the write set equals AC6.1 exactly.
- [x] Completion notes: every re-measured §0 figure, the observed REDs with their text, the
      pre/post sweep pair, the new finding disclosed by path and cause, the 1/2/1 triple, every exit
      code, and **any §0 premise found false**.
- [x] ⛔ If the PR lands squashed or rebased, re-run the regeneration on `master` (`DF-INV-MERGE-A`).

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), via the `bmad-dev-story` workflow, 2026-08-24.

### Debug Log References

All measurement harnesses were throwaway scripts in a scratch directory OUTSIDE the repository;
nothing under `argus/`, `tests/` or `scripts/` was written to produce evidence. `git status
--porcelain` was checked before every commit and the write set is AC6.1 exactly.

- `measure.py` — the §0.1 reproduction, the §0.3 enumeration and the §0.4 250-file sweep, run
  pre-fix and post-fix against the same file population from `git ls-files -- '*.py'`.
- `redplugin.py` — Task 4 mechanism (a): a pytest plugin that restores the SHIPPED (`7a3cc7c`)
  bodies of `is_public_sentinel` / `is_live_production_key` by monkeypatch, so the per-case RED
  text is attributable to a case rather than to an import failure.
- `variantb.py` — the falsifiability probe for `-25`: `DN-18-1-1`'s REJECTED uniform-equality
  alternative, installed the same way.
- Task 4 mechanism (b) was also run: `git stash push -- argus/detectors/secret_suppression.py`
  (EXPLICIT PATH, after `git status --porcelain` confirmed the only change in that file was
  mine), then `git stash pop`. The operator's pre-existing `stash@{0}` on `master` was never
  touched.
- `PYTHONDONTWRITEBYTECODE=1` was exported and every `__pycache__` cleared before each gate run
  (Story 16.5's false RED).

### Completion Notes List

#### 1. ⛔ TASK 0 — EVERY §0 FIGURE RE-MEASURED, AND WHAT CAME OUT DIFFERENT

Re-derived by execution at `7a3cc7c`, not cited. **Every §0 figure held**, which is itself worth
recording because the story predicted at least one would not:

| §0 figure | expected | measured |
|---|---|---|
| three-line reproduction through `run()` | 0 / 0 / 1 | **0 / 0 / 1** |
| per-match detail | `high_entropy_string` 47; `generic_assigned_secret` + `high_entropy_string` 28; CONTROL 44 | **identical**, all three `(True, 'known_sentinel')`, CONTROL `(False, None)` |
| live-key × short-sentinel cells | 7 cells, 7 disabled | **7 cells, 7 disabled, 7 suppressed** |
| e2e `ghp` / `xoxb` / PEM carrying `localhost` | 0 / 0 / 1 | **0 / 0 / 1** |
| 250-file sweep | 86 findings / 36 files | **86 / 36 over 250 files** |
| four secret test modules | 53 passed | **53 passed, exit 0** |
| full suite | green | **1,716 collected, exit 0** |
| `deferred-work.md` bytes | 537,063 · 0 CRLF · 1 lone CR at 407,906 | **identical** |
| max `TC-ArgusAgent-SECRET-001` id | `-22` | **`-22`** |
| module line counts | 231 / 575 / 103 / 276 / 222 / 121 | **identical** |
| last `argus/` commit | `3183e2a` | **`3183e2a`** |

⚠️ **TWO §0 PREMISES WERE FOUND FALSE — both about WHICH GUARD FIRES, not about the defect.**

1. **§0.6 named `TC-ArgusAgent-DOGFOOD-001-50` (`tests/test_dogfood_artifact_currency.py:174`) as
   the guard that reddens when `argus/**` moves. It did NOT fire** — that module was green
   throughout, before and after. The guards that actually fired were
   `tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
   and `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`,
   on the derived figures (`33648` total LOC, 95 files). The *consequence* §0.6 drew — that the
   commit arc is forced to four commits because the regeneration script refuses a dirty `argus/`
   — was correct; only the guard id was wrong.
2. **§0's gate list did not predict `tests/test_gate_seal.py::TC-ArgusAgent-PRECISION-001-94`,
   and it reddened the `feat` commit.** Any post-seal commit touching a declared detector-tuning
   path (`argus/detectors`, `argus/precision/replay_harness.py`) must carry a machine-checkable
   whole-line trailer `Evidence-partition: <sealed|open|none>`. The honest value here is **`none`**:
   this change was driven by a CODE AUDIT and by executing the shipped `run()` over three synthetic
   lines built in a scratch interpreter. No finding from any corpus member, sealed or open, informed
   the design, the threshold of 20 or the table split; the 250-file sweep was a BLAST-RADIUS
   measurement taken *after* `DN-18-1-1` fixed the design, and it tuned nothing. The remedy was the
   one the rule itself prescribes — **write the trailer**, never amend the rule. See §5 for the
   sha-rewrite that followed.

⛔ **`DF-AUD-DETECT-A` is CLOSED by this story** at fix sha `ee7e252`, and `deferred-work.md` carries the matching dated append-only closure note — the story record and the ledger agree, which is what `TC-ArgusAgent-DOCS-001-78` checks (`AI-E12-6`: a disposition recorded in prose and not in the ledger is not a disposition).

#### 2. THE FIX (Task 2 — AC1, AC2, AC6.1–AC6.4)

`argus/detectors/secret_suppression.py`, 231 → **301** lines (NFR-M1 ceiling 1,200):

- `MIN_CONTAINMENT_SENTINEL_LENGTH = 20`.
- `CONTAINMENT_PUBLIC_SENTINELS` — the three published full-length credentials (39–40 chars), still
  matched by containment.
- `EQUALITY_PUBLIC_SENTINELS` — the five short members, matched by **exact equality of
  `snippet.strip()`** through a private derived `frozenset` (O(1) instead of the previous
  O(table × snippet) scan — an incidental side effect, and ⛔ it does **not** disposition the
  detector-cost entry, which stays OPEN as context only).
- `KNOWN_PUBLIC_SENTINELS` survives as their **order-preserving union**, byte-equal to the tuple the
  module exported before (`DN-18-1-2` / NFR-M2). All eight members stay; none added, none removed.
- `is_live_production_key`'s sentinel short-circuit is **deleted**, and its docstring is **corrected**
  per §0.8/(c): it cited `AKIAIOSFODNN7EXAMPLE` as an excluded sentinel and that value is not in the
  table and never was (the table holds the AWS *secret* key, not the *access-key id*). Recorded and
  corrected — ⛔ **NOT** implemented by adding it to the table, which would widen suppression.
- The module docstring's **step-2 bullet** was extended to say what step 2 now DECIDES. ⛔ No step was
  renumbered or reordered, and the `DF-10-3-C` paragraph is intact.
- ⛔ No `lower()`, no `casefold()`, no `re.IGNORECASE` anywhere on the sentinel path; the compare is
  plain `str.__eq__` (NFR-P1). No new import, no new dependency; the module is still PURE (AR8).

#### 3. THE GUARD AND ITS RED (Tasks 3–4 — AC1.3, AC1.4, AC2.3, AC2.4, AC3)

`tests/test_secret_sentinel_matching.py` (NEW, 293 lines) opens `TC-ArgusAgent-SECRET-001-23` and
continues to `-27`. ⛔ **Nothing was renumbered.** Every case runs on the non-test path
`argus/prod/settings.py` (§2.3), asserts its population non-empty first (`AI-E11-1`), builds every
key value in the module (NFR-S1/S2), and asserts only counts, rule ids and `(bool, reason)` tuples.

⚠️ **The REDs are AUTHOR-DRIVEN, so per the guard-fire rule they are VACUITY EVIDENCE — proof the
cases can fail — and NOT "these guards caught a defect".**

**Against the shipped `7a3cc7c` bodies (monkeypatch, mechanism (a)) — 3 RED, 2 GREEN:**

```
FAILED -23 ... AssertionError: the localhost line reports no hardcoded_secret: a credential is
               being dropped because its value carries a public-sentinel SUBSTRING
               (DF-AUD-DETECT-A)
               assert 0 >= 1
                +  where 0 = len([])
FAILED -26 ... AssertionError: the Live-Key Safeguard DISABLES ITSELF for a github_pat value
               carrying 'localhost': the backstop does not merely get bypassed, it declines to fire
               assert False is True
                +  where False = _shipped_is_live_production_key('ghp_localhost000000000000000000000000000')
FAILED -27 ... AssertionError: a short sentinel still matches as a SUBSTRING of a larger value
               — DF-AUD-DETECT-A
               assert True is False
                +  where True = _shipped_is_public_sentinel('postgres://admin:Tr0ub4dor3@example.com:5432/prod')
```

**Against a FULL revert of the module (mechanism (b), `git stash push -- <explicit path>`) — the
whole module fails to collect:**

```
ERROR collecting tests/test_secret_sentinel_matching.py
E   ImportError: cannot import name 'CONTAINMENT_PUBLIC_SENTINELS' from
    'argus.detectors.secret_suppression'
```

so `-24` (the table invariant) has no pre-fix meaning either — it is a guard over a structure the
pre-fix module does not have. Restored with `git stash pop`; re-run: **5 passed, exit 0.**

⛔ **ONE CASE STAYS GREEN AGAINST THE UNFIXED ENGINE AND IT IS RECORDED RATHER THAN GLOSSED.**
`-25` (no suppression lost) cannot go RED against the shipped engine, because containment trivially
satisfies a no-loss invariant. That is by design — `-25` is the AC1.4 direction guard and must hold
BEFORE and AFTER — but "cannot fail against the pre-fix engine" is not "cannot fail". It was
therefore probed against `DN-18-1-1`'s REJECTED uniform-equality variant, and it **catches it**:

```
FAILED -25 ... AssertionError: a published full-length credential embedded in a larger snippet is
               answered below step 2 ... assert (False, None) == (True, 'known_sentinel')
FAILED -27 ... assert False is True
                +  where False = _variant_b_is_public_sentinel('MOCK_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"')
FAILED tests/test_secret_suppression.py::test_public_sentinel_suppression
```

That run also **independently re-confirms §0.5's variant-B measurement**: exactly one shipped-suite
failure, `test_public_sentinel_suppression`, and no other. **No case in the module is vacuous.**

#### 4. THE DIRECTION IS UNDER-REPORTING → CORRECT (Task 5 — AC4)

| measurement | pre-fix | post-fix |
|---|---|---|
| three-line reproduction (findings per line) | 0 / 0 / 1 | **1 / 2 / 1** |
| live-key × short-sentinel cells: safeguard disabled | 7 of 7 | **0 of 7** |
| live-key × short-sentinel cells: suppressed | 7 of 7 | **0 of 7** |
| e2e `ghp` / `xoxb` / PEM carrying `localhost` | 0 / 0 / 1 | **1 / 2 / 2** |
| 250-file sweep | 86 findings / 36 files | **87 / 36** |
| **LOST** | — | **0** |
| **NEW** | — | **1** |

⛔ **The 1 / 2 / 1 triple is RECORDED here and asserted as `>= 1` per line** (`DN-18-1-5`): the
`example.com` line legitimately yields TWO findings because `run()` de-duplicates on
`(start_line, end_line, pattern_id)` and `generic_assigned_secret` + `high_entropy_string` both hit
that span. An exact assertion would redden the moment Story 18.3 narrows those regexes.

⚠️ **A MEASUREMENT-METHOD CORRECTION, disclosed because the first answer was wrong.** A naive
`(file, start_line, rule_id)` set difference reported three LOST and three NEW findings inside
`argus/detectors/secret_suppression.py` itself. Both were artifacts: the file's own findings shifted
line numbers (76/78/128 → 121/123/197) because **this story inserted lines into it**, and every
`rule_id` is `hardcoded_secret` so a *set* also collapsed two distinct findings on one line into
one. Re-derived correctly as a **multiset**, with the edited module compared by COUNT rather than by
line identity (3 pre → 3 post, unchanged): **LOST = {} and NEW = {`tests/test_deep_pass_wiring.py:397`: 1}.**

**The one new finding, disclosed by path and cause** (`DN-18-1-6`, AC4.2): it is
`tests/test_deep_pass_wiring.py:397`, a synthetic literal. Two patterns hit that span. The
`aws_access_key_id` match already reports today. The `high_entropy_string` match is the whole
73-character URL, which contains `example.com`, so step 2 used to answer `(True, 'known_sentinel')`
and drop it; it is now reported at step 3. **Proven non-verdict-eligible, not asserted:** all four
findings on that file carry `advisory=True, depth_supported=None`, `is_verdict_blocking` is `False`
for each, and `blocking_finding_count` over the whole result is **0**. ⛔ `tests/test_deep_pass_wiring.py`
was **NOT edited, annotated or relocated** — `git status --porcelain` never listed it (AC4.3 / `DF-8-5-B`).

⛔ **AC2.5 discharged:** `tests/test_secret_suppression_recording.py` (`-15`..`-22`) was re-run with
**no edit to any assertion, docstring or fixture in it** — 8 passed, and `git status --porcelain`
never listed the file. The evaluation ORDER did not move. ⛔ **No assertion anywhere was loosened.**

#### 5. GATES, THE COMMIT ARC AND THE SHA REWRITE (Tasks 7–8 — AC6.5, AC7)

⚠️ **LOCAL / WINDOWS-ONLY** (`AI-E13-1`, AC6.5). Python 3.11.15, `PYTHONDONTWRITEBYTECODE=1`,
`__pycache__` cleared. The cross-platform claim belongs to the CI ubuntu matrix at the pushed sha
and is **not made here**. The code was written POSIX-safe: no new path handling at all, and the
sentinel compare is a plain host-invariant `str.__eq__`.

| gate | command | exit |
|---|---|---:|
| full suite | `python -m pytest tests/ -q` | **0** (1,716 collected) |
| full suite, grammars required | `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 python -m pytest tests/ -q` | **0** |
| coverage | `python -m pytest tests/ -q --cov=argus --cov-fail-under=80` | **0** (95.69%) |
| types | `python -m mypy argus` | **0** (95 files, no issues) |
| security | `python -m bandit -r argus --severity-level medium` | **0** |
| module ceiling | `python -m pytest tests/test_module_size_ceiling.py -q` | **0** |
| release preflight | `python -m pytest tests/test_release_preflight.py -q` | **0** |
| dogfood currency | `python -m pytest tests/test_dogfood_artifact_currency.py -q` | **0** |
| governance record | `python -m pytest tests/test_governance_record_integrity.py -q` | **0** |
| every `tests/test_gate_*.py` (nine modules) | `python -m pytest tests/test_gate_*.py -q` | **0** |
| dogfood regeneration | `python scripts/regenerate_dogfood_artifacts.py` | **0** |

⚠️ `tests/test_secret_containment.py` was run only as part of the whole-directory collection (§0.0);
its standalone `ModuleNotFoundError: No module named '_cartridge'` was re-confirmed at HEAD and is a
pre-existing property of the file, not this story's.

**The commit arc is four commits, as AC7.2 forced** — messages pure ASCII (`DF-16-6-F`), staged **by
explicit path** every time, ⛔ never `git add -A` (§2.6: a peer session shares this branch):

1. `8b6c304` `chore(18-1)` — story file + `sprint-status` → `in-progress`, carrying Task 0's figures.
2. `ee7e252` `feat(18-1)` — `argus/detectors/secret_suppression.py` + `tests/test_secret_sentinel_matching.py`.
3. `fa5e463` `chore(18-1)` — the three regenerated dogfood artifacts, provenance sha `ee7e252`,
   95 files / 33,648 LOC.
4. `docs(18-1)` — the ledger append and this record, **ledger first in the diff and in the same
   commit** (§0.6: `TC-ArgusAgent-DOCS-001-78` reads the on-disk story files, so the closure must
   already be in the ledger the moment this file claims one).

⛔ **A SHA REWRITE HAPPENED INSIDE THIS STORY AND IS DISCLOSED.** Commit 2 first landed as `30aa12b`;
the artifacts were regenerated against it and committed. `TC-ArgusAgent-PRECISION-001-94` then
reddened on `30aa12b` for the missing `Evidence-partition` trailer, so commit 3 was unwound
(`git reset --soft` + `git restore` of the three artifacts by explicit path), commit 2 was **amended**
to `ee7e252`, and the artifacts were regenerated a **second** time against the new sha. That is
`DF-INV-MERGE-A`'s failure shape reproduced locally by an amend instead of by a squash — the lived
proof that AC7.3 is not theoretical.

⛔ **AC7.3 stands as a hand-off, and the condition has NOT occurred yet.** If this PR lands squashed
or rebased, `ee7e252` is orphaned and `TC-ArgusAgent-DOGFOOD-001-49` reddens `master` **after** the
merge, where no PR check can see it coming. **Re-run `python scripts/regenerate_dogfood_artifacts.py`
on `master` and commit the result.** Recorded here and in commit 3's message.

#### 6. WHAT THIS STORY DID **NOT** DO — named so it is not mistaken for done

- ⛔ `argus/detectors/secret_scan.py` — **not touched.** The dead `_evidence_for` (18.2), the two
  regex precision defects (18.3) and the `Detector` Protocol (18.4) keep their RED.
- ⛔ `--ignore-pattern`'s bare-substring semantics — **`DF-10-3-C` stays OPEN and untouched**, and it
  is still architecture §G's accepted residual risk.
- ⛔ **`DF-10-3-B` stays OPEN.** Only its *safety claim* was falsified, by dated append-only note. Its
  actual subject — that built-in suppressions are not disclosed to a reader — is untouched. A
  repaired sentinel test is still a **silent** test.
- ⛔ `DF-AUD-DETECT-B` / `-C` / `-D` / `-E` / `-F` — **not dispositioned.** In particular the equality
  arm's incidental O(1) improvement does **not** disposition the detector-cost entry.
- ⛔ **No verdict moved.** Every recovered finding is `advisory=True, depth_supported=None` by
  construction. The ≥80% precision keystone is still **NOT CLEARED** and the gate is still `BLOCKED`.
- ⛔ `architecture.md`, `E-PRD/prd.md`, `epics.md` and every `done` story's record — **unmodified**,
  verified with `git status --porcelain`. §G's claim is about the two operator FLAGS and is true
  before and after (`DN-18-1-7` / AC5.6).
- ⛔ **`DF-13-5-A` stays OPEN and UNSPENT** — no member ratified, no protocol re-version, no FR
  amended. The epics.md "AWAITING OPERATOR APPROVAL" paragraphs were not edited.
- ⛔ **Nothing new was filed.** The ledger was greped by id first (`DF-INV-LEDGER-A`): it already
  carries the sentinel table, the disclosure gap, the `--ignore-pattern` semantics and the detector
  cost, so prior art was cited rather than re-filed. The AWS-access-key-id false positive found at
  §0.8/(c) is `AI-E9-8`-owned by the Engineering Lead and belongs to 18.3, the precision story — it
  is recorded in the corrected docstring and here, and it is **not** filed by this story.

#### 7. AC5.4 — THE LEDGER'S BYTE INVARIANT, VERIFIED AFTER WRITING

`deferred-work.md` was edited in **binary mode**. After the append: **544,667 bytes**, **0** CRLF
pairs, **exactly one** lone `\r` (the content one, inside a backtick span discussing line endings),
and `git diff --stat` shows **76 insertions, 0 deletions** — a pure append, with both original
entries above the notes unrewritten. The ledger's closed-id extractor was run pre- and post-edit:
the set gained **exactly one** id, `DF-AUD-DETECT-A`, and lost none.

### File List

| path | change |
|---|---|
| `argus/detectors/secret_suppression.py` | UPDATE — 231 → 301 lines |
| `tests/test_secret_sentinel_matching.py` | NEW — 293 lines, `TC-ArgusAgent-SECRET-001-23`..`-27` |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | APPEND-ONLY — +76 lines |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` | REGENERATED by its own renderer |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` | REGENERATED by its own renderer |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` | REGENERATED by its own renderer |
| `_bmad-output/design-artifacts/ArgusAgent/stories/18-1-the-sentinel-table-matches-values-not-substrings-of-them.md` | this file |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | status transitions only |

⛔ The write set equals **AC6.1 exactly**, verified with `git status --porcelain` (not `git diff
--name-only`, which is blind to the new untracked module). `argus/detectors/secret_scan.py` is not
in it; nothing under `minions_core/apaa/` is in it.

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-24 | 0.2 | IMPLEMENTED. `is_public_sentinel` is length-gated (`MIN_CONTAINMENT_SENTINEL_LENGTH = 20`, equality below it, containment above); `is_live_production_key`'s self-disabling short-circuit deleted and its docstring corrected; `TC-ArgusAgent-SECRET-001-23`..`-27` added and driven RED (3 cases vs the shipped bodies, the whole module vs a full revert, `-25` vs the rejected uniform-equality variant) then GREEN. Measured: reproduction 0/0/1 -> 1/2/1; live-key cells 7-disabled -> 0-disabled; sweep 86/36 -> 87/36 with LOST 0 and NEW 1 (disclosed, non-blocking). Ledger: DF-AUD-DETECT-A closed, DF-10-3-B's safety claim falsified while the entry stays OPEN, both append-only in binary mode. Two Section 0 premises found false, both about WHICH guard fires (DOGFOOD-001-50 did not; test_dogfood_plan/proof and PRECISION-001-94 did). Full suite exit 0 with and without grammars, coverage 95.69%, mypy/bandit clean - LOCAL, Windows-only. Status `review`. | bmad-dev-story (Opus 5) |
| 2026-08-24 | 0.1 | Story contexted at HEAD `7a3cc7c`; §0 measured by execution (three-line reproduction 0/0/1, 7-of-7 live-key matrix, 250-file sweep 86→87 LOST 0, three candidate repairs executed, full suite green under the candidate repair at exit 0). Status `ready-for-dev`. | create-story (Opus 5) |
