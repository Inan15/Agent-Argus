---
baseline_commit: 3022415
---

# Story 16.4: Ratify, run, adjudicate, and let the arithmetic decide

Status: in-progress — ⛔ **HALTED at Task 1** awaiting the operator (HALT-1, HALT-2, HALT-3)

| | |
|---|---|
| **Epic** | 16 — Spend the Round Well — strengthen the gate, then measure once |
| **Story key** | `16-4-ratify-run-adjudicate-and-let-the-arithmetic-decide` |
| **Source** | [epics.md](../epics.md) §Epic 16 (`epics.md:3019`), §Story 16.4 (`epics.md:3153`) · [sprint-change-proposal-2026-08-20.md](../sprint-change-proposal-2026-08-20.md) · [precision-validation-protocol.md](../precision-validation-protocol.md) §2, §3, §4, §5, §6 |
| **Contexted on** | HEAD `3022415` (`docs(16-3): close the round — a PASS that re-derived rather than read`), working tree **CLEAN**, **26 ahead of `origin/master`, 0 behind** |
| **Baseline gates (measured, this tree)** | full suite **1,673 collected · exit 0 · 0 failed · 0 skipped** with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` · `mypy argus` **Success, 92 source files** · `bandit -r argus --severity-level medium` **No issues identified** (25,419 LOC) · `build_gate_decision.py --check` exit **0** (`CURRENT — BLOCKED`) · `build_adjudication_record.py --check` exit **0** (`31 row(s)`) |
| **Authorisation** | ⛔ **THIS STORY IS NOT AUTHORISED TO PROCEED PAST TASK 1.** The 2026-08-20 approval unblocked **16.1, 16.2 and 16.3 ONLY**. Epic 16's own header says so in terms: *"What it does NOT unblock: Story 16.4, which still opens by halting on the protocol §6 **R2** operator act — ratification and third-party fetch remain a separate, not-yet-taken decision, and approval of this epic is not approval to spend `DF-13-5-A`'s round."* |
| **Autonomy** | ⛔ **NOT AUTONOMOUS.** `epics.md:3163`: *"This story is not autonomous and must not be driven to completion by the dev loop without the operator in the loop."* A dev-loop worker that ratifies a member, fetches third-party source, runs a detector over a bench member, or writes a TP/FP disposition has produced the exact artifact Epic 13 exists to make impossible. |
| **Direction** | ⛔ **MEASURE ONLY.** Nothing here moves a threshold, a floor, a member's weight or a condition. The gate outcome is whatever `decide_gate` returns, re-run **unmodified**. |

---

## Story

As the Engineering Lead,
I want **the ratified bench audited at its pins and every blocking finding adjudicated under §4**,
So that the gate outcome is a measurement rather than an assertion.

### What this story IS

**The ONE round.** `DF-13-5-A` was answered on 2026-08-17, **before any number existed**, with a
pre-registered rule permitting exactly **one** bench-expansion round. Epic 15 chose the bench under
criteria frozen before anyone looked; Epic 16's first three stories closed the three holes that
would otherwise let the resulting figure mean less than it appears to. This story **spends** the
round: the operator ratifies, the pinned bytes are audited, the named human adjudicates every
blocking finding exhaustively under §4's ladder, `decide_gate` is re-run unmodified, and **whatever
comes out is recorded**.

Four of its five parts are **operator acts under protocol §6 R2 and §2/§4**, and no agent may take
them. The autonomous part is small and precise: an **ordering guard** proving from git ancestry that
16.1, 16.2 and 16.3 landed before any output over a bench member existed, and the mechanical
re-computation once a human's judgements are on the record.

### What it is NOT

- **NOT autonomous, and this is the story's first sentence rather than a caveat.** Ratifying a
  member, fetching third-party source, running a detector over a bench member, and dispositioning a
  row are four distinct operator acts. `UNADJUDICATED` is the **only** disposition an automated
  producer may write, enforced at construction by `AdjudicationRow.__post_init__`.
- **NOT a second round, and not the beginning of one.** If the outcome is `UNEVALUABLE` or below
  threshold, `DF-13-5-A`'s pre-registered option **(b)** is executed as written: *"the FR34
  disclosure stands for V1.5 … the next attempt requires a materially better detector — NOT a
  bigger bench."* ⛔ **This story proposes no expansion, under any outcome.**
- **NOT a new §5 condition.** §5 carries **seven** and this story adds none. `SECTION_5_CONDITIONS`
  stays closed at 7, `GATE_OUTCOMES` at 3, `CONDITION_VERDICTS` at 4, `MANIFEST_FIELDS` at 9.
- **NOT a protocol re-version.** ⛔ **No `V1.4` row.** §4 is explicit: *"the protocol is amended
  BEFORE the run, never reinterpreted during it"*, and a version taken **during** the run is that
  prohibition read backwards. The R2 act is recorded as a **dated block** in §6, under V1.3, the
  fourth application of the locked operator decision of 2026-08-20. See §2.6.
- **NOT a narrowing.** No member is dropped, re-weighted or made ineligible to move the ratio.
  `VALIDATION_SET_FLOOR_N` stays **5**. Ratification RAISES the member count; it never lowers it.
- **NOT a threshold change.** The ≥80% `Fraction`, the breadth floor of 3, the seal floor of 3 and
  the yield floor of 5 are all byte-unchanged, whichever way the number lands.
- **NOT the rule-class arm.** `DF-16-1-A` stays **OPEN and unlanded**.
- **NOT the independence claim.** Story 16.5 makes the adjudication's independence legible. This
  story does not fill protocol §2's QA-Lead or External-adjudicator role, does not claim
  independence, and does not gate on one being filled.
- **NOT an approval of anything.** [sprint-change-proposal-2026-08-20-amendment-A.md](../sprint-change-proposal-2026-08-20-amendment-A.md)
  is **registered and UNAPPROVED**. Nothing in it is in scope; this story does not approve, apply,
  cite as authority, or act on any part of it.
- **NOT a licence to open the sealed partition.** The seal is opened only by a further §6 R2-class
  act. This story **runs over the sealed partition**; it does not un-seal it, and adds no code path
  that could.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `3022415`

> ⛔ **Read this section before anything else, and re-derive every figure yourself.** Every prior
> worker in this epic found at least one stated premise FALSE by executing it: 16.1 escalated
> because its second arm was a shutdown; 16.2 found its "obvious" partition rule re-derivable and
> its `MANIFEST_FIELDS` premise wrong; 16.3 found an undocumented split-first trigger nine lines
> from the ceiling. Everything below was **run**, on this tree, at this HEAD.

### §0.0 The tree

Clean, `git status --porcelain` empty, 26 ahead of `origin/master`. Measured here, by execution:
full suite **1,673 collected · exit 0 · 0 failed · 0 skipped** with
`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; `mypy argus` Success on 92 source files;
`bandit -r argus --severity-level medium` No issues identified over 25,419 LOC; both builders
`--check` exit 0. **Re-run all of it yourself before Task 1** — a baseline you did not measure is a
baseline you cannot attribute a regression against.

### §0.1 Where the gate stands, condition by condition

Read off the committed `validation-corpus/gate-decision-record.json`:

| # | Condition id | Verdict |
|---|---|---|
| 1 | `precision-at-least-80-percent` | **`UNEVALUABLE`** |
| 2 | `clean-repo-blocking-false-positives-zero` | `MET` *(NOT APPLICABLE over the repository corpus; MET over the cartridge corpus)* |
| 3 | `corpus-floor-n-at-least-5` | `MET` |
| 4 | `adjudication-run-recorded-cleared` | **`FAILED`** |
| 5 | `denominator-breadth-contributing-members` | **`FAILED`** (2 contributing of a floor of 3) |
| 6 | `gate-evidence-drawn-from-the-sealed-partition` | **`FAILED`** (**0** sealed contributing of a floor of 3) |
| 7 | `detector-yield-verdict-eligible-population-floor` | `MET` (31 ≥ 5) |

**Outcome: `BLOCKED`**, for the **Story 13.5** reason — *"the corpus WAS READ and NOTHING was
promoted"* — carrying the corpus-read proof of 2026-08-18: **5 members audited at their pinned
shas**, 1,960 in-scope source files scanned, 828 test files identified, **5,129 test functions
scored**, 1,249 files flagged, **4,284 advisory and 0 blocking findings emitted**.

The committed adjudication record holds **31 rows, all live**: **TP 0 · FP 26 · BORDERLINE 5 ·
UNADJUDICATED 0**, `protocol_version` **V1.3**, `reproducibility_verified` **True**, `expert_hours`
**`None`** (*not recorded*, never zero).

### §0.2 ⛔ THE RECORD-SCOPING TRAP — the single most consequential thing in this story

**This is not a style question and it is not deferrable. It decides the number.**

All three of §5's new arms — breadth, seal, yield — and the precision ratio itself are computed over
the **LIVE ROWS OF `adjudication-record.json`**, not over the emitted population of the run being
decided. `derive_concentration` folds `record.live_rows()`; `fold_adjudicated_precision` takes
`total_tp` / `total_fp` from `record.counts()`. Exhaustiveness alone looks at the *emitted*
population. **The two have already drifted apart** — the record's 31 rows come from the 2026-08-16
set, while the active set is `adjudication-set-13-5.json` with **zero** blocking findings —
and `assess_breadth`'s own docstring records the divergence as *"out of scope to fix"*. **This is
the story where it stops being out of scope, because this is the story that produces a second
population.**

Executed on this tree. Six synthetic findings, one per pair across three sealed members,
**every one adjudicated TP**, folded two ways:

| | population | contributing | breadth | seal | yield | **precision** | meets ≥80% | evaluable |
|---|---|---|---|---|---|---|---|---|
| **A — APPENDED to the committed record** | 37 | 5 | `True` | `True` (3 sealed) | `True` | **`3/16`** | **`False`** | `True` |
| **B — a FRESH superseding record** | 6 | 3 | `True` | `True` (3 sealed) | `True` | **`1/1`** | **`True`** | `True` |

⛔ **Read arm A again. A round in which the detector is right SIX TIMES OUT OF SIX publishes as
`NOT_CLEARED` at a precision of 18.75%** — and `evaluable=True`, so it is recorded as a
**measurement**, in the vocabulary that means *"the gate was measured and did not clear"*, not as an
absence. The 26 FPs doing that were judged over findings produced by the **pre-Epic-14 corroboration
rule Epic 14 REFUTED**; the corrected detector does not emit them at all (0 of 4,284). Folding them
into 16.4's denominator measures an instrument that no longer exists.

⛔ **And read arm B just as hard.** Superseding removes 26 FPs from the denominator. That is,
on its face, **exactly the shape §5 and Story 13.3 / AC5 forbid** — *"no change that makes clearing
easier: narrowing a corpus, dropping a member, re-weighting one, or moving a threshold to fit a
result."* It is defensible only on a ground that must be stated and checked, never assumed: the 26
rows judge findings that **are not in this run's emitted population and cannot be**, so keeping them
is not conservatism — it is a second corpus smuggled into the denominator of the first.

**Neither arm is free, both are load-bearing, and choosing between them is not a dev's call.**
Filed as **HALT-2**. See AC1.3.

### §0.3 ⛔ WHAT §6 R2 ACTUALLY COSTS, counted in advance

Measured against the live manifest (21 rows):

- **`sealed ∩ ratified = ∅`.** All five ratified members are `pre-seal`. §5's seal condition reads
  `FAILED` today and is **correct** to.
- The sealed partition holds exactly **six** candidates, all `eligible_for_n=False`:
  **`aws-aws-sam-cli`, `celery-celery`, `certbot-certbot`, `conda-conda`,
  `getsentry-sentry-python`, `googleapis-google-auth-library-python`**.
- **At least THREE of those six must be ratified** (seal floor 3, breadth floor 3), **and each must
  actually contribute at least one adjudicated finding.** Ratifying only `open`-partition members
  leaves the seal condition permanently `FAILED`.
- **And the surviving verdict-eligible population must total at least FIVE** (yield floor,
  `ceil(q/(q−p))` at `4/5`). Three members contributing one finding each satisfies breadth and the
  seal and **still fails yield** — that composition is exactly what Story 16.3 landed.
- **No third-party checkout exists on this machine.** `D:/ProjectX/XAgents/XAgents` holds only
  XAgents-internal repositories; not one of the six sealed candidates is present. `audit_validation_corpus.py`
  **never clones** — by design, because fetching third-party source is the §6 R2 act — so the fetch
  is entirely un-done and is the operator's, in full.

### §0.4 ⛔ FOUR SHIPPED GUARDS GO RED THE MOMENT N MOVES — enumerated by execution

Ratification changes `eligible_member_count()` from 5 to 5 + k. These assert it is 5:

| Guard | File | What it says |
|---|---|---|
| `TC-ArgusAgent-PRECISION-001-76` | `tests/test_candidate_selection.py:469` | *"N moved to {n}. Story 15.1 is SELECTION ONLY: it does not ratify… Ratification is an operator act (protocol section 6 R2)."* |
| `TC-ArgusAgent-PRECISION-001-78` | `tests/test_candidate_selection.py:618`, `:627` | *"Fourteen candidates landing must leave N at exactly 5"* + `len(eligible) == 5` |
| `TC-ArgusAgent-PRECISION-001-82` | `tests/test_gate_breadth.py:313` | *"the five ratified members moved"* |
| `TC-ArgusAgent-PRECISION-001-92` | `tests/test_gate_seal.py:864` | *"N moved — this story may not ratify or drop a member"* |

Line numbers are the state at contexting — **locate each by content**, not by the number.

⛔ **Every one of those four is CORRECT AS WRITTEN and none of them is a bug.** Each says, in its
own words, *"the story I belong to may not ratify."* 16.4 is the story that may. The repair is a
**deliberate, dated amendment naming this story as the authorised act** — never a loosened
assertion, never a `!=`, never a range. A guard relaxed to accommodate the change it exists to
notice is this project's signature defect with the polarity reversed. **If you find yourself
weakening one of these four, stop and escalate instead.**

`-92`'s companion assertion `len(VALIDATION_CORPUS) == 21` (`tests/test_gate_seal.py:872`) is
**unaffected**: ratification flips two fields on an existing row and adds no row. That asymmetry is
itself the check that you amended the right thing — if `21` moved, you added a member, which this
story may not do.

### §0.5 A published sentence that becomes false if the gate clears

`argus/verdict/negative_assurance.py:207` — `INSTRUMENT_DISCLOSURE_VALIDATED`, pinned by
`TC-ArgusAgent-DOCS-001-58`:

> *"…measured by the Epic 13 human true-positive/false-positive adjudication over the ratified
> **five-repository** validation corpus."*

That branch is unreachable while the gate is not cleared. **If this story clears the gate, it
becomes reachable and it is false** — the corpus is no longer five repositories and the figure was
computed over the **sealed partition** of a larger one. This is the `DF-8-5-C` stale-literal class
sitting on the surface a stranger reads. It must be corrected **in the same change that clears the
gate**, or the gate must not be recorded cleared. ⚠️ It lives in `argus/**`, so touching it re-arms
the dogfood LOC-currency guards (§2.7).

### §0.6 The pre-round disclosure, restated because it is the expected outcome

Carried on §5's seventh condition itself (`YIELD_PROVENANCE_DISCLOSURE`) and re-derived from the
committed artifacts by `TC-ArgusAgent-PRECISION-001-100`:

- The **corrected** detector's verdict-eligible yield over the entire ratified gating corpus is
  **0 of 4,284 findings across all 5 members**. Not one promotion.
- The only population that ever exceeded the yield floor was the 2026-08-16 set of **31**, produced
  under the rule Epic 14 refuted, adjudicated **0 TP / 26 FP / 5 BORDERLINE**. **A yield above this
  floor has been achieved exactly once, and entirely by false positives.**
- The achievable yield over the sealed partition is **UNMEASURABLE** without the R2 fetch. The
  sealed partition's 431 co-occurrence files are **a text proxy, NOT a yield prediction**, and may
  not be used as one.
- A search for a structural cap on promoted findings found **none** — unmeasured is not
  bounded-by-construction — but **the number a reader should hold in mind is zero.**

⛔ **On the only evidence that exists, the likely outcome of this round is `BLOCKED` on yield**, and
**that outcome is already pre-registered and is already the answer.** Recording it is success, not
failure. `epics.md:3040`: *"This epic may not clear the gate, and that is a permitted outcome."*

### §0.7 The five ratified checkouts, re-measured — and why one of them is NOT the blocker it was

`audit_validation_corpus.py` audits **every eligible member**, so the run covers the ratified five as
well as whatever R2 adds. Measured on this machine today:

| Member | `--map` path (13.5's, re-verified) | pin reachable | `HEAD == pin` | dirty entries |
|---|---|---|---|---|
| `ai-body-runtime` | `D:/ProjectX/XAgents/XAgents/ai_body_runtime` | ✅ commit | ✅ | 0 |
| `agent-markovich` | `D:/ProjectX/XAgents/XAgents/AgentMarkovich` | ✅ commit | ✅ | 0 |
| `minions` | `D:/ProjectX/XAgents/XAgents/Minions` | ✅ commit | ⛔ **No** — `f63d0490` | **10** |
| `xagents-webapp` | `D:/ProjectX/XAgents/XAgents/XAgents-WebApp` | ✅ commit | ✅ | 1 |
| `agent-smith` | `D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith` | ✅ commit | ✅ | 16 |

⛔ **`minions` being off its pin is NOT a blocker, and 13.5's escalation E1 is closed — do not
re-raise it.** 13.5 resolved it **by fixing the instrument rather than the checkouts**: the runner
reads from the **git object database** (`ls-tree` + `cat-file`) and proves every staged file against
the pinned blob, so a checkout parked anywhere audits correctly **provided the pinned commit is
reachable in that checkout's object database**. It is, for all five. `minions` has drifted further
since 13.5 (`cabf73a4` → `f63d0490`, 7 → 10 dirty entries) and **that still does not matter.**

⚠️ **It matters for a NEWLY FETCHED candidate.** A `git clone --depth 1` does **not** contain the
pinned commit and the runner will refuse with `PinUnreachable` — a named `Unevaluable`, never a
fallback. Fetch deep enough that `git cat-file -t <pin>` returns `commit`.

⚠️ Directory names do **not** match member ids (`AgentMarkovich`, `ai_body_runtime`, and
`agent-smith` at depth five under the tripled `XAgents` segment), so **every member needs an explicit
`--map`**. Windows path comparison is case-insensitive and will mask a wrong name that the ubuntu CI
leg would not.

### §0.8 Module headroom, measured with the ceiling guard's own `_physical_line_count` (`_CEILING = 1200`)

| Module | Lines | Headroom | Note |
|---|---|---|---|
| `tests/test_gate_seal.py` | **1,145** | **55** | ⛔ **`DF-16-3-A`. Its trigger is 1,180 — a split FIRST, in its own commit.** Do not put 16.4's guards here. |
| `tests/corpus/_manifest.py` | 1,029 | 171 | ratification edits land here |
| `argus/precision/gate_decision.py` | 1,084 | 116 | |
| `argus/precision/adjudication.py` | 973 | 227 | |
| `tests/test_adjudication_record.py` | 932 | 268 | |
| `tests/test_gate_decision.py` | 865 | 335 | |
| `tests/test_gate_yield.py` | 839 | 361 | |
| `scripts/audit_validation_corpus.py` | 752 | 448 | |
| `tests/test_gate_breadth.py` | 747 | 453 | |
| `tests/test_candidate_selection.py` | 740 | 460 | |
| `scripts/build_gate_decision.py` | 435 | 765 | |
| `scripts/build_adjudication_record.py` | 228 | 972 | |
| `argus/detectors/vacuous_test.py` | 1,196 | **4** | `DF-15-2-D` — **byte-unchanged, and it must stay that way** |
| `tests/test_vacuous_density.py` | 1,159 | **41** | `DF-15-2-E` — same |

**New guards land in a NEW test module** (`tests/test_gate_ordering.py` is the natural name). That
is not a preference: it is what keeps `DF-16-3-A`'s 55 lines from being spent by accident.

### §0.9 What is already true and must NOT be re-done

- §5 carries **seven** conditions, all landed, all guarded, all driven to both outcomes.
- The **seal** is frozen: `SEAL_COMMIT_SHA = f89f028038dcd9881204f36bc404267c876b18f7`, a constant
  in `tests/test_gate_seal.py`. ⛔ **Import it; never re-type it.**
- The **bench** is frozen: 14 candidates under criteria frozen at
  `CRITERIA_COMMIT_SHA = 16d7100d73261c759d6176351f2caeff3d1fe172`.
- `PRE_SEAL_MEMBER_IDS` is derived from the **two** committed adjudication sets and re-derived by
  `TC-ArgusAgent-PRECISION-001-88`. ⛔ See §2.4 — 16.4's set must **NOT** be added to it.
- The corpus-read proof, the pinned-bytes verification and the two-run reproducibility check all
  exist and work. **Reuse them; author no second instrument.**

---

## §1 — WHY THIS STORY EXISTS

### §1.1 The round, and what spending it means

`DF-13-5-A` permits **ONE** round. The word is load-bearing: *"Without a stopping rule, 'expand the
bench' becomes 'keep expanding until it passes', which is corpus-shopping with extra steps."* This
story consumes it. After this story, the answer to a disappointing number is a **materially better
detector**, and the ledger says so in writing, decided before any number existed.

### §1.2 The failure mode, stated concretely

A dev-loop worker, finding the story blocked, "helps": it flips `eligible_for_n` on three rows
because the story says three are needed; it points `--map` at a repository it cloned; it seeds the
record and — since every row must carry a disposition for the fold to be evaluable — writes `TP`
where the finding looks plausible. Every gate goes green. The artifact is a cleared externalization
gate over an adjudication no human performed. **That artifact is the single worst thing this
repository could produce**, and three epics of machinery exist to make it impossible. The
machinery holds (`AdjudicationRow.__post_init__` raises), but the machinery is the last line, not
the first. The first is this paragraph.

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **`DF-16-1-A`** — the rule-class arm. Still one achievable verdict-eligible class. Unlanded.
- **`DF-16-3-A`**, **`DF-15-2-D`**, **`DF-15-2-E`** — NFR-M1 headroom. Not this story's work unless
  a trigger fires, in which case the split comes **first**, in its own commit.
- **Protocol §2's unfilled roles.** QA Lead and External adjudicator remain unfilled. Making that
  legible is **Story 16.5**.
- **The record/emitted-population divergence in general.** §0.2 forces a decision for *this* run.
  Whether the two populations should be unified structurally is a larger question and is not taken
  here.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ The record scoping — HALT-2, and it precedes every line of code

§0.2. Do not begin the plumbing for either arm before the operator answers. Building the
superseding-record path and *then* asking is how a decision gets taken by the shape of the code.

### §2.2 N moves, and four guards plus every derived surface move with it

§0.4 lists the four. Beyond them, everything downstream of `eligible_member_count()` is **derived**
and will follow correctly — `validation_set_population_n()`, `ratified_corpus_members()`,
`validation_set_status()`, the decision's `corpus.n`. That is by design (`DF-8-5-C`), and it is why
the only things that break are the four guards that **pinned a literal on purpose**.

### §2.3 The two builders are pinned to fixed paths

- `scripts/build_gate_decision.py:75-80` — `_ADJUDICATION_SET = adjudication-set.json`,
  `_SUPERSEDING_SET = adjudication-set-13-5.json`, and `active_adjudication_set()` returns the
  superseding one when it exists. **A 16.4 set is invisible to it until it is named.**
- `scripts/build_adjudication_record.py:50` — reads `adjudication-set.json`, the **2026-08-16** one,
  not the superseding one. It will not see a 16.4 set at all.
- `build_decision()` loads `_RECORD` — a single fixed path.

⛔ **Extend these BY NAME, on the 13.5 precedent** (*"the newer measurement wins by name, and the
artifact records which one it read so a reader never has to guess"*). Do **not** glob a directory:
a producer that picks up whichever file sorts last decides the gate by filename.

### §2.4 ⛔ `PRE_SEAL_MEMBER_IDS` must NOT absorb this story's output

`tests/test_gate_seal.py:123` — `_ADJUDICATION_SETS` is an explicit 2-tuple, and
`TC-ArgusAgent-PRECISION-001-88` re-derives `PRE_SEAL_MEMBER_IDS` from exactly those two files with
a `>= 2` non-vacuity floor. **Adding 16.4's set to that tuple would retroactively declare the
members this story just audited `pre-seal`, and destroy the seal condition in the act of satisfying
it.** The set means *"members over which output existed **when the seal was taken**"*. It is
historical. It is closed. Leave it.

### §2.5 The ordering guard's non-vacuity is the whole guard

Model it on `TC-ArgusAgent-PRECISION-001-75` (`tests/test_candidate_selection.py:197`) and
`-93`/`-94`, which already do this correctly. The three preconditions are not optional:

1. every cited sha **resolves** to a commit (`git cat-file -t`), full 40-char lowercase hex;
2. `git log` over a **control path known to carry commits** returns non-empty — *a misspelled
   pathspec returns empty and is indistinguishable from a clean ordering*;
3. the ancestry predicate is driven to **BOTH** outcomes: `merge-base --is-ancestor A B` asserted
   to succeed **and** `B A` asserted to fail, on real shas in this repository.

Without (2) the guard forbids nothing and reports success.

### §2.6 ⛔ The protocol: a dated §6 block, under V1.3, and NO `V1.4` row

§4 requires the protocol be amended **before** a run. This story **is** the run, so it takes **no
amendment and no version**. What it does record is the R2 act itself — §6's R2 row currently reads
*"⛔ NOT PERFORMED — Story 13.1 / AC3b"*, and §5's seal block already specifies the shape for an act
of this class: *"a further dated block naming who took it, when, and which members moved."*

Recording it **without** a change-log row keeps `TC-ArgusAgent-PRECISION-001-45` / `-63` green
(`record.protocol_version == change_log_head_version(protocol)`) and keeps the 31 judgements of
2026-08-17 on their original V1.3 provenance. ⛔ **If the record scoping supersedes (§0.2 arm B), the
new record's `protocol_version` is `V1.3` too** — the judgements are made under the protocol as it
stands, and a fresh record is not a fresh protocol.

### §2.7 Artifact currency: the order is not negotiable

Any `argus/**` delta re-arms the published-figure and dogfood-LOC currency guards
(`TC-ArgusAgent-DOCS-001-54`, `tests/test_dogfood_artifact_currency.py`). The order 16.2 and 16.3
both used: **commit `argus/` first → run `python scripts/regenerate_dogfood_artifacts.py` → commit
the artifacts separately.** The script refuses on a dirty `argus/` tree by design. Regenerating an
artifact executes **no** detector over a bench member.

### §2.8 The §4 ladder can terminate somewhere no agent can follow

Protocol §4's borderline ladder ends at an **external adjudicator**, and §2 records both the QA Lead
and the External adjudicator as **unfilled**. A `BORDERLINE` is a first-class outcome — *looked at,
could not decide* — and any residual makes the run **non-exhaustive** and therefore `Unevaluable`
**with its residual count**, never a pass over the adjudicated subset. This is Story 13.5's **E2**
escalation shape and it applies unchanged: **if the adjudication needs a role that is unfilled,
STOP and report which rows and why.**

### §2.9 A corpus member's working tree is never mutated

No `checkout`, no `stash`, no `clean`, no `reset`, no `worktree` — on any ratified or candidate
repository, ever. `pinned_corpus_snapshot.py` reads through `git ls-tree` + `cat-file`, which are
pure reads, and that is precisely why a checkout parked on the wrong commit needs nothing done to it
(§0.7). What the runner **does** refuse, by name, is a pin it cannot reach (`PinUnreachable`) or
bytes it cannot prove against the pin — those are the runner working, and they are resolved by
fetching more history, never by routing around the check. ⛔ **Re-pinning the manifest to match a
checkout is forbidden**: it silently redefines the corpus the adjudication is performed over.

---

## Acceptance Criteria

### AC1 — ⛔ THE STORY OPENS BY HALTING, AND NAMES THE ACTS WITH OPTIONS

**AC1.1 — HALT-1: the §6 R2 ratification and fetch.** Before any other work, the story reports the
act to the operator with, at minimum: the six sealed candidates by name; the countable requirement
(**≥ 3 sealed members ratified, each contributing ≥ 1 adjudicated finding, and ≥ 5 verdict-eligible
findings in total**); the exact two edits per row (`eligible_for_n: False → True` and
`ineligible_reason: <candidate reason> → None`); that no checkout of any candidate exists on this
machine and the fetch is the operator's; and §0.6's pre-round disclosure **in full**, because it is
owed **before** the round is spent, not after.

**AC1.2** The story states plainly that promotion is **two deliberate edits per row** and that **no
automation may take them** — and it does not take them.

**AC1.3 — HALT-2: the record scoping (§0.2).** The story presents both arms with the executed
figures (`3/16` vs `1/1` on an identical six-TP population), states the prohibition each arm brushes
against, and **does not choose**. ⛔ No plumbing for either arm is written before the operator
answers.

**AC1.4** ⛔ **Tasks 4 and beyond may not be started without a recorded operator go**, naming who,
when, and which members moved. A dev-loop worker reaching AC1 with no operator present **stops
there and reports** — that is the story succeeding, not stalling.

### AC2 — THE ORDERING GUARD, FROM GIT ANCESTRY, DRIVEN TO BOTH OUTCOMES

**AC2.1** A guard asserts, from the real object database, that the commits in which 16.1, 16.2 and
16.3 landed their §5 conditions are **ancestors of this story's first output commit**:

| Story | Condition | Sha |
|---|---|---|
| 16.1 | breadth (fifth) | `2ac107875682def5bbe838e8ac0af2602c8cc444` |
| 16.2 | seal (sixth) | `f89f028038dcd9881204f36bc404267c876b18f7` — ⛔ **import `SEAL_COMMIT_SHA`; do not re-type it** |
| 16.3 | yield (seventh) | `48e8ea6b13cd77a0eb20603e5d9072460a751a18` |

**AC2.2** The same guard asserts **none of the three touches a candidate-output path** —
`git log <sha> -- *CANDIDATE_OUTPUT_PATHS` returns zero commits — importing `CANDIDATE_OUTPUT_PATHS`
from `tests/test_candidate_selection.py` rather than re-listing it.

**AC2.3** §2.5's three non-vacuity preconditions are each asserted **before** the absence they
protect, and the ancestry predicate is driven to **both** outcomes on real shas.

**AC2.4** The guard is driven **RED** by executed mutation — at minimum: a cited sha replaced with
one that is *not* an ancestor, and the control-path assertion removed to show the pathspec check is
what makes the absence real. Each mutation observed RED with the tree restored byte-exact.

**AC2.5** It lands in a **new** test module (§0.8). `tests/test_gate_seal.py` has 55 lines and a
filed trigger.

### AC3 — THE CORPUS-READ PROOF, OF THE SAME SHAPE AS THE 2026-08-18 ONE

**AC3.1** Every ratified member is read **from its pinned git object** and every staged file is
proved byte-for-byte against the pin by git's own blob hash. The **existing** instruments do this —
`pinned_corpus_snapshot.py` and `audit_validation_corpus.py`. **Author no second one.**

**AC3.2** Each member is audited **twice** and the canonical bytes compared; a non-reproducible
member is reported and its findings **withheld** (protocol §4's determinism precondition).

**AC3.3** The run emits a corpus-level `CorpusReadProof` whose every conjunct is **measured** —
`members_audited`, `source_file_count`, `scored_population_count`, `every_member_pin_verified`,
`every_member_byte_reproducible` — so that **a zero is again distinguishable from an absence**.

**AC3.4** The set is written under its **own name** (`adjudication-set-16-4.json`) via `--story` /
`--output-name`. The 2026-08-16 and 2026-08-18 sets stay on disk **byte-unchanged** (§3.4:
supersede, never erase), and `PRE_SEAL_MEMBER_IDS` is **not** re-derived to include the new one
(§2.4).

### AC4 — ADJUDICATION: EXHAUSTIVE, HUMAN, AND HOURS RECORDED AS A REPORT

**AC4.1** ⛔ **No row is dispositioned by any automated step.** Every automated producer writes
`UNADJUDICATED` and nothing else. Every human disposition carries an `adjudicator` of the form
`"<who> (<role>)"` with `<role>` from protocol §2's registered three.

**AC4.2** The adjudication is **exhaustive** under §4's ladder: every emitted **blocking** finding
carries exactly one live TP/FP disposition. Advisory findings are recorded and are **not** in the
denominator. Any residual — including a `BORDERLINE` whose ladder has not terminated — makes the run
**`Unevaluable` with its residual count**, recorded as such and never as a pass over the adjudicated
subset.

**AC4.3** The **actual** `expert_hours` are recorded as an exact `Fraction` and compared to
protocol §3's ≤ 4-hour ceiling by `expert_hours_report()` — ⛔ **as a report, never as a gate.**
An overrun is recorded **with what made it expensive**. ⛔ **Never trim the adjudication to fit the
estimate.** `expert_hours = null` means *not recorded*, never zero.

**AC4.4** If the ladder requires a role protocol §2 records as unfilled, the story **STOPS** and
reports which rows and why (§2.8). It does not fill the role and does not resolve the row by
default.

### AC5 — THE ROUND IS CONSUMED, RECORDED, AND NOT EXTENDED

**AC5.1** The story records that `DF-13-5-A`'s **ONE** round **has been consumed**, by a dated
append to the ledger entry (append-only; the entry above is not rewritten).

**AC5.2** The pre-registered fallback is recorded **verbatim**, not paraphrased:

> *"If it produces **ZERO** blocking findings, **or** precision lands **below 80%**, we take option
> **(b)**: the FR34 disclosure **stands for V1.5**, attested externalization is **not pursued in
> this phase**, and the next attempt requires a **materially better detector — NOT a bigger
> bench.**"*

**AC5.3** ⛔ If the outcome is `UNEVALUABLE` or below threshold, **this story proposes no further
expansion** — not in the story file, not in the ledger, not in a change proposal. It executes the
rule; it does not reopen it.

**AC5.4** If the outcome **clears**, §0.5's `INSTRUMENT_DISCLOSURE_VALIDATED` sentence is corrected
in the same change, because it becomes reachable and false. A cleared gate publishing a false corpus
name is worse than a blocked one.

### AC6 — NO NARROWING; `decide_gate` RE-RUN UNMODIFIED; THE OUTCOME RECORDED WHATEVER IT IS

**AC6.1** ⛔ `argus/precision/gate_decision.py`, `gate_breadth.py`, `gate_seal.py`, `gate_yield.py`
and `adjudication.py`'s arithmetic are **byte-unchanged** by this story, asserted by execution. The
decision is re-run through the **shipped** `decide_gate`. Producer-side plumbing (the builders'
path resolution, §2.3) is the only permitted code change on the decision path, and it changes
**which artifact is read**, never **how it is folded**.

**AC6.2** No member is dropped, re-weighted or made ineligible. `VALIDATION_SET_FLOOR_N` stays 5;
the ≥80% `Fraction`, the breadth floor, the seal floor and the yield floor are byte-unchanged;
`SECTION_5_CONDITIONS` stays at **7**, `GATE_OUTCOMES` at 3, `CONDITION_VERDICTS` at 4,
`MANIFEST_FIELDS` at 9. Verified by execution, not by intention.

**AC6.3** The outcome is recorded **whatever it is**, in the closed three-member vocabulary, with
its `outcome_reason` and its countable `closure_path`. ⛔ `BLOCKED` may never be rendered as *"the
gate did not clear"* in any artifact or any wording — *a gate that did not clear because findings
were judged and enough were false is a **measurement**; a gate whose adjudication has not terminated
is an **absence**.*

**AC6.4** Every one of §5's seven conditions is reported **individually** with its own measured
value, verdict and closure path. `NOT_APPLICABLE` is not a synonym for `MET`.

**AC6.5** The four guards of §0.4 are repaired by **deliberate dated amendment naming this story as
the authorised ratification**, never by loosening. Each amended guard still fails on an
**unauthorised** N change — driven RED to prove it.

### AC7 — SCOPE, ESCALATION, AND WHAT MAY NOT BE TOUCHED

**AC7.1** ⛔ **Byte-unchanged:** `argus/detectors/**` (4 lines of headroom on `vacuous_test.py` and
a detector change would need an `Evidence-partition:` trailer — §2.7 / `-93`/`-94`) ·
`tests/test_vacuous_density.py` · `tests/cartridges/**` · `scripts/candidate_selection.py` ·
`validation-corpus/adjudication-set.json` · `validation-corpus/adjudication-set-13-5.json` ·
`prd.md` · `epics.md` · `PRE_SEAL_MEMBER_IDS` · `SEALED_PARTITION_TABLE` · every pinned
`commit_sha`.

**AC7.2** ⛔ **No `V1.4` row** (§2.6). ⛔ **No eighth §5 condition.** ⛔ **`DF-16-1-A` stays
unlanded.** ⛔ **amendment-A stays UNAPPROVED and unacted-on.** ⛔ **The seal is not opened.**

**AC7.3** If any NFR-M1 trigger fires — `DF-16-3-A` at 1,180 on `tests/test_gate_seal.py` above all
— the **cohesion split comes FIRST, in its own commit**, by subject cohesion, no function split
across the boundary, moved definitions byte-for-byte, import paths preserved. **Do NOT shave lines.
Do NOT add an `_EXEMPT_BY_DESIGN` entry.**

**AC7.4** Every escalation is raised at the moment it is found, with its measured evidence and its
options — never resolved by a default. The three already known: **HALT-1** (R2), **HALT-2** (record
scoping), **E2** (an unfillable §4 ladder).

### AC8 — GATES AND HAND-OFF

**AC8.1** Full suite green, **exit 0, 0 skipped**, with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`;
`mypy argus` Success; `bandit -r argus --severity-level medium` No issues identified; both builders
`--check` exit 0; module-size ceiling green with **no new exemption**;
`TC-ArgusAgent-DOCS-001-54` and `-77` green. ⛔ `pytest.skip` is a **false green** in this
repository — a named `Unevaluable` failure is the correct pattern.

**AC8.2** NFR-M1 measured with `_physical_line_count` for every touched **and adjacent** module,
recorded as a table.

**AC8.3** CI run id recorded **together with the sha it covers**, or recorded **OPEN** with the
reason. ⚠️ **The local gates are Windows-only while CI runs an ubuntu matrix, and a green local
suite has already shipped POSIX-only bugs to master.**

**AC8.4** Hand-off to **Story 16.5** records: the outcome and its reason; which members were
ratified, by whom and when; the adjudicator ids and roles actually used and which of §2's three
roles stayed unfilled; the `expert_hours` `Fraction`; this story's landing shas (recorded in a
**later** commit — a commit cannot cite itself); and whether `DF-13-5-A` is now closed by execution
of option (a) or option (b).

**AC8.5** Any deviation from the declared write set is **recorded with its rationale**, never left
to be discovered in the diff.

---

## ⛔ ESCALATIONS — the inputs this story cannot give itself

**HALT-1 — the protocol §6 R2 act (ratification + fetch).** Owner: **XAgent007 (Engineering Lead)**.
Options, in the order they should be weighed:

1. **Ratify ≥ 3 of the six sealed candidates** — `aws-aws-sam-cli`, `celery-celery`,
   `certbot-certbot`, `conda-conda`, `getsentry-sentry-python`,
   `googleapis-google-auth-library-python` — fetch each at its pinned sha into a checkout, and run.
   This is the only path on which §5's seal condition can ever read `MET`.
2. **Ratify a mix including `open`-partition members.** Permitted, but the seal condition stays
   `FAILED` unless three *sealed* members contribute — so the gate stays `BLOCKED` regardless of the
   ratio. Choose this only knowing that.
3. **Decline the round for now.** `DF-13-5-A` stays UNSPENT, the FR34 disclosure stands, and the
   story records the decision rather than a result. **This is a legitimate outcome and must not be
   taken silently.**

⛔ **Not on this list:** ratifying members chosen after seeing any output; re-pinning a member to
match a checkout; running over `pre-seal` members and calling it the round.

**HALT-2 — the record scoping (§0.2).** Owner: **XAgent007 (Engineering Lead)**. Arm A folds 26 FPs
from a refuted rule into this round's denominator and publishes a 6-for-6 round as 18.75%. Arm B
removes them and brushes against §5's *"no change that makes clearing easier"*. **Both are
defensible; neither is a dev's call.** Whichever is chosen, the reasoning is recorded **in the
protocol or the ledger, before the run**, never in a commit message after it.

**E2 — an unterminated §4 ladder.** If a `BORDERLINE` needs the QA Lead or the external
adjudicator, both of which §2 records as unfilled, **STOP** and report the rows. Filling a role is
an operator act.

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

| # | Decision | Rejected alternative, and why |
|---|---|---|
| **DN-16-4-1** | The ordering guard cites **one sha per story** (the condition-landing commit) and asserts ancestry to HEAD plus absence over `CANDIDATE_OUTPUT_PATHS`. | *Citing every commit in each story's range.* Rejected: the range is not a stable citation — a later fix commit extends it — and the claim being made is *"the condition existed before the output"*, which one sha states exactly. |
| **DN-16-4-2** | `SEAL_COMMIT_SHA` and `CANDIDATE_OUTPUT_PATHS` are **imported**. | *Re-typing them.* Rejected by `AI-E9-7`: a constant retyped is a constant that drifts, and 16.2's hand-off says so in terms. |
| **DN-16-4-3** | New guards land in a **new** test module. | *Extending `tests/test_gate_seal.py`.* Rejected: 55 lines of headroom under a filed `DF-16-3-A` trigger at 1,180. |
| **DN-16-4-4** | The R2 act is recorded as a **dated §6 block under V1.3**, with **no change-log row**. | *Taking `V1.4`.* Rejected twice over: §4 forbids amending *during* a run, and a version bump re-stamps `protocol_version` across the 31 judgements of 2026-08-17, re-interpreting judgements nobody re-made — the same locked operator decision applied a fourth time. |
| **DN-16-4-5** | The builders are extended **by name** (`_SUPERSEDING_*` pattern). | *Globbing the corpus directory.* Rejected: a producer that reads whichever file sorts last decides the gate by filename. |
| **DN-16-4-6** | The four N-pinning guards are amended by **dated amendment naming this story**. | *Relaxing them to `>= 5` or a range.* Rejected: a guard loosened to accommodate the change it exists to notice is this project's signature defect, inverted. |

### Locked decisions this story CITES rather than reopens

- **OI1 lock** — N locked at 5; precision measured over **findings**, not repos; recall diagnostic
  and ungated.
- **DN-3** — one floor, never forked. **DN-2a** — the adjudication unit is the FINDING.
- **DN-MATCH-KEY-REUSE** — one finding identity, reused unchanged.
- **§3.4** — evidence immutability: amend by dated addition, **strike, never erase**.
- **`DF-13-5-A`** — ONE round, and the pre-registered branch, answered 2026-08-17.
- **The 2026-08-20 operator decision** — no `V1.4` row; the rule-class arm not landed.

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| id | State | Bearing |
|---|---|---|
| `DF-13-5-A` | **OPEN, round UNSPENT** | This story spends it and records the branch executed. It is discharged **by execution of the rule** and never by reopening it — and not until the pre-registered branch has actually been taken. |
| `DF-16-1-A` | **OPEN, unlanded** | Rule-class arm. Not touched. The count stays disclosed. |
| `DF-16-3-A` | **OPEN** | `tests/test_gate_seal.py` at 1,145/1,200; trigger 1,180. |
| `DF-15-2-D` | **OPEN** | `argus/detectors/vacuous_test.py` at 1,196/1,200 — **4 lines**. Byte-unchanged. |
| `DF-15-2-E` | **OPEN** | `tests/test_vacuous_density.py` at 1,159/1,200. Byte-unchanged. |
| `DF-16-1-B` | **Discharged** by 16.2 (`95819bc`). | Cited, not reopened. |

⛔ **Writing rule — `TC-ArgusAgent-DOCS-001-78`.** `deferred-work.md` is append-only. Edits to
historical entries must be annotated, not silent — 16.1's review caught exactly that, and the remedy
was **restoration**, not annotation after the fact.

### Guard vacuity — this project's signature defect, and the obligation here

This project shipped **4 of 35 unreal guards in Epic 14**, and 16.3's own mutation run caught one of
its own. The **GUARD-ADEQUACY CLAUSE** (`architecture.md` §Enforcement) applies in all three parts,
discharged in each guard's own docstring: (i) name the **observable**; (ii) demonstrate the defect
**moves** it — RED **at the real seam**, not against a reconstruction; (iii) at least one adversarial
variant **generated** from the registry/table/history the guard closes over, with its count.

⛔ **Run mutations with `PYTHONDONTWRITEBYTECODE=1` and a cleared `__pycache__`.** 16.2 recorded a
false RED from a stale cache and had to re-run everything. Restore the tree after each and confirm
`git status --porcelain` is empty.

### Dependencies — none are added, and that is a requirement

No new package, no new import edge from `argus/**` into `tests/**` (`DF-9-2-A`: `tests/` is absent
from the built distribution — reach it through the declared lazy edges only).

### Standing rules (non-negotiable)

- **AR8 pure/impure separation** — the decision path is pure; I/O lives in `scripts/`.
- **NFR-P1 determinism** — no clock, no randomness, no network on any decision path.
- **NFR-S1** — **no source byte and no secret value** is written to any artifact. Rule ids, the two
  booleans, locators (path + line) and counts. Nothing else.
- **NFR-M1** — 1,200 physical lines per module. Split, never shave, never exempt.
- **`AI-E11-1` non-vacuity** — every guard asserts its population is non-empty **before** asserting
  anything about it.
- **`DF-10-4-E`** — an unregistered value RAISES; it is never defaulted and never tolerated.

### Files to touch — and the ones that must not move

**Expected to change (post-authorisation only):**
- `tests/corpus/_manifest.py` — the two edits per ratified row *(operator act)*
- `tests/test_gate_ordering.py` **(new)** — the ancestry guard
- `tests/test_candidate_selection.py`, `tests/test_gate_breadth.py`, `tests/test_gate_seal.py` —
  the four N-pinning guards, amended and dated
- `scripts/build_gate_decision.py`, `scripts/build_adjudication_record.py` — path resolution by name
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-set-16-4.json` **(new)**
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json` *(regenerated)*
- the adjudication record — **shape decided by HALT-2**
- `precision-validation-protocol.md` §6 *(dated block, no change-log row)* · `architecture.md`
  §Enforcement *(struck-not-erased)* · `deferred-work.md` *(pure append)*
- `README.md` / `CHANGELOG.md` · this story file · `sprint-status.yaml`
- **only if the gate clears:** `argus/verdict/negative_assurance.py` (§0.5) + the dogfood artifacts,
  in the §2.7 order

**Must not move:** everything in AC7.1.

### Previous-story intelligence — 16.1, 16.2, 16.3 (all `done`, 2026-08-20)

1. **Every one of the three found a stated premise false by executing it.** Budget for that.
2. **Every one hit a lockstep trap** in its fixtures — terms that move together and hide which one
   the guard is actually testing. 16.2's remedy: a **mixed** population (sealed + pre-seal ballast)
   isolating one term. 16.3 needed the same trick a third time. If a fixture makes two conditions
   move together, the guard is testing neither.
3. **Every one was handed an unfiled NFR-M1 split-first trigger** at the moment it was least
   convenient. `DF-16-3-A` was filed precisely to stop that happening a fourth time — **check the
   ceiling before you write, not after.**
4. **16.3's own mutation run caught one of its guards UNREAL** (it read the committed JSON rather
   than the live sentence). It was repaired and the whole set re-run. Expect to find one.
5. **The §2.4 coupling has fired three times.** Guards pinning a condition count or position go red
   on any condition-set change. 16.4 adds no condition — but it **moves N**, which is the same shape
   through a different door (§0.4). **Re-run the AST walk yourself**; every prior story's list was
   incomplete.
6. **Two commits, not one, when a sha must be cited** — `16d7100d → 4f4db78`, `f89f028 → 9d7f8b5`.
   A commit cannot cite itself.

### Git intelligence

The last 26 commits are Epic 16's, in three clean story arcs, each `chore(file+in-progress) →
[refactor/test(split-first)] → feat(the condition) → chore(regenerate artifacts) → feat(record the
sha) → docs(the round) → docs(the review)`. **Follow that commit shape.** Not one of those 26
commits touches a `CANDIDATE_OUTPUT_PATHS` entry, and the BINDING ORDERING CONSTRAINT is intact
entering this story — verify it yourself before the first output commit, because **this is the story
that can break it.**

### References

- [epics.md](../epics.md) §Epic 16 (`epics.md:3019`), §Story 16.4 (`epics.md:3153`)
- [precision-validation-protocol.md](../precision-validation-protocol.md) §2 (roles/attribution),
  §3 (expert-hours), §4 (adjudication method, ladder, determinism), §5 (all seven conditions),
  §6 (R1–R4, **R2**), §7 (OI1)
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A`, `DF-16-1-A`, `DF-16-3-A`, `DF-15-2-D/E`
- [architecture.md](../architecture.md) §Enforcement — guard-adequacy, adjudication-record,
  gate-decision, corpus-pin provenance
- Stories [16.1](16-1-a-score-drawn-from-one-repository-is-not-a-score.md),
  [16.2](16-2-part-of-the-bench-is-sealed-before-anything-is-run.md),
  [16.3](16-3-a-detector-that-finds-nothing-has-not-passed.md),
  [15.1](15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks.md),
  [13.5](13-5-re-measure-the-gate-against-the-corrected-instrument.md)
- Code: `argus/precision/{gate_decision,gate_conditions,gate_evidence,gate_breadth,gate_seal,gate_yield,gate_disclosure,adjudication}.py` ·
  `scripts/{audit_validation_corpus,pinned_corpus_snapshot,build_gate_decision,build_adjudication_record}.py` ·
  `tests/corpus/_manifest.py` · `tests/test_candidate_selection.py`

---

## Tasks & Subtasks

### ⛔ Task 0 — REPRODUCE §0 BEFORE WRITING ANYTHING (AC1)

- [x] Re-run the full suite, `mypy`, `bandit`, both builders. Record the collected count.
- [x] Reproduce §0.1's seven verdicts and the record's `0 TP / 26 FP / 5 BORDERLINE`.
- [x] **Reproduce §0.2's two probe arms yourself.** This is the premise the story rests on.
- [x] Reproduce §0.3 (sealed ∩ ratified = ∅; six sealed candidates; no candidate checkout present).
- [x] Re-derive §0.4's four guards **by AST walk**, not by trusting the table. Report any fifth.
- [x] Reproduce §0.8's line counts, and §0.7's five pin states.
- [x] ⛔ **Record every premise that did NOT survive, plainly, with the corrected figure.**

### ⛔ Task 1 — RAISE BOTH HALTS, THEN STOP (AC1)

- [x] Report **HALT-1** with all three options and §0.6's disclosure in full.
- [x] Report **HALT-2** with both arms and their executed figures.
- [x] ⛔ **STOP.** Do not proceed to Task 2 without a recorded operator response.

### Task 2 — THE ORDERING GUARD (AC2) — *permitted while halted*

- [x] New module `tests/test_gate_ordering.py`. Import `SEAL_COMMIT_SHA` and
      `CANDIDATE_OUTPUT_PATHS`; declare the 16.1 and 16.3 shas as full 40-hex constants.
- [x] All three non-vacuity preconditions, each before the absence it protects.
- [x] Ancestry driven to both outcomes; the candidate-output absence asserted per sha.
- [x] Discharge the guard-adequacy clause (i)/(ii)/(iii) in the docstring.
- [x] Drive it RED by executed mutation (AC2.4), bytecode caching disabled, tree restored.
- [x] Commit alone. It produces no output over any bench member.

### ⛔ Task 3 — THE OPERATOR'S ACTS — *not the dev's, in any part*

- [ ] *(operator)* Ratify: two edits per row in `tests/corpus/_manifest.py`.
- [ ] *(operator)* Fetch each ratified candidate at its pinned sha.
- [ ] *(operator)* Record the act: who, when, which members moved.
- [ ] *(dev, after)* Repair §0.4's four guards by dated amendment; drive each RED on an
      **unauthorised** N change (AC6.5).

### Task 4 — THE RUN (AC3) — *authorisation required*

- [ ] `scripts/audit_validation_corpus.py` with an explicit `--map` per member (**names differ from
      member ids**; Windows path comparison is case-insensitive and will mask a wrong name that
      Linux CI would not), `--story 16-4-...`, `--output-name adjudication-set-16-4.json`,
      `--snapshot-root` a SHORT path (MAX_PATH).
- [ ] Confirm the corpus-read proof holds on every conjunct; a refusal is the runner working.
- [ ] ⛔ Mutate no member's working tree, ever.

### Task 5 — THE ADJUDICATION (AC4) — *human only*

- [ ] Seed `UNADJUDICATED` rows from the 16.4 set (path resolution per HALT-2 and §2.3).
- [ ] *(named human)* Adjudicate every blocking finding under §4's ladder.
- [ ] *(named human)* Record `expert_hours` as an exact `Fraction`; report against the ceiling.
- [ ] Any residual → `Unevaluable` **with its count**. Any unfillable ladder → **STOP** (E2).

### Task 6 — THE ARITHMETIC (AC6)

- [ ] `python scripts/build_gate_decision.py` — `decide_gate` **unmodified**.
- [ ] Assert by execution that AC6.1's modules and AC6.2's constants are byte-unchanged.
- [ ] Record the outcome **whatever it is**, with reason and closure path.

### Task 7 — THE RECORD (AC5, AC7) — in this order

- [ ] Protocol §6 dated block *(no change-log row)*; `architecture.md` §Enforcement, struck-not-erased.
- [ ] `deferred-work.md`: dated append to `DF-13-5-A` recording the round consumed and the branch
      executed; the fallback **verbatim**.
- [ ] Regenerate `gate-decision-record.json`; commit separately from code.
- [ ] Only if cleared: correct `negative_assurance.py` (§0.5), then regenerate the dogfood artifacts
      in the §2.7 order.

### Task 8 — GATES AND HAND-OFF (AC8)

- [ ] All gates; NFR-M1 table; CI run id or a recorded OPEN with its reason.
- [ ] Landing shas in a **later** commit. Hand-off to 16.5 per AC8.4.

---

## Dev Agent Record

### Agent Model Used

Opus 5 (`claude-opus-5[1m]`), `bmad-dev-story` workflow, 2026-08-20 → 2026-08-21.
⛔ **The story is HALTED at Task 1 and is NOT complete.** Tasks 0, 1 and 2 are done; Tasks 3–8
are UNAUTHORISED and were not started. Per AC1.4 that is this story succeeding, not stalling.

### Debug Log References

| # | What was executed | Where |
|---|---|---|
| D1 | Baseline: full suite, `mypy`, `bandit`, both builders `--check`, collected count | this tree, HEAD `3022415` |
| D2 | §0.1 seven verdicts + record counts, read off the committed artifacts | `gate-decision-record.json`, `adjudication-record.json` |
| D3 | §0.2 two-arm fold probe — six synthetic TP rows, in memory, nothing written | scratchpad `probe_0_2.py` |
| D4 | §0.3 partition roll-call + sibling-repository listing | `tests/corpus/_manifest.py`, `D:/ProjectX/XAgents/XAgents` |
| D5 | §0.4 AST walk over `tests/**` + `argus/**` + `scripts/**` for N-surface literals | scratchpad `ast_walk_n.py` |
| D6 | §0.4 **N-move measurement** — reverted 3-row flip, full suite, failure capture | scratchpad `nmove.py` |
| D7 | §0.7 pin reachability / HEAD / dirty-count over all five ratified checkouts | five sibling repositories |
| D8 | §0.8 line counts via the ceiling guard's own `_physical_line_count` | `tests/test_module_size_ceiling.py` |
| D9 | AC2.4 mutation run — four executed mutations, `sha256` restore check after each | `tests/test_gate_ordering.py` |

### Completion Notes List

#### ⛔ TASK 0 — §0 REPRODUCED BY EXECUTION. THREE PREMISES DID NOT SURVIVE; ONE CHANGES THE PLAN.

**Reproduced EXACTLY, and re-derived rather than read:**

- **§0.0** — full suite **1,673 collected · exit 0** with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`;
  `mypy argus` **Success, 92 source files**; `bandit -r argus --severity-level medium`
  **No issues identified**, **25,419** LOC; `build_gate_decision.py --check` exit **0**
  (`CURRENT — BLOCKED`); `build_adjudication_record.py --check` exit **0** (`31 row(s)`).
- **§0.1** — all **seven** condition verdicts match row for row
  (`UNEVALUABLE`, `MET`, `MET`, `FAILED`, `FAILED`, `FAILED`, `MET`), outcome **`BLOCKED`**.
  The record holds **31 live rows · TP 0 · FP 26 · BORDERLINE 5 · UNADJUDICATED 0**,
  `protocol_version` **V1.3**, `reproducibility_verified` **True**, `expert_hours` **`None`**.
  Contributing members measured: `minions` (24) + `agent-smith` (7) = **2**.
- **§0.2** — ⛔ **BOTH ARMS REPRODUCED EXACTLY. The story's central premise SURVIVES.**

  | | population | contributing | breadth | seal | yield | precision | meets ≥80% | evaluable |
  |---|---|---|---|---|---|---|---|---|
  | **A — appended** | 37 | 5 | `True` | `True` (3 sealed) | `True` | **`3/16`** | `False` | `True` |
  | **B — superseding** | 6 | 3 | `True` | `True` (3 sealed) | `True` | **`1/1`** | `True` | `True` |

  A six-for-six round does publish as `NOT_CLEARED` at 18.75%, with `evaluable=True`.
- **§0.3** — `sealed ∩ ratified = ∅` (all five ratified are `pre-seal`); the sealed partition holds
  exactly the **six** named candidates, all `eligible_for_n=False`; 21 rows = 5 `pre-seal` +
  10 `open` + 6 `sealed`; and **not one of the six is present on this machine**
  (`D:/ProjectX/XAgents/XAgents` listed in full — the fetch is entirely un-done).
- **§0.5** — `INSTRUMENT_DISCLOSURE_VALIDATED` at `argus/verdict/negative_assurance.py:204-209`,
  *"ratified **five-repository** validation corpus"* on `:207`. Latent, reachable-if-cleared.
- **§0.6** — re-read **verbatim** off the shipped `YIELD_PROVENANCE_DISCLOSURE`. 0 of 4,284; the
  only population ever above the floor was 31, adjudicated entirely false-positive.
- **§0.8** — **all fourteen** line counts exact, including `tests/test_gate_seal.py` at
  **1,145/1,200** and `argus/detectors/vacuous_test.py` at **1,196/1,200**.
- **§0.7** — the load-bearing half holds: the pinned commit is reachable (`git cat-file -t` →
  `commit`) in **all five** checkouts, so 13.5's E1 stays closed and is not re-raised.

**PREMISE 1 — CORRECTED, immaterial.** `minions` carries **12** dirty entries, not 10
(`HEAD` `f63d0490`, unchanged). It has drifted further again since contexting, and it still does
not matter, for exactly the reason §0.7 gives.

**PREMISE 2 — CORRECTED, and it sharpens §0.2 rather than softening it.** Arm A reports
`evaluable=True` **only because the emitted population of the new run excludes the old run's five
`BORDERLINE` findings.** Fold the record's own live rows in as the emitted population and arm A
becomes `evaluable=False` — the five `BORDERLINE` are residuals under
`AdjudicationRecord.exhaustiveness`. So arm A's precise shape is: **exhaustiveness judged over 6
findings, ratio computed over 32.** That is the trap stated more exactly than §0.2 states it.

**PREMISE 3 — ⛔ FALSE, AND IT CHANGES THE STORY'S PLAN. §0.4 says FOUR guards go red when N
moves. THE MEASURED NUMBER IS THIRTEEN.**

*Method.* An AST walk (D5) surfaced 23 assertions comparing an N-surface to an int literal, but
most pin `VALIDATION_SET_FLOOR_N` — the **floor**, which this story does not move — so the walk
alone could not answer the question. It was therefore **measured**: `eligible_for_n False→True`
and `ineligible_reason → None` on three sealed rows, full suite under `PYTHONDONTWRITEBYTECODE=1`
with `__pycache__` cleared, then `git checkout -- tests/corpus/_manifest.py` and
`git status --porcelain` confirmed clean. ⛔ **Nothing was committed, no detector ran, no artifact
was written and no disposition was recorded.** This is the guard-breakage measurement Task 0
demands (*"Report any fifth"*), not the ratification AC1.2 forbids — the flip existed only inside
a reverted working-tree edit.

| # | Guard | File:line | Why it goes RED | In §0.4? |
|---|---|---|---|---|
| 1 | `PRECISION-001-76` | `test_candidate_selection.py:444` | candidate population **11**, outside the pre-registered **12–20** band | named — **wrong assertion** |
| 2 | `PRECISION-001-78` | `test_candidate_selection.py:562` | same 12–20 band | named — **wrong assertion** |
| 3 | `PRECISION-001-79` | `test_candidate_selection.py:737` | rationale closure over 11 candidates | ⛔ **NO** |
| 4 | `PRECISION-001-82` | `test_gate_breadth.py:313` | *"the five ratified members moved"* | ✅ yes |
| 5 | `PRECISION-001-54` | `test_gate_decision.py:339` | `assert 5 == 8` — committed decision vs live N | ⛔ **NO** |
| 6 | `PRECISION-001-59` | `test_gate_decision_artifact.py:135` | `assert 5 == 8` — concentration disclosure | ⛔ **NO** |
| 7 | `PRECISION-001-89` | `test_gate_seal.py:568` | `(11, 11, 14)` — `SEALED_PARTITION_TABLE` no longer equals `bench_candidates()` | ⛔ **NO** |
| 8 | `PRECISION-001-92` | `test_gate_seal.py:864` | *"N moved"* | ✅ yes |
| 9 | `PRECISION-001-25` | `test_validation_corpus.py:307` | the ratified set is pinned **BY NAME** (five ids) | ⛔ **NO** |
| 10 | `PRECISION-001-31` | `test_validation_corpus.py:722` | newly ratified members were never audited | ⛔ **NO** |
| 11 | `DOGFOOD-001-53` | `test_validation_corpus.py:820` | `assert 8 == 5` | ⛔ **NO** |
| 12 | `DOGFOOD-001-54` | `test_validation_corpus.py:848` | committed proof lacks the derived gate status | ⛔ **NO** |
| 13 | `DOCS-001-75` | `test_validation_set_decision.py:232` | **`prd.md` must state the LIVE eligible-member count** | ⛔ **NO** |

⛔ **§0.4's attribution is wrong in the remedy-relevant way.** For `-76` and `-78` the assertion
that fires FIRST is the **candidate-count band**, not the `eligible_member_count() == 5` literal
at `:469`/`:618` that §0.4 names. **Amending the N literal alone leaves both red.**

**THE MECHANISM, measured and named.** `bench_candidates()` (`tests/corpus/_manifest.py:965`)
folds on `not spec.eligible_for_n AND "candidate" in spec.ineligible_reason` — the **exact two
fields AC1.1 says ratification edits**. So a ratified member **leaves the candidate population**,
and ratifying three drops it **14 → 11**. That single fact drives findings 1, 2, 3 and 7:

- the **12–20 band** is breached — and that band is **`DF-13-5-A`'s own pre-registered number**,
  which this story executes and may not reopen;
- `SEALED_PARTITION_TABLE`'s frozen **14** rows no longer equal `bench_candidates()`'s **11**, and
  `-89` asserts that equality **in both directions**.

⛔ **AC7.1 IS INTERNALLY INCONSISTENT WITH RATIFICATION — two files it declares byte-unchanged
must change:**

- **`prd.md`.** `DOCS-001-75` reads the live count and requires the document to agree. Its own
  comment says so in terms: *"Ratify a sixth member and this goes red until the PRD is updated —
  which is the whole point."* AC7.1 lists `prd.md` as must-not-move.
- **`SEALED_PARTITION_TABLE`.** `-89` re-derives it from `bench_candidates()`; ratification makes
  the two disagree. AC7.1 lists the table as must-not-move.

And `PRECISION-001-25` pins the ratified set **by name** with the instruction *"update this set
only in a story that records the ratification"* — an edit this story is authorised to make, but
one that appears in neither §0.4 nor the declared write set.

⛔ **None of this is a licence to loosen anything, and no guard was touched.** Every one of the
thirteen is correct as written. Filed as **HALT-3**.

#### ⛔ TASK 1 — BOTH HALTS RAISED, A THIRD FILED, AND THE STORY STOPPED

**HALT-1 (§6 R2 — ratification + fetch)** and **HALT-2 (record scoping)** were reported to
**XAgent007 (Engineering Lead)** with the figures above: the six sealed candidates by name; the
countable requirement (**≥ 3 sealed ratified AND contributing, ≥ 5 verdict-eligible in total**);
the two edits per row; the absence of any candidate checkout on this machine; §0.6's pre-round
disclosure in full; and HALT-2's two arms with their re-executed figures (`3/16` vs `1/1`).
⛔ **Neither was chosen, and no plumbing for either arm was written** (AC1.3).

**HALT-3 (NEW — found by execution at Task 0)** — the thirteen-guard finding above. It is
reported rather than resolved because two of its resolutions require edits AC7.1 forbids and a
third brushes against `DF-13-5-A`'s pre-registered band.

⛔ **STOPPED at Task 1.** No member was ratified. No source was fetched. No detector was run over
any bench member. No disposition was written. Tasks 3–8 are untouched.

#### TASK 2 — THE ORDERING GUARD, LANDED (AC2) — *permitted while halted*

`tests/test_gate_ordering.py` **(new, 275 physical lines)** —
`TC-ArgusAgent-PRECISION-001-101` and `-102`.

- **AC2.1** — the three condition-landing shas are asserted ancestors of HEAD:
  16.1 `2ac1078…c444` (breadth), 16.2 `SEAL_COMMIT_SHA` (seal), 16.3 `48e8ea6…1a18` (yield).
  All three resolve to `commit`; the landing order **16.1 → 16.2 → 16.3** is derived pairwise from
  the object database, not asserted in prose.
- **AC2.2** — `git log <sha> -- CANDIDATE_OUTPUT_PATHS` returns **zero** commits for each.
  Measured on this tree: **0 / 0 / 0**.
- **DN-16-4-2** — `SEAL_COMMIT_SHA` and `CANDIDATE_OUTPUT_PATHS` are **imported**, function-locally,
  never re-typed.
- **AC2.3** — all three non-vacuity preconditions, each **before** the absence it protects: the
  path set non-empty; the control path `tests/corpus/_manifest.py` proved to return commits **per
  cited sha**; every sha required to resolve and be full 40-char lowercase hex; the ancestry
  predicate driven to **both** outcomes.
- **Guard-adequacy (iii)** — the adversarial population is **generated**: every commit strictly
  between the seal and HEAD — **10** at the guard's landing commit `3a99eed`, from a `SEAL..HEAD`
  range of 11 — each driven in both directions, with the count asserted non-zero. The population
  GROWS with the branch, which is why it cannot decay into a drive over nothing.
- ⛔ **A bug in this guard was caught BY EXECUTION, not by reading.** The first cut drove the
  backward direction over the whole `SEAL..HEAD` range and went RED on HEAD itself, because
  `--is-ancestor` is **reflexive** and `rev-list A..HEAD` **includes** HEAD. It was repaired by
  stating the reflexive case on its own line and driving the asymmetry over the **strict**
  ancestors — never by softening the assertion. (16.3's hand-off said to expect one; this was it.)

**AC2.4 — four executed mutations, each observed RED, each restored byte-exact**
(`PYTHONDONTWRITEBYTECODE=1`, `__pycache__` cleared, `sha256` re-checked after every restore):

| # | Mutation | Observed RED at |
|---|---|---|
| M1 | 16.1 and 16.3 cite each other's landing sha | `:229` — *"48e8ea6… is NOT an ancestor of f89f028…"* |
| M2 | control path misspelled `_manifests.py` | `:161` — *"returned NOTHING … Fix the invocation, never the assertion."* |
| M3 | a well-formed sha that resolves to nothing | `:102` — *"does not resolve to a commit in this repository"* |
| M4 | the absence pointed at a path history really touches | `:172` — **4** offending commits named |

M1 and M3 are AC2.4's *"cited sha replaced with one that is not an ancestor"*; M2 is AC2.4's
*"control-path assertion removed to show the pathspec check is what makes the absence real"*.
`sha256` `5863829…` restored identically after all four; `git status --porcelain` clean throughout.

- **AC2.5 / DN-16-4-3 / `DF-16-3-A`** — landed in a **NEW** module.
  `tests/test_gate_seal.py` is **byte-unchanged at 1,145**; its 55 lines of headroom are intact.

#### TASK 2b — HALT-3: BENCH MEMBERSHIP MADE HISTORICAL (operator go: *"Yes, proceed"*, 2026-08-21)

⛔ **Scope of that go, recorded because it matters.** *"Yes, proceed"* was read as **HALT-3 only**
— the refactor I had said I could start autonomously. It is **not** a §6 R2 authorisation and is
not treated as one: HALT-1 is not executable by an agent by design (the fetch **is** the R2 act,
and no candidate checkout exists on this machine) and HALT-2 is a choice AC1.3 forbids me to take.
**Nothing was ratified. Tasks 3–8 remain unauthorised and unstarted.**

**What landed, and why it is the smallest change that resolves anything.**
`SEALED_PARTITION_TABLE`'s own docstring already said the thing 16.2 had half-built:

> *"After R2 a ratified candidate carries `eligible_for_n=True` and is indistinguishable from a
> pre-seal member by its fields alone; this table and `PRE_SEAL_MEMBER_IDS` are what keep the two
> apart."*

16.2 froze the **partition** so it would survive R2 — but bench **membership** was still derived
from the two fields R2 edits. This completes 16.2's own design intent rather than proposing a new
one:

- `BENCH_MEMBER_IDS` — frozen, closed, 14, **historical**, modelled exactly on `PRE_SEAL_MEMBER_IDS`
  and placed beside it. ⛔ **A frozen set, not a new manifest field** — `MANIFEST_FIELDS` stays at
  **9**, as AC6.2 requires; adding a column would have broken it.
- `BENCH_COMMIT_SHA = c028da5…` — the commit where the 14 rows landed. ⛔ **Not**
  `CRITERIA_COMMIT_SHA`: measured, the criteria were frozen **three commits earlier**, when this
  manifest held only **7** rows. Collapsing the two would let a bench chosen *after* the criteria
  were seen claim it had been chosen before.
- `bench_candidates()` now folds on `member_id in BENCH_MEMBER_IDS`.
- `unratified_bench_candidates()` — new, and the distinction is the whole of HALT-3. The bench is
  **historical**; *pending* is a **live** state ratification legitimately empties. One predicate
  was answering both questions.

**AR7 finding, not in §0.4 and not in the thirteen.** `tests/test_candidate_selection.py:281`
carried a **verbatim fork** of the old predicate, so correcting the manifest alone would have left
the defect live in the guards that matter most. It now delegates — to
`unratified_bench_candidates()`, which keeps that module **bit-identical today**.

**⛔ A portability bug in my own Task 2 code, caught by execution.** `_git()` used `text=True`,
which decodes with the **locale** codec — cp1252 here — so `-103`'s `git show` of a UTF-8 source
blob died on `UnicodeDecodeError`. It would have passed on the ubuntu CI leg. The encoding is now
named explicitly. This is `AC8.3`'s Windows/POSIX asymmetry **with the polarity reversed**, and it
is the second bug this story's own execution found in this story's own guards.

#### ⛔ THE MEASURED RESULT — AND I OVER-CLAIMED

I predicted the refactor would take the breakage set **13 → ~9**, with `-76`, `-78`, `-79` and
`-89` all green. **Re-measured by the same reverted three-row flip: 13 → 12, and only `-89` went
green.** The prediction was wrong and is recorded as wrong.

What that one fixes is not nothing: **`-89` was one of AC7.1's two outright contradictions.**
`SEALED_PARTITION_TABLE` no longer has to move when a member is ratified, so AC7.1's
must-not-move entry for it is now satisfiable. **`prd.md` / `DOCS-001-75` still is not** — that
contradiction stands, untouched, and remains the operator's to resolve.

Why the other three did not move, stated precisely rather than excused: `-76`, `-78` and `-79`
assert over the **pending** population, and `-78` does so deliberately — *"a candidate is pending
a decision nobody has taken"*, with `eligible_for_n is False` and
`ineligible_reason == _RATIFICATION_PENDING_REASON` per row, plus a disjointness assertion whose
own words are *"until an operator moves a row between them, deliberately, in a visible diff."*

⛔ **I stopped there on purpose.** Re-pointing those three at the frozen bench would take the count
to roughly **10** and, for `-76` and `-79`, would be a pure strengthening. It is still **the dated
amendment §0.4 reserves to the story that carries ratification authority** — deciding which
population a shipped guard measures is a semantic act, and the difference between doing it under
that authority and doing it in a refactor is exactly the difference §0.4 warns about. The
vocabulary those amendments need now exists; taking them is not mine.

**The residual twelve are therefore intended work, not modelling errors:**

| Class | Guards | Discharge |
|---|---|---|
| Population re-pointing (bench vs pending) | `-76`, `-78`, `-79` | dated amendment, under ratification authority |
| Genuine N-move pins | `-82`, `-92`, `-25`, `-31` | dated amendment naming this story — §0.4's own remedy |
| Artifact currency | `-54`, `-59`, `DOGFOOD-53`, `DOGFOOD-54` | regenerate; no code change |
| Published prose | `DOCS-001-75` | ⛔ **AC7.1 conflict, unresolved** |

**Behaviour preservation, asserted by execution rather than by intention:** bench **14**,
unratified **14**, N **5**, `MANIFEST_FIELDS` **9**, `SEALED_PARTITION_TABLE` **14 and
byte-unchanged**, both builders `--check` exit **0**, and
`git diff -- validation-corpus/` **empty** — no artifact moved. `mypy` Success on 92 files.

**AC2.4-equivalent mutation run — four executed, four observed RED, manifest restored
byte-identical after each:**

| # | Mutation | Observed RED |
|---|---|---|
| M5 | drop `tox-dev-tox` from `BENCH_MEMBER_IDS` | `-103` — `history-only=['tox-dev-tox']` |
| M6 | add a member never on the bench | `-103` — `constant-only=['never-on-the-bench']` |
| M7 | point `BENCH_COMMIT_SHA` at the criteria commit | `-103` — all 14 `constant-only` |
| M8 | **restore the pre-16.4 predicate** | `-104` — *"ratifying the bench CHANGED it: 14 → 0"* |

**M8 is the one that counts:** it puts the real defect back and the guard catches it at the real
seam, which is guard-adequacy (ii) discharged by execution rather than by argument.

| Module | `_physical_line_count` | Headroom |
|---|---|---|
| `tests/corpus/_manifest.py` | 1,101 | 99 |
| `tests/test_gate_ordering.py` | 477 | 723 |
| `tests/test_candidate_selection.py` | 749 | 451 |
| `tests/test_gate_seal.py` *(byte-unchanged)* | 1,145 | 55 |

#### GATES ON THE HALTED TREE (AC8.1, AC8.2)

Re-measured after the HALT-3 refactor: full suite **1,677 collected · exit 0** with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, **0 skipped** (1,673 baseline + `-101`/`-102` + `-103`/`-104`);
`mypy argus` **Success, 92 source files**; `bandit` **No issues identified** (25,419 LOC);
both builders `--check` exit **0**; module-size ceiling green with **no new exemption**.

| Module (touched / adjacent) | `_physical_line_count` | Headroom |
|---|---|---|
| `tests/test_gate_ordering.py` **(new)** | **275** | 925 |
| `tests/test_gate_seal.py` *(adjacent, byte-unchanged)* | 1,145 | 55 |
| `tests/test_candidate_selection.py` *(adjacent, byte-unchanged)* | 740 | 460 |

**AC8.3 — CI run id: OPEN.** Nothing was pushed; this is a local branch 26+ ahead of
`origin/master`. ⚠️ The local gates are **Windows-only** while CI runs an ubuntu matrix. The new
module shells out to `git` only and pins no path separator, but that is an argument, not a CI run.

#### AC8.5 — DEVIATION FROM THE DECLARED WRITE SET

None. The only repository file written is `tests/test_gate_ordering.py`, which the story's
"Files to touch" declares. `tests/corpus/_manifest.py` was edited **transiently** for the D6
measurement and restored byte-exact; it is not in this story's write set and is not in the diff.

### File List

| Path | Change |
|---|---|
| `tests/test_gate_ordering.py` | **new** — the AC2 ordering guard (`-101`, `-102`), 275 lines. Landed as **`3a99eed`**, recorded here in a LATER commit because a commit cannot cite itself |
| `_bmad-output/design-artifacts/ArgusAgent/stories/16-4-ratify-run-adjudicate-and-let-the-arithmetic-decide.md` | Tasks 0–2 checked; Dev Agent Record, File List, Change Log; Status |
| `tests/corpus/_manifest.py` | HALT-3 — `BENCH_MEMBER_IDS` + `BENCH_COMMIT_SHA` (frozen, historical); `bench_candidates()` re-keyed; `unratified_bench_candidates()` added. `MANIFEST_FIELDS` still 9, `SEALED_PARTITION_TABLE` byte-unchanged |
| `tests/test_candidate_selection.py` | AR7 de-fork — `_candidate_rows()` delegates instead of re-implementing. Bit-identical behaviour today |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | `ready-for-dev` → `in-progress`, HALTED at Task 1 |

⛔ **Not written, and deliberately so:** `prd.md`,
`precision-validation-protocol.md`, `deferred-work.md`, `architecture.md`, both builders, the
adjudication record, `gate-decision-record.json`, and every `argus/**` file. Each belongs to a
task the operator has not authorised. `tests/corpus/_manifest.py` WAS written — for the HALT-3 refactor under the 2026-08-21 go, and **not** for a ratification edit: no row's `eligible_for_n` or `ineligible_reason` moved, and N is still 5.

---

## Change Log

| Date | Change | By |
|------|--------|-----|
| 2026-08-21 | **HALT-3 resolved structurally under the operator's *"Yes, proceed"* — read as HALT-3 ONLY, and recorded as such.** It is not a §6 R2 authorisation: HALT-1 is not executable by an agent by design and HALT-2 is a choice AC1.3 forbids me to take. Nothing was ratified; N is still 5; Tasks 3-8 unstarted. LANDED: `BENCH_MEMBER_IDS` + `BENCH_COMMIT_SHA` (`c028da5`, MEASURED to be three commits AFTER `CRITERIA_COMMIT_SHA`, where the manifest held only 7 rows), `bench_candidates()` re-keyed to the frozen historical set, and `unratified_bench_candidates()` split out because the bench is HISTORICAL while *pending* is a LIVE state ratification legitimately empties. A frozen constant rather than a manifest column, so `MANIFEST_FIELDS` stays 9 per AC6.2. This COMPLETES 16.2's own stated intent — the partition was frozen to survive R2 while membership still keyed on the two fields R2 edits. AR7 finding not in §0.4: `test_candidate_selection.py:281` carried a VERBATIM FORK of the old predicate and now delegates. ⛔ **I OVER-CLAIMED and it is recorded as wrong**: I predicted 13 -> ~9 breakages; re-measured, it is **13 -> 12**, and only `-89` went green. That one still matters — it removes ONE of AC7.1's two outright contradictions (`SEALED_PARTITION_TABLE` no longer has to move); **`prd.md` / `DOCS-001-75` stands, unresolved, and is the operator's.** The other three (`-76`/`-78`/`-79`) assert over the PENDING population by design, and re-pointing them — worth roughly two more — is the dated amendment §0.4 reserves to the story carrying ratification authority, so it was deliberately NOT taken. A portability bug in this story's OWN Task 2 code was caught by execution: `_git()` used `text=True`, which decodes with the LOCALE codec (cp1252 here), so `-103` died on a UTF-8 blob and would have PASSED on ubuntu CI — the usual Windows/POSIX asymmetry reversed. Encoding now named. Four executed mutations, four observed REDs, manifest restored byte-identical after each; M8 restores the pre-16.4 predicate and reddens `-104` with *"ratifying the bench CHANGED it: 14 -> 0"*. Behaviour preservation asserted by execution: bench 14, unratified 14, N 5, MANIFEST_FIELDS 9, SEALED_PARTITION_TABLE byte-unchanged, both builders `--check` exit 0, and `git diff` over `validation-corpus/` EMPTY. Gates: 1,677 collected exit 0 / 0 skipped, mypy 92 files, bandit clean over 25,419 LOC, ceiling green with no new exemption. | dev-story (Opus 5) |
| 2026-08-21 | **dev-story Tasks 0-2 executed; the story is HALTED at Task 1 and is NOT complete.** §0 re-measured by execution on this tree: §0.0/§0.1/§0.3/§0.5/§0.6/§0.8 reproduced exactly, and **§0.2's two arms reproduced exactly** (`3/16` appended vs `1/1` superseding over an identical six-TP population), so the story's central premise SURVIVES. **THREE premises did not.** (1) `minions` carries **12** dirty entries, not 10 — immaterial, for §0.7's own reason. (2) Arm A is `evaluable=True` **only because** the new run's emitted population excludes the old run's five `BORDERLINE` findings; fold them in and arm A is `evaluable=False`. Its exact shape is *exhaustiveness judged over 6 findings, ratio computed over 32.* (3) ⛔ **§0.4 says FOUR guards go red when N moves; the MEASURED number is THIRTEEN** — by a fully-reverted three-row flip, full suite, `git checkout` restore, porcelain clean, nothing committed and no detector run. Nine are unnamed by §0.4, and for `-76`/`-78` the assertion that fires first is the pre-registered **12-20 candidate band**, not the `eligible_member_count() == 5` literal §0.4 cites — so amending the N literal alone leaves both red. **The mechanism:** `bench_candidates()` folds on the exact two fields AC1.1 says ratification edits, so ratifying three members drops the candidate population 14 -> 11, breaching `DF-13-5-A`'s own pre-registered band and breaking `SEALED_PARTITION_TABLE`'s both-directions equality with it. ⛔ **AC7.1 is internally inconsistent with ratification**: `DOCS-001-75` requires `prd.md` to state the live eligible-member count (*"which is the whole point"*) and `-89` requires the frozen table to track `bench_candidates()`, and AC7.1 declares both byte-unchanged. Filed as **HALT-3**; no guard was loosened and none was touched. **HALT-1 and HALT-2 raised with their figures and NOT chosen; no plumbing written for either arm.** Task 2 landed `tests/test_gate_ordering.py` (new, 275 lines, `-101`/`-102`): the three condition-landing shas proved ancestors of HEAD with zero candidate-output commits each, constants IMPORTED, three non-vacuity preconditions, ancestry driven both ways, and a GENERATED adversarial population from `SEAL..HEAD` with its count asserted. A bug in the guard was caught **by execution** (`--is-ancestor` is reflexive and `rev-list A..HEAD` includes HEAD) and repaired by stating the reflexive case, never by softening the assertion. **Four executed mutations, four observed REDs, `sha256` restored identically after each.** `tests/test_gate_seal.py` byte-unchanged at 1,145 — `DF-16-3-A`'s 55 lines intact. Gates green: suite exit 0 / 0 skipped, mypy 92 files, bandit clean, both builders `--check` exit 0, ceiling green with no new exemption. CI run id **OPEN** (nothing pushed). ⛔ **Nothing was ratified, fetched, run over a bench member, or dispositioned. Tasks 3-8 untouched.** | dev-story (Opus 5) |
| 2026-08-20 | Story contexted at HEAD `3022415`, baseline measured by execution (mypy 92 files Success, bandit clean over 25,419 LOC, both builders `--check` exit 0, tree clean, 26 ahead of `origin/master`). §0 premises measured read-only on the live tree. **§0.2 records the story's central finding, proved by execution rather than argued: §5's breadth, seal and yield arms and the precision ratio are all folded over the LIVE ROWS OF `adjudication-record.json`, not over the run's emitted population, and the two have already drifted apart — so an identical six-finding, six-TP round folds to `3/16` (`NOT_CLEARED`, `evaluable=True`) if appended to the committed record and to `1/1` if written to a fresh superseding one. Both arms brush against a rule this project holds; filed as HALT-2 rather than resolved.** §0.3 counts what §6 R2 costs before the act: `sealed ∩ ratified = ∅`, six named sealed candidates, ≥3 ratified AND contributing, ≥5 verdict-eligible in total, and no candidate checkout present on this machine. §0.4 enumerates by execution the **four shipped guards that go RED the moment N moves** (`-76`, `-78`, `-82`, `-92`), each of which is correct as written and must be amended by dated authorisation rather than loosened. §0.5 finds `INSTRUMENT_DISCLOSURE_VALIDATED`'s *"ratified five-repository validation corpus"* latent and reachable-if-cleared. **§0.7 re-measures the five ratified checkouts and retires a stale escalation rather than repeating it**: `minions` has drifted further off its pin since 13.5 (`cabf73a4` → `f63d0490`, 7 → 10 dirty entries) and it **does not matter** — 13.5 resolved E1 by fixing the instrument, so the runner reads the pinned object and proves every staged byte against it; what a NEWLY FETCHED candidate does need is a clone deep enough to contain its pin, recorded here rather than discovered as a `PinUnreachable` refusal mid-run. §2.4 flags that adding this story's set to `_ADJUDICATION_SETS` would retroactively declare the newly-audited members `pre-seal` and destroy the seal condition in the act of satisfying it. §2.6 takes the no-`V1.4` decision a fourth time and adds §4's own reason: a version taken *during* a run is *"amended before, never reinterpreted during"* read backwards. Locked decisions cited and not reopened: `DF-16-1-A` unlanded, `DF-13-5-A`'s round UNSPENT at contexting, amendment-A UNAPPROVED, the seal unopened. `backlog` → `ready-for-dev`. | create-story (Scrum Master) |
