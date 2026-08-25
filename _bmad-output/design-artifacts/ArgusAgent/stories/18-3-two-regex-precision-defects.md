---
baseline_commit: 62fd1b9
---

# Story 18.3: Two regex precision defects

Status: in-progress

<!-- Contexted 2026-08-25 at HEAD `62fd1b9` (branch `docs/merge-strategy-decision`) by the
     create-story workflow (Opus 5).

     EVERY FIGURE IN SECTION 0 WAS READ OFF THIS TREE BY EXECUTION, not copied from `epics.md`,
     from `sprint-change-proposal-2026-08-24.md`, from `DF-AUD-DETECT-E` or from Stories 18.1/18.2.
     Both defects were reproduced through the shipped `SecretScanDetector.run()`; the entry's two
     censuses over `argus/**` were re-derived and both reproduce EXACTLY; and every candidate repair
     was executed engine-vs-engine over all 252 tracked `*.py` files and over the whole 1,724-test
     suite before a word of this file was written.

     THREE PREMISES OF THE ENTRY WERE FOUND FALSE BY THAT EXECUTION, and all three change what this
     story must do:
       (1) SECTION 0.2 - the repair the entry proposes for defect 1 ("a negative lookbehind")
           produces THREE MEASURED FALSE GREENS if the lookbehind excludes `_`, and it reddens
           Story 18.1's own `TC-ArgusAgent-SECRET-001-26`. The lookbehind must exclude LETTERS AND
           DIGITS ONLY.
       (2) SECTION 0.4 - defect 2's error direction is NOT "OVER-reporting, never a false green".
           It UNDER-reports as well: the unpaired delimiters CONSUME a real secret's opening quote,
           and 12 measured matches - including `AKIA...`, `wJalrXUtnFEMI/...`, `ghp_...` and a
           `postgres://admin:...` URL - appear only AFTER the repair.
       (3) SECTION 0.5 - the mismatched-delimiter defect occurs at THREE regex sites in the module,
           not the one the entry names.

     NO `argus/`, `tests/`, `scripts/` OR ARTIFACT FILE WAS TOUCHED TO PRODUCE THIS STORY. Every
     simulation was module-attribute monkeypatching inside a throwaway interpreter and a throwaway
     `pytest` plugin, both driven from a scratch directory outside the repository.

     THE WORKING TREE WAS ALREADY DIRTY AT CONTEXTING, AND NOT WITH THIS STORY'S WORK: four files
     carrying Stories 18.1's and 18.2's records are modified-but-uncommitted at `62fd1b9`. See
     SECTION 0.0 and SECTION 2.6 - they are NOT this story's to commit, and `git add -A` would
     swallow them.

     NOTHING HERE SPENDS `DF-13-5-A`. No member is ratified, no protocol row is added, no FR is
     amended, no third-party source is fetched. -->

## Story

As the **Engineering Lead**,
I want **the two measured regex defects in `secret_scan` corrected — the key alternation anchored on its left, and every quoted-literal pattern required to close with the delimiter it opened with**,
so that **the detector stops reporting `topsecret` as a secret, stops losing a real one behind an apostrophe, and the correction actually reaches a repository that was audited before it.**

### What this story IS

The discharge of **`DF-AUD-DETECT-E`**. Two regex bodies decide it, and a third carries the same
defect class:

- **Defect 1 — no left anchor.** `_GENERIC_ASSIGN_RE` (`argus/detectors/secret_scan.py:287`–`:290`)
  anchors nothing to the left of `api[_-]?key|secret|token|password|passwd|pwd`, so `topsecret`,
  `mytoken` and `notapassword` all match the key alternation.
- **Defect 2 — unpaired delimiters.** `_ANY_LITERAL_RE` (`:296`) is
  `['\"](?P<secret>[^'\"\n]+)['\"]` — the opening and closing delimiters are INDEPENDENT character
  classes, so a span opened with `'` and closed with `"` is accepted as one literal. ⛔ **The same
  defect is present at `_AWS_SECRET_KEY_RE` (`:282`) and inside `_GENERIC_ASSIGN_RE` (`:289`)** —
  three sites, one class (§0.5).

The story lands **one lookbehind** and **three backreferences**, **bumps the detector's
`code_identity`** so the correction is not memoized away (§0.7), corrects the module docstring where
this change makes it wrong, and lands **five guards** in a new module that make both defects — and
the false-green mis-repair — unable to recur.

### What it is NOT

- ⛔ **NOT the repair the entry names, taken literally.** `DF-AUD-DETECT-E` says *"a negative
  lookbehind before the alternation"*. Executed, the ordinary word-boundary spelling
  `(?<![A-Za-z0-9_])` **drops `DB_PASSWORD`, `_API_KEY` and `SMTP_PASSWORD` to ZERO findings** and
  reddens `TC-ArgusAgent-SECRET-001-26` — Story 18.1's own live-key guard (§0.2). This story takes
  `(?<![A-Za-z0-9])`, which excludes letters and digits and **admits `_`**. See `DN-18-3-1`.
- ⛔ **NOT a rewrite of the detector into a Python tokenizer.** The scan stays a text regex scan.
  Pairing the delimiters improves alignment; it does not make the scan token-accurate, and the
  residual limit is **disclosed in the docstring, not fixed** (`DN-18-3-5`).
- ⛔ **NOT a change to the LOCKED pattern-family set.** No `pattern_id` is added, removed or
  renamed; `MIN_GENERIC_SECRET_LENGTH`, `MIN_ENTROPY_TOKEN_LENGTH` and
  `ENTROPY_BITS_PER_CHAR_FLOOR` are **not** retuned. Moving a threshold is **AC8**.
- ⛔ **NOT a touch of `argus/detectors/secret_suppression.py`.** Story 18.1 is `done`; its module is
  not reopened and none of `TC-ArgusAgent-SECRET-001-23`..`-27` is edited. ⚠️ `-26` is the guard the
  mis-repair reddens — it is a **witness this story must keep green**, not a test to adjust.
- ⛔ **NOT a touch of `argus/detectors/base.py`** — Story 18.4's fence (`DF-AUD-DETECT-F`).
- ⛔ **NOT a re-opening of Story 18.2's change.** `_evidence_for`, `scan_evidence`,
  `SecretFindingEvidence`, the replaced redaction banner and `TC-ArgusAgent-SECRET-001-28`..`-30`
  are left exactly as `2cc5128` left them.
- ⛔ **NOT output-neutral, and it must not pretend to be.** Unlike Story 18.2, this story **moves
  the numbers**: 91 → 90 findings over 252 tracked files, 38 → 37 files (§0.6). The obligation is
  not *"nothing moves"* — it is **"every removal is an over-report, and no real secret stops being
  reported"**, which is a different and harder proof (AC3).
- ⛔ **NOT a performance story.** `DF-AUD-DETECT-C` is **not** dispositioned by anything here.
- ⛔ **NOT a disclosure feature.** `DF-10-3-B` and `DF-10-3-C` stay OPEN and untouched.
- ⛔ **NOT a verdict move.** Every `hardcoded_secret` finding is `advisory=True,
  depth_supported=None` by construction. The ≥80% precision keystone stays **NOT CLEARED** and the
  gate stays `BLOCKED`.
- ⛔ **NOT an epic-16-or-earlier reopening.** Epics 1–16 are `done`. Story 2.5's, 5.1's, 5.3's and
  10.3's records are cited, never edited.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `62fd1b9`

⛔ **Task 0 re-derives every row below before a line is written.** Six consecutive epics in this
repository found a stated premise false by executing it; Story 18.1 found two, Story 18.2 found
three, and this contexting pass found **three more** (§0.2, §0.4, §0.5). The figures here were true
on 2026-08-25 on a Windows host; **they are a baseline to re-measure, not a fact to cite.**

### §0.0 The tree, the paths and the baseline

| fact | value at contexting |
|---|---|
| repo root | `d:/ProjectX/XAgents/XAgents/ArgusAgent` |
| HEAD | `62fd1b9e318ed46348a652792e710ac39c4c268f` (`62fd1b9`) |
| branch | `docs/merge-strategy-decision` |
| last commit touching `argus/` | `2cc5128` — Story 18.2's `feat` |
| `git status --porcelain` | ⚠️ **NOT empty** — four Story-18.1/18.2 record files (below) |
| python | 3.11.15 |
| tests collected under `tests/` | **1,724** (`--collect-only -q`, summed per module) |
| full suite | **exit 0** (`python -m pytest tests/ -q`, re-run at this HEAD) |
| `python -m mypy argus` | **Success: no issues found in 95 source files** |
| `python -m bandit -r argus --severity-level medium` | clean |
| `argus/detectors/secret_scan.py` | **594** lines (NFR-M1 ceiling 1,200) |
| `argus/cache/key.py` | ⛔ **IN the write set, for ONE token** (§0.7) |
| `argus/detectors/base.py` | 204 lines — ⛔ NOT touched (Story 18.4's fence) |
| `argus/detectors/secret_suppression.py` | 301 lines — ⛔ NOT touched (Story 18.1, `done`) |
| `tests/test_secret_scan_precision.py` | 121 lines — ⛔ **read, not edited** |
| `deferred-work.md` | **556,678 bytes**, **0** CRLF, **exactly one** lone `\r`, **7,138** LF |
| `sprint-status.yaml` | **1,009,407 bytes**, **1,187** CRLF, **0** lone `\r` |
| tracked `*.py` (`git ls-files -- '*.py'`) | **252** |
| `hardcoded_secret` findings over those 252 | **91**, in **38** files |
| `hardcoded_secret` findings over `argus/**` (95 files) | **40** — the figure the dogfood proof records |

⚠️ **THE TREE IS DIRTY AND IT IS NOT YOURS.** At contexting `git status --porcelain` lists exactly:

```
 M _bmad-output/design-artifacts/ArgusAgent/deferred-work.md
 M _bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml
 M _bmad-output/design-artifacts/ArgusAgent/stories/18-1-the-sentinel-table-...-of-them.md
 M _bmad-output/design-artifacts/ArgusAgent/stories/18-2-the-redaction-call-keeps-...-computes.md
```

Those are Stories 18.1's and 18.2's own review-round records, written by sessions that deliberately
did **not** stage them (`DN-DEV-18-2-A`). ⛔ **Stage by explicit path: `git add -A` / `git add .`
would swallow a peer session's uncommitted work into your commit** (§2.6). Re-check the list at
Task 0 — it may have been committed by then, and it may have grown.

⛔ **`AI-E13-1` — the local suite is Windows-only and CI runs an ubuntu matrix.** A green local run
is recorded as **LOCAL** and never on its own discharges a cross-platform claim.

### §0.1 DEFECT 1 REPRODUCED — and the entry's census reproduces EXACTLY

The shipped pattern, verbatim at `:287`–`:290`:

```python
_GENERIC_ASSIGN_RE = re.compile(
    r"(?i)(?:api[_-]?key|secret|token|password|passwd|pwd)\s*[:=]\s*"
    r"['\"](?P<secret>[^'\"\n]+)['\"]"
)
```

Through the shipped `SecretScanDetector.run()` on the NON-test path `argus/prod/settings.py`:

| one-line source | shipped `hardcoded_secret` findings | pattern ids |
|---|---:|---|
| `topsecret = "correct-horse-battery-staple"` | **1** | `generic_assigned_secret` |
| `mytoken = "correct-horse-battery-staple"` | **1** | `generic_assigned_secret` |
| `notapassword = "correct-horse-battery-staple"` | **1** | `generic_assigned_secret` |

**The entry's `argus/**` census, re-derived rather than cited: 3 matches with a word character
immediately left of the key, of which 1 is inside a comment line** — `argus/cache/key.py:181`, the
comment holding `detectors/secret_scan.py::RULE_HARDCODED_SECRET = "hardcoded_secret"`. The other
two are `secret_scan.py:147` and `:154`, the module's own two `RULE_*` constants. **All three
reproduce, at the paths and in the proportion the entry records.**

### §0.2 ⛔ THE REPAIR THE ENTRY NAMES IS A FALSE GREEN. MEASURED, THREE TIMES OVER.

`DF-AUD-DETECT-E` ends: *"Repairs are one token each: a negative lookbehind before the alternation,
and a backreference for the closing delimiter."* The ordinary spelling of a word boundary is
`(?<![A-Za-z0-9_])` — **and every one of this repository's own word-char-left matches is preceded by
`_`, not by a letter.** Over all 252 tracked files:

| left-character class of a reported `generic_assigned_secret` match | count |
|---|---:|
| ALPHA-left (`topsecret`-shaped — the defect the entry describes) | **0** |
| DIGIT-left | **0** |
| UNDERSCORE-left (`DB_PASSWORD`-shaped — ordinary secret naming) | **10** |

⛔ **Driven through the shipped `run()` on `argus/prod/settings.py`, one line each:**

| one-line source | shipped | `(?<![A-Za-z0-9_])` (naive) | `(?<![A-Za-z0-9])` (this story) |
|---|---:|---:|---:|
| `DB_PASSWORD = "Tr0ub4dor3xKqmZw91"` | 1 | ⛔ **0** | 1 |
| `_API_KEY = "sk-test-do-not-leak-me"` | 1 | ⛔ **0** | 1 |
| `SMTP_PASSWORD = "aBcD1234EfGh5678"` | 1 | ⛔ **0** | 1 |
| `password = "Tr0ub4dor3xKqmZw91"` | 1 | 1 | 1 |
| `self.token = "Tr0ub4dor3xKqmZw91"` | 1 | 1 | 1 |
| `topsecret = "correct-horse-battery-staple"` | 1 | 0 | **0** |
| `mytoken = "correct-horse-battery-staple"` | 1 | 0 | **0** |
| `notapassword = "correct-horse-battery-staple"` | 1 | 0 | **0** |

⛔ **THE NAIVE REPAIR INVERTS THE ERROR DIRECTION THE ENTRY'S OWN 🟢 SEVERITY RESTS ON.** It turns a
precision defect into a recall defect on the single most common real-world secret-naming convention
there is: `UPPER_SNAKE_CASE`, where the underscore is a **separator**, not a word character that
could make `PASSWORD` part of a larger innocent word.

⛔ **AND THE SUITE CATCHES IT — by exactly one test, from the story immediately before this one.**
Executed: the whole 1,724-test suite under the naive repair goes **RED at one case**:

```
FAILED tests/test_secret_sentinel_matching.py::test_TC_ArgusAgent_SECRET_001_26_live_key_safeguard_no_longer_disables_itself
E   AssertionError: a live production key is dropped end-to-end by the sentinel short-circuit
    assert 0 >= 1  where 0 = len(_hardcoded_secret_findings('API_TOKEN = "ghp_localhost0000..."\n'))
```

Story 18.1's live-key guard is **the only thing in this repository standing between it and that
false green**. ⛔ **If you see `-26` go RED, you have written the wrong lookbehind. Fix the
lookbehind — never the guard** (`DF-8-5-B`).

**This story's lookbehind, and the whole-suite result under it:** `(?<![A-Za-z0-9])` — **1,724
tests, exit 0, not one case RED** (§0.6).

⚠️ **WHAT THE SAFE LOOKBEHIND DOES *NOT* REMOVE, said plainly.** Over this repository's own 252
files it removes **nothing at all** — all 10 word-char-left matches are `_`-preceded and every one
of them stays. That includes the `argus/cache/key.py:181` comment the entry names: **it is
`_`-preceded, so this story leaves it reported.** The prose-in-a-comment half of the entry's
complaint is **not** fixed here, is **not** fixable by a lookbehind, and is named in §1.3 so it is
not mistaken for fixed. The lookbehind's value is measured on **synthetic** input (the table above),
not on this tree — which is precisely why AC4's guards are synthetic-source guards and **not** a
repo sweep.

### §0.3 DEFECT 2 REPRODUCED — and the entry's second census reproduces EXACTLY

The shipped pattern at `:296`:

```python
_ANY_LITERAL_RE = re.compile(r"['\"](?P<secret>[^'\"\n]+)['\"]")
```

| measurement over `argus/**` (95 files) | entry says | measured 2026-08-25 |
|---|---:|---:|
| spans whose opening and closing delimiters DIFFER | 462 | **462** |
| of those, surviving `_is_entropy_candidate` (i.e. actually reportable) | 3 | **3** |

The three, by path — and the entry's *"one of them, pleasingly, being `secret_scan.py:280`'s own
regex source"* reproduces, now at `:282` after Story 18.2's edit:

```
argus/audit/open_llm_adapter.py:170    ')}/v1/chat/completions"
      <- from  endpoint = f"{self._api_base.rstrip('/')}/v1/chat/completions"
argus/detectors/secret_scan.py:282     "](?P<secret>[A-Za-z0-9/+=]{40})['
argus/precision/gate_decision.py:693   '.join(sorted(unattributed_row_ids)[:5])}"
```

Over all **252** tracked files the census is **2,104 spans / 5 surviving** — the extra two are
`tests/test_verdict_gate.py:719` and `:742`, one golden-JSON sha256 each.

One-line reproduction through the shipped `run()` on `argus/prod/settings.py`:

| one-line source | shipped | with paired delimiters |
|---|---:|---:|
| `x = 'openedSingle1234closedDouble"` | **1** (`high_entropy_string`) | **0** |
| `x = 'Tr0ub4dor3xKqmZw91abcd'` (control, matched) | 1 | 1 |
| `x = "Tr0ub4dor3xKqmZw91abcd"` (control, matched) | 1 | 1 |

### §0.4 ⛔ DEFECT 2 ALSO **UNDER**-REPORTS. THE ENTRY'S SEVERITY RATIONALE IS FALSIFIED BY EXECUTION.

`DF-AUD-DETECT-E` files itself at 🟢 on this sentence: *"the error direction is OVER-reporting,
never a false green"*. **Measured: false, for the second defect.**

**THE TWO-LINE REPRODUCTION.** Through the shipped `SecretScanDetector.run()` on the non-test path
`argus/prod/settings.py`, source exactly:

```python
src = 'blob = "aZ9kPqW3mX7vL2cR8tY4nB6h"'
```

| | `hardcoded_secret` findings |
|---|---:|
| shipped engine | ⛔ **0** |
| paired-delimiter engine | **1** (`high_entropy_string`) |

**THE MECHANISM.** The scanner is left-to-right and non-overlapping. The outer `'` opens a span,
`[^'\"\n]+` eats `blob = `, and the **inner opening `"` is accepted as the CLOSING delimiter**. The
span is consumed, `re.finditer` resumes *after* it — **inside the secret** — and the real literal is
never offered to `_is_entropy_candidate` at all. The defect does not merely add noise; **it eats a
credential's opening quote and takes the credential with it.**

⛔ **AND IT IS NOT A CURIOSITY — IT HAPPENS 12 TIMES IN THIS REPOSITORY.** Engine-vs-engine over the
same 252-file population, at the raw `_scan` level, the paired engine finds **12 matches the shipped
engine does not**. The values speak for themselves:

```
tests/test_secret_scan.py:59                 AKIAIOSFODNN7EXAMPLE
tests/test_secret_scan.py:78                 aZ9kPqW3mX7vL2cR8tY4nB6h
tests/test_secret_sentinel_matching.py:87    postgres://admin:Tr0ub4dor3@localhost:5432/prod
tests/test_secret_sentinel_matching.py:91    aBcD1234EfGh5678@example.com
tests/test_secret_sentinel_matching.py:95    postgres://admin:Tr0ub4dor3@dbhost:5432/prod
tests/test_secret_suppression.py:13          wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
tests/test_secret_suppression.py:55          AKIA1234567890ABCDEF
tests/test_secret_suppression.py:79          AKIA9876543210FEDCBA
tests/test_secret_suppression_recording.py:238   AnotherPlausibleSecretValue0123456789
tests/test_sequential_portability.py:715     ghp_aB3dEfGh1JkLmN0pQrStUvWxYz456789012
tests/test_built_distribution.py:452         argus._story_11_5_canary
_bmad-output/.../research/revalidate-fact-b-widening.py:144   W1_discarded_no_mock_clause
```

⚠️ **READ THAT LIST HONESTLY, BOTH WAYS.** Ten of the twelve are **canonical credential shapes**
(`AKIA…`, an AWS secret key, a `ghp_` GitHub token, two `postgres://` URLs with an inline password)
— exactly the values the module docstring promises **100% recall** over. Two are ordinary
identifiers, i.e. the repair adds a little noise as well as recall. And **most of the twelve land on
spans another pattern family already reports**, which is why the *finding* total still goes DOWN
(§0.6) — the safety net caught them by another route. ⛔ **The claim to make is the narrow one: the
error direction is BOTH ways, so this entry's 🟢 rests on a falsified premise.** The claim NOT to
make is *"we found a live security hole"* — every one of the twelve is inside this repository's own
test corpus, and the two that produce a genuinely new finding are a research script and a test file.

⛔ **THIS FALSIFICATION IS RECORDED, NOT FILED** (AC5.2, `AI-E9-8`). Greped at contexting:
`deferred-work.md` carries **no** entry about regex delimiter alignment or about this recall class
— **166** `- id: DF-` lines and none of them is this. The falsified sentence belongs to
`DF-AUD-DETECT-E` itself, so it is corrected **inside that entry's own dated append-only
disposition note**, the way Story 18.1 handled `DF-10-3-B`'s falsified safety claim and Story 18.2
handled `DF-AUD-DETECT-B`'s falsified Story-2.5 reasoning. ⛔ **The entry above the note is NOT
rewritten** (§3.4).

### §0.5 ⛔ THE DEFECT CLASS OCCURS THREE TIMES IN THE MODULE, NOT ONCE

Greped at contexting — every unpaired `['\"] … ['\"]` in `argus/detectors/secret_scan.py`:

```
:282   _AWS_SECRET_KEY_RE   r"['\"](?P<secret>[A-Za-z0-9/+=]{40})['\"]"
:289   _GENERIC_ASSIGN_RE   r"['\"](?P<secret>[^'\"\n]+)['\"]"
:296   _ANY_LITERAL_RE      r"['\"](?P<secret>[^'\"\n]+)['\"]"
```

The entry names only `:294` (now `:296`). ⛔ **Repairing one of three occurrences of a defect class
inside one module is the half-repair this repository keeps catching** — and it would leave the
module's own `:282` line, which is *itself* one of the three surviving over-reports in §0.3, still
carrying the very shape the story exists to remove.

**Measured: pairing all three is output-identical to pairing only `_ANY_LITERAL_RE`.** Over the same
252-file population, three engines compared field-for-field:

| engine | raw `_scan` matches | `hardcoded_secret` findings | files ≥1 |
|---|---:|---:|---:|
| shipped | 403 | **91** | 38 |
| `_ANY_LITERAL_RE` paired only (the entry's arm) | 410 | **90** | 37 |
| all three paired **+** the safe lookbehind | 410 | **90** | 37 |

The lost set, the new set and the per-file `DetectorResult`s are **identical** between the second
and third rows. ⛔ So the wider repair costs **nothing** measurable and buys the class. See
`DN-18-3-2`.

### §0.6 WHAT THE REPAIR MOVES OVER THE TREE — the numbers this story is accountable for

Engine-vs-engine over **one identical 252-file population** (`git ls-files -- '*.py'`), comparing the
FULL `DetectorResult` (`entries` + `findings` + `degraded`, canonical JSON) per file:

| | `hardcoded_secret` findings | distinct spans | files ≥1 | suppression records | degraded |
|---|---:|---:|---:|---:|---:|
| shipped | **91** | 77 | **38** | 0 | 0 |
| repaired (lookbehind + three backreferences) | **90** | 75 | **37** | 0 | 0 |

**Every span whose finding count moves, exhaustively — five of them, and not one more:**

| span | shipped → repaired | what it is |
|---|---:|---|
| `argus/audit/open_llm_adapter.py:170` | 1 → **0** | `f"{self._api_base.rstrip('/')}/v1/chat/…"` — an f-string, not a secret |
| `argus/detectors/secret_scan.py:282` | 1 → **0** | the module's own regex source |
| `argus/precision/gate_decision.py:693` | 1 → **0** | `f"…{', '.join(sorted(row_ids)[:5])}"` — an f-string |
| `tests/test_secret_scan.py:59` | 1 → **2** | recall: `_run('aws_key = "AKIAIOSFODNN7EXAMPLE"')` realigns |
| `_bmad-output/…/research/revalidate-fact-b-widening.py:144` | 0 → **1** | an f-string identifier, `W1_discarded_no_mock_clause` |

⛔ **THREE REMOVALS, AND ALL THREE ARE OVER-REPORTS BY INSPECTION.** Not one is a credential; two are
f-string fragments and one is a regex source line. ⛔ **Two ADDITIONS, and neither is a removal** —
the epic's *"never a false green"* obligation is about what disappears, and nothing that was a real
secret disappears.

⚠️ **`argus/**`-only, which is what the dogfood proof audits: 40 → 37 findings.** The three
`argus/` removals above are all of them; `argus/` gains nothing. **`minions-dogfood-proof.md`
records `hardcoded_secret` at `40` with `argus/audit/open_llm_adapter.py:170` in its sample-locator
list, and a `Total findings emitted: 173`.** ⛔ **Both figures move (predict 37 and 170) and the
three dogfood artifacts MUST be regenerated** (§0.8, AC7.2).

**THE WHOLE SUITE UNDER THE REPAIR: 1,724 tests, exit 0, not one case RED** — executed at contexting
through a throwaway `pytest` plugin that replaced the three module-level regexes at
`pytest_configure`. ⛔ **That is the measurement behind `DF-AUD-DETECT-E`'s claim that neither defect
is an accepted cost: nothing in this repository pins either behaviour.** Verified separately that no
test imports either regex by name (`grep -rn "_GENERIC_ASSIGN_RE\|_ANY_LITERAL_RE" tests/ scripts/`
returns nothing), so the plugin's patch was faithful.

### §0.7 ⛔ WITHOUT A `code_identity` BUMP THE FIX DOES NOT REACH A RE-AUDITED REPOSITORY

This is the coupling that separates this story from Story 18.2, and it was measured, not assumed.

- `argus/cache/key.py:187` declares `DetectorDescriptor(rule_id="hardcoded_secret",
  code_identity="secret_scan.v1")` inside `FROZEN_DETECTOR_SET`. Its own model docstring (`:152`–
  `:162`) says the token is *"a stable identifier for the detector's code path — **bumped when its
  logic materially changes**"*, and that *"editing any field CHANGES the set hash → CHANGES the
  derived key (the AR6 invalidation lever Story 5.3 rides)"*.
- ⛔ **The detect stage IS memoized in production.** `argus/pipeline.py:166` imports
  `memoize_detect_stage`; `argus/cache/stage_memo.py:155` builds the stage closure from
  `FROZEN_DETECTOR_SET` and `:239` derives the key from it. **A repository audited before this fix
  and re-audited after it would be served the PRE-FIX detect-stage result** — including the
  over-reports this story removes and the realignment recall it gains.
- **Executed:** bumping the token to `secret_scan.v2` moves the detector-set content hash
  `9954e854…` → `fbec7912…`, i.e. the lever works exactly as `DN-DETECTORSET` describes.

⛔ **This is the single most consequential decision in the story and it is NOT the same call Story
18.2 made.** `DN-18-2-5` declined to bump *because that change was provably output-neutral* — and
said so in terms (*"AC2.1 proves no cached result is stale"*). Here §0.6 proves the opposite. See
`DN-18-3-6`.

**WHAT THE BUMP COSTS, MEASURED BY EXECUTION rather than feared:**

- `tests/test_cache_key.py::test_golden_key_pinned` (`TC-ArgusAgent-CACHE-001-03`) goes RED: the
  golden moves `ccf2d132b699060b20afff5a42d4731f72d73f90b0b3cdfd3bc8e48c69f8b6af` →
  **`78239f689c6dd3c92e3268d0787d3e96293c607f66fc0b710e9d76b19cb92850`** (predicted; **re-derive it,
  never paste it**). ⛔ The golden's own docstring permits exactly this: *"Regenerate ONLY with a
  documented intentional invalidation (e.g. a deliberate schema bump), never silently"*, and it
  records one prior regeneration on the same terms (the Story-10.2 schema bump).
- ⚠️ **THREE MORE go RED, and for a reason worth reading.** `tests/test_cache_invalidation.py:229`
  builds its *synthetic perturbed* descriptor as
  `DetectorDescriptor(rule_id="hardcoded_secret", code_identity="secret_scan.v2")` — **the exact
  value a real bump takes**, so the perturbation collides with the live set and the three
  `test_detector_set_change_*` cases fail. ⛔ **Verified by execution that this is the ONLY reason:**
  re-run with the live token bumped to a non-colliding value instead, those three are **GREEN** and
  only the golden moves. The repair is to move the *fixture* to an unmistakably synthetic token in
  the style `tests/test_stage_memo_wiring.py:306` already uses (`secret_scan.v99`) — which
  **restores** the perturbation's non-vacuity rather than loosening it. See `DN-18-3-7`.

### §0.8 THE GUARDS THAT WILL FIRE, AND THE ONES THAT WILL NOT — measured, not predicted

**WILL FIRE (plan for them):**

- ⛔ **`tests/test_cache_key.py::test_golden_key_pinned`** and the three
  `tests/test_cache_invalidation.py::test_detector_set_change_*` cases — §0.7, with the exact
  failure text and the exact cause already measured.
- **`tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`**
  (`:202`, asserting `f"**{result.total_loc}**" in text` at `:243`) and
  **`tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`**
  (`:240`, same assertion at `:273`). The committed artifacts record **95** source files and
  **33667** total physical LOC at provenance sha `2cc5128`. This story changes `secret_scan.py`'s
  line count **and** its finding output, so both derivations move.
  ⚠️ **Story 18.1's §0 predicted `TC-ArgusAgent-DOGFOOD-001-50` and it did NOT fire; Story 18.2
  measured that these two derivation tests fired instead. Watch these two; do not chase `-50`.**
- ⛔ **`scripts/regenerate_dogfood_artifacts.py` REFUSES to run on a dirty `argus/` tree** (exit
  **2**, `_refuse_if_argus_is_dirty`). The ordering is therefore forced: **commit `argus/` +
  `tests/` FIRST, then regenerate, then commit the three artifacts separately.** A commit cannot
  cite itself. That is why AC7.2's arc is **four** commits.
- ⛔ **`tests/test_gate_seal.py::test_TC_ArgusAgent_PRECISION_001_94_the_seal_precedes_every_candidate_output`**
  (`:1035`). Re-verified by importing `argus.precision.gate_seal` at this HEAD:
  `DETECTOR_TUNING_PATHS = ('argus/detectors', 'argus/precision/replay_harness.py')`,
  `SEAL_CITATION_TRAILER = 'Evidence-partition'`, `SEAL_CITATION_VALUES = ('sealed', 'open',
  'none')`. **This story touches `argus/detectors`, so its `feat` commit MUST carry the whole-line
  trailer** `Evidence-partition: none` — *none* is the honest value: the change was driven by a code
  audit and by executing the shipped `run()`, and **no** corpus finding, sealed or open, informed it.
  ⛔ Write the trailer; never amend the rule. Story 18.1 lost a sha over exactly this and Story 18.2
  wrote it the first time.
- ⛔ **`TC-ArgusAgent-DOCS-001-78`** (`tests/test_governance_record_integrity.py:196`) extracts every
  `DF-*` id a **committed story file** claims to have disposed of and cross-checks `deferred-work.md`.
  The moment this file records a disposition for `DF-AUD-DETECT-E`, the ledger must already carry it
  — so the `docs` commit carries **the ledger append and this story's record together, ledger first
  in the diff**. ⚠️ This file as contexted makes **no** such claim, verified by running the guard's
  own analyzer over it: `story_closure_claims()` returns `()`. ⛔ **It is ONE WORD from RED.**
  `_CLOSURE_VERB` (`:48`) matches the bare tokens `CLOSED` / `Closes` / `closes` on the same LINE as
  a `DF-*` id. ⛔ **Do not put any of those three tokens on a line with a `DF-*` id in this file
  until the ledger note exists**, and **re-run the analyzer after every edit you make to this file**.

**WILL NOT FIRE (verified at contexting, so you do not chase them):**

- **The whole 1,724-test suite** under the three repaired regexes: exit **0**. In particular
  `tests/test_secret_scan.py` (`-01`..`-14`), `tests/test_secret_scan_precision.py`
  (`SECRET-002-01`..`-07`), `tests/test_secret_suppression*.py`,
  `tests/test_secret_sentinel_matching.py` (`-23`..`-27`), `tests/test_secret_evidence_contract.py`
  (`-28`..`-30`) and `tests/test_secret_containment.py` are all GREEN with **no edit**.
- `tests/test_module_size_ceiling.py` — `secret_scan.py` is 594 lines against a 1,200 ceiling
  measured as `len(text.splitlines())` (`:176`–`:183`). The **new test module** is swept by the same
  guard and must stay ≤1,200.
- `TC-ArgusAgent-RELEASE-001-11` / `-20` fire on **adding a file under `argus/`**. This story adds
  none — it edits two existing modules.
- `tests/test_status_document_registry.py` — `stories/` is `_EXCLUDED_BY_DESIGN` (`:350`, enforced at
  `:471`–`:475`). ⛔ **This story file must NOT be registered there, and neither must the new test
  module.**
- `tests/test_v1_commitment_closure.py:510` pins **FR28** to the literal `class
  SecretFindingEvidence(` in `secret_scan.py`. Untouched by this story.
- `argus/precision/replay_harness.py` and the **1,032-finding** harness are the **vacuous-test**
  precision surface (`rule_id` `vacuous_test_ast` / `vacuous_test_heuristic`), not this detector's.
  ⛔ **This story does not re-run it and must not claim it as evidence.**

### §0.9 The ledger's byte state and the next free ids — both measured

- `deferred-work.md` at contexting: **556,678 bytes**, **0** CRLF pairs, **exactly ONE** lone `\r`
  (content — a literal `` `\r` `` inside a backtick span discussing line endings), **7,138** LF.
  ⛔ **Edit it in BINARY MODE.** A Windows text-mode write rewrites all 7,138 newlines to CRLF *and*
  eats that CR, producing a 7,000-line diff over a short append.
  ⚠️ The file is **modified-but-uncommitted** at contexting (§0.0). Re-measure at Task 0 and record
  what you find; **the invariant, not the byte count, is the thing that must hold after your
  append.**
- ⚠️ **This story file, `epics.md` and `sprint-status.yaml` are CRLF** (`sprint-status.yaml`
  measured: 1,187 CRLF, **0** lone `\r`). They are not the ledger's file class. **Do not "normalise"
  in either direction.**
- **Verification ids — TWO independent SECRET indices, both measured continuous:**
  - `TC-ArgusAgent-SECRET-001-01`..**`-30`** (detection, the evidence carrier, suppression,
    sentinels, the 18.2 evidence contract). Max **`-30`**.
  - `TC-ArgusAgent-SECRET-002-01`..**`-07`** (`tests/test_secret_scan_precision.py` — *precision of
    the detector's predicates*). Max **`-07`**. ⛔ **This story CONTINUES `SECRET-002` at `-08`**
    (`DN-18-3-4`). **Renumbering anything invalidates citations in `architecture.md` and
    `deferred-work.md`.**
- **No new `DF-*` entry is expected.** ⛔ **Grep the ledger before filing anything** — **166** `- id:
  DF-` lines at contexting, and none of them is the recall class §0.4 measures. Cite prior art
  rather than re-file: `DF-INV-LEDGER-A` exists because someone filed as new what this ledger had
  recorded the day before.

### §0.10 What is already true and must NOT be re-done

**(a)** `tests/test_secret_scan_precision.py` already pins `_is_entropy_candidate`,
`_has_no_whitespace` and `_has_letter_digit_mix` thoroughly, including a `KNOWN_SECRET_SHAPES`
recall tuple of eight real credential shapes and an `ORDINARY_LITERALS` precision tuple of ten.
⛔ **Re-run it; do not rewrite it, do not extend its tuples, do not move a case out of it.** The new
module covers what it does not: **the REGEXES**, which that file says nothing about — which is
`DF-AUD-DETECT-E`'s own observation and reproduces by reading the file.

**(b)** The end-to-end containment property is already CI-blocking:
`tests/test_secret_containment.py` (`TC-ArgusAgent-SECURITY-001-01`+) varies the secret value over a
randomized population and asserts every canary absent from the ledger, every finding, the evidence
bundle, `.argus/**`, the verdict, logs, spans and exception messages. ⛔ **This story does not
reimplement it and does not weaken it.**
⚠️ `tests/test_secret_containment.py` cannot be collected on its own (`from _cartridge import
stage_cartridge` resolves only when the whole `tests/` directory is collected). Pre-existing;
re-confirmed at this HEAD. Run it as `python -m pytest tests/ -q`, never as a single-file
invocation.

**(c)** Story 18.1 repaired `secret_suppression.py` and Story 18.2 removed the dead redaction call.
Both are `done`. ⛔ **`run()`'s suppression call, the `continue` branch, the replaced redaction
banner, `_evidence_for`, `scan_evidence` and `SecretFindingEvidence` are all byte-unchanged by this
story.**

**(d)** ⚠️ `argus/prod/settings.py` **does not exist and must not be created.** `run()` is PURE and
never opens the file; `file_path` is a string used for path-glob matching and locators only. It is
the standard non-test path in this epic's guards precisely because `DEFAULT_TEST_PATH_PATTERNS` does
not match it.

---

## §1 — WHY THIS STORY EXISTS

### §1.1 The module's design argument is denominated in noise

`secret_scan.py`'s docstring rests the entire `high_entropy_string` family on an alarm-fatigue
argument: entropy alone fired on **1108** literals across 53 files of this repository's own
secret-free source, and the two structural discriminators cut that to **12** — *"a supplementary net
that fires on everything catches nothing — an operator who cannot read the report is not protected
by it."* ⛔ **Noise is the currency that argument is denominated in**, which is why
`DF-AUD-DETECT-E` files two small-volume precision defects at all. A detector that argues its own
design from a false-positive count owes that count its accuracy.

### §1.2 Nothing pins either regex, and the suite proves it

`tests/test_secret_scan_precision.py` — the module whose entire subject is precision — pins the
three predicates and says **nothing** about either regex. Measured (§0.6): both defects can be
repaired and **1,724 tests stay green**. ⛔ A behaviour no test constrains is a behaviour the next
edit can silently reverse, in either direction; after this story, five guards constrain it.

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **Prose in a comment still matches.** The detector is a text scan with no comment model. A line
  reading `# … password = "…"` matches before and after (measured), and `argus/cache/key.py:181` —
  the one comment-line match the entry names — is `_`-preceded and **stays reported** (§0.2).
- **The scan is still not a Python tokenizer.** Pairing the delimiters realigns it; it does not make
  it token-accurate, and a literal containing its own delimiter is still invisible to it
  (`'b4c4…eb56",'` at `tests/test_verdict_gate.py:719` is the measured example).
- **A JSON-style `{"api_key": "…"}` mapping is still not matched** — the `"` between the key and the
  `:` defeats `\s*[:=]\s*`. Measured **0 findings before and 0 after**. ⛔ Recorded here, **not
  fixed and not filed** (`AI-E9-8`); it is a recall gap in the shipped family, not a regression of
  this story's making.
- **`DF-10-3-B` (built-in suppressions are not disclosed) stays OPEN.**
- **`DF-AUD-DETECT-C` (detector cost) stays OPEN**, and nothing here dispositions it.
- **`DF-AUD-DETECT-D` / `-F` stay OPEN** — Story 17.3 and Story 18.4.
- **The ≥80% precision keystone is still NOT CLEARED and the gate is still `BLOCKED`.**

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ The obvious repair is the wrong one, and only one test will tell you

§0.2. `(?<![A-Za-z0-9_])` reads like the correct word-boundary repair, matches the entry's own
wording, and **is a security regression**. The only thing that catches it is
`TC-ArgusAgent-SECRET-001-26`, from the story immediately before this one. ⛔ **AC4.3 requires a
guard of this story's own that fails on the wrong lookbehind**, so the next reader does not have to
re-derive this from a sentinel test three modules away.

### §2.2 ⛔ "Prove nothing real disappeared" is the hard half, and a repo sweep cannot do it

The epic's second AC is *"the change is proven not to remove any finding the pre-fix detector
reported for a real secret."* ⛔ **Over this repository, the safe lookbehind removes nothing at all
and the delimiter repair removes exactly three things, all f-string or regex-source fragments** —
so a sweep is a *disclosure* instrument, not a proof. **The proof is the synthetic recall matrix
(AC3.2): the eight `KNOWN_SECRET_SHAPES` already in `tests/test_secret_scan_precision.py`, each
placed in a real assignment on a non-test path, asserted reported both before and after.** Sweep
AND matrix; neither alone.

### §2.3 ⛔ Guard vacuity — this project's signature defect, and this story's version

`AI-E14-1` / trap E.1. **This story's version:** a precision guard that asserts *"`topsecret = "…"`
is not reported"* while choosing a value that is **also** below `MIN_ENTROPY_TOKEN_LENGTH` or
without a letter-digit mix — in which case the assertion passes for a reason that has nothing to do
with the lookbehind and would pass against the shipped engine too. ⛔ **Every negative case must be
driven RED against the shipped body first** (AC4.6), and ⛔ **every case runs on the NON-TEST path
`argus/prod/settings.py`**, with `AI-E11-1` applied: assert the population is non-empty on a
positive control before asserting an absence.

⚠️ **The concrete trap, measured.** `topsecret = "aBcD1234EfGh5678iJkL"` goes **2 → 1** findings
under the repair, not 2 → 0, because that value is *also* a legitimate `high_entropy_string`. ⛔
**Assert on the `generic_assigned_secret` pattern id, or choose a value the entropy family
rejects** (`correct-horse-battery-staple` — no digits — is the one §0 used, and it goes **1 → 0**).

### §2.4 ⛔ The `code_identity` bump is a correctness requirement, not hygiene — and it reddens four tests

§0.7. Skipping it ships a fix that a memoized re-audit never sees. Taking it moves a golden and
collides with a fixture. ⛔ **Both the golden regeneration and the fixture move are recorded, with
their reason, in the ledger note and the completion notes** (AC5.1, AC6.4) — a golden regenerated
silently is the thing `TC-ArgusAgent-CACHE-001-03`'s docstring exists to forbid.

### §2.5 ⛔ The commit arc is FORCED, and it is four commits with a trailer

`chore` (this story file + `in-progress`) → **`feat`** (`argus/` + `tests/`, carrying
`Evidence-partition: none`) → `chore` (regenerate the three dogfood artifacts on a **clean**
`argus/` tree) → `docs` (ledger + this story's record, ledger first in the diff). ⛔ A commit cannot
cite itself, and the regeneration script exits **2** on a dirty `argus/` (§0.8).

⛔ **`DF-INV-MERGE-A` (OPEN, DECIDED-NOT-YET-APPLIED).** Squash and rebase merging orphan the
provenance sha a regenerated dogfood artifact cites, and `TC-ArgusAgent-DOGFOOD-001-49` then reddens
`master` **after** the merge, where no PR check can see it coming. **If the PR lands sha-rewritten,
re-run `python scripts/regenerate_dogfood_artifacts.py` on `master` and commit the result** (AC7.3).

### §2.6 ⛔ The working tree is SHARED and already dirty, and one artifact file has a byte invariant

- **A concurrent session commits to this same branch, and four of its files are uncommitted right
  now** (§0.0). ⛔ **Stage by EXPLICIT PATH. Never `git add -A`, never `git add .`.** Verify the
  write set with `git status --porcelain` — **not** `git diff --name-only`, which cannot see the new
  untracked test module.
- **`deferred-work.md` is LF-only with exactly one content `\r`** (§0.9). ⛔ **Binary-mode edits
  only**, verified after writing.
- ⛔ **`minions_core/apaa/` is DEAD.** `argus/` is the only live tree. Nothing in this story goes
  near it, and a "matching fix" over there is out of scope by construction.

### §2.7 The idioms the guard needs, so you do not go looking for them

- The entry the detector needs is constructed directly, no tree-sitter:
  `AstIndexEntry(file_path=<same string>, ast_eligible=True, definitions=())` from
  `argus.index.ast_index` — the `tests/test_secret_scan.py::_entry` precedent.
- Findings are counted as `[f for f in result.findings if f.rule_id == RULE_HARDCODED_SECRET]`.
  ⛔ De-duplication is on `(start_line, end_line, pattern_id)` (`:441`), so **one source line can
  legitimately yield more than one finding** — `API_TOKEN = "AKIA…"` yields **3**. Where a case is
  about ONE family, read `pattern_id` off `SecretScanDetector()._scan(source)` rather than counting
  findings.
- ⚠️ **Beware the public-sentinel table when choosing values.** `wJalrXUtnFEMI/K7MDENG/…EXAMPLEKEY`
  and anything containing `example.com` are SUPPRESSED by Story 18.1's engine — measured: a case
  built on the AWS documentation key reports **0 findings** and says nothing about any regex.
  ⛔ Choose values that are shaped like credentials and are **not** in the sentinel table; assert the
  positive control fires first.
- Test function names follow the area convention exactly:
  `def test_TC_ArgusAgent_SECRET_002_08_<snake_case_claim>() -> None:` — the id is *in the function
  name*, which is how `tests/conftest.py`'s guard-fire recorder attributes a RED.
- Non-blocking-ness, where asserted, uses `blocking_finding_count` / `is_verdict_blocking` from
  `argus.verdict.verdict_gate` (the `-22` precedent).

---

## §3 — AC ↔ TASK MAP

*(There to be checked, not trusted. Every AC is named by at least one task; every task cites the AC
it discharges. Stories 16.5 and 16.6 each failed a readiness validation where an AC was repaired on
one side of the file and its mirror left defective in the task list.)*

| AC | discharged by |
|---|---|
| AC1 — the two defects are corrected, and the class is corrected everywhere it occurs | Task 3 |
| AC2 — the docstring stops saying what the change makes false | Task 3 |
| AC3 — no real secret stops being reported, proven two independent ways | Task 0, Task 1, Task 4, Task 5 |
| AC4 — five guards, each RED against the shipped body where it can be | Task 2, Task 3 |
| AC5 — the correction actually reaches a re-audited repo (`code_identity`) | Task 3, Task 6 |
| AC6 — the disposition is recorded with its reasons, append-only | Task 5 (AC6.5), Task 6, Task 8 |
| AC7 — gates, dogfood regeneration, the commit arc, the trailer | Task 0 (baseline), Task 7, Task 8 |
| AC8 — escalate, do not decide | all tasks |

---

## Acceptance Criteria

### AC1 — BOTH DEFECTS ARE CORRECTED, AND THE CLASS IS CORRECTED EVERYWHERE IT OCCURS

- **AC1.1 — the left anchor.** `_GENERIC_ASSIGN_RE` gains a negative lookbehind immediately before
  the key alternation that rejects a match when the preceding character is a **letter or a digit**.
  ⛔ **The lookbehind MUST NOT exclude `_`.** `(?<![A-Za-z0-9])` is the measured-correct spelling;
  `(?<![A-Za-z0-9_])` and `\b` are **forbidden by measurement** (§0.2) and any spelling that drops
  `DB_PASSWORD` / `_API_KEY` / `SMTP_PASSWORD` to zero is wrong regardless of how it is written.
- **AC1.2 — paired delimiters, all three sites.** Every quoted-literal pattern in the module closes
  with the delimiter it opened with, via a backreference: `_AWS_SECRET_KEY_RE` (`:282`),
  `_GENERIC_ASSIGN_RE` (`:289`) and `_ANY_LITERAL_RE` (`:296`). ⛔ **Fixing only the site the entry
  names is a half-repair** (§0.5), and it would leave `:282` — itself one of the three surviving
  over-reports — still carrying the defect.
- **AC1.3 — the `secret` group keeps its name and its meaning.** `m.group("secret")`,
  `m.start("secret")` and `m.end("secret")` must all still resolve; a delimiter group must be named
  (e.g. `(?P<q>…)` / `(?P=q)`) or otherwise not disturb the named group the call sites use.
  ⛔ **`_scan`, `run`, `scan_evidence`, `_evidence_for`, `_line_span` and `_ast_span_for_line` are
  otherwise byte-unchanged.**
- **AC1.4 — nothing else in the regex set moves.** `_AWS_ACCESS_KEY_RE` and `_PEM_PRIVATE_KEY_RE`
  are untouched (neither carries the class). No `pattern_id` string changes. No threshold constant
  changes. The `(?i)` flags stay exactly where they are.
- **AC1.5 — AR8 purity preserved.** No new import in `secret_scan.py`; no I/O, clock, randomness or
  network on any decision path; `re` is already imported.

### AC2 — THE MODULE STOPS SAYING WHAT THIS CHANGE MAKES FALSE

- **AC2.1** — the `generic_assigned_secret` bullet in the module docstring (`:59`–`:61`) states the
  left-anchor rule in one clause, and says explicitly that the anchor **admits `_`** and why
  (`DB_PASSWORD` is how credentials are named). ⛔ The sentence must be short and it must not assert
  anything §0 did not measure.
- **AC2.2** — the LOCKED *"V1 detection scope + KNOWN limits"* paragraph (`:45`–`:52`) gains the
  residual limits this story leaves standing and **measured**: the scan is not a Python tokenizer,
  a literal containing its own delimiter is invisible to it, prose in a comment still matches, and a
  JSON-style `{"api_key": "…"}` mapping is not matched (§1.3). ⛔ **The locked FAMILY SET is NOT
  changed** — no `pattern_id` added, removed or renamed. Adding a *disclosed limit* is additive;
  changing the family set is **AC8**.
- **AC2.3** — ⛔ **No other sentence in that 104-line docstring is reflowed, reordered or trimmed.**
  A whitespace-only churn hides the changes that matter. In particular the **1108 → 12** alarm-
  fatigue argument and the *"100% recall over every known secret shape"* claim are **left as
  written** — §0.4 makes the second one *more* true, not less.
- **AC2.4** — a short comment at each of the three repaired regex sites naming the defect and the
  measurement, in the register Story 18.2 left at `run()`'s redaction banner. ⛔ **The comment must
  say what is measured, not what is hoped.**

### AC3 — NO REAL SECRET STOPS BEING REPORTED, PROVEN TWO INDEPENDENT WAYS

- **AC3.1 — the sweep, engine-vs-engine, over ONE identical population.** Re-derive §0.6 at the
  story's own HEAD: `run()` over every file in `git ls-files -- '*.py'`, comparing the FULL
  `DetectorResult` per file, shipped body vs repaired body. ⛔ **Both sides over the SAME file list**
  — once the new test module is tracked, that list is **253**. **Run pre-change engine vs
  post-change engine, never HEAD-vs-worktree over two different lists.** This is the exact finding
  Story 18.1's review raised; do not repeat it.
- **AC3.2 — EVERY REMOVED FINDING IS ENUMERATED AND ADJUDICATED BY PATH AND CAUSE.** For each span
  whose finding count drops, record path, line, the source text, the pattern id and **one sentence
  saying why it is not a credential**. Baseline expectation (three, §0.6):
  `argus/audit/open_llm_adapter.py:170`, `argus/detectors/secret_scan.py:282`,
  `argus/precision/gate_decision.py:693`. ⛔ **If a fourth appears, or any of the three turns out to
  be credential-shaped, that is AC8.**
- **AC3.3 — THE RECALL MATRIX, which the sweep cannot provide.** The eight
  `KNOWN_SECRET_SHAPES` values already in `tests/test_secret_scan_precision.py` (imported or
  re-declared — ⛔ **that file is not edited**) are each placed in an ordinary assignment on the
  non-test path and asserted **reported by the repaired engine**, with the shipped engine's answer
  recorded alongside. ⛔ **Not one may go from reported to unreported.**
- **AC3.4 — THE NAMING MATRIX.** `DB_PASSWORD`, `_API_KEY`, `SMTP_PASSWORD`, `API_TOKEN`,
  `self.token`, `password` and `api-key` forms are each asserted **still reported** after the change
  (§0.2's table). ⛔ This is the false-green fence and it is not optional.
- **AC3.5 — the additions are disclosed too.** Any span that GAINS a finding is recorded by path and
  cause, and proven **non-blocking** with `blocking_finding_count` / `is_verdict_blocking`.
  Baseline expectation: two (§0.6). ⛔ **A gained finding is NOT suppressed, annotated, relocated or
  edited away** — that is `DF-8-5-B`'s forbidden move.
- **AC3.6** — the full suite is green at or above its baseline (**1,724** collected, exit 0), with
  **no test's assertion loosened** and **no edit to any assertion, docstring or fixture** in
  `tests/test_secret_scan.py`, `tests/test_secret_scan_precision.py`,
  `tests/test_secret_suppression.py`, `tests/test_secret_suppression_recording.py`,
  `tests/test_secret_sentinel_matching.py`, `tests/test_secret_evidence_contract.py` or
  `tests/test_secret_containment.py`. ⛔ **`TC-ArgusAgent-SECRET-001-26` staying green is a
  first-class result of this story** (§0.2) — record it explicitly.
- **AC3.7** — coverage stays at or above the `--cov-fail-under=80` floor; record the measured
  percentage either way (baseline 95.69% at `2cc5128`).

### AC4 — FIVE GUARDS, IN ONE NEW MODULE, EACH RED WHERE IT CAN BE

- **AC4.1** — a new module `tests/test_secret_scan_regex_precision.py` opens
  **`TC-ArgusAgent-SECRET-002-08`** and continues upward. ⛔ **CONTINUE the `SECRET-002` index;
  renumber nothing** (§0.9). Its module docstring states both defects, both measurements (§0.1,
  §0.3, §0.4), the false-green measurement (§0.2) and the RED evidence, in the register of
  `tests/test_secret_scan_precision.py`.
- **AC4.2 — `-08`, the LEFT-ANCHOR guard.** `topsecret` / `mytoken` / `notapassword` assignments on
  the non-test path yield **no `generic_assigned_secret` match**, with a positive control
  (`password = …`, same value) asserted to fire first (`AI-E11-1`). ⛔ Choose a value the entropy
  family rejects, or assert on `pattern_id`, per §2.3. **Measured RED against the shipped body.**
- **AC4.3 — `-09`, the FALSE-GREEN FENCE.** `DB_PASSWORD`, `_API_KEY` and `SMTP_PASSWORD`
  assignments are **still reported**. ⛔ **This case is GREEN before and after BY DESIGN** — it is a
  contract pin, not a defect witness, and **AC6.5 requires that disclosed in exactly those terms**
  (`AI-E14-1`: an author-driven RED is vacuity evidence; a case that never goes RED is a fence, and
  calling it a caught defect is the over-claim). ⛔ Its docstring must name the mis-repair it fences
  out and cite `TC-ArgusAgent-SECRET-001-26` as the corroborating end-to-end witness. **Prove the
  fence is not vacuous by executing it against the naive lookbehind and recording that it goes RED
  there.**
- **AC4.4 — `-10`, the PAIRED-DELIMITER guard.** A span opened with `'` and closed with `"` is **not
  reported**, and the two matched-delimiter controls (`'…'`, `"…"`, same value) **are**. **Measured
  RED against the shipped body.**
- **AC4.5 — `-11`, the REALIGNMENT RECALL guard.** §0.4's two-line reproduction: a real,
  entropy-qualifying credential nested inside a single-quoted wrapper
  (`src = 'blob = "…"'`) is **reported** after the change. ⛔ **Measured RED against the shipped body
  — the shipped engine reports 0.** This is the guard that pins the falsified severity claim, and it
  is the reason §0.4 is in this file at all.
- **AC4.6 — `-12`, the CLASS guard.** An assertion over `argus/detectors/secret_scan.py`'s own
  source that **no quoted-literal pattern in the module uses independent open/close character
  classes** — i.e. the `['\"]…['\"]` shape appears **zero** times — and that the module still
  compiles at least the four named pattern families (so the guard cannot pass by a regex having
  vanished). ⛔ It is scoped to this module's pattern constants; it is **not** a blanket rule over
  the repository.
- **AC4.7 — the RED is observed and its exact text recorded**, driven against the **shipped** module
  body (monkeypatch from a pre-change copy held outside the repository, or
  `git stash push -- argus/detectors/secret_scan.py` — **explicit pathspec only**). ⛔ **Never by
  weakening an assertion.** A case that stays GREEN against the shipped body and is not `-09` is
  **not a guard** — fix the case, not the assertion, and record that you found it.
- **AC4.8** — every key value is **built in the module**; ⛔ **no secret is planted in a committed
  fixture file**, no assertion is on a secret value (only on counts, pattern ids, rule ids and
  absence — NFR-S1 / NFR-S2, the `-15`..`-30` precedent), and ⛔ **no chosen value is in the
  public-sentinel table** (§2.7).

### AC5 — THE CORRECTION ACTUALLY REACHES A RE-AUDITED REPOSITORY

- **AC5.1** — `argus/cache/key.py:187`'s `code_identity` for `rule_id="hardcoded_secret"` is bumped
  from `"secret_scan.v1"` to **`"secret_scan.v2"`**, because §0.6 proves the detector's output
  materially changed and `argus/pipeline.py:166` memoizes the detect stage on that token (§0.7).
  ⛔ **No other descriptor, field or line in `argus/cache/key.py` is touched.**
- **AC5.2** — `tests/test_cache_key.py::test_golden_key_pinned`'s golden is **regenerated BY
  EXECUTION** (predicted `78239f68…`; ⛔ **derive it, do not paste it**) and its docstring gains one
  dated sentence recording this as the second documented intentional invalidation, naming this story
  and its reason. ⛔ **No other assertion in that module is edited.**
- **AC5.3** — `tests/test_cache_invalidation.py:229`'s **synthetic perturbed** descriptor moves off
  the colliding literal `"secret_scan.v2"` to an unmistakably synthetic token (the
  `tests/test_stage_memo_wiring.py:306` precedent uses `secret_scan.v99`), with a one-line comment
  saying why. ⛔ **This RESTORES the perturbation's non-vacuity; it is not a loosened assertion, and
  the three `test_detector_set_change_*` cases must be GREEN afterwards for the right reason** —
  verify by confirming the perturbed set's hash still differs from the live set's.
- **AC5.4** — ⛔ **nothing under `argus/cache/` other than that one token is modified**, no
  `CACHE_KEY_SCHEMA_VERSION` is bumped, and no persisted `.argus/` entry is migrated or deleted. If
  the dev concludes a migration is owed, that is **AC8**.

### AC6 — THE DISPOSITION IS RECORDED WITH ITS REASONS, APPEND-ONLY

- **AC6.1** — **`DF-AUD-DETECT-E`** gains a **dated append-only disposition note** naming this
  story, the fix sha, the five new guard ids, the before/after sweep (**91 → 90 findings, 38 → 37
  files, three removals enumerated, two additions enumerated**), and the `code_identity` bump with
  its reason. ⛔ **The original entry above the note is NOT rewritten** (§3.4 evidence immutability
  — the `DF-AUD-DETECT-A` / `DF-AUD-DETECT-B` notes are the form).
- **AC6.2 — THE NOTE CARRIES BOTH FALSIFICATIONS, IN TERMS.** (i) The entry's proposed repair for
  defect 1 — *"a negative lookbehind before the alternation"* — is **a false green in its ordinary
  spelling**: measured, `(?<![A-Za-z0-9_])` drops three real-secret naming conventions to zero and
  reddens `TC-ArgusAgent-SECRET-001-26`; the repair taken excludes letters and digits only. (ii) The
  entry's severity rationale — *"the error direction is OVER-reporting, never a false green"* — is
  **false for defect 2**: measured, the unpaired delimiters consume a credential's opening quote,
  12 matches appear only after the repair, and §0.4's two-line reproduction goes **0 → 1**. ⛔ The
  finding is TRUE and is not disturbed; only these two claims are corrected, dated, append-only.
- **AC6.3** — ⛔ **Binary-mode edit only.** Verify after writing: `deferred-work.md` still has **0**
  CRLF pairs and **exactly one** lone `\r`, and `git diff --stat` over it shows **insertions only**.
- **AC6.4** — the note also records the **collateral this story spent**: the regenerated cache
  golden and the moved perturbation fixture (§0.7), each with its reason — so a later reader does
  not find a silently regenerated golden.
- **AC6.5 — Grep before filing. Nothing new is filed by this story.** The measured gaps §1.3 lists
  (comment prose, non-tokenizer scanning, the JSON-mapping recall gap) are **DISCLOSED in the
  completion notes with their measurements** and **NOT fixed, NOT filed, NOT asserted onto Story
  18.4** (`AI-E9-8`: filing and scheduling are the Engineering Lead's). `-09`'s fence-not-witness
  status is disclosed in the same place.
- **AC6.6** — ⛔ **`architecture.md`, `E-PRD/prd.md` and `epics.md` are NOT edited.** Measured:
  `architecture.md`'s only reference to this module is a directory-tree comment (`:1176`,
  *"secret_scan.py # FR11 — regex/entropy + producer-side redaction"*) which stays true, and
  `sprint-change-proposal-2026-08-24.md` §2 records `prd.md: None` / `architecture.md: None`. If you
  judge one must move, that is **AC8**.
- **AC6.7** — ⛔ **`DF-10-3-B`, `DF-10-3-C`, `DF-AUD-DETECT-C` / `-D` / `-F`, `DF-10-4-B` and
  `DF-13-5-A` are NOT dispositioned.** Naming one in prose without doing its work is the `AI-E12-3`
  defect.

### AC7 — SCOPE, GATES, DOGFOOD REGENERATION AND THE COMMIT ARC

- **AC7.1 — ⛔ THE WRITE SET IS EXACTLY:**
  1. `argus/detectors/secret_scan.py` — UPDATE
  2. `argus/cache/key.py` — UPDATE, **one token** (AC5.1)
  3. `tests/test_secret_scan_regex_precision.py` — NEW
  4. `tests/test_cache_key.py` — UPDATE, the golden + its docstring (AC5.2)
  5. `tests/test_cache_invalidation.py` — UPDATE, the perturbation fixture (AC5.3)
  6. `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — APPEND-ONLY
  7. the three regenerated dogfood artifacts (`minions-dogfood-partition-plan.md`,
     `minions-dogfood-budget-plan.md`, `minions-dogfood-proof.md`) — by their own renderer only
  8. this story file
  9. `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — status transitions only

  ⛔ **NOT in it:** `argus/detectors/base.py`, `argus/detectors/secret_suppression.py`,
  `argus/pipeline.py`, `argus/pipeline_stages.py`, `argus/reports/generator.py`,
  `argus/precision/**`, any other file under `argus/cache/`, the seven secret-domain test modules
  §0.10 names, any `done` story's record, and **anything under `minions_core/apaa/`** — that tree is
  dead; `argus/` is the only live one.
- **AC7.2** — the commit arc is **four** commits, in this order, for §0.8's forced reason:
  **`chore`** (this story file + `sprint-status` → `in-progress`) → **`feat`** (`argus/` + `tests/`)
  → **`chore`** (regenerate the three dogfood artifacts on a clean `argus/`) → **`docs`** (ledger +
  this story's record, **ledger first in the diff**). ⛔ Commit messages **pure ASCII**
  (`DF-16-6-F`), and the **`feat`** commit carries the whole-line trailer **`Evidence-partition:
  none`** (§0.8).
- **AC7.3** — ⛔ `DF-INV-MERGE-A`: if the PR lands squashed or rebased, re-run
  `python scripts/regenerate_dogfood_artifacts.py` on `master` and commit, or
  `TC-ArgusAgent-DOGFOOD-001-49` reddens `master` after the fact.
- **AC7.4** — green at the end, **every exit code recorded**: the full suite (`python -m pytest
  tests/ -q`, and again with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`), coverage `--cov-fail-under=80`,
  `mypy argus`, `bandit -r argus --severity-level medium`, `tests/test_module_size_ceiling.py`,
  `tests/test_release_preflight.py`, `tests/test_dogfood_artifact_currency.py`,
  `tests/test_dogfood_plan.py`, `tests/test_dogfood_proof.py`, `tests/test_cache_key.py`,
  `tests/test_cache_invalidation.py`, `tests/test_stage_memo_wiring.py`,
  `tests/test_governance_record_integrity.py`, `tests/test_v1_commitment_closure.py`,
  `tests/test_gate_*.py`. ⛔ Run with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared — Story
  16.5's dev lost a commit to a **false RED from stale bytecode**.
- **AC7.5** — NFR-M1: `secret_scan.py` is 594 lines and must stay ≤ **1,200**; the new test module
  likewise. **Split, never shave, never exempt.**
- **AC7.6** — `AI-E13-1`: the local run is Windows-only and is recorded as **LOCAL**. The
  cross-platform claim belongs to the CI ubuntu matrix, and only after it is green at the pushed sha.
- **AC7.7** — ⛔ stage by **explicit path**; never `git add -A` / `git add .` (§2.6). Verify the
  final write set equals AC7.1 exactly with `git status --porcelain` — **not**
  `git diff --name-only`, which is blind to the new untracked test module — and confirm none of the
  four §0.0 files rode along unless its own session had already committed it.

### AC8 — ESCALATE, DO NOT DECIDE

⛔ **STOP and escalate — do not decide — if any of these becomes necessary:**

- a **fourth** file's `hardcoded_secret` count drops, or any of §0.6's three removals turns out to be
  credential-shaped;
- **any** of the eight `KNOWN_SECRET_SHAPES` or any naming-matrix case (AC3.3, AC3.4) stops being
  reported;
- `TC-ArgusAgent-SECRET-001-26` — or any case in the seven secret-domain modules — goes RED and the
  cause is not a wrong lookbehind you can fix in your own regex;
- a threshold must move (`MIN_GENERIC_SECRET_LENGTH`, `MIN_ENTROPY_TOKEN_LENGTH`,
  `ENTROPY_BITS_PER_CHAR_FLOOR`), or a `pattern_id` must be added, removed or renamed;
- the LOCKED pattern-family set or the LOCKED file-scope rule must change;
- `CACHE_KEY_SCHEMA_VERSION` must move, a persisted `.argus/` entry must be migrated or deleted, or
  anything under `argus/cache/` beyond AC5.1's single token must be touched;
- `argus/detectors/base.py`, `argus/detectors/secret_suppression.py`, `argus/pipeline*.py`,
  `argus/reports/generator.py` or `argus/precision/**` must be touched;
- any assertion in the seven secret-domain test modules must be edited;
- `architecture.md`, `E-PRD/prd.md`, `epics.md` or any `done` story's record must be edited;
- a **new** `DF-*` entry looks necessary (§1.3) — `AI-E9-8`: recording is this story's job, filing is
  the Engineering Lead's;
- `DF-13-5-A` must be spent, a member ratified, a protocol row added, or an FR amended;
- a finding must become **verdict-eligible**, or the precision gate must move;
- any `DN-*` must be reopened. ⛔ **A `DN-*` you disagree with is an escalation, not a story
  decision.**

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

- **`DN-18-3-1` — THE LOOKBEHIND EXCLUDES LETTERS AND DIGITS, NOT `_`.** `(?<![A-Za-z0-9])`.
  Measured (§0.2): the `_`-including spelling drops `DB_PASSWORD`, `_API_KEY` and `SMTP_PASSWORD` to
  **zero** findings, reddens `TC-ArgusAgent-SECRET-001-26`, and inverts the error direction the
  entry's own 🟢 severity depends on; the chosen spelling rejects all three of the entry's own
  examples (`topsecret`, `mytoken`, `notapassword`) and keeps the whole suite green. **`_` is the
  separator in `UPPER_SNAKE_CASE`, which is how credentials are named.**
  *Rejected: `\b` / `(?<![A-Za-z0-9_])`, the entry's literal wording.* A measured security
  regression.
  *Rejected: `(?<![A-Za-z])` (digits allowed left).* `token2secret`-shaped names would still match;
  no measured cost to excluding digits and no case in the tree needs them.
  *Rejected: leaving defect 1 alone because its in-tree volume is zero.* The entry is chartered work
  and the volume is zero only for the SAFE repair; the defect is structural and reproduces on one
  synthetic line.

- **`DN-18-3-2` — THE PAIRING IS APPLIED AT ALL THREE SITES, NOT THE ONE THE ENTRY NAMES.** Measured
  (§0.5): all-three is **output-identical** to `_ANY_LITERAL_RE`-only over 252 files — same lost
  set, same new set, same per-file `DetectorResult`s — so the wider repair is free and it removes
  the class rather than one instance.
  *Rejected: `:296` only.* Leaves `:282` carrying the defect **and** still emitting one of the three
  over-reports this story is chartered to remove; a reader who greps the module finds the shape the
  ledger says was repaired.
  *Rejected: a shared helper regex or a constructor function.* Over-abstraction for three literals,
  and it would obscure exactly the text a future auditor greps for.

- **`DN-18-3-3` — THE STORY IS NOT OUTPUT-NEUTRAL AND SAYS SO.** Its obligation is directional
  (AC3), not neutral. Story 18.2's `AC2.1` shape ("the differing set must be EMPTY") is **wrong for
  this story** and copying it would make the story unsatisfiable or, worse, satisfiable only by
  doing nothing.
  *Rejected: an output-neutral framing with the removals suppressed.* That is the defect the fix
  exists to remove, moved into the test suite.

- **`DN-18-3-4` — A NEW MODULE `tests/test_secret_scan_regex_precision.py`, CONTINUING
  `TC-ArgusAgent-SECRET-002` AT `-08`.** One module, one subject (`DN-18-1-4` / `DN-18-2-4`
  precedent): the subject here is **the regexes' precision and recall**, which is the `SECRET-002`
  area's charter (*"Story 2.5 pinned that the entropy family DETECTS; this module pins that it does
  not detect EVERYTHING"*) and which the existing `SECRET-002` module measurably says nothing about.
  *Rejected: continuing `SECRET-001` at `-31`.* That index is detection, the evidence carrier,
  suppression, sentinels and the 18.2 evidence contract; regex precision is not in it.
  *Rejected: appending to `tests/test_secret_scan_precision.py`.* That module's subject is the three
  PREDICATES; mixing regex-alignment cases into it blurs the one distinction the file was created to
  draw, and editing it risks AC3.6.

- **`DN-18-3-5` — THE SCAN STAYS A REGEX SCAN; THE RESIDUAL LIMIT IS DISCLOSED, NOT FIXED.** Pairing
  the delimiters realigns the scanner; it does not tokenize Python. `tests/test_verdict_gate.py:719`
  (`'…"…'` — a literal containing its own delimiter) is invisible to the repaired regex too, and is
  recorded as such (AC2.2, §1.3).
  *Rejected: an `ast`-based literal walk.* It would be more correct and it is a different story:
  `run()` is documented as *"it does NOT re-parse"*, the detector must work on non-Python text
  sources, and swapping the scan engine is not a precision fix.

- **`DN-18-3-6` — `code_identity` IS BUMPED TO `secret_scan.v2`.** §0.7: the descriptor's own
  contract says *"bumped when its logic materially changes"*, the output measurably changed, and
  `argus/pipeline.py` memoizes the detect stage on that token — so without the bump a re-audited
  repository is served the pre-fix result, including the over-reports this story removes. ⛔ **This
  is the deliberate inverse of `DN-18-2-5`, which declined to bump on the explicit ground that its
  change was output-neutral.**
  *Rejected: not bumping.* Ships a security-detector fix that a cached re-audit never sees — the
  exact failure `AR6` / Story 5.3's invalidation lever exists to prevent.
  *Rejected: bumping `CACHE_KEY_SCHEMA_VERSION` instead.* That invalidates every closure for every
  detector; the descriptor token is the narrow lever and the one the model documents for this case.

- **`DN-18-3-7` — THE COLLIDING PERTURBATION FIXTURE MOVES, AND THAT IS A REPAIR.**
  `tests/test_cache_invalidation.py:229` pins its *synthetic perturbed* descriptor to
  `"secret_scan.v2"` — a plausible future real value — so a real bump makes three perturbation cases
  fail for a reason that has nothing to do with what they test. Measured: with a non-colliding live
  token those three are GREEN and only the golden moves. Moving the fixture to an unmistakably
  synthetic token (`tests/test_stage_memo_wiring.py:306`'s `secret_scan.v99` is the in-repo
  precedent) **restores** the perturbation.
  *Rejected: choosing `secret_scan.v3` for the live token to dodge the collision.* Numbering a v3
  with no v2 ever shipped is a lie in the artifact a future auditor reads first.
  *Rejected: deleting or skipping the three cases.* `DF-8-5-B` — do not close by loosening.

- **`DN-18-3-8` — `-09` IS A FENCE, NOT A WITNESS, AND IS LABELLED AS ONE.** The false-green guard is
  GREEN before and after by design. `AI-E14-1` makes an author-driven RED vacuity evidence; a case
  that can never go RED against the shipped body is a **contract pin**, and calling it a caught
  defect is the over-claim this repository keeps withdrawing. Its non-vacuity is proven by executing
  it against the naive lookbehind (AC4.3), which is the same shape Story 18.2 used for its `-30`.
  *Rejected: omitting it because it never goes RED.* It is the only guard that fences the specific
  mis-repair the ledger entry recommends.

### Locked decisions this story CITES rather than reopens

- **Story 2.5 / the LOCKED pattern-family set and file-scope rule** — the families and their
  `pattern_id`s are frozen for Story 4.4 + Story 6.5; the detector is deliberately NOT gated to test
  files. Both hold across this change.
- **Story 2.5 / the structural redaction guarantee** — redaction is the ABSENCE of a value field.
  Untouched: no emitted model gains a field here.
- **Story 5.1 / `DN-DETECTORSET`** — the detector-set hash is taken over the declared frozen
  descriptor tuple; editing `code_identity` is the sanctioned invalidation lever. `DN-18-3-6` rests
  on it.
- **Story 5.3 / AR6** — the key-busting lever. Same.
- **Story 10.3 / AC4.5** — built-in suppressions emit **no** `operator_suppressed_secret` record.
  ⛔ This story must not start emitting one; measured, the suppression-record count is **0 → 0**.
- **Story 18.1 / `DN-18-1-1`..`-7`** — the length-gated sentinel match and the safeguard's repaired
  short-circuit. `done`; not reopened, and `-26` is a witness this story keeps green.
- **Story 18.2 / `DN-18-2-1`..`-6`** — the deleted redaction call, the replaced banner, the surviving
  carrier. `done`; not reopened.
- **architecture §Guard-fire ledger (2026-08-23)** — an author-driven RED is vacuity evidence, not
  *"this guard caught a defect"*. `DN-18-3-8` rests on it.

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| entry | bearing |
|---|---|
| **`DF-AUD-DETECT-E`** | **THE SUBJECT.** This story is chartered to discharge it (AC6.1). Its finding is re-measured in §0.1/§0.3; its proposed repair and its severity rationale are both falsified in §0.2/§0.4 and corrected append-only. |
| **`DF-AUD-DETECT-C`** | ⛔ OPEN. Nothing here dispositions it, and no timing figure is taken. |
| **`DF-AUD-DETECT-D`** | Story 17.3. Not this story. |
| **`DF-AUD-DETECT-F`** | Story 18.4. ⛔ `argus/detectors/base.py` is its file; do not touch it. |
| **`DF-10-3-B` / `DF-10-3-C`** | ⛔ OPEN, untouched, out of scope. |
| **`DF-10-4-B`** | Prior art for *"a `DetectorResult` field recorded and never read back"*. Cited by Story 18.2; **not** dispositioned here. |
| **`DF-INV-MERGE-A`** | OPEN, DECIDED-NOT-YET-APPLIED. Governs how this PR may land (§2.5, AC7.3). |
| **`DF-INV-WHEEL-A`** | OPEN. Running Argus inside its own repo reddens `TC-ArgusAgent-DOCS-001-54` for an unrelated reason. If you hit that red, it is **not yours**. |
| **`DF-INV-REFS-A`** | OPEN. Six referenced ids do not resolve. Do not "fix" one in passing. |
| **`DF-13-5-A`** | ⛔ **OPEN and UNSPENT.** Nothing here spends it. |
| **`DF-8-5-B`** | *"Do not close it by loosening an assertion."* The standing rule over AC3.6, AC5.3 and AC8. |
| **`DF-INV-LEDGER-A`** | Why AC6.5 says grep before filing. |
| **`DF-16-6-F`** | Commit messages are pure ASCII (AC7.2). |

### Dependencies — none are added, and that is a requirement

`secret_scan.py` imports `math`, `re`, `Counter`, `Fraction`, `Sequence`, `pydantic`, and four
first-party modules. **This story adds none and removes none.** The repair is four Python `re`
constructs — one negative lookbehind and three named-group backreferences — all of them in the
standard library since forever and all already used elsewhere in this tree.

⛔ **Nothing here requires web research.** There is no third-party API surface involved, the regex
constructs are `re`-module primitives whose semantics are pinned by CPython 3.11 (the version this
suite runs on and the version CI's matrix pins), and every behavioural claim in §0 was obtained by
running them rather than by reading about them. ⚠️ **One CPython detail is load-bearing and was
verified by execution, not assumed:** `re` **does** support a variable-free negative lookbehind of
fixed width 1 (`(?<![A-Za-z0-9])`) — a variable-width lookbehind would raise at compile time, so
**do not** try to widen it into an alternation of different lengths.

### Standing rules (non-negotiable)

- **AR7** — one arithmetic, one vocabulary, never forked. Three spellings of "a quoted literal" in
  one module is that fork; `DN-18-3-2` removes it.
- **AR8** — pure/impure separation. `secret_scan.py` is PURE and stays PURE.
- **AR6** — the cache-invalidation lever exists so a changed detector does not serve stale results.
  `DN-18-3-6`.
- **NFR-P1** — no clock, randomness, network or host-dependent comparison on any decision path.
- **NFR-S1 / NFR-S2** — no source byte, no secret value, no absolute host path in any artifact,
  message or test assertion.
- **NFR-M1** — 1,200 physical lines per module. **Split, never shave, never exempt.**
- **NFR-M2** — frozen, additive-only contracts.
- **`AI-E11-1`** — every guard asserts its population is non-empty before asserting an absence.
- **`AI-E13-1`** — the local suite is Windows-only; CI runs an ubuntu matrix.
- **`AI-E12-3` / `AI-E12-6`** — *a disposition recorded in prose and not in the ledger is not a
  disposition.*
- **`AI-E14-1`** — an author-driven RED is vacuity evidence, not "this guard caught a defect".
- **`AI-E9-7`** — do not re-derive an argument from a stale figure.
- **`AI-E9-8`** — do not assert a new finding onto an existing story to give it a home.

### Previous-story intelligence

**Story 18.2 (`done`, this epic, immediately before) — what it hands you:**

1. ⛔ **It deliberately did NOT touch either regex**, naming *"the regex precision work
   (`DF-AUD-DETECT-E` → Story 18.3)"* in its own "what this story is NOT" list. **Both REDs are
   intact and they are yours.**
2. **Its output-neutrality framing is NOT reusable here.** 18.2 proved *0 of 251 differ*; this story
   must prove the opposite thing (`DN-18-3-3`). ⛔ Copying its AC2 shape would make this story
   satisfiable only by doing nothing.
3. ⛔ **Its `DN-18-2-5` declined a `code_identity` bump on the explicit ground that its change was
   output-neutral.** Read that decision before you read `DN-18-3-6`: this story takes the opposite
   arm for the reason 18.2's own text supplies.
4. **Its sweep discipline is the one to copy:** engine-vs-engine over ONE identical population,
   including the story's own new test module. That was 18.1's only review finding, and 18.2 fixed
   it (AC3.1).
5. **Its ledger note is the FORM for yours**: dated, append-only, entry above unrewritten, measured
   before/after, guards named, collateral disclosed, and the things it does **not** disposition
   listed explicitly.
6. **Four commits, and write the `Evidence-partition: none` trailer the FIRST time** — 18.1 lost a
   sha over it; 18.2 did not.
7. **Its `-30` is the precedent for `-09`**: a contract pin that is GREEN before and after, disclosed
   in exactly those terms rather than claimed as a caught defect (`DN-18-3-8`).

**Story 18.1 (`done`)** left `TC-ArgusAgent-SECRET-001-26`, which is the only end-to-end witness that
catches this story's most likely wrong turn (§0.2). ⛔ **Read `-23`..`-27`; edit none of them.**

**Story 2.5** built this detector, these regexes and the alarm-fatigue argument they serve. ⛔ Read
its record; edit it never.

### Git intelligence

Recent arc (last 8 commits): `8b6c304 → ee7e252 → fa5e463 → c288d40` is Story 18.1's four-commit arc;
`57a278f → 2cc5128 → 25ff87f → 62fd1b9` is Story 18.2's, in the same shape.

- **`argus/` is quiet again.** The last change to it is `2cc5128` (18.2's `feat`), and the three
  dogfood artifacts were regenerated for exactly that sha at `25ff87f`. **Your `feat` commit moves
  past it, so those artifacts go stale and must be regenerated** (§0.8).
- **Both prior stories in this epic were reviewed by re-execution rather than by reading**, and both
  reviews independently reproduced the story's headline measurement. ⛔ **Expect yours to be
  re-executed.** Every figure you write down should be one you can hand someone a command for.
- **The culture this week is: measure, then withdraw what the measurement does not support.** 18.1
  falsified `DF-10-3-B`'s safety claim; 18.2 falsified `DF-AUD-DETECT-B`'s Story-2.5 reasoning; §0.2
  and §0.4 do the same to two claims in `DF-AUD-DETECT-E`. **Do it again in your completion notes if
  Task 0 disagrees with any row of §0.**

### References

- [epics.md](../epics.md) — `## Epic 18` (line ~3609) and `### Story 18.3` (~3688). ⛔ Its *"AWAITING
  OPERATOR APPROVAL"* paragraph and the append-only approval note beneath it are **left as written**
  (§3.4 / the Epic 16 precedent). **Not a blocker; not to be edited.**
- [sprint-change-proposal-2026-08-24.md](../sprint-change-proposal-2026-08-24.md) — §1 (the audit),
  §2 (impact: `prd.md` **None**, `architecture.md` **None**), §4 (Epic 18's four stories).
  **APPROVED 2026-08-24 by XAgent007 (Engineering Lead).**
- [deferred-work.md](../deferred-work.md) — `DF-AUD-DETECT-E` (~line 6619), `DF-AUD-DETECT-A`'s and
  `DF-AUD-DETECT-B`'s disposition notes (the FORM for yours), the Epic 17/18 scheduling table
  (~6730). ⛔ **Line numbers drift; grep by id.**
- [18-1-the-sentinel-table-matches-values-not-substrings-of-them.md](18-1-the-sentinel-table-matches-values-not-substrings-of-them.md)
  and
  [18-2-the-redaction-call-keeps-the-evidence-it-computes.md](18-2-the-redaction-call-keeps-the-evidence-it-computes.md)
  — ⛔ **Read; never edit** (both `done`).
- [2-5-hardcoded-secret-detector-producer-side-redaction.md](2-5-hardcoded-secret-detector-producer-side-redaction.md)
  — the locked family set and the redaction contract. ⛔ **Read; never edit.**
- [E-PRD/prd.md](../E-PRD/prd.md) — **FR11** (`:528`, this detector's FR), **FR28** (`:573`),
  **FR33** (`:551`, the alarm-fatigue driver §1.1 rests on). ⛔ None is amended.
- [architecture.md](../architecture.md) — `:1148` (the guard-fire rule `DN-18-3-8` rests on),
  `:1176` (this module in the directory tree), §G *Security & Governance*. ⛔ **Read, do not edit**
  (AC6.6).
- `argus/detectors/secret_scan.py` — the module under change. **Read the whole docstring (`:1`–
  `:104`) before touching a line**, and `_scan` (`:549`–`:594`) before touching a regex.
- `argus/cache/key.py` — `DetectorDescriptor` (`:152`), `FROZEN_DETECTOR_SET` (`:186`–`:192`),
  `detector_set_content_hash` (`:203`). **One token moves; nothing else.**
- `argus/cache/stage_memo.py` (`:155`, `:239`) and `argus/pipeline.py` (`:166`) — the memoization
  path that makes AC5.1 a correctness requirement. **Read; do not edit.**
- `tests/test_secret_scan_precision.py` — `KNOWN_SECRET_SHAPES` / `ORDINARY_LITERALS` and the
  register the new module should be written in. **Read; do not edit.**
- `tests/test_secret_sentinel_matching.py` (`-23`..`-27`), `tests/test_secret_evidence_contract.py`
  (`-28`..`-30`) — this epic's two prior guard modules. **Read; do not edit.**

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC3.1, AC3.6, AC7.4)

- [ ] `git status --porcelain` — record it. ⚠️ **Expect it to be non-empty** (§0.0: four
      Story-18.1/18.2 files). Record which files are not yours **before** you stage anything.
- [ ] Clear `__pycache__`; export `PYTHONDONTWRITEBYTECODE=1`. **Story 16.5 lost a commit to a false
      RED from stale bytecode.**
- [ ] Re-run §0.1's and §0.3's reproductions through the shipped `run()`. **Expect 1 / 1 / 1 finding
      for the three defect-1 lines and 1 → 0 for the mismatched-delimiter line.** If a premise is
      false, **STOP and report**.
- [ ] Re-run the two `argus/**` censuses. **Expect 3 word-char-left matches (1 in a comment) and
      462 mismatched spans / 3 surviving.** These are the entry's own figures; record any drift.
- [ ] Re-run §0.4's two-line reproduction. **Expect shipped 0, paired 1.** ⛔ This is the falsified
      severity claim; if it does not reproduce, AC6.2(ii) must be withdrawn, not softened.
- [ ] Re-run §0.2's naive-lookbehind probe **and** the whole suite under it. **Expect three zeros
      and `TC-ArgusAgent-SECRET-001-26` RED.** Record the exact failure text.
- [ ] Re-run §0.6's engine-vs-engine sweep. **Expect 252 files, 91 → 90 findings, 38 → 37 files,
      exactly five spans moving.** Record the pair; it is the only baseline you can take.
- [ ] Re-derive the `argus/`-only figure (**expect 40**) and read the committed
      `minions-dogfood-proof.md` numbers (**expect `hardcoded_secret` 40, total 173**).
- [ ] Confirm the `code_identity` coupling: `argus/pipeline.py:166` imports `memoize_detect_stage`,
      and bumping the token moves `detector_set_content_hash` (**expect `9954e854…` → `fbec7912…`**).
- [ ] Full suite (**expect 1,724 collected, exit 0**), `mypy argus` (**95 files, clean**), `bandit`
      (**clean**). Record all three.
- [ ] Re-measure §0.9's ledger byte state and both SECRET indices (**expect `-001-30` and
      `-002-07`**).
- [ ] `python -m pytest tests/test_governance_record_integrity.py -q` — **expect green** (this file
      claims no disposition yet).
- [ ] Record every figure that came out different. **Expect at least one.**

### Task 1 — THE EQUIVALENCE INSTRUMENT, BUILT BEFORE THE CHANGE (AC3.1, AC3.2, AC3.5)

- [ ] Write the sweep as a throwaway script **outside the repository** (scratch dir) that drives
      `run()` over `git ls-files -- '*.py'` and emits a `{path: canonical DetectorResult}` map plus a
      per-span finding census.
- [ ] Capture the **pre-change** map to a scratch file. ⛔ Do not commit the instrument — a whole-repo
      sweep in the suite is the slow, environment-coupled test this project has removed twice
      (`DN-18-2-6`).

### Task 2 — THE GUARDS, WRITTEN AGAINST THE SHIPPED BODY (AC4)

- [ ] Create `tests/test_secret_scan_regex_precision.py`, opening `TC-ArgusAgent-SECRET-002-08` and
      continuing upward. Docstring in the `SECRET-002` register: both defects, both censuses, §0.2's
      false-green table, §0.4's reproduction, the RED evidence, and *"key material is synthetic and
      built in the module"*.
- [ ] `-08` left-anchor guard (AC4.2) — with a positive control asserted first (`AI-E11-1`), and a
      value the entropy family rejects or an assertion on `pattern_id` (§2.3).
- [ ] `-09` false-green fence (AC4.3) — `DB_PASSWORD` / `_API_KEY` / `SMTP_PASSWORD` still reported.
      ⛔ Docstring says **fence, not witness**, cites `TC-ArgusAgent-SECRET-001-26`, and records the
      executed proof that it goes RED against the naive lookbehind.
- [ ] `-10` paired-delimiter guard (AC4.4) — mismatched rejected, both matched controls accepted.
- [ ] `-11` realignment recall guard (AC4.5) — §0.4's `src = 'blob = "…"'` reported after the change.
- [ ] `-12` class guard (AC4.6) — no `['\"]…['\"]` shape survives in the module's pattern constants,
      and the four named families still compile.
- [ ] ⛔ No chosen value is in the public-sentinel table (§2.7); every case runs on
      `argus/prod/settings.py` (AC4.8).
- [ ] Confirm the new module is ≤ **1,200** physical lines (AC7.5) — `len(text.splitlines())`, the
      arithmetic `tests/test_module_size_ceiling.py:176`–`:183` uses.

### Task 3 — DRIVE THEM RED, THEN MAKE THE CHANGE (AC4.7, AC1, AC2, AC5.1)

- [ ] Run the new module **against the shipped `secret_scan.py`**. **Record the exact failure text of
      every case that goes RED, and which do not.** ⛔ Expect `-08`, `-10`, `-11`, `-12` RED and `-09`
      GREEN by design. A case other than `-09` that stays GREEN pre-change is not a guard — fix the
      case, not the assertion, and record that you found it.
- [ ] ⛔ **Two safe mechanisms, one unsafe.** SAFE: (a) monkeypatch from a pre-change copy of the
      module held outside the repository; (b) `git stash push -- argus/detectors/secret_scan.py` —
      **explicit pathspec**, and only after `git status --porcelain -- argus/detectors/secret_scan.py`
      confirms the only change there is yours. ⛔ UNSAFE: `git stash` with no pathspec — a peer
      session's four files are in this tree (§0.0).
- [ ] Apply AC1.1's lookbehind and AC1.2's three backreferences. ⛔ **Verify the named `secret` group
      still resolves at every call site** (AC1.3).
- [ ] Apply AC2's docstring corrections and AC2.4's three site comments. ⛔ **Nothing else in the
      docstring is reflowed.**
- [ ] Bump `argus/cache/key.py:187`'s `code_identity` to `secret_scan.v2` (AC5.1). ⛔ **One token.**
- [ ] Re-run the new module. **Record GREEN, all five.**

### Task 4 — PROVE NOTHING REAL DISAPPEARED (AC3)

- [ ] Re-run Task 1's sweep post-change and diff the two maps. ⛔ Take **both** sides over the SAME
      file list — **253** once the new test module is tracked — and **state which population count
      the pair was taken over** (AC3.1).
- [ ] Enumerate and adjudicate **every** removed finding by path, line, source text, pattern id and
      one sentence of cause (AC3.2). **Expect three.** ⛔ A fourth, or a credential-shaped one, is
      **AC8**.
- [ ] Enumerate every gained finding the same way and prove it non-blocking (AC3.5). **Expect two.**
- [ ] Run the recall matrix over the eight `KNOWN_SECRET_SHAPES` (AC3.3) and the naming matrix
      (AC3.4). ⛔ **Record both tables in the completion notes.**
- [ ] Full suite, green, **no assertion loosened**; the seven secret-domain modules pass **unedited**
      (AC3.6). ⛔ Record `TC-ArgusAgent-SECRET-001-26`'s green explicitly.
- [ ] Coverage with `--cov-fail-under=80`; record the percentage (AC3.7).

### Task 5 — THE CACHE COLLATERAL (AC5.2, AC5.3)

- [ ] Regenerate `tests/test_cache_key.py`'s golden **by execution** and add the dated one-line
      rationale to its docstring (AC5.2). ⛔ **Derive the value; do not paste §0.7's prediction.**
      Record whether the derived value matched the prediction.
- [ ] Move `tests/test_cache_invalidation.py:229`'s perturbation fixture off the colliding literal
      (AC5.3), with a one-line comment. ⛔ Verify the perturbed set's hash still differs from the
      live set's, and that all three `test_detector_set_change_*` cases are green **for the right
      reason**.
- [ ] Record both edits, with their cause, for the ledger note (AC6.4).

### Task 6 — THE LEDGER (AC6.1–AC6.4)

- [ ] ⛔ **Grep first** (`DF-INV-LEDGER-A`). Then append, **in binary mode**, `DF-AUD-DETECT-E`'s
      dated disposition note: the repair taken at each site, **both falsifications in terms**
      (AC6.2), the guard ids, the before/after sweep with the five moving spans, the `code_identity`
      bump with its reason, the cache collateral (AC6.4), and an explicit list of what this does
      **not** disposition.
- [ ] Verify afterwards: **0** CRLF pairs, **exactly one** lone `\r`, and a `git diff` confined to
      the appended lines.
- [ ] ⛔ Confirm `architecture.md`, `E-PRD/prd.md`, `epics.md`, `2-5-…md`, `18-1-…md` and `18-2-…md`
      are **unmodified** (AC6.6) — `git status --porcelain` must not list any of them as *yours*.

### Task 7 — GATES, DOGFOOD REGENERATION AND THE COMMIT ARC (AC7.2, AC7.4, AC7.7)

- [ ] Commit `argus/` + `tests/` **by explicit path**, with the trailer **`Evidence-partition: none`**
      as a whole line in the commit message (§0.8). ⛔ Never `git add -A`.
- [ ] `python -m pytest tests/test_gate_seal.py -q` immediately after that commit — this is where
      Story 18.1 lost a sha.
- [ ] `python scripts/regenerate_dogfood_artifacts.py` on the now-clean `argus/` tree; commit the
      three artifacts separately. ⛔ Exit 2 means the tree is dirty — fix the tree, never pass
      `--allow-dirty-argus`. **Record the artifact deltas** — expect `hardcoded_secret` 40 → 37 and
      the `open_llm_adapter.py:170` locator to leave the sample list.
- [ ] Run the full AC7.4 gate list. **Record every exit code.** Mark the run **LOCAL / Windows-only**
      (AC7.6).

### Task 8 — HAND-OFF (AC6.5, AC7.3, AC7.7)

- [ ] `git status --porcelain` — the write set equals AC7.1 exactly, and no Story-18.1/18.2 file rode
      along.
- [ ] Completion notes: every re-measured §0 figure, the observed REDs with their exact text, the
      pre/post sweep with all five moving spans adjudicated, the recall and naming matrices, the
      cache collateral, `-09`'s fence-not-witness disclosure, §1.3's three unfixed-and-unfiled gaps,
      every exit code, and **any §0 premise found false**.
- [ ] ⛔ If the PR lands squashed or rebased, re-run the regeneration on `master`
      (`DF-INV-MERGE-A`, AC7.3).

---

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

## Change Log

| date | who | what |
|---|---|---|
| 2026-08-25 | bmad-create-story (Opus 5) | Story contexted at HEAD `62fd1b9`; `backlog` → `ready-for-dev`. Every §0 figure measured by execution. Three premises of `DF-AUD-DETECT-E` found false: its proposed lookbehind is a false green (§0.2), its severity rationale is falsified for defect 2 (§0.4), and the defect class occurs at three sites (§0.5). `DN-18-3-6` adds a `code_identity` bump that Story 18.2 explicitly declined for the opposite reason. |
