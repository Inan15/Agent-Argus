# Story 13.5: Re-measure the gate against the corrected instrument

Status: done

<!-- Contexted 2026-08-18 on HEAD 63a0434 (post-Epic-14, epic-14 rolled up to `done`).
     EVERY premise below was RE-DERIVED BY EXECUTION at contexting time, against the tree as it
     stands, through the SHIPPED `build_ast_index`, the SHIPPED `VacuousTestDetector`, the SHIPPED
     `decide_gate` and the ceiling guard's own `_measure_population`. `argus/` was not modified to
     produce any number in this file. FOUR premises this story was chartered on DID NOT SURVIVE
     re-measurement; all four are recorded as failures in §0.2-§0.5 rather than smoothed over.
     Cite §0 for a number — never the sprint-status comment, never the change proposal, never the
     Epic-14 retrospective, all three of which were written before or during Epic 14 and carry
     figures that have since moved. -->

## Story

As the Argus maintainer,
I want the gate re-measured once the blocking rule proves what it claims,
So that the recorded decision reflects the instrument Argus actually ships.

### What this story IS

**One re-measurement, recorded honestly, over an UNCHANGED corpus at UNCHANGED pins.** Epic 14
corrected `vacuous_test_ast` — fact (b) is now a provenance-shape predicate rather than "the test
constructs a mock", and the density scorer counts statements against an 88-name assertion
vocabulary. Story 13.3 measured the *old* detector and recorded `BLOCKED`. This story re-audits the
five ratified members at their unchanged pinned shas through the corrected detector, **APPENDS**
superseding adjudication rows, and re-runs `decide_gate`.

**The expected result is that the gate does NOT clear, and that is this story succeeding.** A
corrected detector emits **zero** verdict-eligible findings on this corpus — re-derived at contexting
time in §0.1, independently of Epic 14's own record. An empty precision denominator is
`Unevaluable` by construction (`architecture.md`, *Adjudication-record enforcement*). **Removing the
findings removed the measurement, not the shortfall.**

### What it is NOT

- **It is NOT a clearing attempt.** The ≥80% threshold, the corpus membership, `VALIDATION_SET_FLOOR_N`
  and FR34 are **byte-unchanged** by this story. A measurement that returns nothing is not a licence
  to change what is being measured.
- **It does NOT flip `protocol_cleared`.** No production call site passes `protocol_cleared=True`
  today (`argus/precision/replay_harness.py:383`, default `False`) and none is added here. The
  declared status stays `InstrumentStatus.NOT_INDEPENDENTLY_VALIDATED` and the FR34 notice **stays on
  every surface**.
- **It does NOT rewrite the 13.1-13.3 record.** Those 31 rows are the true, byte-reproducible
  measurement of the detector as it stood on 2026-08-17. §3.4 evidence immutability: a correction
  **supersedes**, it never erases.
- **It does NOT re-litigate `DF-13-5-A`'s stopping rule**, and it does not execute its branch. See
  §0.7.
- **It does NOT expand the bench.** Bench selection is Story 15.1 and an operator act
  (`precision-validation-protocol.md` §6 R2). A story chartered to *make the gate clear* is the
  corpus-shopping failure mode itself.
- **It does NOT touch `_CORROBORATION_ASSERTION_CALLEES`** (frozen at 23 names, `DN-14-2-1`), the
  RULE vocabulary, or the Story 1.6 eligibility surface.

---

## ⛔ THE ONE WAY THIS STORY'S HEADLINE NUMBER CAN BE FALSE

**A measurement over a corpus that was not read reports zero, and looks identical to a real zero.**
This story's central result is an **ABSENCE** — zero blocking findings. Every other story in this plan
asserts a presence. An absence is the one claim that a broken harness produces for free.

Three concrete, *measured* routes to a false zero on this tree, all three live right now:

1. **`minions` is NOT at its pinned sha** (§0.2). It carries 24 of the 31 findings — 77.4% of the
   entire denominator. The runner will REFUSE it (exit 2), which is the runner working; a dev who
   passes `--only` around the refusal, or who re-pins the manifest to make the refusal go away,
   produces a four-member zero that reads exactly like a five-member zero.
2. **A HEAD that matches the pin does not mean the audited bytes are the pinned bytes** (§0.3).
   `materialize_snapshot` copies **working-tree** bytes. `agent-smith` has 6 in-scope modified source
   files right now, one of them a test file.
3. **The corpus path is written one level too shallow.** `DF-14-3-F` records this happening for
   `xagents-webapp` and `DF-13-3-A` records it for `agent-smith` — twice already. Every path in §0.2
   was re-derived by sha lookup at contexting time; **re-derive them again yourself and record what
   you got**, because a path that does not resolve is a member that contributes nothing.

**AC1 exists solely to make the zero falsifiable.** Do not treat it as bookkeeping.

---

## Acceptance Criteria

### AC1 — The corpus is PROVEN READ before any zero is recorded

**Given** the central result is an absence, and an unread corpus reports the same absence
**When** the re-audit runs
**Then** each of the five ratified members carries a **positive corpus-read proof** recorded in the
adjudication set: `source_file_count > 0`, a non-empty scored-test-function population, and
`byte_reproducible_across_two_runs` genuinely computed across two runs — and the run REFUSES rather
than reports zero if any member fails to produce one.

**And** the five checkout paths are re-derived and **recorded in the story record**, each verified by
`git -C <path> cat-file -t <pinned_sha>` returning `commit` **and** `git -C <path> rev-parse HEAD`
equalling the pinned sha. Pass the **Windows** path form to `git -C` from Python; a Git-Bash `/d/...`
form fails with exit 128 (§0.2).

**And** a member whose working tree is dirty in any **in-scope source file** is refused or its dirty
files are proven not to enter the snapshot — because `materialize_snapshot` copies working-tree bytes,
not the pinned blob (§0.3). Do not `git checkout -- .` or `git clean` anyone's working tree to satisfy
this; refuse and escalate.

**Non-vacuity floor (mandatory, AC7):** the guard that asserts "zero blocking findings" must first
assert that the population it scanned is non-empty and of the expected order of magnitude. A guard
that concludes silence from `findings == ()` over an unread tree is `TC-ArgusAgent-DETECT-001-132`'s
defect, found inside this very detector's own suite eight days ago.

---

### AC2 — `DF-13-3-A`'s reachability half is confirmed already discharged, and the residual is stated, not re-worked

**Given** the epic AC says the entry is "corrected first, so the re-run measures all five members
against their true pinned trees"
**Then** the dev verifies by execution that the correction already landed (it did — the entry carries
a dated `✅ CORRECTED 2026-08-17` note, and `agent-smith`'s sha resolves at depth five), records the
re-verification, and does **not** re-file it.

**And** the entry's **residual** — the 7 `agent-smith` row reasons point at an `evidence_deviation`
header field the record's closed schema does not have — is **restated as still open** in the story
record. This story does not repair it: adding a field to a closed schema, over rows a human already
signed, is a schema change on an append-only evidence record and belongs to a story that says so.
**Do not append any disposition to `deferred-work.md` for this entry.**

---

### AC3 — The re-audit runs over the UNCHANGED corpus at UNCHANGED pins, and the superseding rows are APPENDED

**Given** §3.4 evidence immutability and the epic's append-only requirement
**When** the corrected detector's finding population is adjudicated by the named human (protocol §2,
XAgent007, Engineering Lead)
**Then** the resulting rows are **APPENDED** to `validation-corpus/adjudication-record.json` carrying
`supersedes` pointing at the row they supersede, and the **31 prior rows are BYTE-UNCHANGED**.

**And** byte-unchangedness is **verified by execution, not asserted**: the 31 original row objects are
extracted from the record before and after the append and compared as canonical bytes, and that
comparison is what the guard asserts. A diff of the file is not sufficient — it cannot distinguish a
reordering from an edit.

**And** `expert_hours` is recorded as the **actual** hours the re-adjudication took, against protocol
§3's ≤4 expert-hour ceiling. It is currently `null` — *"NOT RECORDED"*, never zero. A zero here would
claim the work took no time rather than that it has not happened.

> ⚠️ **The 5 residual `BORDERLINE` rows are all `agent-smith` rows and their §4 ladder never
> terminated.** They are what made 13.3 `BLOCKED`. Superseding a `BORDERLINE` row is a **judgement**,
> not a derivation — §4's ladder is locator re-examination → golden-key correction → external
> tie-break, and protocol §2 records the QA-Lead second and the external tie-break as **unfilled**.
> **No agent may fill those roles or terminate that ladder.** If the re-measurement requires it,
> ESCALATE (see the Escalation section) rather than dispositioning them.

---

### AC4 — `decide_gate` is RE-RUN, and the outcome is recorded in ITS vocabulary, not a new one

**Given** `decide_gate` is Story 13.3's instrument and the outcome vocabulary is a **CLOSED
THREE-MEMBER** set that RAISES on an unregistered member (`architecture.md`, *Gate-decision
enforcement*)
**Then** this story **calls** it and records what it returns. It authors no second fold, no second
arithmetic and **no fourth outcome**.

**And** the outcome is recorded as **`BLOCKED`, with protocol §5 condition
`precision-at-least-80-percent` carrying the verdict `UNEVALUABLE`** — because that is what the
instrument returns for an empty denominator, re-derived in §0.4. **`UNEVALUABLE` is a CONDITION
verdict in `CONDITION_VERDICTS`, not a gate outcome**; `GATE_OUTCOMES` has exactly
`CLEARED` / `NOT_CLEARED` / `BLOCKED` and no other member. Where the epic AC, the sprint-status
comment and `DF-13-5-A` say *"recorded as UNEVALUABLE"*, they mean this condition verdict. **Recording
it as a fourth outcome would be inventing a terminal state 13.3 deliberately closed.**

**And** the `BLOCKED` result is **never rendered, serialized, summarised or committed as "the gate did
not clear"**, in any artifact, in any wording — the architecture's *Gate-decision enforcement* rule,
verbatim. *A gate that did not clear because findings were judged and enough were false is a
MEASUREMENT; a gate whose denominator is empty is an ABSENCE.* The recorded wording must let a
stranger tell which happened.

**And** the `BLOCKED` decision records its **closure path** (`GateDecision.__post_init__` raises
without one). The stock closure text for the empty-denominator branch is *"adjudicate at least one
emitted blocking finding TP or FP"*, which is generic; the story record must additionally state that
the actual path is `DF-13-5-A`'s pre-registered rule (§0.7) and that taking it is not this story's act.

---

### AC5 — The instrument REFUSES the outcome this story is chartered to produce, and that refusal is narrowed — never removed

**⛔ THIS IS THE STORY'S CENTRAL ENGINEERING PROBLEM. It was found by execution at contexting time
(§0.5) and it is not in any planning document.**

**Given** the corrected detector emits **zero** verdict-eligible findings on all five members (§0.1)
**Then** the emitted-finding population is empty, and **both** producers refuse:

| Site | Behaviour on an empty blocking population |
|---|---|
| `scripts/build_gate_decision.py:198-203` | raises `Refused("the adjudication set holds ZERO blocking findings, so the emitted population is empty and exhaustiveness over it would pass forever (AI-E11-1)")` |
| `argus/precision/gate_decision.py:695-700` | raises `VacuousDecisionError("the emitted-finding population is EMPTY. That means the corpus could not be read, not that everything in it was judged")` |

**The second error message states the exact confusion this story must resolve.** Both floors conflate
*"the corpus could not be read"* with *"the corpus was read and nothing was promoted"*. As shipped,
**Story 13.5's expected outcome is inexpressible by the instrument that is supposed to record it.**

**Then** the vacuity floor is **NARROWED so it discriminates**, and is **not removed**:

- (a) The floor keeps refusing an empty population that carries **no corpus-read evidence** — that
  case is still `VacuousDecisionError`, unchanged, and a test proves it still fires.
- (b) The floor **admits** an empty population that carries a **positive corpus-read proof** (AC1) —
  members audited, source files scanned, test functions scored, two runs byte-identical — and
  `decide_gate` then returns `BLOCKED` with the precision condition `UNEVALUABLE`, which is the
  outcome the architecture already registers for an empty denominator.
- (c) `TC-ArgusAgent-PRECISION-001-58`'s existing assertion `pytest.raises(VacuousDecisionError)` on
  an empty expected population **stays green** for the no-evidence case, and a **new** case proves the
  with-evidence path returns `BLOCKED`/`UNEVALUABLE`. **Both directions, or the narrowing is a hole.**

**And** `architecture.md`'s *Gate-decision enforcement* registration is amended in the same change,
because its current text says `decide_gate` *"raises `VacuousDecisionError` on an empty record or an
empty emitted population"* and that will no longer be unconditionally true. Amend by **strike, never
erase** (§3.4). `TC-ArgusAgent-DOCS-001-77` asserts the registration prose is present — check its
anchor list before and after and keep every anchor it names resolvable.

> **Rejected alternative, recorded so it is not re-proposed:** add `UNEVALUABLE` as a fourth
> `GATE_OUTCOMES` member. Rejected — the three-member vocabulary is an architecture-registered rule
> with a written rationale, `BLOCKED` already means exactly "the denominator is empty, so no §5
> decision was taken", and a fourth member would give two names to one state, which is the ambiguity
> the three-member design exists to prevent.
>
> **Rejected alternative:** call `decide_gate` with a synthesised placeholder finding id so the floor
> passes. Rejected — that is fabricating a member of the emitted population, i.e. lying to the guard.

---

### AC6 — The FR34 surface is UNTOUCHED where it declares status, and CORRECTED where it is latently false

**Given** Story 11.1's guard `TC-ArgusAgent-DOCS-001-46` requires the declared status to be
`NOT_INDEPENDENTLY_VALIDATED` **iff** no production call site passes `protocol_cleared=True`
**Then** this story **must not touch** `INSTRUMENT_STATUS`, `protocol_cleared`'s call sites, or the
`NOT_INDEPENDENTLY_VALIDATED` disclosure text on any surface. An `UNEVALUABLE`/`BLOCKED` outcome does
**not** clear the gate, so `-46` must stay green and **unchanged** through this story. If `-46` goes
red, you flipped something you were not asked to flip.

**Given** the Epic-13 interim retrospective §11.3(a) records a **live latent falsehood**:
`INSTRUMENT_DISCLOSURE_VALIDATED` says the gate was *"measured by the Epic 13 human
true-positive/false-positive adjudication over the **Argus dogfood corpus**"* — the self-audit Story
13.1 **excluded from N**. The adjudication was over the five-repository validation corpus. The
sentence is reachable only in the `VALIDATED` branch, which is why nobody has ever read it in anger.
**Then** the corpus name in `INSTRUMENT_DISCLOSURE_VALIDATED` is corrected to name the corpus the
adjudication actually ran over, and **nothing else in it changes** — not the claim, not the negation,
not the two-member `InstrumentStatus` vocabulary, not the removal condition. This is the Story 11.5 /
`DF-9-2-B` correction shape applied to the branch 11.5 could not reach. **Correcting an unreachable
string does not flip the gate and must not be allowed to**: assert in the same change that
`INSTRUMENT_STATUS is InstrumentStatus.NOT_INDEPENDENTLY_VALIDATED` and that the rendered notice on
every surface is byte-unchanged.

> ⚠️ **This lands on the two tightest modules in the repository.** See AC7 and §0.6 — the split comes
> FIRST.
>
> ⚠️ **§11.3(b) is explicitly OUT OF SCOPE.** `protocol_cleared_call_sites` matching only a literal
> `True` — so `-46` goes vacuous at the exact moment the gate flips — is real and reproducible now
> (`DF-13-3-B`), but exercising it requires *taking the flip branch*, which this story must not do.
> Restate it as still open in the story record and leave it there.

---

### AC7 — Every guard that asserts a NEGATIVE carries a non-vacuity floor, proven able to fire

**Given** Epic 14 added 35 guards; a sweep covered 11 and found **2 vacuous** — `-131` short-circuited
before reaching the mechanism it cited, and `-132` concluded silence from `scored == []` / `findings
== ()`, which is also exactly what an **unparsed** file produces. Vacuous tests inside the
vacuous-test detector's own suite, in the epic built to stop exactly that. **The other 24 have never
been asked.**
**Then** every guard this story adds that asserts an absence — *no blocking findings*, *no verdict-
eligible rows*, *the 31 rows unchanged*, *the disclosure unchanged* — first asserts the **precondition
that makes the absence meaningful**, and the fixture is proven to reach the mechanism the assertion
names.

**And** each such guard has **at least one adversarial variant GENERATED** (not hand-written) that
makes it fail: inject a synthetic verdict-eligible finding and prove the zero-findings guard goes RED;
perturb one of the 31 preserved rows by one byte and prove the immutability guard goes RED; point the
corpus-read proof at an empty tree and prove the vacuity floor still refuses. `architecture.md`
§Enforcement's **GUARD-ADEQUACY CLAUSE** — *"RED at the REAL SEAM, not against a reconstruction"* —
governs, and `TC-ArgusAgent-DOCS-001-77` asserts that clause is registered.

**And** `pytest.skip` is **NOT** an acceptable outcome for an unavailable tool or an unreachable
checkout. `audit-ci.yml` sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; a skip is a **false green** on
every CI leg. The correct pattern is a named `Unevaluable` outcome recorded with its reason — the same
pattern this whole story is about.

---

### AC8 — The modules this story lands on are SPLIT BY COHESION first; no size exemption is added

**Re-measured 2026-08-18 with the ceiling guard's own `_measure_population()`, `_CEILING = 1200`, and
`MAINT-001-03` pinning 1201 as the failure:**

| Module | Lines | Headroom | On this story's blast radius because |
|---|---|---|---|
| `tests/test_built_distribution.py` | **1200** | **0** | `:1184` asserts `"Argus dogfood corpus" in text` over **both** disclosure constants — AC6 changes one of them |
| `tests/test_instrument_disclosure.py` | **1198** | **2** | holds `-46` and the FR34 surface comparison; AC6's "unchanged" assertions land here |
| `tests/test_vacuous_detector.py` | 1161 | 39 | the detector's guard home; AC1/AC7's detector-level guards would default here |
| `tests/test_gate_decision.py` | 900 | 300 | AC4/AC5's guards; **has room** |
| `tests/test_validation_corpus.py` | 859 | 341 | AC1's corpus-read guards; **has room** |
| `argus/detectors/vacuous_test.py` | 1113 | 87 | do not grow it |
| `argus/pipeline.py` | 1111 | 89 | **do not add to it** |

**Given** `DF-14-3-H`'s claim that `test_vacuous_detector.py` is *"the tightest tracked module in the
repository"* is **measurably false** — it is the third tightest of the three on this blast radius
**Then** the dev **re-measures all of the above before writing a line**, and where a case must go into
a module with insufficient headroom, **splits it by cohesion FIRST** — on the
`argus/detectors/provenance_scan.py` / `tests/test_vacuous_density.py` /
`tests/test_status_document_registry.py` precedent: a module docstring naming why the module exists,
no function split across the boundary, `__all__` and every import path unchanged, and **test ids
byte-identical** (renumbering silently invalidates citations).

**And** **NO `_EXEMPT_BY_DESIGN` entry is added.** `MAINT-001-04` audits that registry and it may only
**shrink**; `_REMEDY` forbids both shaving lines and narrowing the population by name. Narrowing a
population until it goes green is a defect this repository has named.

**And** if a change to `tests/test_built_distribution.py` is genuinely line-neutral, that is still
**not** a reason to skip the split — it is a reason to record the measurement. A module at 0 headroom
that the next story must touch is the same forced choice one story later.

---

### AC9 — Reproducibility of the story's OWN evidence: the tree it measures must exist in history

**Given** `scripts/build_gate_decision.py:259` records `commit_sha = git rev-parse HEAD` **with no
dirty-tree check**, so on a dirty tree the recorded sha names a tree that was not the one measured
**And given** `origin/master` is `47b6dbe` — **the Epic-14 base commit** — so no CI run covers any
commit in Epic 14, and Story 13.4's five-file unit plus the Epic-14 governance record are on disk but
not all in history (§0.8)
**Then** before the decision record is written, the working tree is **clean and committed**, and the
sha the record carries is a real commit describing the tree the measurement ran over.

**And** the story record states plainly that **CI evidence is NOT ESTABLISHED** for this story until
the branch is pushed and `audit-ci.yml` runs green on all three legs. Every gate in this entire run
has been local/Windows. A green local suite in this repository has already shipped POSIX-only bugs to
`master`; that is a measured fact, not a caution. **`NOT ESTABLISHED` is the honest marker and it is
mechanically recognised** — do not write a status claim without either an executed-gate citation or
that marker (`TC-ArgusAgent-DOCS-001-21`).

---

### AC10 — Ledger, hand-off and the FINAL Epic-13 retrospective

**Then** the story record states, for each of the six items the Epic-13 interim retrospective §11
could not assess, exactly what this story contributed:

| §11 item | What 13.5 hands the FINAL pass |
|---|---|
| 1. Whether the epic achieved its purpose | The measurement was **taken**, on a corrected instrument. It returned no denominator. The purpose — *measure, do not delete* — was served; the number does not exist |
| 2. The measured precision figure, and whether the disclosure is replaced or stays | **No figure**: the denominator is empty. The disclosure **STAYS**, and AC6 pins that it was not touched |
| 3. Whether the flip path behaves correctly when it fires | **(a) discharged** — `INSTRUMENT_DISCLOSURE_VALIDATED`'s corpus name corrected (AC6). **(b) NOT discharged and deliberately so** — `protocol_cleared_call_sites`' literal-`True` blindness needs the flip branch taken |
| 4. `expert_hours` against §3's ≤4 ceiling | The **re-adjudication's** actual hours, recorded (AC3). Whether 13.2's original hours are recoverable is a separate question this story does not answer |
| 5. Whether `DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A` were resolved or re-scoped | **Re-derived and restated**, not disposed. Their human half was the adjudication; a re-adjudication over an empty population does not discharge them |
| 6. The epic's own re-derived open-items list | This story's own re-derivation, computed at its close — not copied from `epic-13-open-items.md`, which predates Epic 14 |

**And** any `DF-*` entry this story rules on is written into `deferred-work.md` **append-only** with its
date and its evidence. **`TC-ArgusAgent-DOCS-001-78` cross-checks every ledger disposition a story file
claims against the ledger itself** and it went RED three times on 2026-08-17 from story prose alone —
each time a ledger id sitting on the same line as a closure verb for a disposition the ledger never
received. **NEVER append a disposition to `deferred-work.md` to green a guard.** Fix the prose.

**And** the full suite is re-run to green **after the story record is written**, not before. In this
repository **story files are TESTED ARTIFACTS** and the SM phase runs after Dev and Review with no gate
of its own — the loop defect the Epic-13 retrospective filed as `AI-E13-1`.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (this project's create-story control; thirteen-for-thirteen since Epic 11)

Everything in §0 was executed on **HEAD 63a0434** on **2026-08-18**, after Epic 14 closed. **The
instrument changed three times on 2026-08-18.** Every figure written before that is void. Nothing here
is inherited from `sprint-change-proposal-2026-08-17.md`, from the `13-5` sprint-status comment, or
from `epic-14-retro-2026-08-18.md`.

---

### §0.1 ✅ CONFIRMED, and re-derived independently: the corrected detector emits ZERO verdict-eligible findings on all five members

Two separate measurements, both through the **shipped** `build_ast_index` + `VacuousTestDetector`,
over source read from the **pinned git objects** (`git show <pin>:<path>`) rather than from any
working tree.

**(a) The 31 previously-adjudicated locators, at their unchanged pins:**

| Outcome under the corrected detector | Count |
|---|---|
| Still verdict-eligible (`vacuous_test_ast`) | **0** |
| Demoted to advisory (`vacuous_test_heuristic`) | **8** |
| No longer flagged at all | **23** |
| **Total** | **31** |

The 23 are the 14.2 density correction; the 8 are the 14.1 provenance correction. This **independently
reproduces** the Epic-14 retrospective's *"0 of 31 adjudicated locators remain verdict-eligible"* — it
was not read off that document.

**(b) The whole corpus, every in-scope source file at every pin:**

| Member | Files scanned at pin | `vacuous_test_ast` (blocking) | `vacuous_test_heuristic` (advisory) | Flagged files |
|---|---|---|---|---|
| ai-body-runtime | 15 | **0** | 0 | 0 |
| agent-markovich | 65 | **0** | 72 | 19 |
| minions | 583 | **0** | 648 | 180 |
| xagents-webapp | 862 | **0** | 17 | 5 |
| agent-smith | 435 | **0** | 295 | 65 |
| **TOTAL** | **1,960** | **0** | **1,032** | **269** |

**This is a REAL zero, not an empty-corpus zero**: 1,960 files were staged and read, 269 of them
carried at least one flag, and 1,032 advisory findings were emitted. `agent-smith`'s 295 reproduces
the retrospective's figure exactly.

⚠️ **Caveats the dev must carry, not discard:**
- This is a **detector-level** measurement. `blocking_finding_count` on a real pipeline run is
  additionally a function of promotion, deep ratio and materiality. It is a **necessary** condition
  for the zero, not the full pipeline result. **The dev must re-derive through the actual runner.**
- `minions`: 583 in-scope files at the pin, versus `source_file_count = 591` recorded by 13.1's run.
  **An 8-file delta that is NOT explained.** Reconcile it before treating any count as reproduced.
- `_ASSERTION_CALLEES` is **88** names (density numerator); `_CORROBORATION_ASSERTION_CALLEES` is a
  separate **frozen 23-name** table. **Corroboration and density read different vocabularies now** —
  do not reason about one from the other.
- `ASSERTION_DENSITY_FLOOR` is `Fraction(1, 4)`.

---

### §0.2 ⛔ REFUTED: "the pinned shas are unchanged and the checkouts are on them"

The **shas** are unchanged. **One checkout is not on its sha.** Re-derived by scanning every git
repository under `D:/ProjectX` to depth 5 (the `DF-13-3-A` depth-4 scan stopped one level short; this
one did not) and testing `cat-file -t <pin>` in each:

| Member | Checkout path (RE-DERIVED) | `cat-file -t <pin>` | `rev-parse HEAD` == pin |
|---|---|---|---|
| ai-body-runtime | `D:/ProjectX/XAgents/XAgents/ai_body_runtime` | `commit` | ✅ |
| agent-markovich | `D:/ProjectX/XAgents/XAgents/AgentMarkovich` | `commit` | ✅ |
| minions | `D:/ProjectX/XAgents/XAgents/Minions` | `commit` | ⛔ **NO — HEAD is `cabf73a4`** |
| xagents-webapp | `D:/ProjectX/XAgents/XAgents/XAgents-WebApp` | `commit` | ✅ |
| agent-smith | `D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith` | `commit` | ✅ |

**Note the directory names**: `AgentMarkovich` (no hyphen, unlike the manifest's `agent-markovich`),
`ai_body_runtime` (underscores), `Minions`/`XAgents-WebApp` (capitalised), and `agent-smith` at
**depth five** under the tripled `XAgents` segment. `scripts/audit_validation_corpus.py` resolves
`checkout = --checkout-root / member_id` **unless** `--map` overrides it, so **every one of the five
needs an explicit `--map`**. Windows path comparison is case-insensitive and will mask a wrong name
that a Linux CI leg would not.

**The `minions` drift is substantial, not cosmetic:** at the pin, 583 in-scope source files; in the
current index, **479** — **117 files present at the pin are absent from the checkout's index** and 13
are new. Auditing that checkout as it stands measures a materially different repository.

**The runner will REFUSE it** — `_run_member` compares `rev-parse HEAD` to the manifest pin and raises
`CorpusRefusal` with exit 2. **That refusal is the runner working. Do not route around it.** Getting
`minions` onto its pin is an operator act over a third-party checkout with **7 uncommitted entries in
it** (3 in scope): see the Escalation section. **Do not `git checkout`, `git stash`, `git clean` or
otherwise mutate a corpus member's working tree.**

---

### §0.3 ⛔ NEW, found by execution and recorded nowhere: HEAD == pin does NOT mean the audited bytes are the pinned bytes

`scripts/audit_validation_corpus.py` enforces the pin by comparing `git rev-parse HEAD`. It then calls
`materialize_snapshot`, which stages the snapshot with `shutil.copyfile(root / rel, ...)` —
**working-tree bytes**, `argus/dogfood/proof_run.py:317-322`. A member sitting on the right commit with
a dirty working tree is audited as its **dirty** bytes while the record says "at the pin".

Measured on this tree, in-scope source files only (`_SOURCE_SUFFIXES` minus `_EXCLUDED_TREES`):

| Member | Dirty entries (total) | Dirty **in-scope source** files |
|---|---|---|
| ai-body-runtime | 0 | 0 |
| agent-markovich | 0 | 0 |
| minions | 7 | **3** (incl. two test modules) |
| xagents-webapp | 1 | 0 |
| agent-smith | 16 | **6** (incl. `agentsmith-core/tests/test_surface_envelope.py`) |

**`agent-smith` is the member that carries the other 7 findings and all 5 residual `BORDERLINE` rows**,
and it is dirty in six in-scope source files right now — one of them a test file the vacuous-test
detector reads. A re-run today would produce a byte-reproducible result (both runs read the same dirty
bytes) over a tree that is **not** the pinned tree, and `byte_reproducible_across_two_runs` would say
`True`. **Reproducibility is not provenance.** AC1 requires this be closed by refusal or by proof, and
it is a genuine gap in the runner, not a mistake by the operator.

---

### §0.4 ⛔ REFUTED: "the outcome is `UNEVALUABLE`"

`UNEVALUABLE` is **not** a gate outcome. Read off the shipped module:

```
GATE_OUTCOMES        = CLEARED | NOT_CLEARED | BLOCKED      # closed, RAISES on any other
CONDITION_VERDICTS   = MET | FAILED | NOT_APPLICABLE | UNEVALUABLE
SECTION_5_CONDITIONS = precision-at-least-80-percent
                       clean-repo-blocking-false-positives-zero
                       corpus-floor-n-at-least-5
                       adjudication-run-recorded-cleared
PRECISION_GATE_THRESHOLD = Fraction(4, 5)
```

`decide_gate`'s empty-denominator branch (`argus/precision/gate_decision.py:792-802`) sets
`outcome = "BLOCKED"` with the reason *"the precision DENOMINATOR is empty — no finding entered TP+FP
over this population… An empty denominator is not an 80% result; it is no result."*

So the correct record is **`outcome = BLOCKED` + precision condition `UNEVALUABLE`**. The epics AC, the
sprint-status comment and `DF-13-5-A` all say *"recorded as UNEVALUABLE"* and they are all consistent
with this — `architecture.md`'s *Adjudication-record enforcement* rule uses exactly that word for the
**fold** state (*"a partial, unattributed, non-reproducible or empty record yields `Unevaluable`"*).
**No planning document is wrong; they are describing the condition verdict.** Write it that way and the
ambiguity dies here.

**Already true of the CURRENT committed decision** (`validation-corpus/gate-decision-record.json`, at
`6c59115b`): `outcome = BLOCKED`, `precision.evaluable = false`, `precision.precision = null`,
`precision_ratio = "NOT COMPUTED BY THIS RUN"`, `total_tp = 0`, `total_fp = 26`, `total_borderline = 5`.
13.3 was `BLOCKED` on **exhaustiveness** (5 residual rows). 13.5 will be `BLOCKED` on the **denominator**.
**Different reasons, same outcome member** — the story record must distinguish them explicitly, or a
reader will conclude nothing changed.

---

### §0.5 ⛔ THE BLOCKER, found by execution: the instrument REFUSES this story's expected outcome

Reproduced by reading both shipped call paths:

```
scripts/build_gate_decision.py :198  if not ids: raise Refused("the adjudication set holds ZERO
                                     blocking findings, so the emitted population is empty and
                                     exhaustiveness over it would pass forever (AI-E11-1).")

argus/precision/gate_decision.py:695 if not expected: raise VacuousDecisionError("the emitted-finding
                                     population is EMPTY. That means the corpus could not be read,
                                     not that everything in it was judged; exhaustiveness over
                                     nothing is the guard that passes forever (AI-E11-1).")
```

Both are **correct as written** for the world they were written in — 13.3 could not distinguish the two
cases and chose the safe refusal. Epic 14 created a third world: a corpus that **was** read and
promoted nothing. **This is not a defect in 13.3; it is a consequence of 14 succeeding.** AC5 governs
the narrowing. The floor is narrowed, never removed, and both directions are proven.

`architecture.md`'s *Gate-decision enforcement* registration currently asserts the unconditional form
(*"`decide_gate` raises `VacuousDecisionError` on an empty record or an empty emitted population BEFORE
asserting anything about them"*). Amending it is in scope and is an AC5 obligation.

---

### §0.6 ✅ CORRECTED premise: `tests/test_evidence_citation.py` is NOT at 1200, and `-22` does NOT block this story

**Two carried-forward premises are stale on disk, both in the favourable direction.**

1. **`tests/test_evidence_citation.py` is at 1076 lines, not 1200.** Story 13.4's cohesion split is
   **applied on disk** (uncommitted): `_STATUS_DOCUMENTS` and `TC-ArgusAgent-DOCS-001-21`/`-22` now live
   in `tests/test_status_document_registry.py` at **285** lines, with headroom for many registrations.
   The comment *"The NEXT status document cannot be registered until this module is split"* is struck in
   place in that file and is no longer true.
2. **All three previously-blocked documents ARE registered**: `sprint-change-proposal-2026-08-17.md`,
   `sprint-change-proposal-2026-08-17b.md` and `epic-14-retro-2026-08-18.md` are all in
   `_STATUS_DOCUMENTS`. `pytest tests/test_status_document_registry.py tests/test_module_size_ceiling.py`
   → **8 passed**.

**Does 13.5's output trip `-22`? Determined by execution: NO.** `-22`'s patterns are exactly
`sprint-change-proposal-*.md` and `epic-*-retro-*.md`. This story's artifacts are
`validation-corpus/adjudication-set.json`, `adjudication-record.json` and `gate-decision-record.json` —
JSON, and outside both globs. Story files are excluded from the registry **by design** (`DN-5`, an
`_EXCLUDED_BY_DESIGN` entry with a written reason), so **this story file does not trip it either**.

> ⚠️ **The two-sided closure still binds anyone who writes a `.md` here.** `-22` reds both on an
> unregistered document **and** on a registered document that is missing, so any status-asserting
> markdown 13.5 produces must land in the **same commit** as its registration line. **13.5 is not
> chartered to produce one, and should not.**
>
> ⚠️ **The FINAL Epic-13 retrospective WILL trip it** — `epic-13-retro-*.md` matches the glob. That is
> the retrospective's own step to handle and 13.4's split already made room for it.

**⛔ THE SPLIT PRECONDITION IS REAL — it just moved.** It is `tests/test_built_distribution.py`
(**1200/1200, zero headroom**) and `tests/test_instrument_disclosure.py` (**1198/1200, two lines**),
both of which AC6 lands on. See AC8's table, re-measured.

---

### §0.7 The stopping rule: cite it, do not re-litigate it, do not execute it

`DF-13-5-A` was **ANSWERED on 2026-08-17 as a PRE-REGISTERED RULE** — before Story 13.5 ran, before
Epic 15's bench was chosen, and **before any number existed**. Quoted, not paraphrased:

> If Story 13.5 returns `UNEVALUABLE`, we pursue option **(a)**: **ONE** bench-expansion round of 12-20
> independently selected repositories (Epic 15 / Story 15.1). If that round produces adjudicable
> findings and precision lands **≥80%**, the gate clears. If it produces **ZERO** blocking findings,
> **or** precision lands **below 80%**, we take option **(b)**: the FR34 disclosure **stands for V1.5**,
> attested externalization is **not pursued in this phase**, and the next attempt requires a
> **materially better detector — NOT a bigger bench.**
>
> **ONE round is the load-bearing word.** Without a stopping rule, *"expand the bench"* becomes *"keep
> expanding until it passes"*, which is corpus-shopping with extra steps.

**Three things follow and all three are binding on this story:**

1. **This story does not execute the branch.** The entry says plainly that it is discharged **by
   execution of the rule** after 13.5 records its outcome — which is a later act, by the owner. 13.5
   **records the outcome** and stops. Do not write a disposition for that entry into the ledger.
2. **This story must not read as licence to keep expanding.** Nothing in the story record may suggest a
   second round, a larger bench, or a threshold adjustment as a response to this result.
3. **A zero-finding bench round means the detector is too conservative to be a product** — named in
   advance so it cannot be re-read later. Not *"we need 40 repositories"*.

---

### §0.8 Commit state, and why it is an AC and not a footnote

- **HEAD `63a0434`**, 15 commits today, **none pushed**. `origin/master` is **`47b6dbe`** — the Epic-14
  **base** commit. **No CI run covers any commit in Epic 14.** CI evidence is **NOT ESTABLISHED** for
  every claim Epic 14 makes about itself, and this story's premises are derived from that tree.
- **Uncommitted on disk and NOT to be committed by this story's contexting**: `epic-14-retro-2026-08-18.md`,
  `sprint-change-proposal-2026-08-17.md`, `sprint-change-proposal-2026-08-17b.md`, Story 13.4's five-file
  unit (`tests/test_status_document_registry.py` + `test_evidence_citation.py`, `test_module_size_ceiling.py`,
  `test_spec_claim_scope.py`, `test_v1_commitment_closure.py`), plus `E-PRD/prd.md`, `architecture.md`,
  `epics.md`, `stories/1-5-*.md`, `stories/13-4-*.md`.
- **13.4's unit is atomic**: the four modified test modules import from the untracked registry module.
  Committing any subset reds `master`. `-22` reds in both directions, so each retro/proposal document
  must land with its registration line.
- **Out of scope entirely**: `argusdemo/`, `.bmad-drift-audit/`, `bmad-dev-loop-pack/`,
  `_bmad-output/audit-reports/*`, `stories/15-1-*.md`.

**Why AC9 and not a note:** `build_gate_decision.py` stamps `commit_sha = git rev-parse HEAD` with **no
dirty check**. Run on this tree, the decision record would name `63a0434` for a measurement taken over
a tree `63a0434` does not describe. This story's entire deliverable is a governance record; a governance
record whose provenance field is wrong is worse than none.

---

### Locked decisions this story must CITE rather than reopen

| Decision | Where it is locked | What it forbids here |
|---|---|---|
| ≥80% precision threshold, exact `Fraction(4,5)` | `precision-validation-protocol.md` §5 · Story 13.3 AC5 | Any amendment in response to this result. *A failed measurement is not a reason to amend the threshold* |
| Corpus membership: 5 ratified members, `VALIDATION_SET_FLOOR_N = 5` | `tests/corpus/_manifest.py` · Story 13.1 AC3b · protocol §6 R2 | Adding, removing or re-pinning a member. Re-pinning silently redefines the corpus the adjudication was performed over |
| FR34 disclosure REPLACED, never deleted | PRD FR34 · Story 11.1 · `TC-ArgusAgent-DOCS-001-46` | Any change to the declared status or the `NOT_INDEPENDENTLY_VALIDATED` text |
| Three-member outcome vocabulary | `architecture.md` *Gate-decision enforcement* · Story 13.3 AC1 | A fourth `GATE_OUTCOMES` member; rendering `BLOCKED` as *"the gate did not clear"* |
| Append-only evidence | protocol §3.4 · `architecture.md` *Adjudication-record enforcement* | Rewriting or reordering any of the 31 rows |
| `_CORROBORATION_ASSERTION_CALLEES` frozen at 23 | `DN-14-2-1` | Widening it. It is the moat |
| The PRD governs the validation set; cartridges are the FR20 **recall** instrument | Story 13.1 AC1 | Folding cartridge results into the precision denominator |
| `protocol_cleared` literal `False`, deliberately | `argus/precision/gate_decision.py` docstring · `DF-13-3-B` | Threading a derived flag in — it blinds `-46` |
| The pre-registered ONE-round stopping rule | `DF-13-5-A`, answered 2026-08-17 | Proposing a second round; executing the branch inside this story |
| `-46` goes RED the day the gate clears, and the fix is REPLACEMENT | `tests/test_instrument_disclosure.py:606-629` | Widening its exemptions. It must stay green **and unchanged** through this story |

### Standing engineering constraints

- **AR8 purity** — detectors and folds are pure: no I/O, no clock, no LLM, no `uuid4`/`random`.
- **AR4** — exact `Fraction`, **never** `float`, anywhere a ratio appears.
- **AR7** — one rule, one implementation. `decide_gate` and `fold_adjudicated_precision` are **called**,
  never re-derived.
- **AR10** — closed vocabularies RAISE on an unregistered member; no silent default.
- **Determinism (NFR-P1)** — every set is `sorted()` before it reaches an artifact.
- **NFR-S1** — no audited source byte is written to any artifact. Rule ids, booleans, locators (path +
  line) and counts only.
- **NFR-M1** — 1200-line ceiling; see AC8.
- **Dogfood currency** — regenerate via **AI-E12-11**: commit the `argus/` delta → run
  `scripts/regenerate_dogfood_artifacts.py` → commit the artifacts **separately**. The currency guards
  track `argus/` **LOC**, not behaviour, so a pure-comment edit in `argus/` still reds them.
- **Encoding** — every file opened `encoding="utf-8"` explicitly. The artifact tree carries non-ASCII
  and an inherited host locale is the exact defect that turned CI run `31322881580` red.

---

### Files to touch

**READ FIRST, IN FULL — these are `UPDATE`, not `NEW`:**

| Path | Lines | Current state / what changes |
|---|---|---|
| `argus/precision/gate_decision.py` | 850 | Holds `decide_gate`, `GATE_OUTCOMES`, `CONDITION_VERDICTS`, `VacuousDecisionError`. **AC5 narrows the empty-population floor.** Preserve: the three-outcome dispatch order (§4's order — determinism → exhaustiveness → ratio), every `__post_init__` invariant, the literal-`False` `protocol_cleared` |
| `scripts/build_gate_decision.py` | 318 | `expected_finding_ids()` at :167 raises on zero blocking findings. **AC5 narrows it.** Preserve: deriving the expected population from the adjudication **set**, never from the record (self-referential exhaustiveness is the defect it was written against) |
| `scripts/audit_validation_corpus.py` | 469 | The runner. **AC1 adds the corpus-read proof and the dirty-tree refusal.** Preserve: it never clones, never writes a source byte, never scores its own output, and refuses on a pin mismatch |
| `scripts/build_adjudication_record.py` | 228 | **AC3 appends superseding rows.** Preserve: only `verdict_eligible` findings enter the record |
| `argus/verdict/negative_assurance.py` | — | **AC6 corrects `INSTRUMENT_DISCLOSURE_VALIDATED`'s corpus name and NOTHING else.** Preserve: `INSTRUMENT_STATUS`, both `NOT_INDEPENDENTLY_VALIDATED` texts, the two-member vocabulary, `render_instrument_disclosure`'s exhaustiveness |
| `tests/test_gate_decision.py` | 900 | AC4/AC5 guards. **300 lines of headroom — this is where the gate guards go** |
| `tests/test_validation_corpus.py` | 859 | AC1 corpus-read guards. **341 lines of headroom** |
| `tests/test_built_distribution.py` | **1200** | ⛔ **ZERO headroom.** `:1184` pins `"Argus dogfood corpus"` over both constants. **SPLIT BY COHESION FIRST** |
| `tests/test_instrument_disclosure.py` | **1198** | ⛔ **TWO lines.** Holds `-46` + the FR34 surface comparison. **SPLIT BY COHESION FIRST** |
| `tests/test_adjudication_record.py` | 859 | AC3 append-only + byte-identity guards. Room |
| `_bmad-output/.../architecture.md` | — | **AC5** amends *Gate-decision enforcement* by **strike, never erase**. Keep every `-77` anchor resolvable |
| `_bmad-output/.../validation-corpus/*.json` | — | Regenerated artifacts. **Derived, never hand-edited** (`DF-8-5-C` / `AI-E9-7`) |
| `_bmad-output/.../deferred-work.md` | — | Append-only. Read `TC-ArgusAgent-DOCS-001-78` before writing a line |

**DO NOT TOUCH:** `argus/pipeline.py` (1111/1200) · `argus/detectors/vacuous_test.py` (1113/1200) ·
`_CORROBORATION_ASSERTION_CALLEES` · `tests/corpus/_manifest.py` membership or pins ·
`precision-validation-protocol.md` §5 literals · the four modules in 13.4's uncommitted unit.

---

### Previous story intelligence — traps already paid for; do not pay again

**From Story 13.3** (the instrument this story re-runs):
- The three-outcome vocabulary exists because a two-member one could not distinguish a measurement from
  an absence. Every shortcut you are tempted to take here re-creates that ambiguity.
- It recorded `BLOCKED` on exhaustiveness with a full closure path and did **not** fold the 26
  dispositioned rows into a confident ratio. That restraint is the model for this story.

**From Story 13.4** (the immediately preceding story, `done`, uncommitted):
- The cohesion split is the sanctioned remedy: docstring naming why the module exists, **test ids
  byte-identical**, one import edge new→old and never back (a circular import between two test modules
  fails at collection), `__all__` and import paths unchanged.
- It **rejected** moving a positive control away from the code it controls just because its id said so
  — *"a line-count decision wearing an id's clothes."* Choose the boundary by cohesion, then check the
  arithmetic; never the reverse.
- Its five files are **atomic**. Do not commit a subset.

**From Epic 14, and this is the finding most worth carrying:**
- **Two of eleven swept guards were themselves vacuous**, inside the vacuous-test detector's own suite,
  in the epic built to stop vacuity. `-131` short-circuited at `if not heuristically_vacuous: return
  False` before reaching the mechanism it cited. `-132` concluded silence from `scored == []` /
  `findings == ()` — which is also what an **unparsed** file produces. **24 of the 35 have never been
  asked.** This story asserts an absence as its central result. AC7 is not optional.
- **The dev pass found ZERO of its own substantive defects in any of the three stories.** Both
  independent re-derivation phases found nine between them. Assume your own pass is the weak one.
- The SM contexting control **refuted four premises before any code was written**, including an
  acceptance criterion that would have passed with zero code change. §0 above continues that record and
  refutes four more.
- **Figures were corrected rather than propagated**: 14.2 removed 1,581 flags, not 1,572 — the latter
  was iteration 1's number, carried forward. Do the same: if a figure in this story does not survive
  your re-measurement, **record the corrected figure plainly**.

**From Epic 13's retrospective (`AI-E13-1`), the loop defect:**
- A **story file** turned `master` red and no gate caught it. In this repository **story files are
  tested artifacts**. Re-run the full suite after writing the story record, not before.

---

### Testing requirements

- **Framework**: `pytest`. Run with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, matching `audit-ci.yml`.
- **Baseline**: **1,632 passed / 0 failed / 0 skipped, exit 0** (re-verified at contexting time on
  HEAD `63a0434`).
- **Zero skips is the standard.** `pytest.skip` is a **false green** here. An unavailable tool or an
  unreachable checkout is a named `Unevaluable` outcome recorded with its reason.
- **Test id discipline**: new ids continue the existing verification areas —
  `TC-ArgusAgent-PRECISION-001-*` for gate/record guards, `TC-ArgusAgent-DOCS-001-*` for governance
  surfaces. **Never renumber an existing id**; citations in `architecture.md`, `deferred-work.md` and
  five test modules resolve against them.
- **Every new guard**: non-vacuity floor asserted **first**, then the substantive assertion, then at
  least one **generated** adversarial variant proving it can fail at the real seam.
- **Also run**: `mypy` (clean), `bandit` (0 High / 0 Medium), coverage ≥80%, and `argus audit .`
  end-to-end.
- **CI is a separate obligation.** Local Windows green is necessary and **not sufficient**
  (`architecture.md` §H, `DF-AUD-APAA-C`). CI runs an ubuntu matrix and a green local suite in this
  repository has already shipped POSIX-only bugs to `master`.

---

## Tasks & Subtasks

- [x] **T1 — Re-derive §0 yourself before writing code (AC1, AC9)** — done; two §0 figures CORRECTED (D-1)
  - [x] Re-run the depth-5 repository scan; confirm all five pinned shas resolve; record each path — all five resolve `commit`; paths in D-1
  - [x] Re-run `rev-parse HEAD` per member; confirm the `minions` mismatch is still live — live, but at `8b7be40f`, **not** §0.2's `cabf73a4`
  - [x] Re-measure the in-scope dirty-file counts per member — `minions` is now **0** (§0.3 said 3); `agent-smith` **6**
  - [x] Re-measure all seven module line counts with `_measure_population()` — every AC8 figure confirmed exactly (D-7)
  - [x] Record every figure that differs from §0, as a correction — D-1, D-2, D-4

- [ ] ⛔ **T2 — NOT PERFORMED, by operator instruction.** Committing Story 13.4's five-file unit and the three Epic-14 governance documents was explicitly forbidden for this story; they are not this story's work to commit. AC9's clean-tree clause is therefore **NOT MET** and is recorded as such rather than worked around (N-12). This is a deliberate, directed non-execution, not an omission.
  - [ ] ⛔ Commit 13.4's five-file unit atomically — **NOT PERFORMED** (operator instruction: do not commit 13.4's unit). It stays on disk, atomic, for its owner
  - [ ] ⛔ Commit the Epic-14 governance record — **NOT PERFORMED** (same instruction). `-22`'s two-sided closure means each document must land with its registration line, which is 13.4's unit
  - [x] Confirm the working-tree state before the decision record is written — **measured and RECORDED on the artifact** as `commit_sha_provenance`, with the mechanically-recognised `NOT ESTABLISHED` marker, instead of being assumed (N-12)

- [x] **T3 — E1 RESOLVED by operator ruling: fix the instrument, not the checkouts.** The pin is now read from the git object database, so `minions` was audited at `ec63b729` from a checkout parked on `8b7be40f` **without touching it**. No `checkout`, `stash`, `clean`, `reset` or `worktree` on any member. The result is a five-of-five zero, not the four-of-five zero option 3 would have produced (D-3, D-5)

- [x] **T4 — Split the two zero/two-headroom modules by cohesion (AC8)** — done FIRST, before a line of story code (N-11)
  - [x] `tests/test_built_distribution.py` 1200 -> **954**; `tests/test_instrument_disclosure.py` 1198 -> **893** (re-measured in review iteration 1; **897** was asserted, never measured — D-9)
  - [x] Test ids byte-identical; one import edge (new -> old, never back); no function split across either boundary
  - [x] **No `_EXEMPT_BY_DESIGN` entry added.** `MAINT-001-01`..`-04` green
  - [x] Each new module opens with a docstring naming its verification area, its ids and why the module exists; `TC-ArgusAgent-DOCS-001-77`'s anchor list now names `scripts/pinned_corpus_snapshot.py` and `-65`

- [x] **T5 — Re-audit the five members at their pins, with the corpus-read proof (AC1, AC3)** — done (D-4)
  - [x] Extend `audit_validation_corpus.py`: corpus-read proof emitted per member and corpus-wide; the dirty-tree half closed by **PROOF** rather than refusal — strictly stronger, and it never mutates a third-party tree (N-3)
  - [x] Run with explicit `--map` for all five members; every path re-derived and recorded (D-1)
  - [x] `byte_reproducible_across_two_runs` **true for all five**, and — the part reproducibility alone never proved — all **1,960** staged files hash to their pinned blobs
  - [x] Recorded and reconciled: `vacuous_test_heuristic` 0/72/648/17/295 = **1,032** over **1,960** files reproduces §0.1(b) exactly; `vacuous_test_ast` **0**; §0.1's *269 flagged* is the vacuous-test population, the runner's 1,249 the all-detector one (D-4)

- [x] **T6 — Nothing to append, and that is a MEASURED outcome (AC3).** The corrected detector emitted zero verdict-eligible findings, so no finding existed to adjudicate and no superseding row could honestly be written (N-5)
  - [x] No row appended — there was no finding to adjudicate. The 31 prior rows were not touched, and `adjudication-record.json` is byte-identical to its committed state
  - [x] `TC-ArgusAgent-PRECISION-001-71` drives a **real** append at the real seam and compares the prior rows' canonical bytes keyed by `row_id`; its adversarial variant perturbs one character and is proved to go RED
  - [x] `expert_hours` stays `null` / *"NOT RECORDED"* — **not zero**. No re-adjudication took place because nothing was emitted to adjudicate; zero would claim the work took no time
  - [x] No `BORDERLINE` was terminated, superseded or re-read. Escalation **E2** was never reached; §4's ladder was not engaged and both unfilled roles stay unfilled

- [x] **T7 — Narrow the vacuity floor and re-run `decide_gate` (AC4, AC5)** — done; both directions guarded (N-7)
  - [x] Both sites narrowed (`gate_decision.py` and `build_gate_decision.py`), plus a third correction of the same shape in the fold's `unevaluable_reason`
  - [x] No-evidence direction still raises; `TC-ArgusAgent-PRECISION-001-58` green **and unchanged**, and `-69` re-proves it at the new seam
  - [x] With-evidence direction returns `BLOCKED` + precision `UNEVALUABLE`; the vocabulary is still exactly three members
  - [x] Amended by **strike**, never erased; `-77`'s anchor list extended to cover the strike and the new *Corpus-pin provenance enforcement* rule; every pre-existing anchor still resolves
  - [x] Decision record written; the closure path names `DF-13-5-A`'s pre-registered rule and states that executing it is the owner's act, not this story's

- [x] **T8 — Correct the latently-false cleared text (AC6)** — done (N-8)
  - [x] Corpus name corrected to the ratified five-repository validation corpus; nothing else in the sentence moved
  - [x] The pin updated in `tests/test_minions_claim_classification.py`; `-58` now asserts the **asymmetry** (the two members name different corpora) rather than one literal over both
  - [x] `INSTRUMENT_STATUS` asserted unchanged in the same guard; `TC-ArgusAgent-DOCS-001-46` green **and unchanged**; every rendered surface byte-identical

- [x] **T9 — Guard sweep for vacuity on everything this story added (AC7)** — per-guard table in N-10
  - [x] Seven guards, each with its floor asserted FIRST and at least one **generated** adversarial variant at the real seam
  - [x] Recorded: 5 HARDENED, 2 CONFIRMED, with what each variant proved (N-10)

- [x] **T10 — Record, hand off, and re-run the suite (AC9, AC10)**
  - [x] §11 six-item hand-off table written (N-13)
  - [x] Open-items list re-derived at this story's close (N-14), not copied
  - [x] One ledger entry appended: `DF-13-5-B`, the recorded uncertainty operator RULING 3 required, with a named owner. **No disposition was written for any existing entry**, and nothing was appended to green a guard
  - [x] Regenerated via AI-E12-11: `argus/` delta committed first, `scripts/regenerate_dogfood_artifacts.py` run, artifacts committed **separately**
  - [x] Full suite re-run **after** the story record was written — see the Change Log for the recorded result
  - [x] CI stated **NOT ESTABLISHED**, with the specific things that could not be verified named (N-12)

- [x] **T11 — Address code-review iteration 1 (both Low findings)** — done; neither finding
  touched a gating path, and neither figure moved a guard (D-9, N-16)
  - [x] Finding 1 · the `git status --porcelain -z` rename/copy record boundary in
    `scripts/pinned_corpus_snapshot.py` — reproduced RED at the real seam FIRST, then fixed;
    `TC-ArgusAgent-PRECISION-001-72` (rename, copy, spaces, non-ASCII) and `-73` (the refusal
    paths) added, each with its non-vacuity floor asserted first
  - [x] The sibling `-z` assumptions audited, and one FURTHER hole found and closed by the new
    guard: a stream truncated after a rename entry yielded an EMPTY origin path instead of a
    refusal, because the split leaves a trailing empty field (D-9)
  - [x] Proved on the five live checkouts, by pure `git status` reads, that no member carries a
    rename/copy record — so the committed artifact's `dirty_in_scope_source_files` are
    unaffected and no regeneration is warranted (D-9)
  - [x] Finding 2 · every line count the record states as measured was re-measured with the
    ceiling guard's own `_measure_population()`; **three** were wrong, not one (D-9)
  - [x] Full suite re-run **after** the story record was written — see the Change Log

---

## ⛔ ESCALATION — the two inputs this story cannot give itself

**E1 — The `minions` checkout is not on its pinned sha, and it has uncommitted work in it.**
`minions` carries 24 of the 31 findings. Its checkout is at `cabf73a4`, the manifest pins `ec63b729`,
and the working tree has 7 uncommitted entries (3 in-scope). The runner will refuse it, correctly.

Restoring it to the pin is an **operator act over a third-party checkout containing someone's
uncommitted work**. No agent may `checkout`, `stash`, `clean` or `reset` it. The admissible options,
for XAgent007:
1. Preserve the uncommitted work (branch or stash, operator-performed), detach onto `ec63b729`, run,
   restore. **The pinned sha is reachable**, so nothing is lost.
2. Clone the pin into a scratch directory and point `--map` at that. Preferred if any doubt exists —
   it touches nothing.
3. Record the member as **`Unevaluable` for this run** with the reason, and record plainly that the
   result covers **four of five** members and therefore **cannot** be reported as a corpus-wide zero.

**Option 3 changes the story's headline and must be stated in the record if taken. It is not a
fallback to be chosen quietly.** Re-pinning the manifest is **not** on this list: it silently redefines
the corpus the adjudication was performed over, which Story 13.3 / AC5 forbids.

**E2 — Any residual `BORDERLINE` that needs terminating.** Protocol §4's ladder ends at an external
tie-break, and protocol §2 records the QA-Lead second and the external tie-break adjudicator as
**unfilled**. Filling them is an operator act no agent may perform. If the re-adjudication requires
either, **STOP** and report which rows and why.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (BMAD dev-story worker), 2026-08-18, on HEAD `63a0434`.

### Debug Log

**Every figure below was produced by executing the shipped instrument on this tree. Where a
§0 premise did not survive, the corrected figure is recorded plainly rather than the story's.**

**D-1 — T1, the five checkouts re-derived (AC1).** `git -C <windows path> cat-file -t <pin>`
returned `commit` for **all five** pinned shas, and `rev-parse HEAD` was compared separately:

| Member | Checkout (re-derived) | `cat-file -t <pin>` | HEAD == pin | dirty entries | in-scope files AT PIN | in index |
|---|---|---|---|---|---|---|
| ai-body-runtime | `D:/ProjectX/XAgents/XAgents/ai_body_runtime` | `commit` | ✅ | 0 | 15 | 15 |
| agent-markovich | `D:/ProjectX/XAgents/XAgents/AgentMarkovich` | `commit` | ✅ | 0 | 65 | 65 |
| minions | `D:/ProjectX/XAgents/XAgents/Minions` | `commit` | ⛔ HEAD `8b7be40f` | 0 | **583** | **479** |
| xagents-webapp | `D:/ProjectX/XAgents/XAgents/XAgents-WebApp` | `commit` | ✅ | 1 (0 in scope) | 862 | 862 |
| agent-smith | `D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith` | `commit` | ✅ | 16 (**6 in scope**) | 435 | 435 |

**Two §0 figures corrected, both by measurement:**
- §0.2 records `minions` HEAD as `cabf73a4`; it is **`8b7be40f`** today. The drift is live, the
  sha has moved since contexting, and the pinned commit **is reachable** in that checkout.
- §0.3 records `minions` as carrying **3** dirty in-scope files; it carries **0** today. The
  member that is dirty in-scope is **`agent-smith`, with 6** — the member holding all five
  residual `BORDERLINE` rows, exactly as §0.3 warned.

**D-2 — the `minions` 583-vs-479 discrepancy, reconciled (AC1, §0.1 caveat).** At the pin the
in-scope population is **583**; the current index holds **479**; 13.1 recorded
**`source_file_count = 591`**. The recorded figure matches **neither**, and no reading of the
pinned object database reproduces it. That is not a rounding difference — it is the signature
of a measurement taken over a working tree whose bytes are not recoverable. Recorded, not
explained away: `DF-13-5-B`.

**D-3 — the instrument fix (operator RULING 1 + 2).** Materialization now reads the **pinned
git object**: `git ls-tree -r <pin>` for the population (never `git ls-files`, which reads the
INDEX — that is the 583/479 gap), `git cat-file --batch` for the bytes (raw objects, no
`core.autocrlf` / `.gitattributes` filter), and then **every staged file is re-hashed with
git's own blob identity and compared to the id `ls-tree` reported**. `PinUnreachable` is a
named `Unevaluable` for a member and never a fallback to the working tree; a Windows
`MAX_PATH` overrun is a refusal **before** the write. **No corpus member's working tree was
mutated** — no `checkout`, no `stash`, no `clean`, no `worktree`; `ls-tree` and `cat-file` are
pure reads of the object database, and the Windows path form was passed to `git -C` throughout.
Snapshots were materialized under the short root `D:/_argus_snap` (deepest in-scope relative
path measured at **104** characters).

**D-4 — the re-audit, five members, pin-verified, two runs each (AC1, AC3, T5).**

| Member | files at pin | verified vs pin | test files | test fns scored | flagged files | advisory | **blocking** | repro |
|---|---|---|---|---|---|---|---|---|
| ai-body-runtime | 15 | 15/15 | 4 | 4 | 7 | 13 | **0** | yes |
| agent-markovich | 65 | 65/65 | 26 | 421 | 33 | 152 | **0** | yes |
| minions | 583 | 583/583 | 327 | 3,509 | 385 | 1,727 | **0** | yes |
| xagents-webapp | 862 | 862/862 | 285 | 73 | 586 | 1,494 | **0** | yes |
| agent-smith | 435 | 435/435 | 186 | 1,122 | 238 | 898 | **0** | yes |
| **TOTAL** | **1,960** | **1,960/1,960** | **828** | **5,129** | **1,249** | **4,284** | **0** | 5/5 |

Per-rule, corpus-wide: `orphan_code` 1,675 · `hardcoded_secret` 1,330 · **`vacuous_test_heuristic`
1,032** · `cross_partition` 231 · `traceability_not_establishable` 16 · **`vacuous_test_ast` 0**.

**§0.1(b) is reproduced EXACTLY through the pin-verified path, member by member**:
`vacuous_test_heuristic` 0 / 72 / 648 / 17 / 295 = **1,032**, over **1,960** files. `agent-smith`'s
295 lands on the retrospective's figure. **The zero moved nowhere** — and §0.1's own caveat
(*"a detector-level measurement… the dev must re-derive through the actual runner"*) is
discharged: `blocking_finding_count` is **0 for every member through the full pipeline**, not
only for the detector.

**One §0.1 figure restated rather than reproduced:** §0.1(b)'s *"269 flagged files"* is the
**vacuous-test-flagged** population; the runner's **1,249** is the **all-detector** flagged
population, because the runner measures the pipeline and §0.1 measured one detector. Different
questions, both true. The comparable number is `vacuous_test_heuristic = 1,032`, which matches.

**D-5 — `agent-smith` is the proof that the fix is not decorative.** It was audited from a
checkout carrying **six dirty in-scope source files**, and all 435 staged files hashed to their
pinned blobs. Under the old instrument those six bytes would have entered the measurement
silently while `byte_reproducible_across_two_runs` reported `True`. `minions` was audited at
`ec63b729` from a checkout parked on `8b7be40f` — **without touching it**. Escalation **E1** is
therefore dissolved by the instrument rather than by an operator act on a third-party tree, and
the result is a five-of-five zero, not a four-of-five one.

**D-6 — the gate, re-run through `decide_gate` (AC4).** Outcome **`BLOCKED`**, precision
condition **`UNEVALUABLE`**, clean-repo `MET`, floor-N `MET`, recorded-cleared `FAILED`. No
fourth outcome was invented; `GATE_OUTCOMES` is still exactly three and `UNEVALUABLE` appears
only in `CONDITION_VERDICTS`. `decide_gate` was **called**, never re-derived (AR7).

**D-7 — module sizes, re-measured with the ceiling guard's own `_measure_population()` BEFORE
a line was written (AC8).** `test_built_distribution.py` **1200/0 headroom** · `test_instrument_
disclosure.py` **1198/2** · `test_vacuous_detector.py` 1161/39 · `test_gate_decision.py` 900 ·
`test_validation_corpus.py` 859 · `test_adjudication_record.py` 859 · `vacuous_test.py` 1113 ·
`pipeline.py` 1111. **Every AC8 figure confirmed exactly.** Note `tests/test_status_document_
registry.py` is **ABSENT from the measured population** — `_measure_population()` reads tracked
files and Story 13.4's unit is uncommitted, so the ceiling guard cannot see it yet.

**D-8 — validations.** `ruff check` clean on every touched module. `mypy` clean on the changed
`argus/` modules and on `scripts/pinned_corpus_snapshot.py`. Full suite: see Completion Notes.

**D-9 — review iteration 1: the figures RE-MEASURED, and three were wrong (2026-08-18, on
HEAD `313c94b`).** The review found one stated-as-measured figure that measurement
contradicted. Rather than patch the one number, every line count this record states was
re-executed through the ceiling guard's own `_measure_population()` — the same
`len(text.splitlines())` predicate `MAINT-001-02` drives — with the pre-split column taken
from `git show 63a0434:<path>`. **Three of the asserted figures were wrong; all three had
been written without measurement, which is the defect class, not the arithmetic.**

| Figure | Record stated | RE-MEASURED | |
|---|---|---|---|
| `tests/test_instrument_disclosure.py`, after the split | 897 | **893** | ⛔ corrected |
| `tests/test_minions_claim_classification.py` (new, N-11) | 297 | **350** | ⛔ corrected |
| `tests/test_instrument_disclosure_surfaces.py` (new, N-11) | 372 | **367** | ⛔ corrected |
| `tests/test_built_distribution.py`, after the split | 954 | 954 | ✅ |
| pre-split: 1198 · 1200 · 900 · 859 · 859 · 1161 · 1111 · 1113 | as D-7 | identical | ✅ |
| `mypy argus` | clean, 87 source files | clean, 87 source files | ✅ |
| `bandit -r argus` | 0 High / 0 Medium / 20 Low | identical | ✅ |

**Nothing here moved a guard**: the largest corrected figure is 350 against a 1200 ceiling, and
`MAINT-001-02` measures the files rather than reading these numbers. The reason to fix them
anyway is that the module-size table is what the NEXT story cites when it decides whether it
must split before writing — a table that is 53 lines optimistic is a trap laid for that story.

**The corpus figures were RECONCILED, not re-run**, and the distinction is recorded rather
than blurred: the per-member `corpus_read_proof` blocks in the committed
`adjudication-set-13-5.json` were summed and compared to its corpus-wide block — 1,960 files ·
828 test files · 5,129 scored test functions · 1,249 flagged · 4,284 advisory · **0 blocking**,
reconciling exactly, member for member. They were **not** re-measured over the checkouts,
deliberately: `minions` has moved again since this story ran (D-1 recorded HEAD `8b7be40f`;
§0.2 recorded `cabf73a4` before that), so a re-run's *checkout-state* fields could not be
compared against the artifact's even though the *pinned* bytes are invariant to exactly that
drift. Measured today, `minions` carries **9** dirty in-scope files where the run recorded 0 —
third-party movement, and precisely the thing the pinned-object instrument exists to be
immune to.

**D-10 — the `-z` record boundary, reproduced before it was fixed (review finding 1).** The
defect was reproduced RED at the real seam first: over a real repository carrying a real
`git mv`, `dirty_in_scope_paths` reported **`/alpha.py`** and **`/has space.py`** — two origin
paths with their first three characters eaten. `git status --porcelain -z` emits an ordinary
entry as `XY <path>` but a rename or copy as **two** records, the second being the origin path
**bare, with no `XY ` prefix**, so a uniform `record[3:]` slices into it.

Three things were established by execution, not argument:
- **The blast radius is exactly zero on the committed artifact.** All five live checkouts were
  re-read with pure `git status` calls (no mutation of any third-party tree): 0 · 0 · 14 · 1 ·
  16 entries, and **not one rename or copy record among them**. The old rule and the new rule
  were both applied to each of those five real streams and returned **identical** sets. The
  artifact's `dirty_in_scope_source_files` therefore cannot differ, and regenerating it would
  change nothing but its provenance.
- **The field never reached a gate.** `verify_pinned_bytes` proves the audited bytes against
  the pin by blob hash and never reads this field; no refusal or gating path consults it.
- **A second, separate hole was found while auditing the siblings, and closed.** A stream
  truncated immediately after a rename entry produced an EMPTY origin path rather than a
  refusal, because splitting on NUL leaves one empty trailing field and the end-of-stream test
  never fired. It was the new guard `-73` that turned it up, on its first run.

The remaining `-z` assumptions were audited and found sound, and are now asserted rather than
assumed: `-z` suppresses `core.quotepath`, so paths with **spaces** and **non-ASCII** bytes
arrive literally and need no unquoting (both are in the fixture, both asserted); `??`
untracked records carry the ordinary three-character prefix; and `pinned_tree`'s separate
`ls-tree -r -z` parse partitions on a TAB, which is correct for that format and was left
alone. One residue is stated rather than fixed: the stream is decoded with
`errors="replace"`, so a path whose bytes are not valid UTF-8 would be recorded with
replacement characters. It is evidence-only, no such path exists in the corpus, and inventing
a surrogate-escape round-trip for a field nothing reads would be scope this finding does not
carry.

### Completion Notes

**N-1 — What this story did, in one line.** It made the pin **structurally enforced instead of
assumed**, re-measured the corpus through it, and made the resulting outcome **expressible**:
`BLOCKED` + precision `UNEVALUABLE`, over a corpus proved read.

**N-2 — AC1 · the corpus is PROVEN read, and the proof is the artifact's own field.** The
runner now emits a `corpus_read_proof` block per member and corpus-wide, and every conjunct is
measured on the run being decided: members audited, source files scanned, **test functions
scored** (the field that separates *"read and clean"* from *"unparsed"* — both emit nothing),
every member's bytes proved against its pin, both runs byte-identical. `flagged_file_count` and
`advisory_finding_count` are recorded but deliberately **not** part of the predicate: requiring
a flag would make a genuinely clean corpus unprovable and would reward a noisier detector.

**N-3 — AC1 · the dirty-tree half was closed by PROOF, not by refusal.** AC1 offered two ways:
refuse a dirty member, or prove its dirty files do not enter the snapshot. The second is
strictly stronger and it is what shipped — *"the tree was dirty and it provably did not matter"*
is a checkable statement, and it does not make the measurement hostage to somebody else's
working tree. No corpus member was mutated.

**N-4 — AC2 · `DF-13-3-A` re-verified, and its residual restated as STILL OPEN.** The
reachability half was verified by execution: `agent-smith`'s pinned sha resolves at depth five
(`D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith`), `cat-file -t` returns `commit`, and all
five paths were re-derived and are recorded in D-1. It was **not** re-filed and **no disposition
was written to the ledger for it**. Its residual — the seven `agent-smith` row reasons pointing
at an `evidence_deviation` header field the record's closed schema does not have — **remains
open and untouched**. Adding a field to a closed schema, over rows a human already signed, is a
schema change on an append-only evidence record and belongs to a story that says so.

**N-5 — AC3 · nothing was appended, and that is a MEASURED outcome rather than a decision.**
The re-audit emitted **zero** verdict-eligible findings, so there was no finding to adjudicate
and therefore no superseding row to write. Two consequences, both deliberate:
- The 31 rows are **byte-unchanged**, and that is now **verified by execution** rather than
  asserted: `TC-ArgusAgent-PRECISION-001-71` extracts the canonical bytes of every committed
  row, drives a **real** `AdjudicationRecord.append` at the real seam, and compares the prior
  rows byte-for-byte afterwards — keyed by `row_id`, so a reordering cannot pass as identity,
  which a file diff could not distinguish. Its adversarial variant is **generated**: one
  character of one committed row is perturbed and the comparison is proved to go RED.
- `expert_hours` stays **`null`** with its *"NOT RECORDED"* note. **It was not set to zero.**
  Zero would claim a re-adjudication took no time; the truth is that no re-adjudication
  happened, because the corrected detector left nothing to adjudicate.
- **No `BORDERLINE` row was terminated, superseded or re-read.** Escalation **E2** was
  therefore never reached: protocol §4's ladder was not engaged, and the QA-Lead second and the
  external tie-break remain unfilled. Superseding a `BORDERLINE` is a judgement, and no agent
  made one here.

**N-6 — AC4 · the outcome, in the instrument's own vocabulary.** `BLOCKED`, with protocol §5's
`precision-at-least-80-percent` carrying the condition verdict `UNEVALUABLE`. **13.3 was
`BLOCKED` on EXHAUSTIVENESS** (five unterminated ladders). **13.5 is `BLOCKED` on the
DENOMINATOR** (the corpus was read and nothing was promoted). Same registered outcome member,
two different facts — and the recorded reason now says which, in words a stranger can separate:
*"the corpus WAS READ and NOTHING was promoted… This is NOT an unread corpus and it is NOT a
shortfall."* The `BLOCKED` result is nowhere rendered as *"the gate did not clear"*, and
`TC-ArgusAgent-PRECISION-001-70` asserts that on the live artifact. The closure path names
`DF-13-5-A`'s pre-registered rule and states that executing it is the owner's act, not this
story's.

**N-7 — AC5 · the floor was NARROWED in both directions, and both are guarded.** The two
producers both refused this story's expected outcome, and their refusals were correct for the
world they were written in. What changed is that Epic 14 created a third world.
- `argus/precision/gate_decision.py` — `decide_gate` takes a `CorpusReadProof`. An empty
  emitted population with **no** proof, or with one whose any conjunct fails, still raises
  `VacuousDecisionError` with the same claim it always made. With a **positive** proof it
  returns `BLOCKED` + `UNEVALUABLE`.
- `scripts/build_gate_decision.py` — the same narrowing at the producer end, reading the proof
  off the artifact rather than re-deriving it a day later over whatever the checkouts look like
  now.
- `argus/precision/adjudication.py` — one further correction of the same shape: the fold's
  `unevaluable_reason` rendered *"NOT EXHAUSTIVELY ADJUDICATED — 0 of 0"* for an empty
  population, which reads as a judgement that has not finished when there is nothing to judge.
  That is the `DF-9-2-B` false-subject class on the surface that publishes the gate. It now
  says `EMPTY EMITTED POPULATION` and states plainly that the record alone cannot decide
  between *read-and-clean* and *unread*.
- `TC-ArgusAgent-PRECISION-001-69` proves **both** directions and **generates** its adversarial
  variants by flipping each conjunct of the proof in turn — plus a positive control proving the
  generator is testing the conjunct and not the fixture, and a case proving a **non-empty**
  population ignores the proof entirely, so the narrowing cannot become an exhaustiveness bypass.
- The **rejected alternative is not re-proposed**: no fourth `GATE_OUTCOMES` member was added,
  and no placeholder finding id was synthesised. `-69` asserts the vocabulary is still exactly
  three.
- `architecture.md`'s *Gate-decision enforcement* registration was amended **by strike**
  (`~~…~~` plus the amendment), never erased, and `TC-ArgusAgent-DOCS-001-77`'s anchor list was
  extended to cover both the strike and the new *Corpus-pin provenance enforcement* rule, so
  the registration cannot be deleted silently. Every anchor `-77` already named still resolves.

**N-8 — AC6 · the latent falsehood corrected, and pinned so it cannot flip anything.**
`INSTRUMENT_DISCLOSURE_VALIDATED` said the ≥80% gate was measured *"over the **Argus dogfood
corpus**"*. It was not: the Epic 13 adjudication ran over the ratified five-repository
validation corpus — the population Story 13.1 **excluded** the dogfood self-audit from. The
corpus name, and nothing else, was corrected. `INSTRUMENT_STATUS`, `protocol_cleared`'s call
sites, both `NOT_INDEPENDENTLY_VALIDATED` texts, the two-member vocabulary and the removal
condition are **untouched**; `TC-ArgusAgent-DOCS-001-46` is green **and unchanged**. `-58` now
asserts the **asymmetry** rather than a shared literal — which is precisely why the old text was
wrong and green at the same time: it looped over both constants asserting `"Argus dogfood
corpus" in text`, and one literal over two different corpora can only be right about one of
them. Both directions are asserted (the corrected name present **and** `"dogfood"` absent), and
the non-vacuity floor sits in the same guard: `INSTRUMENT_STATUS` is still
`NOT_INDEPENDENTLY_VALIDATED` and the rendered notice is byte-identical to the live text, so
the corrected sentence provably reaches no user today.

**N-9 — AC6 · §11.3(b) restated as STILL OPEN, deliberately.** `protocol_cleared_call_sites`
matches only a literal `True`, so `TC-ArgusAgent-DOCS-001-46` goes vacuous at the exact moment
the gate flips (`DF-13-3-B`). It is real and reproducible now. Exercising it requires **taking
the flip branch**, which this story must not do. Not touched, not disposed, restated here.

**N-10 — AC7 · every new negative-asserting guard carries a non-vacuity floor and a GENERATED
adversarial variant.** Recorded per guard, with what was proven:

| Guard | The absence it asserts | Non-vacuity floor asserted FIRST | Generated adversarial variant | Result |
|---|---|---|---|---|
| `-65` | the dirty working-tree byte is **absent** from the snapshot | the pinned population is non-empty and is the pin's, not the index's (`gamma.py` absent, `alpha.py` present) | a real git repo built with an uncommitted edit **and** a moved HEAD; both the pinned byte's presence and the dirty byte's absence asserted | HARDENED |
| `-66` | the verification reports **no** mismatch | the UNPERTURBED snapshot must verify first, or the perturbations prove nothing | one byte changed · one file deleted · an empty population — each mutating a **real** materialized snapshot, and a missing file must not report as a content mismatch | HARDENED |
| `-67` | an unreachable pin yields **no** measurement | the fixture's pin is asserted reachable before the absent one is tried | a well-formed sha absent from the object DB; `blob_sha1` cross-checked against `git rev-parse <pin>:<path>` rather than a second implementation; a `MAX_PATH`-length path | HARDENED |
| `-68` | **zero** blocking findings over the corpus | 5 members · >1000 files · >1000 scored functions · >1000 advisory · every member pin-verified — **all before the zero is read** | `vacuous_test_heuristic > 500` asserted **beside** `vacuous_test_ast == 0`: a detector that never ran produces zero of both | CONFIRMED |
| `-69` | the floor still **refuses** without evidence | the committed record is non-empty; the positive fixture is asserted to pass | each of the five conjuncts flipped in turn, each must refuse; plus a positive control on the generator itself | HARDENED |
| `-70` | the artifact never says *"the gate did not clear"* | the artifact must carry a proof with >1000 files and >1000 scored functions before its zero is read | `UNEVALUABLE` asserted **absent** from the outcome vocabulary and **present** as the condition verdict | HARDENED |
| `-71` | the 31 rows are **unchanged** | the record holds >0 rows and row ids are unique | one character of one committed row perturbed; the canonical-bytes comparison proved to go RED | HARDENED |

**Two existing guards were AMENDED, and both got stronger, not weaker.**
`TC-ArgusAgent-PRECISION-001-55` and `-61` encoded the pre-13.5 world, in which `BLOCKED`
implied *either* a residual *or* an empty denominator. There is now a third way — an empty
emitted population beside a record that still holds 26 historical dispositions — and it is
admitted **only** against a positive corpus-read proof whose own counts are asserted, which is
strictly **more** evidence than the two legs it joins, not less.

**No `pytest.skip` was added anywhere.** The one platform-conditional assertion (`-67`'s
`MAX_PATH` branch) still asserts the constant and the refusal path's existence on every
platform; only the Windows-specific raise is gated.

**N-11 — AC8 · both zero-headroom modules split by COHESION, before a line was written.**
- `tests/test_built_distribution.py` **1200 → 954**. `TC-ArgusAgent-DOCS-001-57`/`-58` moved to
  `tests/test_minions_claim_classification.py` (**350** — re-measured; the **297** first written
  here was never measured, D-9). The boundary is the section banner
  Story 11.5 itself drew: that module measures a **built wheel**; those two guards read the
  **source tree** and the disclosure **constants** and never build anything.
- `tests/test_instrument_disclosure.py` **1198 → 893** (re-measured; **897** was asserted, D-9). `TC-ArgusAgent-CLI-001-50`/`-51` and
  `TC-ArgusAgent-REPORT-002-30`..`-32` moved to `tests/test_instrument_disclosure_surfaces.py`
  (**367** — re-measured; **372** was asserted, D-9). Static guards stayed; behavioural ones moved. `protocol_cleared_call_sites`
  deliberately **stayed** — it is what `-46` rests on and `tests/test_gate_decision.py` imports
  it from there by name.
- **Test ids are byte-identical**, no function was split across either boundary, and the import
  edge runs **one way only** (new → old, never back: a cycle between two test modules fails at
  collection). **No `_EXEMPT_BY_DESIGN` entry was added**; `MAINT-001-01`..`-04` are green.
- `tests/test_vacuous_detector.py` (1161/39) was **not** split, because no case went into it —
  `DF-14-3-H`'s precondition is *"the next story that needs a case there must split first"*, and
  this story needed none. The entry stays open and its measured claim that it is *"the tightest
  tracked module in the repository"* is confirmed **false** by D-7: it was the third tightest of
  the three on this blast radius, and is now the tightest only because the other two were split.

**N-12 — AC9 · reproducibility of this story's own evidence, stated honestly.**
- The instrument no longer stamps a sha without checking. `GateDecision` carries
  `commit_sha_provenance`, and `build_gate_decision.py` measures the working tree and writes
  either `ESTABLISHED` or the mechanically-recognised **`NOT ESTABLISHED`** marker with the
  entry count. It records rather than refuses, deliberately: refusing would make the honest
  artifact unwritable on a tree carrying unrelated uncommitted work, and an unwritten record
  states nothing at all.
- **T2 was NOT performed, by operator instruction, and AC9's clean-tree clause is therefore
  NOT MET.** Story 13.4's five-file unit and the three Epic-14 governance documents remain
  uncommitted on disk. They are not this story's to commit. What this changes about the
  evidence is bounded and is stated on the artifact: what is unestablished is the provenance of
  the **Argus revision that did the reading**, not of the **bytes it read** — every corpus
  member was read from its pinned object and every staged file was proved against the pin by
  blob hash.
- `_bmad-output/…/architecture.md` carries **two** uncommitted changes on disk: Story 13.4's
  registration (pre-existing, not this story's) and this story's AC5 strike + AC1 registration.
  Only **this story's** edits were staged, by materialising the committed base and applying this
  story's two amendments to it. 13.4's prose stays on disk, uncommitted, with the rest of its unit.
- ⛔ **CI evidence is NOT ESTABLISHED for this story.** Every gate in this run was
  local/Windows. `origin/master` is still `47b6dbe` — the Epic-14 **base** commit — so no CI run
  covers any commit in Epic 14 or in this story, and nothing here is pushed. A green local suite
  in this repository has already shipped POSIX-only bugs to `master`. **What specifically could
  not be verified:** the ubuntu matrix legs with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; the
  behaviour of `scripts/pinned_corpus_snapshot.py`'s `MAX_PATH` branch on POSIX (it is `os.name
  == "nt"`-gated by design and its constant is asserted on every platform); and whether the two
  cohesion splits collect cleanly under a case-sensitive filesystem.

**N-13 — AC10 · what 13.5 hands the FINAL Epic-13 retrospective**, per §11's six items:

| §11 item | What 13.5 contributed |
|---|---|
| 1. Whether the epic achieved its purpose | The measurement was **taken**, on a corrected detector **and** a corrected instrument. It returned no denominator. *Measure, do not delete* was served: nothing was removed from the corpus, the threshold, the manifest or the disclosure — the number does not exist because nothing was promoted |
| 2. The measured precision figure; disclosure replaced or stays | **No figure** — the denominator is empty (`precision: null`, `precision_ratio: "NOT COMPUTED BY THIS RUN"`). The disclosure **STAYS**; AC6 pins that its declared status and every rendered surface are byte-unchanged |
| 3. Whether the flip path behaves correctly when it fires | **(a) discharged** — `INSTRUMENT_DISCLOSURE_VALIDATED`'s corpus name corrected, with the status and rendered surfaces asserted unmoved in the same guard. **(b) NOT discharged, deliberately** — `protocol_cleared_call_sites`' literal-`True` blindness needs the flip branch taken (N-9) |
| 4. `expert_hours` against §3's ≤4 ceiling | **No hours to record**: no re-adjudication took place, because the corrected detector left nothing to adjudicate. The field stays `null` / *"NOT RECORDED"* and was **not** set to zero (N-5). Whether 13.2's original hours are recoverable is a separate question this story does not answer |
| 5. `DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A` | **Re-derived and restated, not disposed.** Their human half was the adjudication; a re-measurement that produced an empty population does not discharge them, and no ledger disposition was written for any of them |
| 6. The epic's re-derived open-items list | Below (N-14), computed at this story's close — not copied from `epic-13-open-items.md`, which predates Epic 14 |

**N-14 — the open items, re-derived at this story's close (not copied):**
1. `DF-13-3-A`'s **residual**: seven `agent-smith` row reasons cite an `evidence_deviation`
   header field the record's closed schema does not have. Open. Needs a schema story.
2. `DF-13-3-B` / retrospective §11.3(b): `protocol_cleared_call_sites` matches only a literal
   `True`, so `-46` goes vacuous the day the gate flips. Open, and only reachable by taking the
   flip branch.
3. `DF-13-5-A`'s **ONE**-round stopping rule is now **live**: 13.5 has recorded its outcome, so
   the rule's branch is executable by its owner. This story did **not** execute it and wrote no
   ledger disposition for it. Quoted verbatim in §0.7 and not re-litigated here.
4. `DF-13-5-B` (new): the 31 rows' provenance is unestablished — they were measured through the
   working-tree-reading instrument. Recorded uncertainty, **not** a re-measurement request.
5. `DF-14-3-H`: `tests/test_vacuous_detector.py` at 1161/39 is still unsplit. Open; its
   *"tightest module"* premise is measurably false (D-7).
6. **CI is NOT ESTABLISHED** for all of Epic 14 and for this story. `origin/master` is `47b6dbe`.
7. Story 13.4's five-file unit and the three Epic-14 governance documents are on disk and not in
   history. Owner-side; not this story's to commit.

**N-15 — what this story deliberately did NOT do.** It did not expand the bench, re-pin a
member, amend a threshold, touch `_CORROBORATION_ASSERTION_CALLEES`, flip `protocol_cleared`,
add a fourth gate outcome, add a size exemption, mutate any corpus member's working tree,
terminate a `BORDERLINE` ladder, or append any ledger disposition in order to green a guard.
Nothing in this record may be read as licence for a second bench-expansion round: **ONE round**
is `DF-13-5-A`'s load-bearing word, and a zero-finding bench round means the detector is too
conservative to be a product — **not** that the bench needs to be bigger.

**N-16 — review iteration 1 · both Low findings resolved, and one of them grew (2026-08-18).**
The review returned CONCERNS with two Low findings, no High, no Medium and no unmet AC. Both
are resolved. Neither touched a gating path, and that is stated as the *reason they were still
worth fixing properly*, not as a reason they were not.

✅ **Resolved review finding [Low] — the `-z` rename/copy record boundary**
(`scripts/pinned_corpus_snapshot.py`). Reproduced RED at the real seam **before** anything was
changed (D-10): a real `git mv` in a real repository made the parser report `/alpha.py` for
`pkg/alpha.py`. The parse is now record-aware rather than uniform, and the shape of the format
is modelled instead of assumed: `parse_porcelain_z` is a **pure** function (AR8) returning
`PorcelainEntry` records that carry the origin path as its own field, and `dirty_in_scope_paths`
became a three-line flatten over it. Three consequences worth naming:
- **The guessing stopped, not just the slicing.** A record that is neither a well-formed
  `XY <path>` entry nor the expected origin half is now a named `PinnedSnapshotError` rather
  than a silent slice. The old failure mode was a *plausible-looking wrong path recorded as
  evidence*, which is worse than a loud one in a deliverable that is entirely a governance
  record. All five live checkouts were parsed with the strict rule as a precondition of
  shipping it: none refuses.
- **The audit found a second hole, and the new guard is what found it.** A stream truncated
  after a rename entry yielded an EMPTY origin rather than a refusal. Closed in the same pass.
- **The evidence-only status was verified, not assumed.** No live corpus member carries a
  rename or copy record, old and new rules agree on all five real streams, and the committed
  artifact is provably unchanged (D-10). Regeneration was therefore **not** performed, and the
  reason is recorded rather than the omission being silent.

`TC-ArgusAgent-PRECISION-001-72` covers the rename, a copy (produced by a real
`status.renames=copies` checkout, not a synthesised stream), paths with spaces on both halves
of a rename, and a non-ASCII untracked path. Its non-vacuity floor is asserted **first and off
the RAW stream**: git must actually have emitted an origin record with no `XY ` prefix, or the
guard proves nothing about the parser it names. Its adversarial variant is **generated** —
the OLD uniform-slice rule is applied to the SAME real stream and its corruption derived, so
the fixture is proved to *discriminate between the two parsers* rather than merely to pass.
`-73` covers the refusal paths, and its floor is the direction that matters for a guard about
raising: the real stream must PARSE, and the rename must model as one entry naming two paths,
before any refusal is asked for — a parser that raised unconditionally fails it.

✅ **Resolved review finding [Low] — an asserted figure that measurement contradicted.** `897`
is corrected to `893` everywhere it appeared. The finding was treated as being about *trusting
unverified numbers* rather than about one number, so every line count this record states was
re-measured; **three** were wrong, not one (D-9). None moves a guard — 350 against a 1200
ceiling — but the module-size table is what the next story reads to decide whether it must
split before writing, and an optimistic one is a trap laid for that story.

**Gates executed this pass** (`TC-ArgusAgent-DOCS-001-21` wants a citation or the marker): full suite **1,641 passed / 0 failed / 0 skipped, exit 0** with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, re-run AFTER this record was written; `ruff check` clean; `mypy argus` clean over 87 source files and `mypy scripts/pinned_corpus_snapshot.py` clean; `bandit -r argus` 0 High / 0 Medium / 20 Low. `TC-ArgusAgent-DOCS-001-78` green — no ledger id was written beside a closure verb, and nothing was appended to `deferred-work.md`.

⛔ **What this pass did NOT verify, restated because it has not changed.** CI is still **NOT
ESTABLISHED**: `origin/master` remains `47b6dbe`, nothing is pushed, and every gate in this
round was local and Windows-only. **The `-z` parsing changed in this pass is exactly the class
of code that differs across platforms**, so the specific unverified claims are named: that
`git status --porcelain -z` emits the same record boundary under the ubuntu matrix legs; that
a rename of a path containing a space and the non-ASCII fixture path survive a case-sensitive
filesystem and a non-UTF-8 host locale; and that `status.renames=copies` produces a `C` record
on CI's git build — the guard does not depend on that last one (its floor rests on the rename),
but the copy assertion is the half that would fail first if it did not. No `pytest.skip` was
added; the unverifiable is recorded by name, which is the pattern this whole story is about.

### File List

**New**
- `scripts/pinned_corpus_snapshot.py` — pinned-object materialization + byte-level pin proof
- `tests/test_pinned_corpus_snapshot.py` — `TC-ArgusAgent-PRECISION-001-65`..`-68`
- `tests/test_minions_claim_classification.py` — AC8 cohesion split (`-57`, `-58`)
- `tests/test_instrument_disclosure_surfaces.py` — AC8 cohesion split (CLI/REPORT surfaces)
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-set-13-5.json`
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/blocking-worklist-13-5.md`

**Modified — review iteration 1 (2026-08-18)**
- `scripts/pinned_corpus_snapshot.py` — record-aware `-z` parsing: `PorcelainEntry` +
  `parse_porcelain_z` (pure, AR8), the rename/copy origin record, the truncated-stream and
  unreadable-record refusals (378 → 448)
- `tests/test_pinned_corpus_snapshot.py` — `TC-ArgusAgent-PRECISION-001-72`, `-73` (370 → 559)
- `_bmad-output/design-artifacts/ArgusAgent/stories/13-5-re-measure-the-gate-against-the-corrected-instrument.md`
  — D-9, D-10, N-16, T11, the three corrected line counts, both findings checked off
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — `897` → `893` in the 13-5
  comment; status back to `review`

**Unchanged by review iteration 1, and verified so rather than assumed:**
`validation-corpus/adjudication-set-13-5.json` and `gate-decision-record.json` (no live corpus
member carries a rename/copy record, so the parser defect cannot have touched them — D-10),
every `argus/` module (this pass changed **no** `argus/` LOC, so the dogfood currency guards
cannot move), `architecture.md`, `deferred-work.md` (**no ledger entry was appended or
dispositioned in this pass**).

**Modified**
- `argus/precision/gate_decision.py` — `CorpusReadProof`; the narrowed floor; the
  empty-population dispatch branch; `commit_sha_provenance`
- `argus/precision/adjudication.py` — the empty-population `unevaluable_reason`
- `argus/verdict/negative_assurance.py` — `INSTRUMENT_DISCLOSURE_VALIDATED` corpus name (AC6)
- `scripts/audit_validation_corpus.py` — pinned materialization, pin verification, corpus-read
  proof, `--snapshot-root` / `--output-name` / `--supersedes` / `--story`
- `scripts/build_gate_decision.py` — superseding set, proof plumbing, narrowed refusal,
  working-tree provenance
- `tests/test_built_distribution.py` — split (1200 → 954)
- `tests/test_instrument_disclosure.py` — split (1198 → 893)
- `tests/test_gate_decision.py` — `-69`, `-70`; `-55`/`-61` amended for the third BLOCKED leg
- `tests/test_adjudication_record.py` — `-71`
- `tests/test_governance_record_integrity.py` — `-77` anchor list extended
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — AC5 strike + AC1 registration
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — `DF-13-5-B`
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
- `_bmad-output/design-artifacts/ArgusAgent/stories/13-5-re-measure-the-gate-against-the-corrected-instrument.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`,
  `minions-dogfood-partition-plan.md`, `minions-dogfood-budget-plan.md` — regenerated via
  AI-E12-11 and committed **separately**

**Unchanged, and asserted so:** `validation-corpus/adjudication-record.json` (the 31 rows),
`validation-corpus/adjudication-set.json` (13.1's run), `tests/corpus/_manifest.py`,
`precision-validation-protocol.md`, `argus/pipeline.py`, `argus/detectors/vacuous_test.py`.

### Review Findings

**Adversarial code review, iteration 1 (2026-08-18).** Reviewed `git diff 63a0434..313c94b`
(commits `d7886ba` + `91b95e3` + `313c94b`) against AC1-AC10, the three operator rulings, and
`architecture.md`'s enforcement registrations. Independently re-derived rather than read back:
the full suite (1639 passed / 0 failed / 0 skipped, exit 0, both before and after this review
pass), `mypy` clean on the touched `argus/` modules and `scripts/pinned_corpus_snapshot.py`,
`bandit` 0 High / 0 Medium on the same set, the `corpus_read_proof` reconciliation (1,960 =
15+65+583+862+435; 5,129 test functions; 1,249 flagged; 4,284 advisory; 0 blocking — all sum
correctly from the D-4 per-member table), byte-identity of `adjudication-record.json`'s 31 rows
before/after this commit range, `agent-smith`'s live dirty state (still 16 entries at `9ab774d7`)
and `minions`' `git worktree list` (no extra worktree registered) confirming Ruling 1's hard
constraint held. `GATE_OUTCOMES` is exactly `{CLEARED, NOT_CLEARED, BLOCKED}`; no production call
site passes `protocol_cleared=True`; `expert_hours` is `None` with a "NOT RECORDED" report string,
never coerced to `0`; both AC5 floor directions are proved at the real seam
(`TC-ArgusAgent-PRECISION-001-69`); `DF-13-5-A` was cited, not executed or dispositioned. Two
Low-severity, non-blocking findings, both new-code robustness/accuracy gaps rather than
correctness or gating defects:

- [x] [Review][Patch] `dirty_in_scope_paths` mis-parses a `git status --porcelain -z` RENAME
  record — the old-path half of an `R  new\0old` pair carries no `XY ` status prefix, but the
  parser unconditionally slices `record[3:]`, corrupting the reported old path (e.g.
  `pkg/alpha.py` renders as `/alpha.py`, confirmed by executing `git status --porcelain -z` over
  a real rename fixture). [`scripts/pinned_corpus_snapshot.py:371-378`] — Severity Low: this
  field is recorded as evidence only (`dirty_in_scope_source_files`) and is never consulted by
  `verify_pinned_bytes` or any gating/refusal path, so it cannot produce a wrong `BLOCKED` vs.
  `CLEARED` outcome; the live corpus's 6 `agent-smith` dirty files and 0 `minions` dirty files
  measured by this run are plain modifications, not renames, so the committed artifact's
  `dirty_in_scope_source_files` lists are unaffected. Untested by `tests/test_pinned_corpus_snapshot.py`
  (no rename fixture exists). Suggested fix: track record parity from the preceding entry's
  status letter (`R`/`C`) and treat the following record as the raw old path with no prefix to
  strip, rather than slicing every record uniformly.
- [x] [Review][Patch] The story record's own D-7 table and File List state
  `tests/test_instrument_disclosure.py` split as "1198 -> 897", but the ceiling guard's own
  `_measure_population()` measures **893** lines on the committed file (re-executed directly
  against the shipped function, not read off the story). [this file, D-7 table and the sprint-
  status comment carry the same "897" figure] — Severity Low: cosmetic inaccuracy only; 893 is
  still comfortably under the 1200-line ceiling either way (`tests/test_module_size_ceiling.py`
  passes), and no gate or guard reads this number. Suggested fix: correct "897" to "893" in the
  story record's D-7 table (and the sprint-status comment, on its next edit) so the module-size
  table a future story cites is exact.

No other findings. AC1-AC10 are each independently discharged as claimed; the AC5 narrowing (the
story's stated central engineering problem) is correctly bidirectional and does not create a
false-negative path for an unread corpus; the T2/AC9 non-completion and CI-NOT-ESTABLISHED
disclosures are honest and match the operator's recorded instruction; `DF-13-5-B` is well-formed
with a named owner and does not re-run Epic 13's original measurement.

**Adversarial code review, iteration 2 (2026-08-19).** Reviewed `git diff 313c94b..ad838f6` (the
single fix commit) against both iteration-1 findings and the diff's own claims. Independently
re-executed rather than read back: the full suite (**1,641 passed / 0 failed / 0 skipped**, exit
0, dot-counted directly from a redirected run — the summary line pytest normally prints was
absent from this environment's captured output on both a background and a foreground run, so
pass/fail/skip counts were derived by counting result-marker characters instead of trusting the
missing line); `mypy` clean on `scripts/pinned_corpus_snapshot.py` and on `argus` (87 source
files); `bandit -r argus` 0 High / 0 Medium / 20 Low and `bandit` on the touched script 0
High / 0 Medium; `ruff check` clean on both touched files; the diff touches exactly the four
files the record claims (`sprint-status.yaml`, this story file, `scripts/pinned_corpus_
snapshot.py`, `tests/test_pinned_corpus_snapshot.py`) — `architecture.md`, `deferred-work.md`
and every `argus/` module are byte-unchanged in this commit, confirmed by `git diff --name-only`.

Re-derived by execution, not read back:
- **The `-72` discrimination claim.** Reverted `dirty_in_scope_paths` to the old uniform
  `record[3:]` slice in a working-tree edit, re-ran `-72` alone: it goes RED, reproducing exactly
  the failure the story describes (`/alpha.py`, `/has space.py` in the reported set). Restored the
  fix; all 6 tests in `tests/test_pinned_corpus_snapshot.py` pass again and the file diff against
  `HEAD` is empty. The fixture genuinely discriminates between the two parsers, as claimed.
- **The three corrected line counts.** Called the shipped `_measure_population()` from
  `tests/test_module_size_ceiling.py` directly: `test_instrument_disclosure.py` = 893,
  `test_minions_claim_classification.py` = 350, `test_instrument_disclosure_surfaces.py` = 367,
  `scripts/pinned_corpus_snapshot.py` = 448, `tests/test_pinned_corpus_snapshot.py` = 559 — all
  five figures match the story record exactly.
- **The five-checkout blast-radius claim.** Ran `git status --porcelain -z` directly against
  all five live checkouts (`ai_body_runtime`, `AgentMarkovich`, `Minions`,
  `XAgents-WebApp`, `Agent-Smith`): zero rename/copy (`R`/`C`) records among them. Ran both the
  shipped `parse_porcelain_z` and the old uniform-slice rule over each checkout's raw stream:
  identical resulting path sets on all five (`Minions` 9 dirty in-scope, `Agent-Smith` 6, the
  other three 0 — matching the story's own re-measurement, and confirming `Minions`' further
  drift this session was correctly not re-run into the artifact). No write path exists in
  `scripts/pinned_corpus_snapshot.py` into any of the five checkouts: the only subprocess verbs
  used are `cat-file`, `ls-tree` and `status` — no `checkout`, `stash`, `clean`, `reset` or
  `worktree`.
- **AR8 purity of `parse_porcelain_z`.** No I/O, clock, `uuid4`, `random` or network reference in
  the function body; it operates only on its `stream` argument and the tests assert
  `parse_porcelain_z(real) == entries` (call-twice determinism) directly.
- **The truncation refusal.** `parse_porcelain_z("R  pkg/renamed.py\0")` raises
  `PinnedSnapshotError` naming the truncation, and a too-short record (`"M\0"`) and an
  unexpected bare record (`"pkg/orphan.py\0"`) each raise distinctly named refusals — `-73`
  is not a single catch-all, as claimed.

**One inaccuracy noted, not filed as a finding.** N-16 states that the `-72` guard's floor does
not depend on CI's git emitting a `C` (copy) record, "but the copy assertion is the half that
would fail first if it did not." Reading the assertions line by line: `assert "pkg/copied.py" in
reported` only checks set membership and is satisfied whether `pkg/copied.py` arrives as a `C`
pair or as a plain staged `A` entry (`git add` was run on it either way), so in fact **no**
assertion in `-72` or `-73` depends on the `C` record firing — the guard is more robust to a
missing `C` record than the prose claims, not less. This does not weaken the portability
disclosure (the load-bearing part — "the floor rests on the rename" — is correct and verified);
it is a one-line prose overclaim in the story's own self-assessment, inconsequential to
correctness or to CI risk, and not worth a fix-loop round on its own.

**Severity assessment: no High, no Medium, no Low.** Both iteration-1 findings are resolved as
claimed, a third defect in the same class (the truncated-stream empty-origin hole) was found and
closed correctly, and the two additional wrong line counts are now correct. No new defect was
introduced by this diff.

---

## References

- [epics.md — Epic 13 / Story 13.5](../epics.md) · Epic 14 header (*"this epic does not clear the gate
  and cannot"*)
- [precision-validation-protocol.md](../precision-validation-protocol.md) §2 roles · §3 expert-hour
  ceiling · §3.4 evidence immutability · §4 method and ladder · §5 four conditions · §6 R2 ratification
- [architecture.md](../architecture.md) — *Adjudication-record enforcement* · *Gate-decision
  enforcement* · *Ledger-claim cross-check enforcement* · §Enforcement GUARD-ADEQUACY CLAUSE
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A` (pre-registered rule) · `DF-13-3-A` (corrected
  reachability + residual) · `DF-14-1-A` (name-level proxy) · `DF-14-3-F` (stale path) · `DF-14-3-H`
  (headroom; its *"tightest module"* premise is measurably false — see AC8) · `DF-13-3-B` · `DF-8-5-B`
- [epic-13-retro-INTERIM-2026-08-17.md](../epic-13-retro-INTERIM-2026-08-17.md) §11 — the six items the
  FINAL pass must cover
- [epic-14-retro-2026-08-18.md](../epic-14-retro-2026-08-18.md) — SD-1 (uncommitted governance record) ·
  SD-2 (24 unswept guards) · SD-3 (three modules at 0 / 2 / 39)
- [stories/13-3-record-the-result-and-let-it-decide.md](13-3-record-the-result-and-let-it-decide.md) ·
  [stories/13-4-split-the-status-document-registry.md](13-4-split-the-status-document-registry.md)
- Source: `argus/precision/gate_decision.py` · `argus/precision/adjudication.py` ·
  `argus/precision/replay_harness.py` · `argus/detectors/vacuous_test.py` ·
  `argus/detectors/provenance_scan.py` · `argus/verdict/negative_assurance.py` ·
  `scripts/audit_validation_corpus.py` · `scripts/build_adjudication_record.py` ·
  `scripts/build_gate_decision.py` · `tests/corpus/_manifest.py`

---

## Change Log

| Date | Change |
|---|---|
| 2026-08-19 | **Code review iteration 2 — VERDICT pass, no findings.** Reviewed `git diff 313c94b..ad838f6` (the single fix commit) against both iteration-1 findings. Independently re-derived by execution: reverted `dirty_in_scope_paths` to the old uniform slice and confirmed `-72` goes RED, then restored the fix and confirmed all 6 tests green; re-measured all five corrected line counts through `_measure_population()` and all five match exactly (893/350/367/448/559); ran `git status -z` directly against all five live checkouts and confirmed zero rename/copy records and identical old/new parsing results on all five, with no write-capable subprocess verb in the module; confirmed AR8 purity and three distinctly named refusals in `-73`; confirmed the diff touches exactly the four claimed files. `mypy`/`bandit`/`ruff` clean; full suite 1,641 passed / 0 failed / 0 skipped, exit 0 (pytest's summary line was absent from this environment's captured output on two separate runs, so the count was independently derived by counting result-marker characters). One prose overclaim noted but not filed as a finding: N-16 names a specific `-72` assertion as depending on CI's git emitting a `C` record, but inspection shows none of the assertions actually do — the guard is more robust than claimed, not less, and this does not weaken the load-bearing portability disclosure. `review` -> `done`. |
| 2026-08-18 | **Code review iteration 1 addressed — 2 of 2 findings resolved, both Low, neither on a gating path.** (1) `scripts/pinned_corpus_snapshot.py` mis-parsed a `git status --porcelain -z` **rename/copy** record: the origin path is emitted BARE, with no `XY ` prefix, and a uniform `record[3:]` ate its first three characters (`pkg/alpha.py` -> `/alpha.py`). Reproduced RED at the real seam FIRST over a real `git mv`, then fixed by modelling the format instead of assuming it — `parse_porcelain_z` is a pure (AR8) function returning `PorcelainEntry` records, and an unreadable record is now a NAMED refusal rather than a silent slice. **Auditing the sibling assumptions turned up a SECOND hole, found by the new guard on its first run**: a stream truncated after a rename entry yielded an EMPTY origin instead of refusing. Closed in the same pass. `TC-ArgusAgent-PRECISION-001-72` (rename, a real `status.renames=copies` copy, spaces on both halves, non-ASCII) and `-73` (the refusal paths) added — each with its non-vacuity floor asserted FIRST off the RAW stream, and `-72`'s adversarial variant **generated** by applying the old rule to the same real stream, so the fixture is proved to discriminate between the two parsers. Blast radius measured, not assumed: all five live checkouts re-read with pure `git status` calls (no third-party tree mutated), **not one rename/copy record among them**, old and new rules identical on all five — so the committed artifacts are provably unaffected and were NOT regenerated. (2) Every line count this record stated as measured was re-executed through the ceiling guard's own `_measure_population()`: **three were wrong, not one** — `test_instrument_disclosure.py` 897 -> **893**, `test_minions_claim_classification.py` 297 -> **350**, `test_instrument_disclosure_surfaces.py` 372 -> **367**; every pre-split figure, `mypy` (87 source files) and `bandit` (0 High / 0 Medium / 20 Low) confirmed exactly. Corpus figures RECONCILED from the committed artifact (per-member sums == corpus totals: 1,960 / 828 / 5,129 / 1,249 / 4,284 / **0**) rather than re-run, because `minions` has drifted again (9 dirty in-scope files today vs 0 at the run) and the pinned bytes are invariant to exactly that. **No `argus/` LOC changed**, so the dogfood currency guards cannot move and regeneration was correctly skipped (verified, not assumed). No ledger entry appended or dispositioned. **Full suite after the story record was written: 1,641 passed / 0 failed / 0 skipped, exit 0** (baseline 1,639; +2 = `-72` and `-73`). `ruff check` clean, `mypy` clean on `scripts/pinned_corpus_snapshot.py` and over `argus` (87 source files), `bandit` 0 High / 0 Medium. ⛔ CI still **NOT ESTABLISHED** (`origin/master` is `47b6dbe`, nothing pushed) — and the `-z` parsing touched here is exactly the class of code that differs across platforms; the specific unverified claims are named in N-16. `in-progress` -> `review`. |
| 2026-08-18 | **Implemented.** Materialization moved off the working tree and onto the **pinned git object** (`scripts/pinned_corpus_snapshot.py`): `git ls-tree -r <pin>` for the population, `git cat-file --batch` for the bytes, and **every staged file re-hashed with git's own blob identity** and refused by name if it is not the pinned byte. No corpus member's working tree was mutated. Re-measured through that path: **1,960** in-scope files, **828** test files, **5,129** test functions scored, **1,249** files flagged, **4,284** advisory findings, **0** blocking — all five members pin-verified (1,960/1,960 files) and byte-reproducible across two runs. `vacuous_test_heuristic` **1,032** reproduces §0.1(b) member for member; `vacuous_test_ast` is **0**. Both vacuity floors NARROWED so an empty population with a positive corpus-read proof is admitted and one without is still refused; `decide_gate` re-run -> **`BLOCKED`** + precision condition **`UNEVALUABLE`**, no fourth outcome. `architecture.md`'s *Gate-decision enforcement* amended by **strike** and a new *Corpus-pin provenance enforcement* rule registered. `INSTRUMENT_DISCLOSURE_VALIDATED`'s corpus name corrected (AC6) with `INSTRUMENT_STATUS` and every rendered surface asserted unmoved. `tests/test_built_distribution.py` 1200 -> 954 and `tests/test_instrument_disclosure.py` 1198 -> 893 split by cohesion FIRST; no size exemption added. Seven new guards (`TC-ArgusAgent-PRECISION-001-65`..`-71`), each with a non-vacuity floor and a **generated** adversarial variant; `-55`/`-61` amended to admit the third `BLOCKED` leg against strictly MORE evidence. Ledger: `DF-13-5-B` appended (RULING 3's recorded uncertainty). **Full suite after the story record was written: 1,639 passed / 0 failed / 0 skipped, exit 0** (baseline 1,632; +7 = the new guards). `mypy` clean over 87 source files; `bandit` 0 High / 0 Medium / 20 Low. Commits `d7886ba` (delta) + `91b95e3` (dogfood artifacts, separate). ⛔ **CI NOT ESTABLISHED** — every gate this run was local/Windows and nothing is pushed; `origin/master` is still `47b6dbe`. ⛔ **T2 not performed** by operator instruction, so AC9's clean-tree clause is NOT MET and is recorded on the artifact as `commit_sha_provenance: NOT ESTABLISHED`. `in-progress` -> `review`. |
| 2026-08-18 | Contexted on HEAD `63a0434` after Epic 14 rolled up to `done`. Four premises refuted by re-measurement and recorded in §0.2 (the `minions` checkout is off-pin), §0.3 (HEAD == pin does not imply pinned bytes), §0.4 (`UNEVALUABLE` is a condition verdict, not a gate outcome) and §0.5 (both producers refuse this story's expected outcome). Two carried-forward premises corrected in the favourable direction in §0.6. `backlog` → `ready-for-dev`. |
