---
baseline_commit: 6128466f86c3c34591d0338df4d4995b75663ba7
---

# Story 16.2: Part of the bench is sealed before anything is run

Status: done

| | |
|---|---|
| **Epic** | 16 — Spend the Round Well — strengthen the gate, then measure once |
| **Story key** | `16-2-part-of-the-bench-is-sealed-before-anything-is-run` |
| **Source** | [sprint-change-proposal-2026-08-20.md](../sprint-change-proposal-2026-08-20.md) §4.3(2), **✅ APPROVED by XAgent007 (Engineering Lead) 2026-08-20** · [epics.md](../epics.md) §Epic 16 (`epics.md:3019`), §Story 16.2 (`epics.md:3098`) |
| **Contexted on** | HEAD `6128466` (`docs(16-1): record the passing re-review, and close the story`), working tree **CLEAN**, **13 ahead of `origin/master`, 0 behind** |
| **Baseline gates (measured, this tree)** | full suite **1,658 collected · exit 0 · 0 failed · 0 skipped** with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` · `mypy argus` **Success, 88 source files** · `bandit -r argus --severity-level medium` **No issues identified** · `build_gate_decision.py --check` exit **0** · `build_adjudication_record.py --check` exit **0** |
| **Authorisation** | The 2026-08-20 approval unblocks **16.1, 16.2 and 16.3 only**, each deriving and recording its **own** constants. It does **not** unblock 16.4, does **not** authorise ratification (protocol §6 **R2**), a fetch, staging, or spending `DF-13-5-A`'s ONE round. |
| **Ordering** | 🔒 **BINDING.** This story's commits must **precede** every commit containing Argus output over any bench member. The ancestry *guard* is 16.4's deliverable; this story's obligation is to **land first** and to **record its own seal sha** for 16.4 to cite — the Story 15.1 `CRITERIA_COMMIT_SHA` pattern, in two commits. |
| **Direction** | ⛔ **STRENGTHENING ONLY.** Every change here makes clearing **harder**. It touches neither the ≥80% `Fraction`, `VALIDATION_SET_FLOOR_N`, the five ratified members, nor `MANIFEST_FIELDS`. |

---

## Story

As the Argus maintainer,
I want **a partition of the ratified bench sealed before any detector output exists over it**,
So that the gate figure is computed over a population the tool was never tuned against.

### What this story IS

**A pre-committed, mechanically reproducible partition of the bench, and one new protocol §5
condition that makes it binding.** The partition is a **function of each member's pinned commit
sha** — a per-row bisection, not a rank within a set — frozen in a commit that precedes every commit
containing Argus output over any member. A member's partition is **structurally** readable off its
manifest row and **validated at construction**, so it cannot be edited to flatter a result. The gate
becomes evaluable only over evidence drawn from the **sealed** partition; tuning happens against the
**open** one; and a guard requires any detector change dated after the seal to say which partition
its evidence came from.

### What it is NOT

- **NOT a narrowing.** `VALIDATION_SET_FLOOR_N` stays **5**. No member is dropped, no member is
  re-weighted, `eligible_member_count()` is unchanged, and every member stays a member of the
  manifest with its findings recorded and disclosed. It **partitions**; it does not narrow.
  ⛔ **AC5 makes this concrete and forbids the obvious implementation** — see §2.5, where the
  narrowing design is proved by execution to `raise`.
- **NOT a `MANIFEST_FIELDS` change.** The schema stays **CLOSED at 9**. §0.5 establishes by
  execution that the partition can be a validated, structural property of the row *without*
  extending it, and names the escalation path if anyone judges otherwise. **The dev may not extend
  `MANIFEST_FIELDS` on its own authority.**
- **NOT a run, a ratification, a fetch or a stage.** All 14 candidate rows keep
  `eligible_for_n=False`; `eligible_member_count()` stays **5**; no detector executes over any
  repository, ratified or candidate. Protocol §6 **R2** is 16.4's operator act.
- **NOT an adjudication.** No row moves; no `expert_hours` are recorded; the record's 31 judgements
  of 2026-08-17 are untouched.
- **NOT a protocol re-version.** ⛔ **No `V1.4` row.** See §2.3 — this is a **locked operator
  decision of 2026-08-20**, not a preference.
- **NOT the rule-class arm.** `DF-16-1-A` stays **OPEN and unlanded**. Do not reopen it.
- **NOT the yield floor (16.3).** This story must **compose** with it and must not pre-empt it.
- **NOT an approval of anything.** [sprint-change-proposal-2026-08-20-amendment-A.md](../sprint-change-proposal-2026-08-20-amendment-A.md)
  is **registered and UNAPPROVED**; nothing in it is in scope, and this story does not approve,
  apply, cite as authority, or act on any part of it.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `6128466`

> Every figure below was derived on the live tree during contexting, **read-only**, out of tree.
> `git status --porcelain` was **empty** before and after. Story 15.1's fix round and Story 16.1's
> round 1 both exist because a figure *stated as measured* turned out wrong inside the story's own
> record; §0 exists so the dev starts from measurements rather than from prose. **Re-derive before
> you write anything down, and strike rather than erase if a figure moves.**

### §0.1 The corpus, the bench, and what has been run over what

| Quantity | Value | Read from |
|---|---|---|
| Manifest rows | **21** | `tests/corpus/_manifest.VALIDATION_CORPUS` |
| Ratified eligible members (`N`) | **5** | `_manifest.eligible_member_count()` |
| Bench candidates awaiting R2 | **14**, all `primary_language=python`, all `eligible_for_n=False` | `ineligible_reason == "candidate - awaiting operator ratification (protocol section 6 R2)"` |
| Permanently ineligible | **2** — `argus-self-audit`, `minions-story-7-2-superseded` | same |
| `VALIDATION_SET_FLOOR_N` | **5**, one floor, never forked (DN-3) | `registry_module().VALIDATION_SET_FLOOR_N`; `_manifest.validation_floor_n()` |
| `MANIFEST_FIELDS` | **9**, CLOSED | `_manifest.MANIFEST_FIELDS` |
| **Members with PRIOR Argus output** | **exactly the 5 ratified** — `ai-body-runtime`, `agent-markovich`, `minions`, `xagents-webapp`, `agent-smith`. **ZERO of the 14 bench candidates.** | the `members[]` arrays of **both** `adjudication-set.json` (2026-08-16) and `adjudication-set-13-5.json` (2026-08-18); `corpus_read_proof.members_audited = 5` |
| Live adjudication-record rows | **31**, from **2** members (`minions` 24, `agent-smith` 7), **1** rule class, **26 FP / 5 BORDERLINE / 0 UNADJUDICATED**, all judged by `XAgent007 (Engineering Lead)` on 2026-08-17, `protocol_version: V1.3` | `adjudication-record.json`, read through the shipped `load_record` / `live_rows` API |
| Committed gate outcome | **`BLOCKED`** — empty emitted blocking population with a positive corpus-read proof | `gate-decision-record.json` |
| §5 condition verdicts today | `precision` **UNEVALUABLE** · `clean-repo-FP` **MET** · `corpus-floor` **MET** · `recorded-cleared` **FAILED** · `denominator-breadth` **FAILED** (16.1's) | same |

⛔ **The load-bearing fact on this page: the five ratified members have all been run over, twice.
The fourteen bench candidates have never been run over at all.** That asymmetry is what makes a
seal possible now and impossible later, and it is the reason the rule below has two conjuncts
rather than one.

### §0.2 ⛔ THE RULE, AND THE PARTITION IT PRODUCES — derived, then measured

**The rule this story freezes (AC1), stated once:**

1. **PRIOR-OUTPUT OVERRIDE.** A member over which Argus output already existed when the seal was
   taken is **`pre-seal`**, unconditionally, whatever its sha says. *A member that has already been
   run over cannot be a holdout, and a rule capable of sealing one would manufacture a fake
   holdout.*
2. **THE BISECTION.** Every other member is **`sealed`** iff `int(commit_sha, 16) % 2 == 1` — the
   **parity of the pinned object name read as an integer** — and **`open`** otherwise.

> ✅ **Measured, so the dev does not spend a round on a false choice:** across all 21 rows,
> `int(sha, 16) % 2` and `int(sha[-1], 16) % 2` agree on **every** row (0 disagreements).
> *"Parity of the whole sha"* and *"parity of the last hex digit"* are **the same rule**, not two
> options. State it as the parity of the integer, because that is the canonical property of the
> object name rather than a choice of digit position.

**THE FROZEN PARTITION, computed on this tree (this is the table AC1.3 requires the dev to
materialize and a guard to re-derive — it is reproduced here so a reviewer can check the dev's
by hand):**

| # | member_id | pin (first 8) | parity | **partition** | co-occurrence files |
|---|---|---|---|---|---|
| 1 | `ai-body-runtime` | `4480ffde` | 0 | **pre-seal** | — |
| 2 | `agent-markovich` | `a5616686` | 0 | **pre-seal** | — |
| 3 | `minions` | `ec63b729` | 0 | **pre-seal** | — |
| 4 | `xagents-webapp` | `33a86525` | **1** | **pre-seal** ⚠️ | — |
| 5 | `agent-smith` | `9ab774d7` | **1** | **pre-seal** ⚠️ | — |
| 6 | `argus-self-audit` | `bc55e361` | 0 | open (permanently ineligible) | — |
| 7 | `minions-story-7-2-superseded` | `00000000` | 0 | open (permanently ineligible) | — |
| 8 | `aws-aws-sam-cli` | `5b6ebdba` | 1 | **SEALED** | 215 |
| 9 | `celery-celery` | `2c42237d` | 1 | **SEALED** | 71 |
| 10 | `certbot-certbot` | `abf9d1b2` | 1 | **SEALED** | 53 |
| 11 | `conda-conda` | `ad60271d` | 1 | **SEALED** | 22 |
| 12 | `getsentry-sentry-python` | `064542dd` | 1 | **SEALED** | 25 |
| 13 | `googleapis-google-auth-library-python` | `2ea24b03` | 1 | **SEALED** | 45 |
| 14 | `mitmproxy-mitmproxy` | `bae1a7e1` | 0 | open | 18 |
| 15 | `pypa-pip` | `0268b0aa` | 0 | open | 12 |
| 16 | `python-poetry-poetry` | `92b74dcf` | 0 | open | 35 |
| 17 | `redis-redis-py` | `39722758` | 0 | open | 42 |
| 18 | `scrapy-scrapy` | `df64fe32` | 0 | open | 12 |
| 19 | `spotify-luigi` | `715f65c4` | 0 | open | 32 |
| 20 | `streamlink-streamlink` | `a9d6db50` | 0 | open | 22 |
| 21 | `tox-dev-tox` | `c3927c64` | 0 | open | 10 |

**Bench split: 6 SEALED / 8 open of 14.**
Sealed co-occurrence mass **431 of 614 (70.2%)**; all **6 of 6** sealed candidates clear Story
15.1's `COOCCURRENCE_FILE_FLOOR = 10`, as do all 8 open ones — they were selected on it.

⚠️ **Rows 4 and 5 are why conjunct 1 is load-bearing rather than decorative.** `xagents-webapp` and
`agent-smith` both have **odd** pins: the bisection *alone* would have declared two already-audited
members "sealed", one of which (`agent-smith`) supplied 7 of the record's 31 judged findings.
A holdout that has already been peeked at is not a holdout, and this project would have shipped one.

> ⛔ **The order in which this was decided, recorded because it is the whole integrity claim.** The
> rule was chosen on **structural** grounds (§0.2's three rejected alternatives, DN-16-2-2) and the
> table above was computed **afterwards**. The 70.2% sealed mass is a **consequence measured after
> the choice**, not a reason for it. To make that checkable rather than asserted, all three
> candidate rules were computed and are recorded in DN-16-2-2 with their outcomes — including the
> two that put **less** defect-class mass on the sealed side. **A rule chosen because of the split
> it produces is the corpus-shopping failure mode with an extra step.**

### §0.3 ⛔ THE BREADTH INTERACTION — MEASURED, because a seal that shuts the gate is a shutdown

Story 16.1 landed §5's fifth condition: the ratio is evaluable only over **≥ `(VALIDATION_SET_FLOOR_N + 1) // 2` = 3**
distinct **contributing** members. Story 16.1 HALTED rather than land an arm that could not be
satisfied. **The same question must be answered here, and it is:**

| Question | Answer | How it was measured |
|---|---|---|
| Is the breadth floor a function of the corpus size? | **No** — `(VALIDATION_SET_FLOOR_N + 1) // 2`. It is **3** regardless of how many members are sealed or ratified. That stability was a deliberate 16.1 decision (a proportion *"would demand 3 today and 12 after"*). | `gate_breadth.contributing_member_floor`, read live |
| How many members are on the sealed side? | **6** | §0.2's table |
| Do they carry the defect class? | **All 6** clear `COOCCURRENCE_FILE_FLOOR = 10`; they hold **431 of the bench's 614** co-occurrence files | `adjudication_caveat` measurements frozen by Story 15.1 |
| So is breadth **satisfiable** over the sealed partition? | ✅ **YES — 6 available against a floor of 3, slack 3.** This is a strengthening with room, not a shutdown. | derived |
| Is it satisfiable **today**? | ❌ **No, and that is correct.** Sealed ∩ ratified = **∅**, so sealed contributions = **0**. The gate cannot clear on evidence that predates the seal. | measured: 0 of the record's 31 live rows come from a sealed member |

⛔ **THE DISTINCTION FROM 16.1's HALT-1, STATED SO IT IS NOT MISREAD AS THE SAME THING.** 16.1
halted because a rule-class floor of ≥2 was unreachable **by construction with the shipped detector
set** — no operator act could make it reachable, and the work that would was outside the
authorisation. Here, reachability is restored by an act **the plan already schedules**: 16.4's §6 R2
ratification. **The closure path is countable and belongs in the hand-off:**

> **To make `CLEARED` reachable at all, protocol §6 R2 must ratify at least THREE of these six:**
> `aws-aws-sam-cli`, `celery-celery`, `certbot-certbot`, `conda-conda`, `getsentry-sentry-python`,
> `googleapis-google-auth-library-python`. Ratifying only open-partition members leaves the gate
> permanently `BLOCKED` on this condition — which is honest, and which the operator must be told
> **before** taking the act, not discovered after.

**This is a condition, not a prediction.** Whether three sealed members actually *emit* a
verdict-eligible finding is unknowable without running, and this story does not run. The claim
here is narrow and true: **the seal does not make the breadth condition unsatisfiable.**

### §0.4 Module headroom, measured with the ceiling guard's own `_physical_line_count` (`_CEILING = 1200`)

| Module | Lines | Headroom | Note |
|---|---|---|---|
| **`argus/precision/gate_decision.py`** | **1,197** | ⛔ **3** | **`DF-16-1-B`'s SPLIT-FIRST trigger. See §2.1 — this is a TASK, not a footnote.** |
| **`tests/test_gate_decision.py`** | **1,193** | ⛔ **7** | Effectively full. Only the minimum re-authorings may land here; new guards go to a NEW module. |
| `argus/precision/gate_breadth.py` | 436 | 764 | 16.1's module — **read it, copy its shape, do not edit its subject** |
| `argus/precision/gate_disclosure.py` | 341 | 859 | ✅ the natural home for `sealed_corpus_member_ids` / the `partition` key on `ratified_corpus_members()` |
| `tests/corpus/_manifest.py` | 886 | 314 | the manifest — comfortable |
| `tests/test_validation_corpus.py` | 927 | 273 | `-22`..`-31` live here; comfortable |
| `tests/test_candidate_selection.py` | 698 | 502 | `-74`..`-79`; the `-75` ordering-guard **template** lives here |
| `tests/test_gate_breadth.py` | 622 | 578 | holds `expected_section_5_outcome` — **extend it, never fork it** |
| `argus/precision/replay_harness.py` | 825 | 375 | the shared arithmetic — read and reuse, never fork |
| `scripts/build_gate_decision.py` | 435 | 765 | comfortable |
| `argus/detectors/vacuous_test.py` | 1,196 | 4 | `DF-15-2-D`. ⛔ **NOT on the write set — do not open it.** |
| `tests/test_vacuous_density.py` | 1,159 | 41 | `DF-15-2-E`. Not on the write set. |

### §0.5 `MANIFEST_FIELDS` — the AC2 question, ANSWERED BY EXECUTION

AC2 requires *"a member's partition is a field on its manifest row, validated at construction"*.
`MANIFEST_FIELDS` is **LOCKED at 9**. The question was measured rather than assumed:

- **`TC-ArgusAgent-PRECISION-001-22` compares `{f.name for f in dataclasses.fields(CorpusMemberSpec)}`
  against `set(MANIFEST_FIELDS)`, in both directions** (`tests/test_validation_corpus.py:153`).
  A `@property` is **not** a dataclass field. ✅ **A derived `partition` property therefore satisfies
  "structurally readable off the row" WITHOUT touching `MANIFEST_FIELDS` and WITHOUT reddening `-22`.**
- ✅ **It is also the STRONGER answer, not merely the permitted one.** A stored field can be edited
  to move a member across the seal in one character. A **derived** partition cannot be changed at
  all without changing the **pin** — which changes which bytes are audited, is visible in the diff,
  and would fail `TC-ArgusAgent-PRECISION-001-76`'s pin validation. AC2's requirement is that the
  partition be *unforgeable*, and derivation is what makes it so.
- ⛔ **THE CONSTRUCTOR GAP, MEASURED — and this is where "validated at construction" earns its
  keep.** `CorpusMemberSpec.__post_init__` validates `commit_sha` **only inside the
  `eligible_for_n=True` branch**; the `not eligible_for_n` branch `return`s first. Proved by
  execution: a row with `commit_sha="NOT-A-SHA"` and `commit_sha=""` both **construct successfully**
  today, on exactly the candidate rows the partition rule keys on. **A sha-ordered rule over
  unvalidated shas is not mechanically reproducible.** ✅ Measured safe to close: **all 21 committed
  rows already satisfy 40-character lowercase hex** (including the deliberate all-zero pin on
  `minions-story-7-2-superseded`), so hoisting the sha check to apply to **every** row breaks no
  existing row and closes the gap. **That hoist is AC2's "validated at construction".**

> ⚖️ **DECISION AND ITS ESCALATION PATH (DN-16-2-3).** This story takes the derived-property reading
> of AC2 and records why. **If the dev or the reviewer judges that AC2's words "a field on its
> manifest row" require a real tenth dataclass field, that is an ESCALATION to the operator, not a
> decision either of them may take** — extending `MANIFEST_FIELDS` from 9 to 10 changes a constant
> this epic's own authorisation lists as untouched, and Story 16.1's locked-decision table names it
> explicitly as *"16.2 will face this squarely"*. **HALT and present both options with their costs.
> Do not extend it quietly.**

### §0.6 What is already true and must NOT be re-done

- **The pins are already frozen, and frozen before any output.** The 14 candidate rows and their
  shas landed under Story 15.1; the selection criteria were frozen in commit
  `16d7100d73261c759d6176351f2caeff3d1fe172` (`feat(15-1): freeze the selection criteria in code,
  before anything is looked at`), and `TC-ArgusAgent-PRECISION-001-75` asserts against **real git
  history** that no commit reachable from it touches a candidate-output path. **The seal rule
  inherits that freeze — this story does not need to re-establish it, and must not re-derive a pin.**
- **`sprint-change-proposal-2026-08-20.md` and `sprint-change-proposal-2026-08-20-amendment-A.md`
  are BOTH already registered** in `_STATUS_DOCUMENTS` (`tests/test_status_document_registry.py:250`).
  Do not re-register either. ⚠️ The "one red guard" Story 16.1's round 2 recorded (`DOCS-001-22` over
  the then-unregistered amendment-A) is **resolved**: the baseline suite is green at 1,658/0/0/0.
- **The Epic 16 keys** (`epic-16`, five stories, `epic-16-retrospective`) already exist in
  `sprint-status.yaml`. Story files are excluded by design from the status-document glob closure —
  **this story file needs no registry entry.**
- **16.1's repairs are landed and must be composed with, never duplicated:** the fifth §5 condition;
  the hoisted `derive_concentration` (one instance, read by threshold **and** disclosure);
  `section_5_condition(...)` by-id lookup with `MissingSection5Condition`; the count-derived
  *"ALL n"* messages; `expected_section_5_outcome(fold, *, breadth_holds)` as the ONE §5 dispatch
  mirror.

---

## §1 — WHY THIS STORY EXISTS

**H-2, verbatim from the proposal:** *"Nothing is held back. The cartridge corpus has an
author-blind holdout (`holdout_vacuous`). The repository corpus that actually gates has none. If all
14 bench members are adjudicated and the detector is then tuned, no untouched population remains to
show the tool was not shaped to fit its own exam."*

### §1.1 The precedent to follow — how the cartridge holdout is actually implemented

Read the real thing before designing anything (`tests/cartridges/_registry.py`):

- **The partition is a FIELD on the registry row, in a closed vocabulary.** `CartridgeSpec.kind` ∈
  `{planted_defect, clean_control, holdout, trap, no_crash}`. `holdout_vacuous` carries
  `kind="holdout"`; so does `cross_partition_seam`. **Two holdouts, not one** — that is worth
  knowing, and the proposal's prose names only the first.
- **Downstream predicates are DERIVED from the vocabulary, never from a hand-list of ids:**
  `LABELED_CARTRIDGE_KINDS = ("planted_defect", "holdout")` is named once, and
  `populated_planted_defect_count()` folds `spec.kind in LABELED_CARTRIDGE_KINDS`. **Copy that
  shape exactly:** name the vocabulary once, derive every predicate from it.
- **The blindness is a PROCESS property recorded in the protocol, not a code property.** Protocol §6
  step 1 and §3: *"A holdout cartridge is labeled **author-blind** (the labeler does not know…)"*.
  ⛔ **What the code enforces is that the row IS a holdout; what makes it a holdout is that nobody
  looked. This story is what supplies the second half for the repository corpus — the "nobody
  looked" must be enforced by the SEAL and its ordering, because the repository corpus has no
  golden key a labeler could be blinded to.**
- ⚠️ **The gap this story must NOT inherit:** `CartridgeSpec` has **no `__post_init__`** — `kind` is
  a bare string, validated by nothing. That is precisely the weakness AC2's *"validated at
  construction"* closes for the repository corpus. **Follow the shape; do not copy the omission.**

### §1.2 The failure mode this story prevents, stated concretely

16.4 ratifies all 14. The detector emits over them, findings are adjudicated, precision comes out at
0.74 — below the gate. Someone tunes the detector against the members that produced the false
positives, re-runs, and gets 0.83. **Every member of the corpus has now been tuned against, and
nothing in the record can tell the difference between a tool that got better and a tool that got
fitted.** The number is quotable and means nothing. A sealed partition is the only thing that makes
those two hypotheses distinguishable, and it has to exist **before** the first run, or it does not
exist at all.

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **H-1 (breadth)** — Story 16.1, landed with **one** arm. `DF-16-1-A` (the rule-class arm) stays open.
- **H-3 (a tiny denominator clears at 100%)** — Story 16.3. Seal and yield are **different**
  conditions and must compose: three findings from three sealed members still fails 16.3.
- **H-4 (the adjudicator is the author)** — not closable by code. Story 16.5 makes it legible.
- **The operator can still choose what to ratify.** A seal cannot constrain a §6 R2 act. What it
  *can* do is make the consequence of that choice **countable in advance** — see §0.3's closure
  path — and this story's hand-off is where that lands.

---

## §2 — THE FIVE COUPLINGS THAT WILL BITE

Each is **measured on this tree**, not predicted. Four of them turn the tree red in files the dev
did not edit.

### §2.1 ⛔ `gate_decision.py` IS AT 1,197 / 1,200 — SPLIT FIRST. THIS IS TASK 1.

`DF-16-1-B` is a ledgered **SPLIT-FIRST trigger** and it names this story by name: *"the **next**
change to this module — which is Story 16.2's sixth §5 condition — performs the cohesion split
**FIRST**."* Measured: **1,197 of 1,200. Three lines.** A sixth condition does not fit in three
lines, and `MAINT-001-04` forbids the exemption, while `_REMEDY` forbids the shave:

> *"Split the file along a COHESION boundary into a sibling module and re-export … a module
> docstring naming why the module exists, no function split across the boundary, `__all__` and every
> import path unchanged. **Do NOT shave lines, and do NOT narrow this guard's population.**"*

**The boundary is already named and now measured by AST rather than estimated:**

| Member | Lines | Span |
|---|---|---|
| `CleanRepoEvidence` | **97** | `:364-460` |
| `CorpusReadProof` | **76** | `:463-538` |
| **together** | **173** | contiguous, `:364-538` |

`gate_decision.py` **1,197 → ≈1,024**, headroom **≈176**. They are the **EVIDENCE the decision
consumes**, not the decision itself — a real cohesion boundary, on the `argus/pipeline_stages.py`
(12.1) and `argus/precision/gate_breadth.py` (16.1) precedent.

**Every importer, enumerated by execution so the re-export contract is checkable:**
`scripts/build_gate_decision.py:60-61` · `tests/test_gate_decision.py:67,69` ·
`tests/test_gate_breadth.py:71` · `tests/test_gate_condition_lookup.py:60` — **all four import from
`argus.precision.gate_decision`**. ⛔ **Re-export from `gate_decision`; change no import line
anywhere.** `_REMEDY` requires it and it keeps the split reviewable as a pure move.

⚠️ **Land the split as its OWN commit, with `git diff -M` showing a pure move plus the re-export.**
A split folded into the commit that adds a §5 condition makes the one change a reviewer most needs
to read unreviewable — which is the reason `DF-16-1-B` records this as a precondition rather than
16.1 having done it.

⛔ **`tests/test_gate_decision.py` is at 1,193 / 1,200 — 7 lines.** New guards go to a NEW test
module. If the required re-authorings there cannot fit in 7 lines, **split it too, by the same
rule** — do not shave it, and do not delete a guard to make room.

### §2.2 A sixth §5 condition invalidates the committed gate-decision record

`TC-ArgusAgent-PRECISION-001-54` asserts `len(payload["section_5_conditions"]) == len(SECTION_5_CONDITIONS)`
and that the committed verdict list equals a live re-derivation. Extending `SECTION_5_CONDITIONS`
therefore requires `python scripts/build_gate_decision.py` to be re-run and the regenerated
`gate-decision-record.json` committed. **16.1 armed and spent this coupling once; it will fire again.**

✅ **Regenerating is NOT Argus output over a bench member and does not violate the ordering
constraint.** `build_gate_decision.py` reads the committed adjudication record, the committed
adjudication set and the manifest. It executes **no** detector, stages **no** repository, touches
**no** candidate. **State this explicitly in the Dev Agent Record** so a reviewer need not re-derive it.

⚠️ Re-running without `--check` re-stamps `commit_sha`, `commit_sha_provenance` and `decided_on`
from the live tree. **Land the code first, then regenerate, then commit** — and expect
`commit_sha_provenance` to read `NOT ESTABLISHED` if the tree is dirty when it runs.
⚠️ `-54` also asserts `payload["story"].startswith("13-3")`. **`_STORY` on `gate_decision.py` stays
`"13-3-record-the-result-and-let-it-decide"`** — the decision record is still 13.3's artifact.

### §2.3 ⛔ The protocol amendment is ADDITIVE, under V1.3 — NO `V1.4` ROW

`decide_gate` **raises** when `record.protocol_version != protocol_change_log_head`
(`gate_decision.py:977`), and `TC-ArgusAgent-PRECISION-001-45` / `-63` assert the same equality. The
record says `V1.3`; the change-log head is `V1.3`. **Adding a `V1.4` row turns all three red
immediately** and, worse, re-stamps **31 human judgements nobody re-made**.

⛔ **This is a LOCKED OPERATOR DECISION of 2026-08-20 (XAgent007), not a judgement call.** 16.1 amended
§5 by a **dated block under the existing V1.3** for exactly this reason and the protocol now carries
that reasoning in writing. **16.2 does the same: a second dated block under V1.3, adding bytes,
editing none.** Do not take a version. Do not re-run `build_adjudication_record.py` — §2.1's
coupling stays **unarmed** and `--check` stays green over all 31 rows.

### §2.4 ⛔ EVERY GUARD THAT ASSERTS A §5 OUTCOME RUNS OVER PRE-SEAL MEMBERS

**This is §2's most expensive item and it is measured, not predicted.** Story 16.1's hand-off point 5
warns that any guard asserting `CLEARED`/`NOT_CLEARED` is coupled to a new condition whether or not
it mentions it — 16.1's story named `-55` and `-56`, and the suite found `-58`. **Here the coupling
is total, because every §5-outcome fixture in the tree is built over the five ratified members, and
after this story all five are `pre-seal`.**

| Generator | Where | What it spreads over | Consequence |
|---|---|---|---|
| `_spread(record)` | `tests/test_gate_decision.py:164` | `ratified_corpus_members()` — the 5 | every generated population is 100% `pre-seal` |
| `_population(contributing_members=, size=)` | `tests/test_gate_breadth.py:108` | `_ratified()` — the same 5 | same |
| `_decide(record)` | `tests/test_gate_breadth.py:148` | passes `ratified_members=ratified_corpus_members()` | same |

**The coupled guards, ENUMERATED BY AST WALK of the three modules — outcome literals counted in
executable code only, docstrings excluded** (an earlier, looser scan over-reported: `-80`/`-81`
name `CLEARED` only in prose, while `-61`, `-69`, `-70` and `-85` were missed. **Re-run the walk
yourself; do not trust this table without reproducing it**):

**Tier 1 — assert `CLEARED` or `NOT_CLEARED` in code. These BREAK unless their fixture is extended:**

| Guard | Module | Fixture helpers used | What to check |
|---|---|---|---|
| `-56` | `test_gate_decision.py` | `_decide`, `_record` | asserts a `CLEARED` construction |
| `-58` | `test_gate_decision.py` | **`_spread`**, `_decide`, `_judged`, `_record` | 16.1's *"third latent trap"*, re-authored once already |
| `-83` | `test_gate_breadth.py` | **`_population`**, `_decide`, `_ratified` | asserts **where** the breadth verdict flips |
| `-86` | `test_gate_breadth.py` | **`_population`**, `_decide`, `_ratified` | the mirror-driven both-directions guard |
| `-53` | `test_gate_decision.py` | *(none)* | vocabulary only — verify by execution that it is unaffected, and **record the verification** |
| `-62` | `test_gate_decision.py` | *(reads the committed payload)* | branches on `payload["outcome"] == "CLEARED"`; conditional, not an assertion — verify and record |

**Tier 2 — built on a pre-seal generator, so the SUBJECT can change silently even where the
assertion still passes.** Every one needs a recorded verification (AC6.3): `-54`, `-55`, `-59`,
`-61`, `-63`, `-64`, `-69`, `-70` (`test_gate_decision.py`) · `-84`, `-85` (`test_gate_breadth.py`)
· `-80`, `-81` (`test_gate_condition_lookup.py`, via `_live_decision`).

⚠️ **Note the two modules define SEPARATE helpers with overlapping names** — `test_gate_decision.py`
has `_record` / `_judged` / `_spread` / `_decide`; `test_gate_breadth.py` has `_record` /
`_ratified` / `_population` / `_decide`. They are **not** the same functions. Do not fix one and
assume the other moved.

✅ **The fix, and it needs no new seam:** `decide_gate` takes `ratified_members` as an **argument**
(a `Sequence[Mapping[str, str]]`). A fixture may therefore be driven over the **sealed bench
candidates read live from the manifest** — real rows, real pins, never fabricated — by passing them
as `ratified_members`. **Non-vacuity floor: assert that at least `contributing_member_floor(...)`
sealed rows exist before generating, or the generator silently produces a population that cannot
satisfy breadth and every assertion over it becomes about the wrong thing.**

⛔ **`expected_section_5_outcome()` is the ONE §5 dispatch mirror (16.1 hand-off point 10). ADD your
term to it; do not fork it. And pass `seal_holds` IN as an argument derived from the fixture — never
read back out of the predicate under test.** A mirror fed the predicate's own answer moves in
lockstep with the defect and survives exactly the mutation that should kill it. That is not a
hypothetical: it is the finding that cost Story 16.1 a whole review round.

⛔ **16.1 hand-off point 11, which applies here verbatim:** the committed record carries 5
`BORDERLINE` rows and is therefore **never** `Exhaustive`, so every dispatch clause after the first
is unreachable over it. **If your new clause sits below `exhaustiveness` in the dispatch, it needs a
GENERATED population, or it is documentation.**

### §2.5 The published figures and the dogfood LOC currency both move on any `argus/**` delta

- **Four published figures, measured live this tree — `shipped_modules` 88 · `importable_modules` 88
  · `wheel_entries` 96 · `sdist_members` 95.** This story adds **at least two** new `argus/` modules
  (§2.1's split sibling + the seal module), so all four move. `TC-ArgusAgent-DOCS-001-54` pins them
  across `README.md` and `CHANGELOG.md` in **both** directions; `TC-ArgusAgent-RELEASE-001-11` pins
  the test-tree-reach set. ⛔ **Read the numbers from `tests/test_built_distribution.py::_live_figures()`.
  Never estimate them.**
- **The dogfood LOC-currency guards fire on any `argus/**` delta.** Order:
  commit `argus/` → `python scripts/regenerate_dogfood_artifacts.py` → commit the regenerated
  artifacts **separately**. The script refuses on a dirty `argus/` tree by design.

---

## Acceptance Criteria

### AC1 — The rule is PRE-COMMITTED, MECHANICALLY REPRODUCIBLE, and FROZEN BEFORE ANY OUTPUT

**AC1.1** The partition rule is **executable code, in one place**, never prose: a pure function of a
pinned commit sha plus the prior-output override, with the vocabulary
(`sealed` / `open` / `pre-seal`) named **once** as a closed tuple that **RAISES** on an unregistered
value — the `PROVENANCE_VALUES` / `GATE_OUTCOMES` / `CONDITION_VERDICTS` shape this codebase already
uses. **Purity (AR8):** no I/O, no clock, no network, no manifest resolution inside the predicate.

**AC1.2** The rule's **derivation and its rejected alternatives are recorded with it**, in the module
that owns it (DN-16-2-2), not in story prose only — the `BREADTH_MEMBER_FLOOR_DERIVATION` precedent.
It must state, in the code, that the rule was chosen on structural grounds and that the resulting
split was measured **afterwards**.

**AC1.3** The partition of every bench member is **materialized as a frozen table** at the seal
commit, and a guard **re-derives every row from the rule and asserts equality in BOTH directions**
(no table row the rule contradicts; no rule output the table omits). The table exists so the
partition survives §6 R2 ratification — after which a candidate row is indistinguishable from a
pre-seal one by its fields alone. ⛔ **The table is a frozen materialization of a rule, never a
hand-list: a guard that only read the table would be a guard over a hand-list.**

**AC1.4** The `pre-seal` set is **DERIVED, not typed**: a guard asserts it equals exactly the member
ids carried by the committed adjudication sets' `members[]` arrays, with a non-vacuity floor (both
sides non-empty) so a broken extractor goes RED rather than silently green. **Measured today: 5
members, `ai-body-runtime` / `agent-markovich` / `minions` / `xagents-webapp` / `agent-smith`; zero
bench candidates.**

**AC1.5** ⛔ **The seal is frozen in a commit that PRECEDES every commit containing Argus output over
any member, and the sha is RECORDED for 16.4 to cite.** Follow Story 15.1 exactly: the rule lands in
one commit; its sha is recorded in a **later** commit (`16d7100d` → `4f4db78` is the precedent). The
*ancestry guard* is 16.4's deliverable — this story's obligation is to land first, to record
`SEAL_COMMIT_SHA` as a full 40-character lowercase hex sha, and to verify by execution that
`git diff --name-only` over its own commits touches **no** candidate-output path
(`CANDIDATE_OUTPUT_PATHS`, `tests/test_candidate_selection.py:84`).

### AC2 — The partition is STRUCTURAL on the row and VALIDATED AT CONSTRUCTION

**AC2.1** A member's partition is readable **off its manifest row** as an attribute
(`spec.partition`), derived from the row's own pin through AC1.1's single rule — never recomputed at
a call site, never stored as an editable duplicate.

**AC2.2** ⛔ **`MANIFEST_FIELDS` STAYS CLOSED AT 9 and `TC-ArgusAgent-PRECISION-001-22` stays green
unedited.** §0.5 establishes by execution that a derived property is not a dataclass field. **If the
dev concludes a tenth field is required, HALT to the operator with both options and their costs
(DN-16-2-3). Do not extend the constant.**

**AC2.3** ⛔ **The constructor validates the sha for EVERY row, not only eligible ones.** §0.5 proves
by execution that `commit_sha="NOT-A-SHA"` and `commit_sha=""` construct successfully today on
exactly the candidate rows the rule keys on. Hoist the 40-character lowercase-hex check above the
`not eligible_for_n` early return, with a message that says what a reader must do (AR10). ✅ Measured
safe: **all 21 committed rows already satisfy it.** Drive the new refusal RED by an executed mutation.

**AC2.4** **Opening the sealed partition is a single recorded act, not a side effect of running the
harness.** State the act, where it is recorded, and who may take it (protocol §6, operator). ⛔ **This
story does not open it, does not schedule opening it, and adds no code path that opens it.**

### AC3 — The gate is computed over the SEALED partition, as a §5 CONDITION

**AC3.1** `SECTION_5_CONDITIONS` gains **one** member, **APPENDED** at the end (DN-16-1-2's rule,
inherited): §5 is amended by dated addition, the five existing ids keep their positions, and the
regenerated record's condition list is a clean prefix-plus-one diff. Its id is named **once** as a
module constant beside `BREADTH_CONDITION_ID`.

**AC3.2** Below the condition, §5's **precision** condition is recorded `UNEVALUABLE` with the counts
that made it so and the outcome is `BLOCKED` with a **countable** closure path — exactly 16.1's
shape, composed with it rather than replacing it. ⛔ **`GATE_OUTCOMES` stays closed at three and
`CONDITION_VERDICTS` at four. No terminal state is invented.** The seal condition's **own** verdict
is `MET`/`FAILED` — it *was* evaluated over a named population; `UNEVALUABLE` would tell a reader the
provenance of the evidence was unknown, which is a different and false claim.

**AC3.3** The counts are **read from the same `ConcentrationDisclosure` instance** 16.1 hoisted —
`contributing_member_ids` joined against the members the decision already carries. ⛔ **Do not
recount and do not re-resolve the manifest.** A second count is a second thing that can disagree with
the disclosure, invisibly. The partition reaches production through the **existing** lazy edge —
`gate_disclosure.ratified_corpus_members()` already returns each member's `commit_sha`; extend that
mapping with the member's `partition`. ⛔ **No new lazy edge, and no module-level repository-only
path in `argus/**` (`DF-9-2-A`).**

**AC3.4** The condition's `measured` sentence **names which population it counted and which
partition each contributing member is in**, and discloses the sealed/open/pre-seal split of the
corpus it measured. A reader must never have to guess whether "0 sealed contributions" means *no
sealed member was audited* or *sealed members were audited and emitted nothing*.

**AC3.5** ⛔ **VERIFY BY EXECUTION that the live outcome is UNCHANGED, and record the verification.**
Expected and measured on this tree: today's outcome is `BLOCKED` with precision already
`UNEVALUABLE`; the record should gain a sixth condition reading `FAILED` **and nothing else should
move** — `outcome`, `outcome_reason`, `closure_path` and the precision `gate_status` sentence
byte-identical across the amendment. If any of them moves, **stop and record why** before proceeding.

### AC4 — A DETECTOR CHANGE DATED AFTER THE SEAL SAYS WHICH PARTITION ITS EVIDENCE CAME FROM

**AC4.1** A guard reads **real git history** (the `TC-ArgusAgent-PRECISION-001-75` template, same
module conventions) and asserts: **every commit touching a declared detector-tuning path set that is
NOT an ancestor of the seal commit carries an explicit partition citation** in its message, in a
declared, machine-checkable form (a trailer token naming `sealed` / `open` / `none`).

**AC4.2** ⛔ **Three non-vacuity preconditions, each asserted BEFORE the absence it protects** — copy
`-75`'s structure, which already gets this right:
1. the declared detector-path set is **non-empty**;
2. `git log` over a **control path known to carry commits** returns non-empty — a misspelled
   pathspec returns empty and is **indistinguishable from a clean history**;
3. the seal sha **resolves** (`git cat-file -t` → `commit`) and is a full 40-char lowercase hex sha.

**AC4.3** ⛔ **DRIVEN TO BOTH OUTCOMES.** The citation predicate is asserted **True** for a message
that cites a partition and **False** for one that does not — over synthetic message strings, so the
guard is watched **failing**, not only passing. ⚠️ **At the moment this story lands the post-seal
commit population is EMPTY**, so a guard that only iterated it would pass forever over nothing. That
is this project's signature defect and AC4.3 is what forbids it here: **the predicate must be driven
both ways independently of the population.**

**AC4.4** The rule is **written down where the next author will read it** — a `SEAL_CITATION_RULE`
constant (the `SOURCING_RULE` / `_REMEDY` precedent) naming the trailer, the accepted values and what
a reader must do — and the guard's failure message names the remedy. ⛔ **`argus/detectors/**` stays
BYTE-UNCHANGED in this story; the guard governs future changes, and this story creates none.**

### AC5 — IT PARTITIONS; IT DOES NOT NARROW

**AC5.1** `VALIDATION_SET_FLOOR_N` stays **5**. `eligible_member_count()` stays **5**. No member is
dropped from `VALIDATION_CORPUS`, none is re-weighted, none changes `eligible_for_n`, and no
`adjudication_caveat` is edited. Assert all of it by execution and record the readings.

**AC5.2** ⛔ **The population passed to the fold is NOT filtered.** Both narrowing designs were proved
by execution to `raise` on today's tree, and the reason they raise is the reason they are wrong:

| Narrowing design | Result, EXECUTED | Why that is the right refusal |
|---|---|---|
| filter `record.rows` to sealed members | `VacuousDecisionError` — *"the adjudication record holds ZERO rows…"* | 0 of 31 live rows come from a sealed member |
| `derive_concentration` over the sealed subset | `VacuousDisclosureError` — *"the concentration of an EMPTY population is unobservable, not 'even'…"* | same |

**A filter narrows the population — which §5 and Story 13.3 / AC5 forbid — and would make
`build_gate_decision.py` refuse, turning the tree red in files this story never edited. A CONDITION
adds a requirement and is a strengthening.** Take the condition.

**AC5.3** Every finding from every partition **stays recorded and stays disclosed**. The seal governs
what may **gate**, never what is **reported**. The concentration disclosure keeps reporting all
contributing members; the new condition reports how many of them were sealed.

**AC5.4** This story records **explicitly that it makes clearing HARDER** — every population that
cleared before either still clears or is now `BLOCKED`, and no population that failed before can pass
because of it — and touches neither the ≥80% `Fraction`, `VALIDATION_SET_FLOOR_N`, the five ratified
members, `MANIFEST_FIELDS`, FR34, nor `protocol_cleared`.

### AC6 — DRIVEN TO BOTH OUTCOMES BY EXECUTED MUTATION, EACH OBSERVED RED

**AC6.1** Every new guard and every re-authored guard is observed **RED by an executed mutation of
the shipped code**, tree restored byte-exact and re-verified green after each. Record **what was
mutated** and **what the failure said**. *This project shipped 4 of 35 unreal guards in Epic 14, and
16.1's round-2 `-55` was believed tested and was not.*

**AC6.2** The seal condition is driven to **both** verdicts over **GENERATED** populations — one that
satisfies it and one that does not — built at the **real seam** from real rows over real manifest
rows (§2.4's recipe), never hand-written and never fabricated. Assert **where the verdict flips**,
not merely that it has two values.

**AC6.3** ⛔ **Re-authoring a guard is a RECORDED ACT.** Each of §2.4's eleven coupled guards is either
(a) re-authored as an **INTENDED BEHAVIOUR CHANGE** with the change recorded and the re-authored
guard driven RED, or (b) verified by execution to need no change **and the verification recorded**.
Silence about one of them is not an option. **And audit beyond the list: 16.1's story named two and
the suite found a third.**

**AC6.4** New TC ids are allocated from **`TC-ArgusAgent-PRECISION-001-87`** upward (the area is
allocated through `-86`). If a DOCS-area guard is needed, allocate from **`TC-ArgusAgent-DOCS-001-80`**
(allocated through `-79`). Record each id against the guard it names.

### AC7 — THE ARTIFACTS ARE CURRENT, ADDITIVE, AND THE ORDERING IS NOT BROKEN

**AC7.1** Protocol §5 is amended by a **dated block under the existing V1.3** that edits **no
existing byte** and does not re-wrap the conjunction sentence `-63` pins. ⛔ **No `V1.4` row** (§2.3).

**AC7.2** `architecture.md` §Enforcement is amended **struck-not-erased**, extending the
**Gate-decision enforcement** registration (the surface 16.1 amended) with: the seal rule, the
enforcing module(s), the guard ids, and the split of §2.1. `TC-ArgusAgent-DOCS-001-77` asserts these
registrations are present — **run it and confirm every anchor still resolves.**

**AC7.3** `gate-decision-record.json` is regenerated and committed (§2.2); both builders `--check`
exit **0**; and the Dev Agent Record states in terms that regeneration executed no detector and
touched no candidate.

**AC7.4** The four published figures are re-read from `_live_figures()` and updated in `README.md`
and `CHANGELOG.md`; the dogfood artifacts are regenerated in the declared order (§2.5).

**AC7.5** ⛔ **Verify `git diff --name-only` over this story's commits touches NO candidate-output
path and that no corpus-audit script ran. Record the landing shas for 16.4's ancestry guard.**

### AC8 — GATES, SCOPE AND HAND-OFF

**AC8.1** Full suite green with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, **exit code recorded**, **0
skipped** (`pytest.skip` is a FALSE GREEN). `mypy argus` clean. `bandit -r argus --severity-level
medium` clean. Baseline to beat: **1,658 / 0 / 0 / 0, exit 0**.

**AC8.2** NFR-M1 measured **with the ceiling guard's own `_physical_line_count`** for every module
touched, **before and after**, and recorded. ⛔ **`argus/detectors/vacuous_test.py` (1,196) and
`tests/test_vacuous_density.py` (1,159) stay byte-unchanged — confirm by execution.**

**AC8.3** Push; record the CI run id **together with the sha it covers**. ⚠️ **The local gates are
Windows-only while CI runs an ubuntu matrix, and a green local suite has already shipped POSIX-only
bugs to master.** If instructed not to push, record AC8.3 **OPEN** rather than claiming it.

**AC8.4** Write the hand-off for **16.3 and 16.4**, carrying at minimum: the seal sha; the frozen
partition table; **§0.3's countable R2 constraint (≥3 of the six named sealed candidates)**; the
`expected_section_5_outcome` term you added; and the §2.4 guards you re-authored.

**AC8.5** ⛔ **Nothing outside the declared write set moves without being RECORDED as a deviation
with its rationale.** No `DF-*` entry is disposed of. No ledger text is edited without the
append-only / strike-not-erase annotation — the Story 16.1 review found exactly that defect, and the
remedy taken was restoration.

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

**DN-16-2-1 — the seal is a §5 CONDITION, not a filter on the population.** *Rejected:* filtering the
record's rows, or `derive_concentration`'s inputs, to sealed members — **proved by execution to
`raise` on today's tree** (AC5.2's table), and wrong on principle: a filter **narrows**, which §5 and
Story 13.3 / AC5 forbid, while a condition **requires**, which is the strengthening the 2026-08-20
approval authorises. *Also rejected:* letting the payload's `precision.evaluable` stay `True` while
§5 says the evidence is not sealed — the `DF-9-2-B` shape, a true status carrying a false subject, on
the gate surface. **16.1 already built the composition point; use it.**

**DN-16-2-2 — the bisection is `int(commit_sha, 16) % 2`: a PER-ROW function of the pin.** Recorded
with the alternatives, and with all three outcomes computed **so the choice is checkable rather than
asserted**:

| Rule | Split | Sealed co-occurrence mass | Verdict |
|---|---|---|---|
| **`int(sha,16) % 2` (SELECTED)** | 6 / 8 | 431 of 614 | per-row; canonical property of the object name |
| `int(sha[0],16) % 2` | 6 / 8 | 354 of 614 | **REJECTED** — an arbitrary digit position, not a property of the number |
| sort by sha, alternate index | 7 / 7 | 211 of 614 | **REJECTED** — *set-relative* |

⛔ **Why set-relative rules are rejected, and this is the decisive argument:** the ratified set is not
known until 16.4's operator act. A rank-within-set rule **re-partitions silently** when the operator
ratifies 11 instead of 14 — removing one member shifts every subsequent index — and it is therefore
*re-derivable after the fact to a different answer*, which is precisely what "pre-committed" forbids.
A per-row function of the pin is stable under any ratification subset: **each of the 14 members'
partitions is already determined and publishable today**, so the operator can change the partition's
*size* but never a *member's* partition. *Also rejected:* hashing `member_id` — a local name we chose
and can edit; the pin is the stronger anchor, frozen by Story 15.1 in `16d7100d` before any output,
and changing it changes which bytes are audited and fails `-76`.

**DN-16-2-3 — the partition is a DERIVED property, and `MANIFEST_FIELDS` stays closed at 9.** See
§0.5 for the execution that establishes it and **for the HALT this decision is conditional on**.
*Rejected:* a tenth dataclass field — it changes a constant this epic's authorisation lists as
untouched, reddens `-22`, and is **weaker**: a stored field can be flipped in one character, while a
derived one cannot change without changing the pin.

**DN-16-2-4 — three partition values, not two.** `sealed` / `open` / `pre-seal`, closed, raising on
an unregistered member. *Rejected:* collapsing `pre-seal` into `open` — arithmetically identical (only
`sealed` counts), but it would tell a reader the five ratified members were assigned by the bisection
when in fact they were **excluded from sealing** because output already existed. **A measured result
and an unobservable one are different claims**, and this project's dominant defect class is exactly
the surface that cannot tell them apart. §0.2's rows 4 and 5 are the concrete proof that the
distinction is load-bearing.

**DN-16-2-5 — the split of `gate_decision.py` lands FIRST and as its own commit.** *Rejected:* folding
it into the condition commit — it makes the one change a reviewer most needs to read unreviewable.
*Rejected:* shaving — `_REMEDY` forbids it. *Rejected:* an `_EXEMPT_BY_DESIGN` entry — `MAINT-001-04`
allows that registry only to shrink.

**DN-16-2-6 — the derivation lives in the Dev Agent Record of this story and in the module that owns
the rule, not in a side file.** `DF-15-2-C` exists because a per-id verdict table was left with no
durable home.

### Locked decisions this story CITES rather than reopens

| Decision | Where | What it forbids here |
|---|---|---|
| **`DF-16-1-A` stays OPEN and UNLANDED** — the rule-class arm; max achievable verdict-eligible rule classes = **1** | ledger, protocol §5, `gate_breadth.py` | writing any rule-class threshold, anywhere, in any form |
| **NO protocol re-version** — no `V1.4` row; the 31 judgements of 2026-08-17 keep V1.3 provenance | operator decision 2026-08-20; protocol §5 block | taking a change-log version, or re-running `build_adjudication_record.py` |
| **OI1 lock** — `N` LOCKED at 5; precision over **FINDINGS**, not repos | protocol §7 | changing the unit, or forking `N` |
| **DN-1 / DN-2** — the gate is measured over the REPOSITORY corpus; cartridges are the RECALL corpus | `_manifest.py`, protocol §1 | citing `holdout_vacuous` as gate evidence rather than as the *shape* precedent |
| **DN-3** — one floor constant, two populations | `_manifest.py`, `-25` | a second `N`, or restating `5` |
| **AR4 / AR7 / AR8 / AR10** — exact `Fraction`; reuse never fork; pure predicates; typed failures | throughout | a second dispatch mirror, a second concentration count, I/O in a predicate |
| **§5 / Story 13.3 AC5** — no change that makes clearing easier | protocol §5 | narrowing, dropping or re-weighting a member |
| **§6 R2 is an operator act** | protocol §6 | ratifying, fetching or staging anything |
| **`DF-13-5-A`** — exactly ONE round, pre-registered 2026-08-17, **UNSPENT** | ledger | spending it, or proposing any expansion |
| **`MANIFEST_FIELDS` closed at 9** | `_manifest.py`, `-22` | adding a field (see DN-16-2-3's HALT) |
| **`NEVER_ELIGIBLE_FIELDS`** | `_manifest.py` | stars / forks / downloads as any kind of signal |
| **amendment-A is UNAPPROVED** | `sprint-change-proposal-2026-08-20-amendment-A.md` §8 | applying it, citing it as authority, or absorbing a red guard by registering it |

### Open ledger entries bearing on this story — verified against `deferred-work.md` on disk, 2026-08-20

**All entries below are OPEN and are CITED. This story disposes of NONE of them.**

| Entry | State on disk | Bearing here |
|---|---|---|
| **`DF-16-1-B`** | OPEN — `gate_decision.py` at 1,197/1,200, **SPLIT-FIRST trigger naming Story 16.2** | **§2.1 / AC-task 1. The trigger fires on this story.** |
| `DF-16-1-A` | OPEN — the rule-class arm, unachievable with the shipped detector set | do not land any rule-class threshold |
| `DF-13-5-A` | OPEN, owner XAgent007, `target_story: NONE`; ONE round, **UNSPENT** | the round is 16.4's; this story may not propose an expansion |
| `DF-15-2-A` | OPEN — a vacuity sweep is in no definition of done | AC6 in full |
| `DF-15-2-C` | OPEN — the 24-guard sweep's per-id table has no durable home | do **not** cite *"22 of 24 REAL"* as established |
| `DF-15-2-D` | OPEN — `vacuous_test.py` at 1,196/1,200 | AC8.2 — do not open that module |
| `DF-15-2-E` | OPEN — `tests/test_vacuous_density.py` at 1,159/1,200 | AC8.2 — not on the write set |
| `DF-8-5-C` | OPEN — a hand-written number in a proof artifact about the gate | AC1.2 — every figure derived, none pinned |
| `DF-9-2-A` | OPEN — no module-level repository-only path in shipped code | AC3.3 — the new module resolves no repo-only `Path` at import time |
| `DF-9-2-B` | OPEN — a true status carrying a false reason | AC3.2, AC3.4, DN-16-2-1 |
| `DF-13-3-A` | OPEN — residual is the missing `evidence_deviation` header field | not in scope |

#### ⛔ Writing rule — `TC-ArgusAgent-DOCS-001-78`

That guard goes RED when a `DF-` id sits **on the same line** as a closure verb
(`CLOSED` / `Closes` / `closes` / `Closed by this story`) for an entry the ledger never received,
unless the line is negated by `not` / `NOT` / `never`. It is **line-scoped**, it reads **every** file
under `stories/`, and it has gone RED repeatedly. **Rule for the dev agent: never put a `DF-` id on
the same line as a closure verb** — in this story file or anywhere else under `stories/`. And **never
append a disposition to `deferred-work.md` to green a guard**; the remedy is always to correct the prose.

### Guard vacuity — this project's signature defect, and the specific obligation here

Three of this story's guards are **structurally at risk of passing over nothing**, and each has a
named answer:

1. **AC4's post-seal detector-commit guard.** Its population is **empty on the day it lands**. Answer:
   AC4.3 — drive the **predicate** to both outcomes over synthetic messages, independently of the
   population, plus `-75`'s three preconditions.
2. **The seal §5 condition.** On the committed record it can only read `FAILED` — `MET` is
   **impossible** without a constructed fixture, and the fold is *already* unevaluable for reasons
   that have nothing to do with the seal. A guard built only against the committed record would be
   green, silent and useless. Answer: AC6.2's **generated** populations over sealed manifest rows,
   plus 16.1 hand-off point 11 (the committed record is never `Exhaustive`, so any clause below
   `exhaustiveness` is unreachable over it).
3. **AC1.3's partition table.** A guard that read only the table would be a guard over a hand-list.
   Answer: re-derive every row **from the rule**, both directions.

Model the fixtures on `tests/test_gate_breadth.py::-86` (generated one per count, live `decide_gate`,
expectation derived from the fixture and **passed in**) and `-83` (asserts directly against
`decide_gate`'s live outcome, corroborating without going through the mirror).

### Dependencies — none are added, and that is a requirement, not an observation

No new runtime or test dependency. Everything needed is in the tree: `int(x, 16)`, `dataclasses`,
`pathlib`, `subprocess` (git reads only, as `-75` already does) and `pytest`. Declared runtime set
(`pyproject.toml`): `pydantic>=2.0`, `jsonschema>=4.0`, `radon>=4.1.0`, `httpx>=0.24.0`, the pinned
`tree-sitter-*` grammars — **do not move a bound; the ceilings are load-bearing (Story 11.4)**.
`requires-python` is `>=3.10`: no `typing.Self`, no PEP-695 generics. **Adding a dependency to
compute the parity of an integer would be its own defect.**

### Standing rules (non-negotiable)

- **Determinism (NFR-P1/D1)** — no wall-clock, no `uuid4`, no `random`, no reliance on dict/set
  iteration order; every set rendered `sorted()`.
- **NFR-S1** — counts, rule-id provenance and locators only. Never a source byte, never a secret.
  **No third-party source is vendored: a member is metadata and a pin (DN-4).**
- **Canonical serialization** — every committed artifact goes through `argus.store.canonical`,
  never `json.dumps`.
- **AR10** — typed failures; any new error subclasses `ValueError` and says what a reader must do.
- **Platform neutrality** — `pathlib` throughout, explicit `encoding="utf-8"`, `.as_posix()` at every
  path→string boundary, no assertion on `os.sep`, a drive letter or a CRLF-sensitive byte count.
  ⚠️ **Local gates are Windows-only; CI runs an ubuntu matrix.**
- **No corpus member's working tree is ever mutated** — no `checkout`, no `stash`, no `clean`, no
  `worktree`. Git reads only.
- **`pytest.skip` is a FALSE GREEN.**
- **Validate findings against the story first** — an absence here is usually a locked decision, not a
  defect.

### External prior art — checked so this story does not reinvent a wheel, and what was taken

The public literature on **benchmark contamination** converges on exactly this story's shape and is
worth one paragraph, not a design: benchmarks are partitioned into a **public development split and a
held-out private evaluation split**, contamination is detected by **comparing performance across the
two splits**, and the held-out side is maintained **for ongoing uncontaminated evaluation**. Two
things transfer and one does not.

- ✅ **Taken:** the split must be **decided and published before** any evaluation, and the held-out
  side must be **structurally distinguishable** rather than remembered.
- ✅ **Taken:** the value of the holdout is a **comparison across partitions**, which is why AC4
  requires post-seal detector changes to *cite* their partition — the citation is what makes the
  comparison possible later.
- ❌ **Not taken:** submission-API / private-server enforcement. Argus is a single-repository tool
  with no evaluation server, and a mechanism nobody can operate is worse than a rule they can read.
  **The enforcement here is git ancestry plus a §5 condition, which this repository already knows how
  to check** (`-75`).
- ❌ **Not taken:** canary strings and statistical contamination detectors. They answer *"was this
  data in a training corpus"*; the question here is *"was this repository tuned against"*, which
  ordering answers directly and cheaply.

### Files to touch — and the ones that must not move

**Write set:**
- `argus/precision/gate_evidence.py` *(NEW — §2.1's split sibling; name it for its subject)* —
  `CleanRepoEvidence` + `CorpusReadProof`, **moved unchanged**, re-exported from `gate_decision`.
- `argus/precision/gate_seal.py` *(NEW)* — the partition vocabulary, the pure rule, its derivation,
  the seal assessment and the published sentences. **One direction only: `gate_decision` → `gate_seal`.**
- `argus/precision/gate_decision.py` — the re-export, `SECTION_5_CONDITIONS` +1, the seal
  `ConditionResult`, the seal term in `_precision_condition`.
- `argus/precision/gate_disclosure.py` — the `partition` key on `ratified_corpus_members()`.
- `tests/corpus/_manifest.py` — the frozen partition table, the `pre-seal` set, the `partition`
  property, the hoisted sha validation.
- `tests/test_gate_seal.py` *(NEW)* — the seal guards, ids from `-87`.
- `tests/test_validation_corpus.py` — the manifest-side guards (273 lines of headroom).
- `tests/test_gate_decision.py` / `tests/test_gate_breadth.py` / `tests/test_gate_condition_lookup.py`
  — **only** the §2.4 re-authorings and the `expected_section_5_outcome` term. ⛔ **7 lines of
  headroom in `test_gate_decision.py`** — keep the re-authorings minimal or split.
- `README.md`, `CHANGELOG.md` — the four published figures, read from `_live_figures()`.
- `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` — §5 dated block under
  V1.3. **No change-log row.**
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §Enforcement amendment (AC7.2).
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json` — regenerated.
- `minions-dogfood-*.md` — regenerated by the script, in the declared order.
- **this story file** — the derivation, the REDs, the shas, the CI run id.
- `sprint-status.yaml` — status transitions only.

⚠️ **`argus/precision/__init__.py` is NOT on the write set.** It re-exports `replay_harness` symbols
only; `gate_decision`, `gate_disclosure` and `gate_breadth` are deliberately not re-exported and
every caller imports them by module path. **Follow that convention.**

**Not touched:** `argus/detectors/**` (byte-unchanged, AC4.4) · `argus/precision/adjudication.py` ·
`argus/precision/replay_harness.py` · `argus/precision/gate_breadth.py` (read it; do not edit its
subject) · `argus/pipeline*.py` · `tests/cartridges/**` · `tests/test_vacuous_density.py` ·
`prd.md` · `epics.md` · `deferred-work.md` (nothing is disposed of, nothing appended to green a
guard) · `validation-corpus/adjudication-record.json` · `validation-corpus/adjudication-set*.json` ·
`tests/test_status_document_registry.py` (both 2026-08-20 documents already registered) ·
`scripts/candidate_selection.py` (15.1's frozen criteria — **frozen means frozen**).

**Next TC ids:** `TC-ArgusAgent-PRECISION-001-*` is allocated through **`-86`** → allocate from
**`-87`**. `TC-ArgusAgent-DOCS-001-*` is allocated through **`-79`** → allocate from **`-80`**.

### Previous-story intelligence — Story 16.1 (`done`, 2026-08-20) and Story 15.1 (`done`, 2026-08-19)

- **16.1's hand-off is written FOR this story. Read all eleven points** (*Hand-off to 16.2 and 16.3 —
  ROUND 2* and *Hand-off addendum*, `16-1-…md:1597` and `:1904`). Points 1 (split first), 2 (copy the
  condition shape), 3 (read conditions by id), 4 (§2.2 armed / §2.1 unarmed), 5 (audit every §5-outcome
  guard), 6 (four published figures), 8 (dogfood order), 10 (`expected_section_5_outcome`) and 11
  (generated populations) are **all** live obligations here.
- **16.1 cost a review round on exactly the mistake this story is most likely to repeat.** Its round 2
  ticked *"BOTH DONE"* for a guard that stayed **GREEN** under both of the reviewer's mutations,
  because that guard's only fixture was the committed record. **Do not tick a box you have not
  observed RED.**
- **16.1's round 1 found a stated premise FALSE inside its own story** (*"zero human judgements"* — the
  record carries **31**). **Re-derive every figure with a second instrument before writing it down,
  and strike rather than erase if it moves.**
- **15.1's ordering discipline is the template**: code delta, artifact regeneration and story record in
  **separate commits**, so the commit that had to contain no Argus output demonstrably contained none.
  Here that is **three or four** commits: split → seal + condition + protocol → regenerated artifacts →
  story record.
- **15.1's `CRITERIA_COMMIT_SHA` is the exact pattern for AC1.5's seal sha**: freeze in `16d7100d`,
  record the constant in the later `4f4db78`. **A commit cannot cite itself.**
- **15.2's lesson, quoted by its own review:** *"a disposition recorded in prose and not in the ledger
  is not a disposition."* This story disposes of nothing; do not write as if it does.

### Git intelligence

`6128466` `docs(16-1): record the passing re-review, and close the story` · `0733a33`
`docs(16-1): record round 3's landing shas, which a commit cannot cite about itself` · `a20a0ef`
`docs(16-1): record round 3 — the review finding fixed by executed mutation, not by rewording` ·
`7323f61` (round-3 guards) · `11f40cb` (16.1's regenerated artifacts) · `2ac1078` (16.1's code +
protocol) · `0a6e121` (the epic-16 approval).

Three habits to copy exactly: **(i)** an approval, a correction or a supersession is recorded as a
**separate, later act** with the original wording left unedited (§3.4 evidence immutability); **(ii)**
couplings that close in both directions land **together** in one commit (`7f54506` landed a document
and its registration together); **(iii)** the story record is its **own** commit, after the code and
after the regenerated artifacts.

⚠️ The branch is **13 commits ahead of `origin/master`**. Push, and record the CI run id against the
sha it covers.

### References

- [epics.md](../epics.md) §Epic 16 (`:3019` — the **BINDING ORDERING CONSTRAINT** and the
  **permitted-failure clause**), §Story 16.2 (`:3098`), §Story 16.3 (`:3127`), §Story 16.4 (`:3153`)
- [sprint-change-proposal-2026-08-20.md](../sprint-change-proposal-2026-08-20.md) §1.3 (H-2), §1.4,
  §4.3(2), §5, §6 (what approval does and does **not** authorise)
- [sprint-change-proposal-2026-08-20-amendment-A.md](../sprint-change-proposal-2026-08-20-amendment-A.md)
  — **registered, UNAPPROVED, out of scope, cited only so it is not mistaken for authority**
- [precision-validation-protocol.md](../precision-validation-protocol.md) §1, §2, §3, §4, §5 (the
  2026-08-20 block), §6 **R1–R4** and the cartridge phased plan (`holdout_vacuous`, *author-blind*),
  §7 (OI1), Change log (head **V1.3**)
- [validation-corpus/gate-decision-record.json](../validation-corpus/gate-decision-record.json) —
  `section_5_conditions`, `concentration`, `breadth`, `corpus`, `corpus_read_proof`
- [validation-corpus/adjudication-record.json](../validation-corpus/adjudication-record.json) — 31
  rows, `protocol_version: V1.3` · `adjudication-set.json` / `adjudication-set-13-5.json` — the
  `members[]` arrays AC1.4 derives the `pre-seal` set from
- [deferred-work.md](../deferred-work.md) — `DF-16-1-B` (`:5322`), `DF-16-1-A` (`:5262`),
  `DF-13-5-A` (`:4654`), `DF-15-2-A`, `-C`, `-D` (`:5188`), `-E` (`:5229`)
- [architecture.md](../architecture.md) §Enforcement — *Gate-decision enforcement* (`:1136`),
  *Adjudication-record enforcement* (`:1134`), *Corpus-pin provenance enforcement* (`:1138`),
  *GUARD-ADEQUACY CLAUSE* (`:1132`), *Ledger-claim cross-check enforcement* (`:1140`)
- [16-1-a-score-drawn-from-one-repository-is-not-a-score.md](16-1-a-score-drawn-from-one-repository-is-not-a-score.md)
  · [15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks.md](15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks.md)
  · [13-3-record-the-result-and-let-it-decide.md](13-3-record-the-result-and-let-it-decide.md)
- `tests/cartridges/_registry.py` (the holdout precedent) · `tests/corpus/_manifest.py` ·
  `argus/precision/gate_breadth.py` · `argus/precision/gate_decision.py` ·
  `argus/precision/gate_disclosure.py` · `scripts/build_gate_decision.py` ·
  `tests/test_candidate_selection.py` (`-75`, the ordering-guard template) ·
  `tests/test_module_size_ceiling.py` (`_REMEDY`, `_physical_line_count`) ·
  `tests/test_built_distribution.py` (`_live_figures`)

---

## Tasks & Subtasks

- [x] **Read §0, §1.1 and §2 first, then re-verify §0.2, §0.3 and §0.5 INDEPENDENTLY.** The premises
      are measured, but AC1/AC2 require **your own** reproduction, not this file's. (AC: all)
- [x] ⛔ **TASK 1 — SPLIT `argus/precision/gate_decision.py` FIRST, as its own commit** (§2.1,
      `DF-16-1-B`). Move `CleanRepoEvidence` (97) + `CorpusReadProof` (76) to a new sibling; re-export
      from `gate_decision`; **change no import line** at any of the four importers. Verify with
      `git diff -M` that it reads as a pure move. Re-measure NFR-M1 before and after. Full suite green
      **before** anything else lands. (AC: AC8.2)
- [x] Create `argus/precision/gate_seal.py`: the closed 3-value vocabulary raising on an unregistered
      member, the pure `partition_of`, the derivation with its rejected alternatives, the seal
      assessment and the published sentences. **No I/O, no manifest resolution, no repo-only path.**
      (AC: AC1.1, AC1.2, AC3.3)
- [x] Materialize the frozen partition table for the 14 bench members and the derived `pre-seal` set;
      add the `partition` property to `CorpusMemberSpec`; **hoist the sha validation above the
      `not eligible_for_n` early return** and drive the new refusal RED. (AC: AC1.3, AC1.4, AC2.1,
      AC2.3)
- [x] ⛔ Confirm by execution that `MANIFEST_FIELDS` is still 9 and `-22` is green **unedited**. **If
      a tenth field seems required, HALT to the operator with both options and their costs** —
      do not extend the constant. (AC: AC2.2, DN-16-2-3)
- [x] Extend `gate_disclosure.ratified_corpus_members()` with each member's `partition`, through the
      **existing** lazy edge. (AC: AC3.3)
- [x] Extend `SECTION_5_CONDITIONS` by one, **appended**; build the seal `ConditionResult`; thread the
      seal term into `_precision_condition` so a non-sealed denominator makes precision `UNEVALUABLE`
      and the outcome `BLOCKED` with a countable closure path. **`GATE_OUTCOMES` stays at three,
      `CONDITION_VERDICTS` at four.** (AC: AC3.1, AC3.2)
- [x] Write the seal `measured` sentence naming the population, each contributing member's partition,
      and the sealed/open/pre-seal split. (AC: AC3.4)
- [x] ⛔ **Add your term to `expected_section_5_outcome()` — do not fork it — and pass `seal_holds`
      IN, derived from the fixture, never read back out of the predicate under test.** (AC: AC6.2)
- [x] ⛔ **Re-run §2.4's AST walk yourself, then audit EVERY guard it returns — Tier 1 and Tier 2 —
      and look beyond the list.** For each, either re-author as an
      INTENDED BEHAVIOUR CHANGE (recorded, driven RED) or verify by execution that it needs no change
      (recorded). Extend `_spread()` / `_population()` / `_decide()` to generate over **sealed
      manifest rows**, with a non-vacuity floor asserting enough sealed rows exist. (AC: AC6.1, AC6.3)
- [x] Create `tests/test_gate_seal.py`; allocate ids from **`-87`**; drive the condition to **both**
      verdicts over GENERATED populations and assert **where the verdict flips**. (AC: AC6.2, AC6.4)
- [x] Build AC4's git-history citation guard on the `-75` template: three non-vacuity preconditions,
      the predicate driven to **both** outcomes over synthetic messages, the `SEAL_CITATION_RULE`
      written down, the remedy in the failure message. ⛔ **`argus/detectors/**` stays byte-unchanged.**
      (AC: AC4.1–AC4.4)
- [x] Amend protocol §5 by a **dated block under V1.3** that edits no existing byte and does not
      re-wrap the conjunction sentence `-63` pins. ⛔ **No `V1.4` row.** (AC: AC7.1)
- [x] Amend `architecture.md` §Enforcement struck-not-erased, extending *Gate-decision enforcement*;
      run `TC-ArgusAgent-DOCS-001-77` and confirm every anchor resolves. (AC: AC7.2)
- [x] Re-run `python scripts/build_gate_decision.py`; commit the regenerated record **separately**;
      confirm `-54` green and both builders `--check` exit 0. Record that no detector executed and no
      candidate was touched. (AC: AC7.3)
- [x] ⛔ **Verify by execution that `outcome`, `outcome_reason`, `closure_path` and the precision
      `gate_status` sentence are BYTE-IDENTICAL across the amendment**, and that the record gained a
      sixth condition reading `FAILED` and nothing else. If anything else moved, **stop and record why.**
      (AC: AC3.5)
- [x] Re-read the four published figures from `_live_figures()`; update `README.md` / `CHANGELOG.md`;
      regenerate the dogfood artifacts in the declared order and commit them separately. (AC: AC7.4)
- [x] Assert by execution: `VALIDATION_SET_FLOOR_N == 5`, `eligible_member_count() == 5`, the ≥80%
      `Fraction` unmoved, `MANIFEST_FIELDS` at 9, no member dropped or re-weighted, all 14 candidates
      still `eligible_for_n=False`. Record every reading. (AC: AC5.1, AC5.4)
- [x] Record `SEAL_COMMIT_SHA` in a **later** commit; verify `git diff --name-only` over this story's
      commits touches **no** `CANDIDATE_OUTPUT_PATHS` entry and that no corpus-audit script ran;
      record the landing shas for 16.4. (AC: AC1.5, AC7.5)
- [x] Full suite with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, **exit code recorded, 0 skipped**; `mypy`;
      `bandit`; NFR-M1 measured for every touched module; confirm `vacuous_test.py` and
      `test_vacuous_density.py` byte-unchanged. (AC: AC8.1, AC8.2)
- [x] Push; record the CI run id **with the sha it covers**, or record AC8.3 **OPEN** if instructed
      not to push. (AC: AC8.3)
- [x] Write the hand-off for 16.3 and 16.4 — **including §0.3's countable R2 constraint: ratify at
      least 3 of the six named sealed candidates, or `CLEARED` is unreachable.** (AC: AC8.4)

---

### Review Findings

**Round 1 — adversarial re-review, independent of the dev's own transcript.** Every claim below
was checked BY EXECUTION on this tree — the dev's own transcript was read but never trusted as
evidence. Nothing was patched; this round found nothing to patch.

- [x] [Review][Verified] The 6/8 partition and the override — RE-DERIVED independently, not
      read from the story. `int(commit_sha, 16) % 2` recomputed over all 21 manifest rows via
      `spec.partition`: bench split is exactly 6 sealed / 8 open, `bench_candidates()` ids equal
      `SEALED_PARTITION_TABLE` keys in both directions with zero mismatches, and
      `PRE_SEAL_MEMBER_IDS` equals the measured union of both committed adjudication sets'
      `members[]` arrays byte-for-byte. `xagents-webapp` (`33a86525…`) and `agent-smith`
      (`9ab774d7…`) both re-derive `sealed` with the override disabled, confirming the override
      is load-bearing and scoped only to the 5 pre-seal ids, not an arbitrary lever.
      `MANIFEST_FIELDS` reads 9. [tests/corpus/_manifest.py]
- [x] [Review][Verified] Git ancestry — `git log f89f028038dcd9881204f36bc404267c876b18f7 --
      <CANDIDATE_OUTPUT_PATHS>` returns zero commits, independently re-run. The seal commit
      resolves to a real commit object and is an ancestor of HEAD.
- [x] [Review][Verified] D1's circular-import claim (two siblings, not one) — read
      `gate_conditions.py` / `gate_evidence.py` / `gate_decision.py`: `CleanRepoEvidence.condition()`
      genuinely constructs a `ConditionResult` whose `__post_init__` validates against
      `SECTION_5_CONDITIONS`, so a single `gate_evidence` sibling holding both the evidence types
      and that vocabulary would need `gate_decision` to import it for `CleanRepoEvidence` while it
      imports `gate_decision` for `ConditionResult` — a real cycle, not a boundary chosen for line
      count. The three-way split is genuine cohesion (vocabulary / evidence / result), each layer
      imports only downward, and NFR-M1 line counts for all twelve touched/adjacent modules were
      independently recomputed with the shipped `_physical_line_count` and match the story's
      table exactly (`gate_decision.py` 986, `gate_conditions.py` 220, `gate_evidence.py` 214,
      `gate_seal.py` 777, `_manifest.py` 1029, `test_gate_seal.py` 1135, etc. — all OK).
- [x] [Review][Verified] AC3.5 byte-identity — re-diffed the committed
      `gate-decision-record.json` before/after field-by-field: `outcome`, `outcome_reason`,
      `closure_path`, `precision.gate_status` byte-identical; exactly four keys moved
      (`section_5_conditions` 5→6, each `corpus.members` row gained `partition`,
      `precision.seal_holds` added, top-level `seal` added) — matches the story's claim exactly.
- [x] [Review][Verified — central adversarial task] Independently mutated the shipped code and
      observed RED with fresh eyes, `PYTHONDONTWRITEBYTECODE=1` and cleared `__pycache__` before
      every run, tree restored via `git checkout` and `git status --porcelain` empty after each:
      bisection-parity flip (RED on `-87`/`-89`), override deleted (RED on `-87`/`-88`/`-90`/`-91`/`-92`),
      pin-check disabled in `partition_of` (RED on `-87`), one table row flipped and run against
      `test_gate_breadth.py` only — **GREEN, confirming the dev's own R5/R5b finding**: the
      breadth-side sealed-population generator (`sealed_corpus_members()`) derives from
      `spec.partition` (the RULE), not from `SEALED_PARTITION_TABLE` (the RECORD), so the two are
      a genuine independent cross-check and not one derived from the other; the same mutation
      against `-89` (the guard whose actual subject is the table-vs-rule agreement) is RED. Seal
      predicate stuck TRUE (RED on `-90`/`-91`) and stuck FALSE (RED on `-90`), the seal dispatch
      branch removed from `gate_decision.py` (RED on `-90`, and the failure is exactly the
      claimed shape: the condition still reads `FAILED` while the outcome moves from `BLOCKED` to
      `NOT_CLEARED` — proving the branch decisive), the seal term removed from
      `_precision_condition` (RED on `-90`, verdict flips `UNEVALUABLE`→`MET`), the pin check
      un-hoisted in `_manifest.py` (RED on both `-92` and `-76`, confirming the cross-story
      coupling), the citation predicate forced to accept everything and to accept nothing (RED on
      `-93` both ways), the seal floor forked to a literal (RED on `-90`, confirms DN-16-2-7's
      "resolved not forked" claim), and the sixth condition id dropped from
      `SECTION_5_CONDITIONS` in `gate_conditions.py` (RED on `-90` and on `-83`..`-86` in
      `test_gate_breadth.py`, confirming the cross-module coupling the split claims to preserve).
      Every mutation observed RED as claimed; no guard in the sample was unreal.
- [x] [Review][Verified] Gates re-run independently on this tree: full suite collects 1,667
      tests (matches the story's 1,658+9 baseline claim exactly) and completed with exit 0, no
      failures observed in the run; `mypy argus` → `Success: no issues found in 91 source files`;
      `bandit -r argus --severity-level medium` → `No issues identified`, 24,874 LOC, 0
      Medium/High; `tests/test_module_size_ceiling.py` green; both
      `scripts/build_gate_decision.py --check` and `scripts/build_adjudication_record.py --check`
      exit 0 on the committed artifacts. `git status --porcelain` clean throughout and at the end
      of this review.
- [x] [Review][Verified] Byte-unchanged claims spot-checked by diffing the base commit against
      HEAD: `argus/precision/gate_breadth.py`, `replay_harness.py`, `adjudication.py`,
      `tests/cartridges/**`, `tests/test_vacuous_density.py`, `scripts/candidate_selection.py`,
      `deferred-work.md`, `prd.md`, `epics.md`, `validation-corpus/adjudication-record.json` all
      show empty diffs against `6128466`.
- [x] [Review][Note] AC7.5's own recorded figure ("18 files") vs. this review's re-measurement
      ("21 files" over `981891e^..HEAD`) — not a defect: the extra 3 are the final story-record
      commit's own edits (`sprint-status.yaml`, the story file itself growing, and the
      hand-off/deviation prose), landed after the dev's own AC7.5 measurement was taken and
      recorded. Zero `CANDIDATE_OUTPUT_PATHS` entries are touched either way — AC7.5's actual
      claim holds under re-measurement. Not actioned; noted for the record only.
- [x] [Review][Note] `sealed ∩ ratified = ∅` today, so §5's new condition can only read
      `FAILED` on the committed record until 16.4's R2 ratifies ≥3 of the six named sealed
      candidates. This is judged **not** a repeat of Story 16.1's HALT-1: unlike the rule-class
      arm (unreachable by construction with the shipped detector set, under this epic's
      authorisation), reachability here is restored by an act the plan already schedules
      (§6 R2), the six eligible candidates and the exact count are named in the hand-off before
      the act rather than discovered after, and the story's own AC8.4 hand-off states the
      constraint explicitly. Recorded here as read, not as a defect.

No `decision-needed` or `patch` findings. No `defer` findings — nothing found here is pre-existing
and out of scope; everything checked was this story's own change. 0 dismissed.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), BMAD `dev-story` worker, single implementation round,
2026-08-20. Baseline HEAD `6128466`; the story file and its `ready-for-dev` transition were
untracked/uncommitted at that point and landed as this story's first commit.

### Debug Log References

Every figure below was produced by execution on this tree, out of tree and read-only unless it is
a commit. `git status --porcelain` was empty before the first commit, after every mutation restore,
and at the end.

#### §0 premises RE-DERIVED INDEPENDENTLY (the story's own instruction; 16.1's round 1 exists
because a "measured" premise was false inside its own story)

| Premise | Story says | I measured | Agrees |
|---|---|---|---|
| Manifest rows | 21 | **21** | ✅ |
| `eligible_member_count()` | 5 | **5** | ✅ |
| Bench candidates | 14, all `eligible_for_n=False` | **14, all False** | ✅ |
| `MANIFEST_FIELDS` | 9, CLOSED | **9** | ✅ |
| `int(sha,16)%2` vs `int(sha[-1],16)%2` | agree on every row | **21 of 21 agree, 0 disagreements** | ✅ |
| Bench split under the rule | 6 SEALED / 8 open | **6 / 8** | ✅ |
| `pre-seal` from the two adjudication sets | 5 members | **5**, `agent-markovich`, `agent-smith`, `ai-body-runtime`, `minions`, `xagents-webapp` | ✅ |
| Rows 4 & 5 carry ODD pins | yes — the override is load-bearing | **`xagents-webapp` `33a86525…` and `agent-smith` `9ab774d7…` both re-derive `sealed` with the override disabled** | ✅ |
| `gate_decision.py` | 1,197 / 1,200 | **1,197** | ✅ |
| `test_gate_decision.py` | 1,193 / 1,200 | **1,193** | ✅ |
| Split boundary by AST | `CleanRepoEvidence` 97 `:364-460`, `CorpusReadProof` 76 `:463-538` | **identical, to the line** | ✅ |
| The constructor gap | `commit_sha="NOT-A-SHA"` and `""` construct on a candidate row | **both constructed; so did `"ABCDEF…abcd"` (uppercase)** | ✅ |
| All 21 rows already satisfy 40-hex | yes | **yes — 0 rows fail** | ✅ |
| Baseline suite | 1,658 / 0 / 0 / 0, exit 0 | **exit 0** | ✅ |

**Nothing in §0 moved.** No figure had to be struck.

#### §2.4's AST walk, RE-RUN rather than trusted

Walked `test_gate_{decision,breadth,condition_lookup}.py`, counting `CLEARED`/`NOT_CLEARED`/
`BLOCKED` string literals in **executable code only**, docstrings excluded. Result: `-53`, `-55`,
`-56`, `-58`, **`-60`**, `-61`, `-62`, `-69`, `-70` (`test_gate_decision.py`); `-83`, `-85`, `-86`
and `expected_section_5_outcome` itself (`test_gate_breadth.py`); none in
`test_gate_condition_lookup.py`.

⚠️ **The walk returned one guard §2.4's table does not name: `-60`.** The story's own instruction
was *"look beyond the list"*, and this is what that found. `-60`'s outcome literals are all inside
`derive_residual_completion_bound` assertions and one `if payload["outcome"] == "BLOCKED"` branch
over the committed payload; verified by execution to need no change, and it stayed green
throughout. Recorded here rather than left implicit.

⚠️ **And one coupling NEITHER the story nor the walk names, found by running the suite:
`TC-ArgusAgent-PRECISION-001-76` in `tests/test_candidate_selection.py`.** It asserts, *as a
premise*, that `CorpusMemberSpec(commit_sha="deadbeef", eligible_for_n=False)` **constructs
silently** — a deliberate tripwire whose docstring says *"if `__post_init__` ever stops returning
early, this guard says so rather than quietly becoming redundant."* AC2.3's hoist made it fire.
It is re-authored as an intended behaviour change (below), never reverted and never relaxed.

### Completion Notes List

#### AC6.3 — the §2.4 audit, one line per guard, none silent

| Guard | Disposition | Evidence |
|---|---|---|
| `-53` | **verified, no change** — vocabulary only, no fixture | green throughout; uses no generator |
| `-54` | **no source change**; went red on the STALE committed record and green after regeneration | it compares the artifact to a live re-derivation, which is exactly its job |
| `-55` | **RE-AUTHORED** — the mirror call gains `seal_holds`, DERIVED here from the committed corpus (every ratified member is `pre-seal`, so no contributing member can be sealed), never read out of `assess_seal` | its docstring already records that this fixture reaches the mirror's FIRST clause; the seal clause is driven by `-90` |
| `-56` | **no source change**; red on the stale record, green after regeneration | asserts `reported == list(SECTION_5_CONDITIONS)` |
| `-58` | **RE-AUTHORED** — `_spread` now generates over SEALED rows and the same rows are passed as the decision's corpus | RED under R2 and R6 |
| `-59` | **verified, no change** | green; `_decide` default is unchanged |
| `-60` | **verified, no change** (found by my walk, absent from §2.4's table) | green |
| `-61` | **verified, no change** | green; RED under R6, so it is not inert |
| `-62` | **verified, no change** — conditional on the payload, not an assertion | green |
| `-63` | **verified, no change** — `protocol_version` did not move; no `V1.4` row | green; `build_adjudication_record.py --check` exit 0 |
| `-64` | **verified, no change** | green |
| `-69` | **verified, no change** | green; RED under R6 |
| `-70` | **verified, no change** | green |
| `-76` | **RE-AUTHORED** (not in §2.4's list) — premise moves from "constructs" to "RAISES", struck-not-erased in the docstring, and made **strictly stronger**: 5 generated bad pins refused on an INELIGIBLE row, plus a legal-shape control | RED under M12 / R4 |
| `-80` / `-81` | **verified, no change** | green; both assert `len(conditions) == len(SECTION_5_CONDITIONS) >= 4`, which is why they survived |
| `-83` | **RE-AUTHORED** — generates over `_sealed()` with the sealed corpus | RED under R1, R3 |
| `-84` | **RE-AUTHORED** — same | RED under R1, R3 |
| `-85` | **RE-AUTHORED** — `== 5` → `== 6`, plus a NEW assertion that `SECTION_5_CONDITIONS[4]` is still `BREADTH_CONDITION_ID`, so a condition INSERTED rather than appended reddens it even at the right count | RED under R3 |
| `-86` | **RE-AUTHORED** — `expected_section_5_outcome(..., seal_holds=)`, derived from the fixture; plus a new assertion that the generated population really is entirely sealed | RED under R1, R3 |

`expected_section_5_outcome` gained a **REQUIRED** keyword (no default) so no caller could silently
inherit the old answer — which is exactly how 16.1's breadth clause came to be unreachable in `-55`.

#### AC6.1 — EXECUTED MUTATIONS, EVERY ONE OBSERVED RED

Harness: apply one mutation → run the named modules with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`,
`PYTHONDONTWRITEBYTECODE=1`, `-p no:randomly -p no:cacheprovider` → record → restore the file
**byte-exact** with `write_bytes(original)` → assert `git status --porcelain` empty.

⚠️ **A methodology defect found and fixed mid-verification, recorded because it would have made
this evidence untrustworthy.** The first pass ran without disabling bytecode caching, and a
restored file whose byte-length was unchanged was later served from a stale `__pycache__`,
producing a **false RED** in an unrelated subsequent run. Every result below is from the **re-run
with caching disabled**, and the first pass's numbers were identical.

| # | File | Mutation | Guard(s) observed RED | Observed failure (first line) |
|---|---|---|---|---|
| M1 | `gate_seal.py` | bisection `% 2 == 1` → `== 0` | `-87`, `-89` | `AssertionError: ('000…0', 'sealed', 'open')` |
| M2 | `gate_seal.py` | prior-output override deleted (`if False and has_prior_output`) | `-87`, `-88` | `AssertionError: 000…0` (override direction) |
| M3 | `gate_seal.py` | pin check disabled in `partition_of` | `-87` | `ValueError: invalid literal for int() with base 16: ''` |
| M4 | `_manifest.py` | `agent-smith` DROPPED from `PRE_SEAL_MEMBER_IDS` | `-88` | *"frozen-only=[] run-over-only=['agent-smith']"* |
| M5 | `_manifest.py` | `pypa-pip` ADDED to `PRE_SEAL_MEMBER_IDS` | `-88` | *"frozen-only=['pypa-pip'] run-over-only=[]"* |
| M6 | `_manifest.py` | one table row flipped `sealed`→`open` | `-89` | *"the frozen table says 'open' and the rule re-derives 'sealed' from the pin '2c42237d…'"* |
| M7 | `_manifest.py` | a bench candidate omitted from the table | `-89` | *"'tox-dev-tox' is a bench candidate with no row in SEALED_PARTITION_TABLE"* |
| M8 | `gate_seal.py` | seal predicate stuck **TRUE** | `-90` | *"seal = 0 SEALED contributing member(s) of 3 contributing, against a floor of 3"* |
| M9 | `gate_seal.py` | seal predicate stuck **FALSE** | `-90` | *"seal = 3 SEALED contributing member(s) of 6 contributing, against a floor of 3"* |
| M10 | `gate_decision.py` | **the seal DISPATCH BRANCH removed** | `-90` | *"the measurement RAN … and 2 of protocol §5's 6 conditions did not hold"* — i.e. the condition still read FAILED while the OUTCOME stopped moving. This is the mutation that proves the clause is decisive rather than decorative. |
| M11 | `gate_decision.py` | the seal TERM removed from `_precision_condition` | `-90` | `AssertionError: precision = 1/1 over 18 adjudicated finding(s) … >= 4/5` (verdict `MET` where `UNEVALUABLE` was required) |
| M12 | `_manifest.py` | pin check **un-hoisted** behind the eligible branch | `-92`, `-76` | `Failed: DID NOT RAISE ValueError` |
| M13 | `gate_seal.py` | `cites_partition` accepts everything | `-93` | refused-direction assertion |
| M14 | `gate_seal.py` | `cites_partition` accepts nothing | `-93` | `AssertionError: Evidence-partition: sealed` |
| M15 | `test_gate_seal.py` | `SEAL_COMMIT_SHA` → a non-resolving sha | `-94` | `AssertionError: 000…0` |
| M16 | `gate_seal.py` | a declared detector-tuning path misspelled | `-94` | *"'argus/detectors-typo' does not exist … a misspelled pathspec reads exactly like a clean history"* |
| M17 | `gate_disclosure.py` | `partition` key dropped from the published row | `-87`.. + `MissingMemberPartition` | *"the fixture's corpus-member shape forked from the shipped producer's"* |
| M18 | `gate_seal.py` | seal floor FORKED (`return 1`) | `-90` | *"the seal floor forked from §5's breadth floor … two floors is how two corpora happened"* |
| M19 | `gate_seal.py` | counts `open` members as sealed | `-90`, `-91` | `AssertionError: ()` |
| M20 | `gate_seal.py` | a zero-member partition stops being STATED as zero | `-91` | `AssertionError: ['pre-seal', 'sealed']` |
| M21 | `gate_seal.py` | AC3.4's discrimination sentence removed | `-91` | *"assert 'NO SEALED MEMBER WAS IN THE POPULATION AT ALL' in 'seal = 0 SEALED …'"* |
| M22 | `gate_conditions.py` | the sixth id dropped from `SECTION_5_CONDITIONS` | `-90`, `-83`..`-86` | `ValueError: 'gate-evidence-drawn-from-the-sealed-partition' is not one of protocol §5's conditions` |
| R1 | `gate_seal.py` | seal stuck FALSE, run against `test_gate_breadth.py` only | **`-83`, `-84`, `-86`** | three FAILED |
| R2 | `gate_seal.py` | seal stuck FALSE, run against `test_gate_decision.py` only | **`-58`** | FAILED |
| R3 | `gate_conditions.py` | sixth id dropped, `test_gate_breadth.py` only | **`-83`, `-84`, `-85`, `-86`** | four FAILED |
| R4 | `_manifest.py` | pin check un-hoisted, `test_candidate_selection.py` only | **`-76`** | FAILED |
| R6 | `gate_decision.py` | the seal `ConditionResult` never built | **`-54`, `-56`, `-58`, `-59`, `-61`, `-69`** | six FAILED |

**27 mutations, 27 observed RED. Tree restored byte-exact and `git status --porcelain` empty after
every single one**, and the full suite re-run green afterwards.

⚠️ **One mutation I EXPECTED to be red was GREEN, and it is recorded rather than dropped.** **R5**
re-tabled three `sealed` rows as `open` in `SEALED_PARTITION_TABLE` and ran `test_gate_breadth.py`;
it stayed **GREEN**. That is **correct behaviour and my expectation was wrong**: the sealed
generators derive from `gate_seal.partition_of` (the RULE), not from the frozen table (the
RECORD) — which is the whole point of AC1.3. Re-running the identical mutation against its actual
guard (**R5b**) gives **RED** on `-89`. Recorded because a mutation whose expectation was wrong is
evidence about the design, and quietly deleting it would be the same class of act this epic exists
to prevent.

#### The seal condition, DRIVEN — why `-90` needed a mixed population

A population built only from sealed members has `sealed contributing == contributing`, so its seal
term and its breadth term move in **lockstep**, and a mutation deleting the seal clause outright
leaves every assertion green — **exactly** the unreal-guard finding the 2026-08-20 review made
against 16.1's round 2. `-90` therefore generates **`k` sealed members PLUS a fixed `floor`
pre-seal members**, which pins **breadth TRUE** while the sealed count sweeps `0..6`, so the seal
is the only term that can move the answer. Observed: `BLOCKED` for `k ∈ {0,1,2}`, `CLEARED` for
`k ∈ {3,4,5,6}`, verdict `FAILED`→`MET` flipping exactly at the derived floor of 3. M10 confirms
the branch is load-bearing.

#### AC3.5 — the amendment is INERT, VERIFIED AT THE PRODUCING SEAM

`build_decision(...)` was run with the committed artifact's own sha/date/provenance and compared
field-by-field, in **serialized** form (a first comparison of live payloads showed `threshold` and
`residual_completion_bound` "moving" — that was `Fraction` vs. its serialized form, not a real
difference, and it is recorded here because it is exactly the kind of artefact that would otherwise
be reported as a finding):

- `outcome` **BYTE-IDENTICAL** (`BLOCKED`) · `outcome_reason` **BYTE-IDENTICAL** ·
  `closure_path` **BYTE-IDENTICAL** · `precision.gate_status` **BYTE-IDENTICAL**
- `section_5_conditions` 5 → 6, a **clean prefix-plus-one**; the five historical verdicts unchanged
  (`UNEVALUABLE` / `MET` / `MET` / `FAILED` / `FAILED`), the appended one `FAILED`
- exactly four keys moved, **all of them this story's own**: `section_5_conditions`,
  `corpus.members` (each row gained `partition`), `precision.seal_holds`, `seal`

#### AC7.3 — regeneration executed NO detector and touched NO candidate

`scripts/build_gate_decision.py` reads the **committed** adjudication record, the **committed**
adjudication sets and the manifest, and folds the **CARTRIDGE** corpus for §5's clean-repo
condition — `tests/cartridges/`, this repository's own recall corpus, which is **not** a
validation-set member (DN-2). It executes no detector over any repository, stages nothing, fetches
nothing, and touches no candidate. All 14 bench candidates remain unrun. `adjudication-record.json`
is byte-unchanged and `build_adjudication_record.py --check` exits 0, so §2.3's coupling stayed
**unarmed**.

#### AC5.1 / AC5.4 — the readings that prove it PARTITIONS and does not NARROW

`VALIDATION_SET_FLOOR_N` **5** · `validation_floor_n()` **5** · `eligible_member_count()` **5** ·
`len(VALIDATION_CORPUS)` **21** · `len(MANIFEST_FIELDS)` **9** · `PRECISION_GATE_THRESHOLD`
**4/5** · `len(GATE_OUTCOMES)` **3** · `len(CONDITION_VERDICTS)` **4** ·
`len(SECTION_5_CONDITIONS)` **6** · bench candidates **14, every one still `eligible_for_n=False`**
· every candidate's `adjudication_caveat` intact · partition census over all 21 rows **6 sealed /
10 open / 5 pre-seal** · bench split **6 sealed / 8 open** · seal floor **3** == breadth floor
**3** · frozen table **14 rows** · committed record **31 rows, `protocol_version` V1.3**.

#### AC8.2 — NFR-M1, before and after, with `_physical_line_count`

| Module | Before | After | Headroom |
|---|---|---|---|
| `argus/precision/gate_decision.py` | **1,197** | **986** | 214 |
| `argus/precision/gate_conditions.py` | — | **220** | 980 |
| `argus/precision/gate_evidence.py` | — | **214** | 986 |
| `argus/precision/gate_seal.py` | — | **777** | 423 |
| `argus/precision/gate_disclosure.py` | 341 | **350** | 850 |
| `tests/corpus/_manifest.py` | 886 | **1,029** | 171 |
| `tests/test_gate_decision.py` | 1,193 | **1,191** | 9 |
| `tests/test_gate_breadth.py` | 622 | **704** | 496 |
| `tests/test_gate_seal.py` | — | **1,135** | 65 |
| `tests/test_candidate_selection.py` | 698 | **740** | 460 |
| `argus/detectors/vacuous_test.py` | 1,196 | **1,196 — BYTE-UNCHANGED** | 4 |
| `tests/test_vacuous_density.py` | 1,159 | **1,159 — BYTE-UNCHANGED** | 41 |

`git diff --name-only 981891e^..HEAD` over `argus/detectors/` and `tests/test_vacuous_density.py`:
**0 files.** AC4.4's *"`argus/detectors/**` stays BYTE-UNCHANGED"* holds by execution.

### Decisions this story TOOK beyond the story's own DN table, each with its rationale

**DN-16-2-7 — the seal floor IS §5's breadth floor, resolved through the same function.** The
condition requires at least `contributing_member_floor(VALIDATION_SET_FLOOR_N)` = **3** distinct
SEALED contributing members. *Rejected:* **every contributing member must be sealed** — a SHUTDOWN
by construction, because the five pre-seal members will keep contributing and the only way to
satisfy it would be to drop them, which is the NARROWING AC5 forbids; 16.1 HALTED rather than land
an unsatisfiable arm and the same test applies here. *Rejected:* **≥ 1 sealed member** — that is
H-1 (*a score drawn from one repository is not a score*) re-introduced on the sealed side, one
epic after it was closed. *Rejected:* **a majority of contributing members** — set-relative, so the
threshold would move as a side effect of how many pre-seal members happened to emit. *Rejected:* a
second seal-specific constant — DN-3's one-floor rule, forked. The chosen floor also makes §0.3's
closure path exactly countable: **ratify ≥ 3 of the six sealed candidates, or `CLEARED` is
unreachable.** Guarded by `-90`, and M18 proves the resolution is real.

**DN-16-2-8 — `sealed_precision_gate_status` is a sibling of `effective_precision_gate_status`,
not a widening of it.** Both are thin wrappers over the ONE shared renderer
`replay_harness.precision_gate_status_for`; neither authors a status string. The story's write set
holds `argus/precision/gate_breadth.py` **byte-unchanged** (*"read it; do not edit its subject"*),
and that module's subject is the breadth arm — giving its renderer a second reason would make it
not-about-breadth. `GateDecision.precision_gate_status` reports the **FIRST binding reason in §5's
own condition order**, so a population failing both is told about breadth: reporting the later
reason would tell a reader the evidence was un-sealed when there was not enough of it to ask.

**DN-16-2-9 — the sealed-population generators live in the TEST tree, not in `argus/**`.** §0.4
suggested `gate_disclosure` as the home for `sealed_corpus_member_ids`. It has **no production
caller**, and shipping a public function no shipped code calls is dead surface. `partition` on
`ratified_corpus_members()` — which does have one — went to `gate_disclosure` exactly as §0.4 says.
The fixtures (`sealed_corpus_members`, `pre_seal_corpus_members`, `spread_over_sealed`,
`mixed_population`) are named **once**, in `tests/test_gate_seal.py`, and IMPORTED by
`test_gate_decision.py` and `test_gate_breadth.py` — the precedent this tree already sets with
`expected_section_5_outcome` and `protocol_cleared_call_sites`. **AR7 satisfied without shipping
dead code**, and `sealed_corpus_members()` asserts its mapping shape against the shipped producer
so the fixture cannot fork from it (M17 proves that assertion real).

### ⚖️ DEVIATIONS from the declared write set, each RECORDED with its rationale (AC8.5)

**D1 — the split is TWO sibling modules, not one, and it moves 319 lines rather than 173.**
§2.1 measured the boundary as `CleanRepoEvidence` (97) + `CorpusReadProof` (76) = 173 contiguous
lines. **Executing that alone produces a CYCLE**, measured not predicted:
`CleanRepoEvidence.condition()` CONSTRUCTS a `ConditionResult`, whose `__post_init__` validates
against `SECTION_5_CONDITIONS` — so the sibling would import `gate_decision` while `gate_decision`
imports the sibling. Three layers were tangled and they are strictly ordered, so they became three
modules: `gate_conditions.py` (what a §5 condition IS, 152 moved lines), `gate_evidence.py`
(what one is MEASURED FROM — **exactly** the story's measured boundary, 173 lines),
`gate_decision.py` (what the result IS). *Rejected:* a function-local import to dodge the cycle
(a smell, and it hides a real layering fact); *rejected:* relocating `CleanRepoEvidence.condition()`
out to `gate_decision` the way DN-16-1-3 has it build the breadth condition — that would make the
split a **behaviour change** on the one commit whose entire value is that it is not one. The move
is proved byte-exact: each of the six moved spans was compared against `git show
HEAD:argus/precision/gate_decision.py` and is identical in the new module and absent from the old.
**Every import line in the repository is byte-unchanged.**

**D2 — `tests/test_candidate_selection.py` was edited, and it is not on the declared write set.**
`TC-ArgusAgent-PRECISION-001-76` is a deliberate tripwire over the exact `__post_init__` early
return AC2.3 requires closing, and it fired. Re-authored strictly stronger, struck-not-erased.
Not touching it was not an option: the alternative was reverting AC2.3.

**D3 — `tests/test_release_preflight.py` was edited, and it is not on the declared write set.**
`RELEASE-001-11`'s `_MODULES_NAMING_THE_TEST_TREE_IMPORT` is a registry whose own docstring says an
addition is *"DELIBERATE, which is what this registry exists to force someone to say."* Three new
`argus/**` modules join it, each with its reason, each transitively and each resolving no path at
module level.

**D4 — the four published figures were updated TWICE, in two commits.** §2.5 implies one update.
`DF-16-1-B` requires the split as its own commit, and `DOCS-001-54` pins the figures in both
directions — so a single update would have left one of the two commits red. They move 88→90 in the
split commit (naming the split) and 90→91 in the seal commit (naming `gate_seal.py`), so each
commit is green and each parenthetical states what that commit did.

**D5 — nothing else.** `deferred-work.md`, `prd.md`, `epics.md`, `adjudication-record.json`, the
adjudication sets, `scripts/candidate_selection.py`, `argus/detectors/**`, `gate_breadth.py`,
`replay_harness.py`, `adjudication.py`, `tests/cartridges/**`, `tests/test_vacuous_density.py` and
`tests/test_status_document_registry.py` are all **byte-unchanged**. **No `DF-*` entry is disposed
of; this story disposes of none.**

### What this story did NOT do, because none of it is authorised

No member was ratified, fetched, staged or checked out. **No detector executed over any repository
— ratified or candidate.** `DF-13-5-A`'s ONE round is **UNSPENT**. `DF-16-1-A` stays **OPEN and
unlanded** and no rule-class threshold is written anywhere. No protocol version was taken and there
is **no `V1.4` row**. `sprint-change-proposal-2026-08-20-amendment-A.md` is registered and
**UNAPPROVED**; nothing here applies it, cites it as authority or acts on it. **Opening the sealed
partition is a single recorded §6 R2-class operator act, and this story adds no code path that
opens it** — the partition is derived from pins, the pins are frozen, and no writer exists.

### AC1.5 / AC7.5 — the ordering, and the landing shas for 16.4

**`SEAL_COMMIT_SHA = f89f028038dcd9881204f36bc404267c876b18f7`**, recorded in
`tests/test_gate_seal.py` in a **later** commit (`9d7f8b5`), on Story 15.1's `16d7100d → 4f4db78`
pattern: *a commit cannot cite itself.*

| # | Sha | Subject |
|---|---|---|
| 1 | `981891e` | `chore(16-2): file the contexted story and take it in-progress` |
| 2 | `95819bc` | `refactor(16-2): split gate_decision before a sixth condition lands in it` (`DF-16-1-B`) |
| 3 | **`f89f028`** | **`feat(16-2): seal part of the bench before anything is run` — THE SEAL COMMIT** |
| 4 | `fd20c32` | `chore(16-2): regenerate the record and the dogfood artifacts, in the declared order` |
| 5 | `9d7f8b5` | `feat(16-2): record the seal sha, which a commit cannot cite about itself` |
| 6 | *(this commit)* | the story record |

Verified by execution: `git diff --name-only 981891e^..HEAD` touches **18 files and NOT ONE**
`CANDIDATE_OUTPUT_PATHS` entry; `git log` over those paths across the whole range returns **0
commits**; no corpus-audit script ran and no audit output exists in the tree.

### AC8.1 / AC8.3 — gates

| Gate | Result |
|---|---|
| `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 python -m pytest` | **1,667 collected · 1,667 passed · 0 failed · 0 skipped · exit 0** (baseline 1,658; +9 new guards) |
| `mypy argus` | **Success: no issues found in 91 source files** (was 88) |
| `bandit -r argus --severity-level medium` | **No issues identified** (24,874 LOC; by severity: Low 20, Medium 0, High 0) |
| `python scripts/build_gate_decision.py --check` | **exit 0** (`CURRENT — BLOCKED`) |
| `python scripts/build_adjudication_record.py --check` | **exit 0** |
| module-size ceiling (`TC-ArgusAgent-MAINT-001-01`..`-05`) | **green**; see AC8.2's table |
| `TC-ArgusAgent-DOCS-001-54` (four published figures) | **green** — 91 / 91 / 99 / 98, read from `_live_figures()` |
| `TC-ArgusAgent-DOCS-001-77` (architecture registrations) | **green** |
| **AC8.3 — CI run id** | ⛔ **OPEN.** I was instructed **not to push**, so no CI run covers these shas. ⚠️ **The local gates are Windows-only while CI runs an ubuntu matrix, and a green local suite has already shipped POSIX-only bugs to master.** This is recorded OPEN rather than claimed. |

### Hand-off to 16.3 and 16.4 (AC8.4)

1. **THE SEAL SHA, for 16.4's ancestry guard: `f89f028038dcd9881204f36bc404267c876b18f7`.** It is
   already a constant in `tests/test_gate_seal.py`; **import it, do not re-type it.**
2. ⛔ **THE COUNTABLE §6 R2 CONSTRAINT, which the operator must be told BEFORE the act.** §5's seal
   condition needs **≥ 3 distinct SEALED contributing members**. The sealed partition holds exactly
   six candidates: **`aws-aws-sam-cli`, `celery-celery`, `certbot-certbot`, `conda-conda`,
   `getsentry-sentry-python`, `googleapis-google-auth-library-python`.** **Ratifying only
   open-partition members leaves the gate permanently `BLOCKED` on this condition.** And ratifying
   three is necessary, not sufficient: each must actually *emit* a verdict-eligible finding that
   survives adjudication, which is unknowable without running.
3. **THE FROZEN PARTITION TABLE** is `_manifest.SEALED_PARTITION_TABLE` — 6 sealed / 8 open — with
   `PRE_SEAL_MEMBER_IDS` (5) beside it. `-89` re-derives every row from the rule in both
   directions; **never read the table as a hand-list.**
4. **`expected_section_5_outcome(fold, *, breadth_holds, seal_holds)`** — both keywords REQUIRED,
   no defaults. 16.3 adds its yield term the same way: **add to the mirror, never fork it**, and
   derive every term from the fixture. Note that over a purely-sealed population `breadth_holds`
   and `seal_holds` move in lockstep; `-90`'s **mixed** population (sealed + pre-seal ballast) is
   the pattern that isolates one term. **16.3 will need the same trick.**
5. **The §2.4 coupling will fire a THIRD time.** Every §5-outcome fixture now generates over
   SEALED rows via `tests/test_gate_seal.py`'s generators. A seventh condition re-couples `-83`,
   `-84`, `-85`, `-86`, `-58`, `-55`, `-90`, `-91` — and `-85`/`-91` pin the condition COUNT
   explicitly, so both go red the moment `SECTION_5_CONDITIONS` grows. Re-run the AST walk
   yourself; my run found `-60`, which §2.4's table does not name.
6. ⚠️ **NFR-M1 headroom that 16.3 should know about before it starts:** `tests/corpus/_manifest.py`
   **1,029 / 1,200** (171) and `tests/test_gate_seal.py` **1,135 / 1,200** (65) are the tightest
   files this story leaves. `tests/test_gate_decision.py` came back to **1,191** (9) by MOVING
   `_spread` out rather than shaving it. `argus/precision/gate_decision.py` is at **986** (214) —
   `DF-16-1-B`'s trigger is discharged, but a seventh condition is not free.
7. **Protocol §5 now carries TWO dated blocks under V1.3.** A third amendment adds a third block.
   ⛔ **Still no `V1.4` row** — locked operator decision; the 31 judgements of 2026-08-17 keep
   their V1.3 provenance, and `build_adjudication_record.py` stays un-re-run.
8. **§2.2's coupling is now armed for you:** any change to `SECTION_5_CONDITIONS` requires
   `python scripts/build_gate_decision.py` re-run and the record re-committed, **in its own commit
   after the code commit** — and regenerating is not Argus output over a bench member.
9. **The dogfood artifacts cite `f89f028`.** Any further `argus/**` delta re-arms the LOC-currency
   guards: commit `argus/` first, then `python scripts/regenerate_dogfood_artifacts.py`, then
   commit the artifacts separately. The script refuses on a dirty `argus/` tree by design.
10. **AC8.3 is OPEN.** Nothing was pushed and no CI run covers `981891e..HEAD`. The local gates are
    Windows-only; the ubuntu matrix has not seen this change.
11. **A post-seal detector change must now carry `Evidence-partition: sealed | open | none`.**
    `-94` enforces it over real git history and its population is EMPTY today — `-93` is what makes
    the predicate real. If 16.3 or 16.4 touches `argus/detectors/**` or
    `argus/precision/replay_harness.py`, **write the trailer**; amending the rule to make a red
    commit green is the corpus-shopping failure mode with an extra step.

### File List

**New (`argus/`)**
- `argus/precision/gate_seal.py` — the partition vocabulary, the pure rule, its derivation, the
  seal assessment, the published sentences and the citation rule
- `argus/precision/gate_conditions.py` — `DF-16-1-B` split: what a §5 condition IS
- `argus/precision/gate_evidence.py` — `DF-16-1-B` split: what one is MEASURED FROM

**New (`tests/`)**
- `tests/test_gate_seal.py` — `TC-ArgusAgent-PRECISION-001-87`..`-94`, the sealed-population
  generators, and `SEAL_COMMIT_SHA`

**Modified**
- `argus/precision/gate_decision.py` · `argus/precision/gate_disclosure.py`
- `tests/corpus/_manifest.py` · `tests/test_gate_decision.py` · `tests/test_gate_breadth.py` ·
  `tests/test_candidate_selection.py` · `tests/test_release_preflight.py`
- `README.md` · `CHANGELOG.md`
- `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` (§5, second dated
  block under V1.3) · `architecture.md` (§Enforcement, struck-not-erased)
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json`
  (regenerated) · `minions-dogfood-{partition-plan,budget-plan,proof}.md` (regenerated)
- this story file · `sprint-status.yaml`

**Byte-unchanged, confirmed by execution:** `argus/detectors/**` ·
`argus/precision/gate_breadth.py` · `argus/precision/replay_harness.py` ·
`argus/precision/adjudication.py` · `tests/cartridges/**` · `tests/test_vacuous_density.py` ·
`scripts/candidate_selection.py` · `deferred-work.md` · `prd.md` · `epics.md` ·
`validation-corpus/adjudication-record.json` · `validation-corpus/adjudication-set*.json` ·
`tests/test_status_document_registry.py`

---

## Change Log

| Date | Change | By |
|---|---|---|
| 2026-08-20 | **Story IMPLEMENTED in one round; Status `in-progress` → `review`.** §0's premises were re-derived independently before anything was written and **none moved** — 21 rows, N=5, 14 candidates, `MANIFEST_FIELDS` 9, whole-sha and last-digit parity agreeing on all 21 rows, the 6/8 bench split, the 5-member pre-seal set, the 1,197/1,193 line counts, the AST boundary to the line, and the constructor gap (`commit_sha="NOT-A-SHA"`, `""` and an uppercase 40-char sha all constructed on a candidate row). **`DF-16-1-B`'s SPLIT-FIRST trigger was discharged FIRST and in its own commit (`95819bc`)**, 319 lines moved byte-for-byte and proved identical against `git show HEAD:...`, every import line in the repository unchanged — **as TWO siblings rather than one, because executing §2.1's measured boundary alone produces a CYCLE** (`CleanRepoEvidence.condition()` constructs a `ConditionResult` that validates against `SECTION_5_CONDITIONS`), recorded as deviation D1 with the two rejected alternatives. **The seal landed in `f89f028`**: the rule as ONE pure function with a closed three-value vocabulary, the prior-output override that stops two odd-pinned already-audited members being declared holdouts, the derivation and its three rejected alternatives recorded in code, the frozen 14-row table re-derived from the rule in both directions, the derived `pre-seal` set, the `partition` property (`MANIFEST_FIELDS` stays closed at 9 — a `@property` is not a dataclass field), the hoisted 40-hex pin check that now validates EVERY row, and §5's SIXTH condition APPENDED with its floor RESOLVED from 16.1's rather than forked (DN-16-2-7). **AC3.5 verified at the producing seam: `outcome`, `outcome_reason`, `closure_path` and `precision.gate_status` BYTE-IDENTICAL across the amendment; exactly four keys moved, all of them this story's own.** **27 EXECUTED mutations of the shipped code, 27 observed RED, tree restored byte-exact and `git status --porcelain` empty after every one** — including both directions of the bisection, the override, the pin refusal, the seal predicate, the citation predicate, and the dispatch branch whose removal leaves the CONDITION reading FAILED while the OUTCOME stops moving. A 28th (**R5**) was GREEN and is recorded rather than dropped: my expectation was wrong, because the generators derive from the RULE and not from the frozen TABLE, and re-running the identical mutation against `-89` gives RED. A methodology defect is also recorded: the first pass ran without `PYTHONDONTWRITEBYTECODE`, a stale `__pycache__` produced one false RED in a later run, and every number above is from the re-run with caching disabled. Eleven §2.4 guards audited plus **two the story's table does not name** (`-60`, found by re-running the AST walk; **`-76`**, a deliberate tripwire that fired on the AC2.3 hoist and was re-authored strictly stronger). Protocol §5 amended by a SECOND dated block under **V1.3** — no `V1.4` row, `adjudication-record.json` byte-unchanged, the 31 judgements of 2026-08-17 keep their provenance. `architecture.md` §Enforcement extended struck-not-erased. Gates: **1,667 passed / 0 failed / 0 skipped / exit 0** with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; `mypy argus` Success (91 files); `bandit --severity-level medium` No issues identified; both builders `--check` exit 0. **AC8.3 recorded OPEN — instructed not to push, so no CI run covers these shas, and the local gates are Windows-only.** Nothing was ratified, fetched, staged or run over; `DF-13-5-A`'s round is UNSPENT, `DF-16-1-A` stays unlanded, amendment-A stays UNAPPROVED and unacted-on, and no `DF-*` entry is disposed of. | dev-story |
| 2026-08-20 | **Code review round 1 — PASS. Status `review` → `done`.** Adversarial re-review independent of the dev's own transcript: every load-bearing arithmetic claim (the 6/8 partition, the override, `PRE_SEAL_MEMBER_IDS` derived from the two adjudication sets, `MANIFEST_FIELDS` at 9) was RE-DERIVED by execution rather than read from the story; git ancestry re-run and confirms zero commits reachable from `f89f028038dcd9881204f36bc404267c876b18f7` touch `CANDIDATE_OUTPUT_PATHS`; AC3.5's byte-identity claim re-diffed field-by-field and confirmed exact (four keys moved, all this story's own); D1's circular-import justification for the three-way split read against the actual code and confirmed real, not line-count-driven, with all twelve touched/adjacent NFR-M1 line counts independently recomputed with the shipped `_physical_line_count` and matching exactly. **Central adversarial task — independently mutated the shipped code with `PYTHONDONTWRITEBYTECODE=1` and a cleared `__pycache__`, restored via `git checkout` after each, `git status --porcelain` clean throughout**: bisection flip, override deletion, pin-check disable, seal predicate stuck both ways, the seal dispatch branch removed (confirmed decisive: condition stays `FAILED` while outcome moves `BLOCKED`→`NOT_CLEARED`), the seal term removed from `_precision_condition`, the pin check un-hoisted (RED on both `-92` and `-76`, cross-story coupling confirmed), the citation predicate forced both directions, the seal floor forked to a literal, and the sixth condition id dropped from `SECTION_5_CONDITIONS` — every one observed RED as claimed. The dev's own R5/R5b finding (one guard family derives from the RULE, the other from the frozen TABLE, and they genuinely cross-check rather than one deriving from the other) was independently reproduced: the same table-row-flip mutation is GREEN against `test_gate_breadth.py` and RED against `-89`. Gates re-run independently: 1,667 tests collected (matches exactly), full suite exit 0 with no observed failures; `mypy argus` Success on 91 files; `bandit --severity-level medium` No issues identified, 24,874 LOC; module-size ceiling green; both builders `--check` exit 0; byte-unchanged claims for `gate_breadth.py`, `replay_harness.py`, `adjudication.py`, `tests/cartridges/**`, `tests/test_vacuous_density.py`, `scripts/candidate_selection.py`, `deferred-work.md`, `prd.md`, `epics.md` and `adjudication-record.json` spot-checked and confirmed. Two notes recorded, neither actioned: AC7.5's own "18 files" figure reads 21 under re-measurement, entirely accounted for by the final story-record commit's own edits, with zero candidate-output paths touched either way; and `sealed ∩ ratified = ∅` today is judged an honest, countable strengthening rather than a repeat of Story 16.1's HALT-1, because 16.4's R2 act (named, with its exact count, in the hand-off) restores reachability, unlike the rule-class arm's unreachability by construction. Zero `decision-needed`, zero `patch`, zero `defer` findings. `sprint-status.yaml` `development_status` set to `done`. | code-review |
| 2026-08-20 | Story contexted at HEAD `6128466`, baseline measured GREEN by execution (1,658 tests exit 0, mypy 88 files, bandit clean, both builders `--check` exit 0). §0 premises measured on the live tree, read-only. **§0.2 records the rule and the partition it produces (6 SEALED / 8 open of 14), with the proof that "parity of the sha" and "parity of the last hex digit" are ONE rule, and with the measurement that makes the prior-output override load-bearing: `xagents-webapp` and `agent-smith` both carry ODD pins and would have been declared "sealed" despite having been audited twice.** **§0.3 answers the shutdown question 16.1 escalated on: the breadth floor is 3, invariant under corpus size; six sealed candidates are available against it, slack 3, all six clearing Story 15.1's co-occurrence floor — so the seal does NOT make breadth unsatisfiable — and the countable R2 consequence (ratify ≥3 of six named candidates) is recorded for 16.4 rather than discovered after the act.** **§0.5 answers the `MANIFEST_FIELDS` question by execution rather than by assumption: `-22` compares `dataclasses.fields`, so a derived property is not a field and the schema stays closed at 9 — with a HALT recorded if anyone judges otherwise, because extending a locked constant is not a dev's decision; and the measured constructor gap (a candidate row accepts `commit_sha="NOT-A-SHA"` today) is what AC2's "validated at construction" repairs.** §2.1 raises `DF-16-1-B`'s SPLIT-FIRST trigger to **Task 1** with the boundary measured by AST (173 contiguous lines, four importers enumerated). §2.4 records the coupling that will bite hardest: **all three §5-outcome fixture generators spread over the five ratified members, every one of which becomes `pre-seal`**, with the coupled guards enumerated by AST walk into two tiers (6 Tier-1 asserting `CLEARED`/`NOT_CLEARED` in code, 12 Tier-2 built on a pre-seal generator) — and with the first, looser scan's over-report corrected in place rather than quietly fixed, because a stated-as-measured list that is wrong is the exact defect Story 15.1's fix round exists for. §2.5 records the two narrowing designs proved by execution to `raise`, which is why the seal is a §5 CONDITION and not a filter. Locked decisions cited and not reopened: `DF-16-1-A` stays unlanded, no `V1.4` row, `DF-13-5-A`'s round UNSPENT, amendment-A UNAPPROVED and out of scope. Status `backlog` → `ready-for-dev`. | create-story |
