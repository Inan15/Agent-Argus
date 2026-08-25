# Successor vacuity predicate `S1` — SPECIFICATION

| field | value |
|---|---|
| **Date** | **2026-08-25** |
| **Specified by** | **Engineering Lead** (Epic 17 / Story 17.2), recorded by the dev-story workflow |
| **Epic / Story** | Epic 17 — *Say What The Assertion Constrains* / Story 17.2 — *A different predicate, argued as one* |
| **Predicate as code** | ⛔ **DOES NOT EXIST YET. Story 17.3 builds it.** This document is prose that CITES; it declares nothing executable (`DN-17-2-1`). |
| **Criterion that will judge it** | `scripts/precision_preregistration.py`, frozen at `PREREGISTRATION_COMMIT_SHA` **before** this document was written |
| **Guards** | `tests/test_successor_predicate_specification.py` — `TC-ArgusAgent-PRECISION-001-142`..`-144` |
| **Adjudication protocol in force** | `PROTOCOL_VERSION` — **named**, not created, not amended |
| **Status of the externalization gate** | `BLOCKED`, and this document moves it nowhere (§5) |

> **⚠ EVERY VALUE IN THIS DOCUMENT IS CITED BY CONSTANT NAME OR BY ARTIFACT FIELD, NOT COPIED.**
> `AI-E9-7`: a prose copy of a pinned constant is a second source of truth that drifts silently,
> and this project has already paid for one (`DF-8-5-C`). Where a number lives in a committed
> artifact, the artifact and the field are named here and the reproduction command is given, so a
> reader gets the value from the same place the arithmetic does.
> `TC-ArgusAgent-PRECISION-001-142` re-derives every figure in §7's anchored table from those
> artifacts on every test run, and `-144` compares §2.4's quotation to the imported constant
> character for character. **A stale figure in this document is a RED test, not a reading error.**

> **⚠ THIS DOCUMENT IS DELIBERATELY NOT REGISTERED IN `_STATUS_DOCUMENTS`.**
> `TC-ArgusAgent-DOCS-001-22` closes in both directions — it fails on a globbed file nobody
> registered **and** on a registered name its globs cannot find. Its globs are
> `sprint-change-proposal-*.md` and `epic-*-retro-*.md`; this filename matches neither, so
> registering it would turn `-22` RED (`DN-17-1-8`, cited rather than re-derived). This document
> asserts a **specification**. It asserts no release status of any kind.

---

## 1. What this document is, and what order it was written in

`DF-16-7-B` recorded a rule and then stopped short of applying it:

> *"Promoting V2 would be a genuinely DIFFERENT predicate, not a loosening of fact (b) by clause
> removal, **and it must be argued as one**."*

**This document is that argument.** It is written in the only order that makes it worth anything:
**before the successor predicate exists**, and **immediately after the criterion that will judge
it was frozen** (Story 17.1, at `PREREGISTRATION_COMMIT_SHA`). Story 17.1 wrote down what *"good
enough"* means while the answer was still zero. Story 17.2 writes down **what the thing being
judged actually is**, while it still does not exist and cannot yet be tuned towards that standard.

⛔ **It is not an implementation, not a measurement, not a promotion, not a protocol amendment and
not a proposal to move anything.** §5 states each of those refusals in terms.

---

## 2. The predicate

### 2.1 `S1` — three conjuncts

The successor vacuity predicate is named **`S1`**. Over a flagged test span it is:

> **(a) REACHABILITY — UNCHANGED.** The span reaches a candidate SUT: at least one
> non-assertion, non-mock call on the span's edges. *This is the shipped fact (a),
> byte-for-byte* — `argus/detectors/vacuous_test.py::VacuousTestDetector._ast_corroborated`,
> the `len(self._sut_call_sites(span_edges)) >= 1` clause.
>
> **(b′) DISCARD — UNCHANGED.** `discarded_sut_calls >= 1`: at least one SUT call's result is
> thrown away. *This is fact (b)'s own arithmetic*, computed by
> `argus.detectors.provenance_scan.provenance_evidence` through the **FROZEN**
> `_CORROBORATION_ASSERTION_CALLEES` table, exactly as the shipped detector computes it.
>
> **(c′) NO ASSERTION CONSTRAINS AN SUT-DERIVED VALUE — NEW.** Every assertion in the span grades
> at the **weakest band** of Story 17.3's committed assertion-strength scale — *does not reference
> an SUT-derived value* — **including the degenerate case of a span with no assertions at all**.

⛔ **(c′) is the whole of the difference, and it is an ADDITION of evidence, not a subtraction of a
clause.** (a) and (b′) are the shipped facts unchanged. What `S1` does **not** carry is fact (b)'s
remaining two clauses — `consumed == 0` and `mock_referencing_assertions >= 1` — and §6 is the
argument that dropping them is not how `S1` reaches corroboration.

### 2.2 The threshold, stated so it cannot drift

`S1` requires **EVERY** assertion in the span to grade at the weakest band. A span carrying a
single *constrains only its existence or type* assertion is **NOT** corroborated by `S1`.

⛔ **Widening `S1` to admit that band is a SEPARATE, FUTURE ACT REQUIRING ITS OWN
PRE-REGISTRATION.** It is not a tuning knob, and this document pre-refuses it in the same
discipline and for the same reason Story 17.1 pre-registered its floors: a threshold moved once
the yield is in view is not a threshold, it is a description of the yield written in the grammar
of a standard.

### 2.3 The defect shape `S1` claims to detect

> **A test that runs the code under test, throws the result away, and does not meaningfully
> constrain what it returned.**

That is **one** definition of vacuity, and it is the same one **both stages** — the heuristic
stage and the AST-corroboration stage — would then be graded on. That single-definition property
is the architectural repair `DF-INV-VACUOUS-A` measured the need for: today the two stages select
populations that are **disjoint**, and no amount of tuning either one closes a gap that is a
definition mismatch rather than a threshold mismatch.

### 2.4 ⛔ `S1` is NOT a member of the `V0`..`V5` family, and `V6` was rejected

The `V0`..`V5` names are the **research harness's investigation vocabulary**
(`research/investigate-per-call-scoping.py`). Naming the successor `V6` was **rejected**
(`DN-17-2-2`): adopting a `V` number would imply `S1` had been measured by that harness. **It has
not been measured at all yet.**

`V2` and `V5` are **two disjoint bands of (c′)**, measured separately and by two different
instruments (§4). `V2` requires the span to assert nothing; `V5` requires it to assert something.
`S1` is **the predicate they are bands of** (`DN-17-2-3`) — not either one of them, and not their
sum published as a reach.

The `V2` band already ships as `argus.precision.silent_class.SILENT_CLASS_DEFINITION`, and that
constant already carries this document's core argument in its own committed words. ⛔ **It is
QUOTED here verbatim from the imported constant and is NOT paraphrased** (`AI-E9-7` /
`DF-8-5-C`); `TC-ArgusAgent-PRECISION-001-144` compares the quotation below to the imported
constant character for character.

**Reproduce:** `python -c "from argus.precision.silent_class import SILENT_CLASS_DEFINITION as D; print(D)"`

<!-- SILENT-CLASS-DEFINITION-QUOTATION:BEGIN -->
```text
V2 SILENT: the flagged test span reaches the system under test and DISCARDS at least one result (discarded_sut_calls >= 1, fact (b)'s own arithmetic, frozen table), AND the span asserts NOTHING AT ALL under the WIDE assertion vocabulary (no bare assert opens any line of the span, and no callee on any edge of the span is a registered assertion name). Measured at HEAD over the 1,032 recorded vacuous_test_heuristic findings: 36 members. NOTE for anyone who later proposes promoting this predicate: V2 is NOT a relaxation of shipped fact (b). V1 (drop the provably-dead mock-referencing clause) reaches 6, V3 (V1 AND silent) also reaches 6, so V1 is a SUBSET of V2 and 30 of the 36 lie outside V1 entirely — 30 members have at least one CONSUMED SUT call, one of them thirteen, which no clause removal from fact (b) can ever reach. Promoting V2 would be a genuinely DIFFERENT predicate, not a loosening.
```
<!-- SILENT-CLASS-DEFINITION-QUOTATION:END -->

---

## 3. The differential, in BOTH directions

The comparison that carries weight is **not** the one against the shipped predicate — that one is
one-sided and must be labelled as such — but the one against the **clause-removal lattice**: every
predicate reachable from fact (b) by deleting some subset of its clauses.

| comparison | `S1` admits, the other does not | the other admits, `S1` does not | source |
|---|---|---|---|
| vs `V0` — **the shipped predicate** | everything `S1` admits: `V0` is **empty** | **∅** — and `V0` is empty **by measurement** (zero of the walked population), not by construction | 2026-08-24 research §2; `silent-class-record.json` |
| vs `V1` — **drop the `mref` clause** | ⛔ **at least 30 findings, each carrying at least one CONSUMED SUT call** (one of them thirteen) — findings that `cons == 0` **affirmatively excludes**, and which **no removal of any subset of fact (b)'s clauses can ever reach while `cons == 0` stands** | **∅** — `V1 ⊂ V2 ⊆ (c′)`, measured: `V3` (`V1` ∧ silent) reaches the same count as `V1` | `SILENT_CLASS_DEFINITION`; `DF-16-7-B` |
| vs `V4` — **BOTH remaining clauses removed** | **∅** — `S1 ⊆ V4`, since both require `discarded_sut_calls >= 1` | ⛔ **the large majority of `V4`'s population**, refused by `S1` on **positive new evidence**: those spans *do* constrain the SUT result | 2026-08-24 research §5 |

⚠️ **The `V4` residual is deliberately written as *"the large majority"* and NOT as a figure.**
Subtracting the two known bands from `V4` would be arithmetic across two instruments at two HEADs
(§4). **Story 17.4 measures it.** This document records the direction and the reason, and hands
the number to 17.4 by name.

### 3.1 ⛔ THE ARGUMENT, IN ONE SENTENCE

> **`S1` is not on the clause-removal axis at all: it admits findings the lattice cannot reach at
> its tightest, and refuses findings the lattice admits at its loosest, and it does both on
> evidence fact (b) never computed.**

A loosening moves *along* the lattice — it grows the admitted set monotonically as clauses come
off, and every predicate it can reach is a subset of `V4`. `S1` is **not** ordered against `V1` by
inclusion in the direction a loosening would produce: it admits an entire class of findings
(consumed SUT calls present, span silent) that **every** `cons == 0`-preserving member of the
lattice excludes **by construction**, and it refuses a large majority of the class that the
lattice's loosest member admits. **A predicate that both admits what the lattice cannot and
refuses what the lattice does is a different predicate. That is the whole claim, and it is
checkable in both directions.**

### 3.2 Rejected successors, each with its reason

| rejected successor | why not |
|---|---|
| **`V1` — drop the mock clause** | It is a **clause removal**, which is exactly what Epic 17's charter forbids; it reaches a population an order of magnitude smaller than the `V2` band alone, drawn from two contributing members; and it leaves the two stages graded on **different** definitions, which is `DF-INV-VACUOUS-A` unfixed. |
| **`V2` alone — the silent class** | Already derived, published and **UNJUDGED** (§7.1). It is a **band** of (c′), not the predicate: it **cannot see a test that asserts loudly about nothing**. |
| **`V5` alone — asserts, none about the SUT** | The complementary band, and it **cannot see a span that asserts nothing at all**. Half a predicate — and the half whose figure is not a shipped measurement (§4). |
| **`V4` — `discarded_sut_calls >= 1` alone** | The research's own word for it is *"too loose"*. It is fact (b) with **both** remaining clauses removed and **no new evidence at all** — the textbook loosening. |
| **widen `_mock_bound_names` to all four dominant mock idioms** | ⛔ **Measured, and it is worth 0 → 1.** `DF-INV-VACUOUS-B` exists *"specifically so the gap is not rediscovered in six months and mistaken for the remedy"* — see §7.3. |
| **widen the FROZEN `_CORROBORATION_ASSERTION_CALLEES` table** | ⛔ Measured at **36 → 84**: *"48 false accusations is what the moat is worth here"* (`DF-16-7-B`). Widening that table moves tests **towards** an accusation, which is the direction `DN-14-2-1` split the two tables to prevent. |

⛔ **The two-table split is load-bearing for `S1` and 17.3 must not "unify" it.** (c′)'s *asserts
anything* question reads the **WIDE** vocabulary (`_ASSERTION_CALLEES` plus the `assert`-prefix
naming convention) because **narrowing** it would score an asserting test as silent — harm in the
**reversed** direction. (b′)'s arithmetic reads the **FROZEN** corroboration table because
**widening** that one moves a test towards an accusation. Two questions, opposite harm directions,
two tables. `argus.precision.silent_class.span_asserts_anything` already writes that reasoning out
in full.

---

## 4. ⛔ Instrument provenance — the two instruments, and the two HEADs

**A figure is cited with the instrument that produced it and the HEAD it was produced at, or it is
not written down.**

| figure | instrument | status |
|---|---|---|
| `V0`, `V1`, `V3`, `V4` reaches | the research harness, over the **shipped** `provenance_evidence` evidence | shipped-code measurement, 2026-08-24 |
| the `V2` band | **shipped** `argus.precision.silent_class`, recorded in `silent-class-record.json` | shipped-code measurement, at a **different HEAD** from the harness run |
| the `V5` band | ⛔ **the research script's OWN `ast` reasoning** | ⛔ **NOT a shipped measurement** |

The harness says so on the line, in its own docstring:

> *"V5 additionally needs SUT-derived name binding, which no shipped helper provides; it is
> computed with Python `ast` and is therefore THIS SCRIPT'S OWN reasoning, not the shipped
> predicate. Flagged as such in the output."*

Three consequences, all load-bearing:

1. **PROVISIONAL — adding the two band counts together is arithmetic across two instruments at two HEADs, and it is NOT a measurement of anything.** It is named here only so that nobody performs it silently later and publishes the result as `S1`'s reach.
2. ⛔ **THEREFORE `S1`'s REACH IS NOT STATED AS A NUMBER IN THIS DOCUMENT.** It is **Story 17.4's to measure**, once, against the criterion frozen before any of this existed. A story chartered to prevent a number being fitted to a standard may not publish a number that was never measured (`DN-17-2-4`).
3. **The `V5` band's resolver does not exist in `argus/`.** Story 17.3 must build it. That is the single largest piece of unbuilt work in Epic 17, and it is what `DF-16-7-A` means by *"per-call observation analysis needs real dataflow"*.

---

## 5. What this act does NOT do

- **5.1 — No measurement is run.** ⛔ **No detector is run over any corpus member. No corpus blob is materialised. No research harness is re-executed. No successor-predicate output is produced or committed.** Four reasons, recorded so the refusal is not re-litigated:
  1. **Story 17.4 is chartered to run it *once*** and to report *"the eligible population, its distribution across contributing members and rule classes."* That is 17.4's deliverable, by name, and a story that quietly ran it first would make 17.4's own ordering guard argue about a commit nobody planned.
  2. **A number produced here would arrive without an adjudication.** `DF-16-7-B`: *"until it is, no promotion proposal for this predicate carries evidence."* An unadjudicated reach figure is a headline, not evidence.
  3. **It would put successor-predicate output in the object database on an unplanned commit.** If successor output is ever committed it lands under a declared `SUCCESSOR_OUTPUT_PATHS` prefix **and nowhere else** — both declared prefixes are **absent on disk today**, verified, and that absence is what makes 17.4's ancestry guard provable.
  4. **`AI-E16-7` is UNFILLED** — protocol §4's External adjudicator tie-break. A measurement that reaches a borderline before the ladder has a third rung **STOPS**. That is 17.4's stated precondition, not a surprise for 17.4 to discover.

  ⚠️ **Considered and declined, with the pointer handed on:** the harness already collects a per-member breakdown for the `V5` band and prints it. That breakdown is one re-run away, and the re-run belongs to **17.4**.
- **5.2 — No corpus member is ratified.** The eligible member count is **unchanged**, before and after.
- **5.3 — No third-party source is fetched.** Nothing here reaches the network.
- **5.4 — No round is spent.** `DF-13-5-A` stays **OPEN and UNSPENT**: branch (a) is not executed, branch (b) is not declared, and its 2026-08-24 substantive trigger is **17.4's** to evaluate.
- **5.5 — No protocol row is added.** No `§5` condition is created and no terminal state is invented. `precision-validation-protocol.md` is **byte-unchanged** and `PROTOCOL_VERSION` is **named, not moved** (`DN-17-1-2`, cited rather than re-derived).
- **5.6 — ⛔ Story 17.1's criterion is NOT MOVED.** `scripts/precision_preregistration.py` is **byte-unchanged** by this story. `POPULATION_ID`, `PROTOCOL_VERSION`, the resolved ratio floor and `MAX_FALSE_ACCUSATION_EXPOSURE` are identical to their values at the pin, so `TC-ArgusAgent-PRECISION-001-140` stays green. ⛔ **This document does not propose that any of them be moved.** A specification written *after* the criterion may not move the criterion. The criterion was written while the answer was still zero and it stays there.
- **5.7 — Nothing published changes.** No FR is amended. **No finding becomes verdict-eligible.** The externalization gate stays `BLOCKED`, `protocol_cleared` stays `False`, the ≥80% keystone stays **NOT CLEARED**, and FR34's disclosure stands.
- **5.8 — ⛔ No `argus/` byte is written by this story.** The specification is a document, the guards are under `tests/`, and the ledger note is an artifact. `TC-ArgusAgent-PRECISION-001-144`'s second half proves it against the object database rather than promising it in prose.

---

## 6. `consumed == 0` IS NOT LOOSENED

This is the most misreadable requirement in the epic, so it is answered in **four registers**
rather than one sentence, plus the advisory clause.

### 6.1 Register one — NOT EDITED

`consumed == 0` is **not deleted from, not weakened in, not widened within and not re-scoped in**
any shipped module by this story. ⛔ **`argus/` is byte-unchanged**, and that is **proved**
against the object database by `TC-ArgusAgent-PRECISION-001-144`, not promised in prose. The
shipped `_ast_corroborated` still returns
`evidence.sut_result_is_discarded and evidence.mock_referencing_assertions >= 1`, over evidence
computed with the `consumed` term inside it, exactly as it did before this document existed.

### 6.2 Register two — NOT THE ROUTE TO CORROBORATION

Where `S1` admits a finding that carries **consumed** SUT calls, it does so on the strength of
**new positive evidence** — *every assertion in the span grades at the weakest band* — and **not**
on the absence of the clause. That is precisely what the epic's *"does not reach corroboration by
removing it"* means, and it is the entire difference between `S1` and `V4`:

- `V4` admits such a finding because it **stopped asking**. It has no evidence about the
  assertions at all.
- `S1` admits it because it **asked and got an answer**: it examined every assertion in the span
  and found that not one of them constrains a value derived from the SUT.

**Two predicates can admit the same finding and still be different acts.** One is the absence of a
refusal; the other is a positive finding. The distinction is not rhetorical — it is what makes
`S1` falsifiable where `V4` is merely permissive: `S1` has an observable that can be wrong about a
given span, and `V4` has none.

### 6.3 Register three — THE MOAT IS PRESERVED BY SHAPE, NOT BY THAT CLAUSE

Cross-cutting concern #6's moat is **two** things:

1. corroboration requires **positive** AST evidence, and
2. **failure to establish it REFUSES** (`NFR-R1`; the conservative default IS the moat).

**`S1` keeps both.** Story 17.3's acceptance restates the second verbatim: when (c′) cannot be
established over a span — an unparseable span, an unresolved edge set, a grading the scale cannot
assign — the answer is **NOT corroborated**, never *"corroborated by default"*.

What `S1` does **not** keep is `cons == 0` as a **whole-function-scope PROXY** for (c′). It was
never (c′); it was a cheap stand-in for it, evaluated over the whole test function so that one
observed call anywhere withheld corroboration from the entire test. `DF-INV-VACUOUS-A` measured
what that proxy selects: a population **disjoint** from the one stage 1 produces. A proxy that
selects a disjoint population is not a conservative version of the question — it is a **different
question**, and replacing it with the question itself is a strengthening of the evidence
requirement, not a weakening of the moat.

### 6.4 Register four — HONEST ABOUT DIRECTION

⛔ **`S1`'s population is LARGER than every clause-removal variant that keeps `cons == 0`.**

That is stated here without hedging because it is true and because it would be caught. `V1` and
`V3` — the only two lattice members that keep `cons == 0` and are not the empty shipped predicate
— reach the same small count, from **two** contributing members. The `V2` band alone is several
times that, and `S1` is strictly broader than the `V2` band.

⛔ **The epic's constraint is NOT that the population must be smaller.** It is that the predicate
must be **different** and must be **argued**, and §3 is that argument. **Yield and precision move
in opposite directions.** That is exactly why Story 17.1's criterion was frozen **first**, and why
**Story 17.4 — not 17.2, and not 17.3 — decides**, against a standard fixed at
`PREREGISTRATION_COMMIT_SHA` before any of this existed.

### 6.5 Advisory until an operator says otherwise

`S1` landing in Story 17.3 makes **nothing verdict-eligible**. Story 17.1's `CONSEQUENCE_MET` is
explicit that meeting the criterion *"promotes nothing"* and produces a **proposal**. ⛔ **17.3
must land `S1` such that no finding's `verdict_eligible` flips on it within Epic 17.**

---

## 7. What the evidence does and does not support

### 7.1 ⛔ The `V2` band is DERIVED, PUBLISHED and UNJUDGED

Every figure in the table below is re-derived from a committed artifact by
`TC-ArgusAgent-PRECISION-001-142` on every test run. **Authorities:**
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/silent-class-record.json` and
`argus.precision.silent_class.SILENT_CLASS_DEFINITION`.

**Reproduce the record fields:**
`python -c "import json,pathlib; d=json.loads(pathlib.Path('_bmad-output/design-artifacts/ArgusAgent/validation-corpus/silent-class-record.json').read_text(encoding='utf-8')); print(d['class_size'], d['population_walked'], d['counts'])"`

**Reproduce the definition's own figures:**
`python -c "from argus.precision.silent_class import SILENT_CLASS_DEFINITION as D; print(D)"`

<!-- CITED-FIGURES:BEGIN -->
| key | value | authority |
|---|---:|---|
| `record.class_size` | **36** | `silent-class-record.json` → `class_size` |
| `record.class_by_corpus_member.agent-smith` | **22** | `silent-class-record.json` → `class_by_corpus_member` |
| `record.class_by_corpus_member.minions` | **14** | `silent-class-record.json` → `class_by_corpus_member` |
| `record.files_by_corpus_member.agent-smith` | **10** | `silent-class-record.json` → `files_by_corpus_member` |
| `record.files_by_corpus_member.minions` | **9** | `silent-class-record.json` → `files_by_corpus_member` |
| `record.population_walked` | **1032** | `silent-class-record.json` → `population_walked` |
| `record.population_skipped` | **0** | `silent-class-record.json` → `population_skipped` |
| `record.counts.UNADJUDICATED` | **36** | `silent-class-record.json` → `counts` |
| `record.counts.TP` | **0** | `silent-class-record.json` → `counts` |
| `record.counts.FP` | **0** | `silent-class-record.json` → `counts` |
| `record.counts.BORDERLINE` | **0** | `silent-class-record.json` → `counts` |
| `record.exhaustiveness.adjudicated_count` | **0** | `silent-class-record.json` → `exhaustiveness` |
| `record.exhaustiveness.residual_count` | **36** | `silent-class-record.json` → `exhaustiveness` |
| `definition.population_walked` | **1032** | `SILENT_CLASS_DEFINITION` — *"over the 1,032 recorded … findings"* |
| `definition.class_size` | **36** | `SILENT_CLASS_DEFINITION` — *"36 members"* |
| `definition.v1_reach` | **6** | `SILENT_CLASS_DEFINITION` — *"V1 … reaches 6"* |
| `definition.v3_reach` | **6** | `SILENT_CLASS_DEFINITION` — *"V3 … also reaches 6"* |
| `definition.outside_v1` | **30** | `SILENT_CLASS_DEFINITION` — *"30 of the 36 lie outside V1 entirely"* |
| `definition.outside_v1_denominator` | **36** | `SILENT_CLASS_DEFINITION` — *"30 of the 36"* |
<!-- CITED-FIGURES:END -->

⛔ **THE TP/FP/BORDERLINE JUDGEMENT IS AN OPERATOR ACT AND NO AUTOMATED PRODUCER MAY TAKE IT**
(protocol §2). Every row of the `V2` band is `UNADJUDICATED`, and this story judges none of them.

⛔ **The DELIBERATE-SMOKE-TEST proportion — the idiom where *"does not raise"* IS the assertion —
remains NOT MEASURED.** `silent-class-record.json` refuses to report it as a proportion rather
than reporting it as zero, because a proportion over rows nobody read is not a measurement
(`AI-E11-1`). `DF-16-7-B`'s sentence is carried forward here unaltered:

> ***"until it is, no promotion proposal for this predicate carries evidence."***

⛔ **This document therefore does not build on the `V2` band as though it were a count of true
positives.** It is a count of **candidates**.

### 7.2 The breadth floor is NOT argued down

The two known bands of (c′) draw from **two** contributing members (`agent-smith` and `minions`),
against a resolved breadth floor of **three**. Story 17.1 **already pre-registered the
consequence** for exactly this situation: the outcome is `UNEVALUABLE` — *"NEVER a pass and NEVER
a failure, and never an invitation to argue the floor down"* — recorded before either candidate
was measured, precisely so that nobody has to argue it now.

⛔ **This document does not argue the floor down and does not propose a bigger bench.** It records
that the floor exists, that the pre-registered consequence applies, and that Story 17.4 evaluates
it.

### 7.3 Mock binding is NOT an input to `S1`

**The decision:** `S1` takes **no** mock-binding input. `_mock_bound_names`,
`mock_referencing_assertions` and the `mref` clause play **no part** in (a), (b′) or (c′).

**The evidence, all of it already committed or measured against the tree:**

1. The `mref >= 1` clause holds in **zero** of the walked population — measured **twice**, by two
   independent instruments (argus's own tree-sitter path and CPython `ast`).
2. An extended resolver covering **all four** dominant Python mock idioms moves that count
   **0 → 1** (`DF-INV-VACUOUS-B`, **measured**, not estimated).
3. (c′) needs an **SUT-derived name binding** resolver. That is a **different question** from mock
   binding, and it requires a resolver that does not exist in `argus/` today (§4).
4. ⛔ **Measured by an AST walk over every module of the `argus` package:
   `mock_referencing_assertions` has EXACTLY ONE DECISION SITE in the whole package** —
   `argus/detectors/vacuous_test.py`, inside `_ast_corroborated`'s return expression. Every other
   reference is a field declaration or a value carried for a reader. **One comparison. One branch.
   One predicate.** `TC-ArgusAgent-PRECISION-001-143` is what keeps that true.

`DF-INV-VACUOUS-B`'s own severity note says the entry *"becomes load-bearing only if a future
predicate depends on mock binding"*. **The successor specified here does not.** That is why the
entry's disposition is true **today** rather than a claim about the future.

⚠️ **The residual is recorded WITH the decision, not omitted from it.** Until Story 17.3 lands
`S1`, the shipped `mref >= 1` clause still stands and the resolver gap still exists — **latent and
harmless**, direction of error **under-claiming**, worth a measured **0 → 1**. This document does
**not** claim the code changed.

---

## 8. Hand-off — the constraints, each naming the story that owns it

### 8.1 To Story 17.3 — four constraints, learned here because here is where they are cheapest

1. ⛔ **`TC-ArgusAgent-PRECISION-001-127` FENCES THE DETECTOR PACKAGE AND `argus/precision/gate_*.py` OUT OF `argus/precision/silent_class.py`, TRANSITIVELY.** The `S1` scorer **cannot** be assembled by importing `silent_class` from the detector package: **one import line turns `-127` RED.** ⛔ **The correct response is NEVER to widen the fence** (`DF-8-5-B`). The shared helpers `silent_class` composes — `provenance_evidence`, `opens_bare_assert`, `is_assertion_callee`, `body_statement_count` — are **already on the detector side of the fence**, which is exactly why `silent_class` was able to compose them one-way. The guard's own words: *"A predicate in the detector package is a promotion waiting for someone to wire it up."*
2. ⛔ **`TC-ArgusAgent-DETECT-001-145` goes RED from the moment a new class defining `run() -> DetectorResult` is written, until its `if TYPE_CHECKING:` static conformance pin lands** inside the `argus` package. There are four such pins today and the fifth is 17.3's obligation. ⛔ **No Epic-17 guard may decide conformance by `isinstance`/`issubclass`** — `@runtime_checkable` is deliberately absent from the `Detector` Protocol and the check it used to offer was measured vacuous.
3. ⛔ **The `Evidence-partition:` trailer.** `gate_seal.DETECTOR_TUNING_PATHS` covers the detector package, so **a new module there DOES trigger the trailer obligation.** Story 18.1 lost a sha to a forgotten one. Story 17.2 stays out of those paths entirely; **17.3 cannot.**
4. ⛔ **The SUT-derived name binding resolver DOES NOT EXIST and 17.3 must build it** (§4). Three further costs come with any byte written inside the `argus` package, and none has moved since Story 17.1 counted them: dogfood-artifact currency (a regeneration commit of its own), the `--cov=argus --cov-fail-under=80` gate, and the blocking `mypy argus` / `bandit -r argus` gates.

### 8.2 To Story 17.4 — three pointers

1. **`SUCCESSOR_OUTPUT_PATHS`** — both declared prefixes are **absent on disk** today, verified. If successor output is ever committed it lands under one of them **and nowhere else**; output committed elsewhere makes 17.4's ordering guard unprovable against the object database, which is the one thing the epic's binding ordering constraint exists to prevent.
2. **The harness already collects a per-member breakdown for the `V5` band** and prints it under its *"per-member for the two live candidates"* heading. That breakdown is **one re-run away**, and the re-run is 17.4's. Story 17.2 declined it (§5.1).
3. **`AI-E16-7` is UNFILLED** — protocol §4's External adjudicator tie-break. It is **not** needed here, because nothing is adjudicated here. It **is** a stated precondition for 17.4: a measurement that reaches a borderline before the ladder has a third rung STOPS.

### 8.3 To Story 17.5

The re-homing and scheduling notes for `DF-INV-VACUOUS-A`, `DF-16-7-A`, `DF-16-7-B`,
`DF-14-1-A`, `DF-12-2-D` and `DF-12-3-A` belong to Story 17.5 by name. Story 17.2 wrote **exactly
one** ledger entry — the `DF-INV-VACUOUS-B` disposition of §7.3 — and left every other entry
untouched, because splitting a re-homing across two stories is how an append-only ledger acquires
two half-notes.

---

## 9. What this document does NOT fix

- `DF-INV-VACUOUS-A` — **OPEN.** The stage mismatch is what Epic 17 exists to fix, and specifying
  the replacement is not shipping it.
- `DF-16-7-A`, `DF-16-7-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A` — **OPEN and untouched.**
- `DF-13-5-A` — **OPEN and UNSPENT.**
- `DF-AUD-DETECT-C` (unscheduled) and `DF-AUD-DETECT-D` (scheduled on 17.3) — **untouched.**
- `AI-E16-7` — **UNFILLED.**
- The `V2` band's rows — **UNADJUDICATED**, and an operator act.
- The SUT-derived name binding resolver — **does not exist**, and is **17.3's** to build.
