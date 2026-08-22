---
baseline_commit: 1ecf618
---

# Story 16.3: A detector that finds nothing has not passed

Status: done

| | |
|---|---|
| **Epic** | 16 — Spend the Round Well — strengthen the gate, then measure once |
| **Story key** | `16-3-a-detector-that-finds-nothing-has-not-passed` |
| **Source** | [sprint-change-proposal-2026-08-20.md](../sprint-change-proposal-2026-08-20.md) §4.3(3), **✅ APPROVED by XAgent007 (Engineering Lead) 2026-08-20** · [epics.md](../epics.md) §Epic 16 (`epics.md:3019`), §Story 16.3 (`epics.md:3127`) |
| **Contexted on** | HEAD `1ecf618` (`docs(16-2): record the passing review — the seal story closes`), working tree **CLEAN**, **20 ahead of `origin/master`, 0 behind** |
| **Baseline gates (measured, this tree)** | full suite **1,667 collected · exit 0 · 0 failed · 0 skipped** with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` · `mypy argus` **Success, 91 source files** · `bandit -r argus --severity-level medium` **No issues identified** · `build_gate_decision.py --check` exit **0** · `build_adjudication_record.py --check` exit **0** |
| **Authorisation** | The 2026-08-20 approval unblocks **16.1, 16.2 and 16.3 only**, each deriving and recording its **own** constants. This is the **LAST of the three**. It does **not** unblock 16.4, does **not** authorise ratification (protocol §6 **R2**), a fetch, a stage, an adjudication, or spending `DF-13-5-A`'s ONE round. |
| **Ordering** | 🔒 **BINDING.** This story's commits must **precede** every commit containing Argus output over any bench member. The ancestry *guard* is 16.4's deliverable; this story's obligation is to **land first** and to **record its own landing shas** for 16.4 to cite — the Story 15.1 `CRITERIA_COMMIT_SHA` / Story 16.2 `SEAL_COMMIT_SHA` pattern, in two commits. |
| **Direction** | ⛔ **STRENGTHENING ONLY.** Every change here makes clearing **harder** — measurably: a population that clears today at **3 findings** is `BLOCKED` after it. It touches neither the ≥80% `Fraction`, `VALIDATION_SET_FLOOR_N`, the five ratified members, `MANIFEST_FIELDS`, nor the sealed partition. |

---

## Story

As the Argus maintainer,
I want **the gate to distinguish "accurate" from "silent"**,
So that a detector emitting three ultra-safe findings cannot score 100% and be called validated.

### What this story IS

**One new protocol §5 condition — the SEVENTH — that puts a floor under the size of the
verdict-eligible population the precision ratio is computed over.** `UNEVALUABLE` (Story 13.2) closed
the hole for an **empty** denominator and Story 13.5 made *"the corpus was read and nothing was
promoted"* expressible. Neither closes the **tiny** one. §0.1 proves by execution, on the shipped
code at HEAD, that a population of **exactly three findings, one per sealed member, all true
positives, returns `CLEARED`** with all six §5 conditions `MET` and an outcome sentence reading
*"Clearing authorises ATTESTED externalization."* That is the story title, reproduced as a
measurement rather than argued as a risk.

The floor is **derived from the ONE locked threshold** and not typed, it **composes** with 16.1's
breadth arm and 16.2's seal arm rather than replacing either, and it is **frozen before 16.4 runs**.

### What it is NOT

- **NOT a recall condition, and this is the delicate one.** Recall is diagnostic-only by the **OI1
  lock**. §0.4 establishes by measurement *where the number comes from*, which is the only thing
  that decides the question: a floor derived from **the threshold's own arithmetic** contains no
  `FN` term and makes no claim about undetected defects; a floor derived from **how much of the
  defect class the bench carries** is recall with an estimated denominator, and would be an
  operator escalation rather than something to paper over. This story takes the first and
  **forbids the second by a structural guard** (AC2.4).
- **NOT a replacement for the breadth condition.** AC3 makes *"quantity without breadth still
  fails"* a driven guard, not prose. Measured today: 40 findings from one sealed member is
  `BLOCKED` and must stay `BLOCKED`.
- **NOT a change to what is REPORTED.** Like the seal, the yield floor governs what may **GATE**.
  Every finding from every member stays recorded and stays disclosed.
- **NOT a narrowing.** `VALIDATION_SET_FLOOR_N` stays **5**, `eligible_member_count()` stays **5**,
  no member is dropped, re-weighted or made ineligible, `MANIFEST_FIELDS` stays **CLOSED at 9**, the
  partition table is byte-unchanged.
- **NOT a protocol re-version.** ⛔ **No `V1.4` row.** This is the **THIRD dated block under V1.3**.
  See §2.3 — a **locked operator decision of 2026-08-20**, not a preference.
- **NOT the rule-class arm.** `DF-16-1-A` stays **OPEN and unlanded**. Do not reopen it.
- **NOT a run, a ratification, a fetch, a stage or an adjudication.** All 16 candidate rows keep
  `eligible_for_n=False`; no detector executes over any repository, ratified or candidate;
  `DF-13-5-A`'s ONE round stays **UNSPENT**.
- **NOT 16.4, and not a step into it.** 16.4 opens by HALTING on the protocol §6 **R2** operator
  act. This story does not start it, prepare a ratification, or pre-select a member.
- **NOT an approval of anything.** [sprint-change-proposal-2026-08-20-amendment-A.md](../sprint-change-proposal-2026-08-20-amendment-A.md)
  is **registered and UNAPPROVED**; nothing in it is in scope, and this story does not approve,
  apply, cite as authority, or act on any part of it.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `1ecf618`

> ⛔ **Read this section before anything else.** Every prior worker in this epic found at least one
> stated premise FALSE by executing it. 16.1 escalated because its second arm was a shutdown;
> 16.2 found its "obvious" partition rule re-derivable and its `MANIFEST_FIELDS` premise wrong.
> Everything below was **run**, on this tree, at this HEAD. Re-derive it yourself; do not trust
> this text over your own execution.

### §0.1 ⛔ THE HOLE IS REAL — PROVED, not argued

Driven through the **shipped** `decide_gate` using `tests/test_gate_seal.py::mixed_population` and
`tests/test_gate_breadth.py::_decide`, over synthetic populations spread across **sealed** members:

| population size | outcome | precision | contributing | sealed contributing | breadth | seal |
|---|---|---|---|---|---|---|
| **3** | **`CLEARED`** | `1/1` | 3 | 3 | `True` | `True` |
| **4** | **`CLEARED`** | `1/1` | 3 | 3 | `True` | `True` |
| 5 | `CLEARED` | `1/1` | 3 | 3 | `True` | `True` |
| 6 | `CLEARED` | `1/1` | 3 | 3 | `True` | `True` |

At size 3 all six §5 conditions report `MET`:

```
[('precision-at-least-80-percent', 'MET'),
 ('clean-repo-blocking-false-positives-zero', 'MET'),
 ('corpus-floor-n-at-least-5', 'MET'),
 ('adjudication-run-recorded-cleared', 'MET'),
 ('denominator-breadth-contributing-members', 'MET'),
 ('gate-evidence-drawn-from-the-sealed-partition', 'MET')]
```

and the record's own outcome sentence reads *"all 6 protocol §5 conditions hold … Clearing
authorises ATTESTED externalization and NOTHING ELSE."*

**Three findings. One per sealed member. All correct. `CLEARED`.** That is exactly the epic's
sentence — *"a detector emitting three ultra-safe findings cannot score 100% and be called
validated"* — and it is currently false. This is the single premise the whole story rests on and it
is the first thing the dev must reproduce.

### §0.2 ⛔ THE FLOOR — DERIVED from the locked threshold, then CHECKED FOR VACUITY

**The derivation, and it is a property of the RATIO, not of the corpus.** The gate threshold is
`PRECISION_GATE_THRESHOLD = Fraction(4, 5)`. At a denominator `d`, the largest number of false
positives a population can carry and still clear is `max{ k : (d−k)/d ≥ 4/5 }`. Executed:

| `d` | FPs affordable at ≥ 80% | what "≥ 80%" actually demands |
|---|---|---|
| 1 | **0** | 100% |
| 2 | **0** | 100% |
| 3 | **0** | 100% |
| 4 | **0** | 100% |
| **5** | **1** | **80%** |
| 6 | 1 | 80% |

**Below a denominator of five, the ≥ 80% gate is silently a 100% gate.** A detector that emits three
findings and gets all three right has not cleared an 80% bar — it has cleared a bar it never faced,
and the record publishes the figure as though it had. The floor is the smallest denominator at
which the threshold means the thing it is written as.

**The GENERAL FORM, stated correctly the first time.** For a threshold `T = p/q` in lowest terms,
`(d−1)/d ≥ p/q ⟺ d ≥ q/(q−p)`, so the floor is **`ceil(q / (q − p))`** — verified against brute
force over eight thresholds, and it **diverges from `q`**: at `5/7` it is 4 and at `7/9` it is 5,
not 7 and 9.

> ⛔ **This is 16.1's correction, pre-applied.** 16.1's dev wrote the floor as
> `(VALIDATION_SET_FLOOR_N + 1) // 2` and *described* it as "a strict majority", then corrected
> itself under review: half-rounded-up is a strict majority **only at odd floors**. The identical
> trap is here — at `4/5` the floor equals `q` (5), and writing `threshold.denominator` would be a
> derivation describing something it does not compute, correct by coincidence at exactly the one
> threshold shipped. **Express it as `ceil(q / (q − p))`. Do not write `.denominator`.**

**AT THE SHIPPED THRESHOLD THE FLOOR IS 5.** Derived, executed, not typed.

**⚠️ A COINCIDENCE THAT MUST BE DISCLOSED, NOT LEANED ON.** `VALIDATION_SET_FLOOR_N` is also **5**.
The two are independent locked quantities that happen to be equal today: one counts members that
must EXIST, the other is the smallest denominator at which a ratio threshold is the threshold it
is written as. **Deriving the yield floor from `VALIDATION_SET_FLOOR_N` is REJECTED** (DN-16-3-2) —
it would fork the meaning of that floor a third time and would move the yield floor as a side
effect of a change to the corpus floor. The equality is stated in the derivation string so nobody
later "simplifies" one into the other.

**THE VACUITY CHECK, executed — and it rules out the obvious numbers.** A §5 condition that cannot
fail is not a threshold (this protocol's own words). Two separate vacuity tests:

1. **Against any admissible population.** `derive_concentration` **raises** `VacuousDisclosureError`
   on an empty population, so `adjudicated_population ≥ 1` for every population the decision
   accepts. **A yield floor of 1 could not fail** — 16.1's rule-class arm died on exactly this.
2. **Against the populations that can REACH the branch.** Measured: the smallest population that
   passes **both** breadth and seal is **3** (three sealed members, one finding each). So a yield
   floor of **2 or 3 can never fire** — every population it would block is already blocked by
   breadth or seal, and the dispatch branch would be an unreachable guard. **The floor must exceed
   3.** A floor of 4 fires on exactly one population size; **the derived floor of 5 fires on sizes 3
   and 4**, which is precisely the pair §0.1 measured as wrongly `CLEARED`.

The derivation and the vacuity floor agree, from two directions that share no reasoning. That
agreement is the reason this number is defensible rather than convenient.

### §0.3 ⛔ THE SHUTDOWN CHECK — and the honest answer, which is NOT the same shape as 16.1's or 16.2's

16.1 escalated because a rule-class floor of ≥2 was **unachievable by construction** (max
verdict-eligible rule classes = 1). 16.2 answered its equivalent by measurement (six sealed
candidates against a floor of three, slack three). **16.3's cannot be answered the same way, and
saying so is the point of this subsection.**

**What IS measured, at this HEAD:**

- **The corrected detector's verdict-eligible yield over the gating corpus is ZERO.** Counted
  directly out of `adjudication-set-13-5.json` (2026-08-18, post-Epic-14): **4,284 findings across
  all five ratified members — `verdict_eligible: 0`, `blocking: 0`.** Rule classes emitted:
  `orphan_code` 1,675 · `hardcoded_secret` 1,330 · `vacuous_test_heuristic` 1,032 ·
  `cross_partition` 231 · `traceability_not_establishable` 16. **Not one promotion.**
- `argus/detectors/vacuous_test.py` records the same thing from the other side, in its own comment:
  *"0 of 4,673 are corroborated at all after 14.1 — an EMPTY DENOMINATOR."*
- **The only population that ever exceeded a yield of five was produced by the REFUTED
  corroboration rule.** The 2026-08-16 run promoted **31** — under the pre-Epic-14 rule where
  `ast_corroborated` was equivalent to `mock_sites >= 1` in 1,835 of 1,836 flagged tests — and those
  31 adjudicated **0 TP / 26 FP / 5 BORDERLINE**. Yield ≥ 5 has been achieved exactly once, and it
  was achieved entirely by false positives.
- **The bench's defect-class content, per partition** (derived from the manifest, not typed):
  **sealed = 6 members / 431 co-occurrence files**; open = 10 members / 183; **pre-seal (the five
  ratified) = 1 co-occurrence file across 315 Python test files.**

**What CANNOT be measured, and why that is not a dodge.** The achievable yield over the sealed
partition is a function of what the corrected detector promotes over six repositories **nobody has
run it over, and nobody may run it over**: fetching third-party source is a §6 **R2** operator act
and no sealed member is staged. `scripts/candidate_selection.py` states in its own words that
co-occurrence is *"a TEXT PROXY … It cannot see whether the SUT result is DISCARDED versus
CONSUMED, which is what actually decides eligibility … a proxy for the DEFINITION, never for the
VERDICT."* **431 co-occurrence files is therefore not a yield prediction and may not be used as
one.**

**THE DISPOSITION — decided here, so it cannot surface mid-round in 16.4.**

> **This is NOT a shutdown, and the distinction is arithmetic rather than optimistic.** 16.1's test
> was *"`CLEARED` unreachable **by construction** with the shipped detector set"* — an impossibility
> independent of any corpus. A yield floor is not impossible by construction; it is **unmeasured**.
> Recording an unmeasured outcome as an impossible one would itself be the false-subject class this
> project files against, applied in the direction of not doing the work.
>
> **It is also NOT vacuous** — §0.2's second test proves the branch fires on real populations.
>
> **⚠️ THE PRE-ROUND DISCLOSURE, owed to the operator BEFORE the round is spent, not after.** On the
> only evidence that exists — a promotion rate of **0 of 4,284** over the ratified corpus — the
> likely 16.4 outcome is `BLOCKED` on **yield**, and `DF-13-5-A`'s ONE round is spent producing a
> finding about the detector rather than a precision figure. **That outcome is already
> pre-registered and is already the answer:** `DF-13-5-A`, answered 2026-08-17 before any number
> existed, says a round producing zero blocking findings takes option **(b)** — *"the FR34
> disclosure stands for V1.5 … the next attempt requires a materially better detector — NOT a
> bigger bench."* The epic header says the same thing in its own words: *"this epic may not clear
> the gate, and that is a permitted outcome."*
>
> **So the yield floor is not a new hurdle — it is `DF-13-5-A`'s own stopping rule made
> arithmetic.** The pre-registered rule already routes a **zero**-yield round to option (b). Without
> this condition, a round yielding **three** would route to `CLEARED` instead, which is a different
> destination for a materially identical result. Closing that gap is the whole of this story.

**⛔ THE ONE CONDITION UNDER WHICH THE DEV MUST ESCALATE RATHER THAN LAND (AC7.4).** If the dev's own
re-measurement finds that the achievable verdict-eligible yield is bounded above by something
**below the derived floor for a STRUCTURAL reason** — a cap in the pipeline, a budget ceiling, a
promotion path that admits at most *k* findings by construction — that is 16.1's shutdown shape and
it must be **escalated to the operator, not landed**. *Unmeasured* is not *impossible*; *bounded by
construction* is. Search for such a bound and record the result either way.

### §0.4 ⛔ IS A "YIELD FLOOR" RECALL BY ANOTHER NAME? — measured, and answered honestly

**The OI1 text, located exactly.** `precision-validation-protocol.md`:

- **line 313** — §5's table row: `| **Recall** (TP / (TP + FN)) | reported as a **diagnostic** (not
  gated in V1) — a low recall is a coverage signal, but the externalization gate is **precision**
  (the OI1 lock) | PrecisionResult.recall_ratio |` ← **THIS is the bullet AC2 names.**
- line 312 — §5's *"Recall over planted defects"* row, which is the **cartridge** corpus's FR20
  instrument. **Do not touch it.** It governs a different corpus and this condition does not.
- line 8 and §7 (lines 562–582) — the OI1 lock's own statement. §7 carries **no** recall bullet;
  its four invariants are N-locked-at-5, phased 3→5, precision-over-findings, and
  provisional-below-N=5. **§7 is not edited.** Confirmed by reading; do not "find" a §7 recall
  bullet that is not there.

**THE ANSWER, and it turns entirely on where the NUMBER comes from.**

`recall = TP / (TP + FN)`. It requires `FN` — the defects that exist and were missed. Over the
repository corpus `FN` is **unknowable**: protocol V1.1 records that *"a real repository has no
golden key"*, and `replay_harness` computes `recall_den = total_tp + total_fn` with `total_fn`
sourced from cartridge golden keys, so over the gating corpus it degenerates to `1/1` vacuously.

The condition this story lands has **no `FN` term, no estimate of one, and no reference to how many
defects the bench contains.** Its two inputs are (i) the count of verdict-eligible findings that
reached adjudication and (ii) the gate threshold. It says: *the denominator must be large enough
that the ≥80% threshold is a ≥80% threshold.* **That is a statement about the resolution of the
measurement that was taken — not a claim about what was missed.** It is precision-side arithmetic
end to end, and it does not re-open OI1.

**⛔ THE FRAMING THAT WOULD MAKE IT RECALL, named so it is refused rather than stumbled into.** The
epic's clause *"over a bench selected **because** it carries the defect class"* is the **motivation**
for why a low yield is informative. It is **not** a calibration input. Any derivation of the form
*"the sealed partition holds 431 co-occurrence files, so expect at least X"* estimates `FN` from a
text proxy and gates on it — **that IS recall by another name**, it re-opens OI1, and it is an
**operator escalation**, not a story decision. This story's floor comes from `PRECISION_GATE_THRESHOLD`
and from nowhere else, and **AC2.4 makes that mechanically checkable** rather than promised: the new
module must import no recall symbol and reference no `FN`/`recall`/co-occurrence term, asserted by
an **AST walk of the module's own names and imports** — the same structural technique
`gate_seal.py`'s purity assertion already uses.

**What the amendment to line 313 therefore says.** Not a softening and not a contradiction: recall
stays ungated and diagnostic, **and** the amendment states explicitly what the yield floor is and
is not, so no future reader can mistake a floor on the ratio's denominator for a quietly-landed
recall gate. **Struck-not-erased, by dated addition (§3.4).** That is a *strengthening of the lock's
legibility*.

### §0.5 ⛔ MODULE HEADROOM — measured with the ceiling guard's own `_physical_line_count` (`_CEILING = 1200`)

| file | lines | headroom | |
|---|---|---|---|
| **`tests/test_gate_decision.py`** | **1,191** | **9** | ⛔ **SPLIT-FIRST. THIS IS TASK 1.** |
| `tests/test_gate_seal.py` | 1,135 | 65 | tight — put this story's guards in a NEW module |
| `argus/precision/gate_decision.py` | 986 | 214 | fine (16.2 discharged `DF-16-1-B`) |
| `argus/precision/gate_seal.py` | 777 | 423 | not touched |
| `argus/precision/gate_breadth.py` | 436 | 764 | mirror lives in its test module |
| `argus/precision/gate_conditions.py` | 220 | 980 | `SECTION_5_CONDITIONS` grows by one id |
| `tests/corpus/_manifest.py` | 1,029 | 171 | **not touched** |
| `tests/test_gate_breadth.py` | 704 | 496 | the dispatch mirror lives here |
| `argus/detectors/vacuous_test.py` | 1,196 | **4** | ⛔ `DF-15-2-D` — **NOT in the write set. Do not touch.** |
| `tests/test_vacuous_density.py` | 1,159 | **41** | ⛔ `DF-15-2-E` — **NOT in the write set. Do not touch.** |

> ⛔ **`tests/test_gate_decision.py` HAS NINE LINES OF HEADROOM AND NO LEDGER ENTRY AT ALL.**
> 16.2's contexted story flagged it at 1,193 and said it "gets the same rule"; 16.2 split the
> *production* module (`DF-16-1-B`), left this one, and **filed no `DF-16-2-*` entry** — verified:
> `deferred-work.md` has zero `DF-16-2` ids and 16.2's review recorded *"zero defer findings."* So
> this trigger is real, is undocumented, and lands on this story.
>
> **The edit is UNAVOIDABLE, not a judgement call.** `expected_section_5_outcome` — §5's dispatch
> mirror, in `tests/test_gate_breadth.py` — is called from
> `tests/test_gate_decision.py::TC-…-001-55` (lines 339–451). 16.2 set the rule in that function's
> own docstring: *"Both terms are REQUIRED keyword arguments — no default — so every existing caller
> had to state what it believes … which is how 16.1's breadth clause came to be unreachable."* A
> seventh condition adds a seventh dispatch branch and therefore a third required term, so `-55`
> **must** be edited — with this project's comment discipline, inside nine lines. It does not fit,
> and `MAINT-001-04` forbids the exemption that would be tempting at that moment.
>
> **The boundary, measured by AST rather than suggested.** `test_gate_decision.py` is six shared
> fixtures (lines 123–236: `_record`, `_decision_payload`, `_judged`, `_clean_evidence`,
> `_read_proof`, `_decide`) followed by fourteen guards. There is a clean contiguous cohesion
> boundary at **`-59`..`-64`, lines 704–1056 (353 lines)** — the guards over the **ARTIFACT the
> decision publishes** (the concentration disclosure, the completion bound, locators-and-counts, the
> disclosure's persistence, no-threshold-moved, the unevaluable sentence) as against the guards over
> the **decision function itself** (`-53`..`-58`, `-69`, `-70`). That is the *test-side mirror of the
> split 16.2 already made in production* — `gate_conditions.py` (what a condition IS) /
> `gate_evidence.py` (what one is MEASURED FROM). **Confirm it with your own AST walk before moving
> a line**; do not take this table on trust. No function may be split across the boundary; the
> shared fixtures are **imported, not copied** (`tests/invocation_sources.py` precedent,
> `architecture.md:1045`); moved definitions are **byte-for-byte**.

### §0.6 What is already true and must NOT be re-done

- **§5 carries SIX conditions**, ids and order verified: `precision-at-least-80-percent`,
  `clean-repo-blocking-false-positives-zero`, `corpus-floor-n-at-least-5`,
  `adjudication-run-recorded-cleared`, `denominator-breadth-contributing-members`,
  `gate-evidence-drawn-from-the-sealed-partition`. **Append the seventh; never insert.**
- **`decide_gate` reads conditions BY ID** (`section_5_condition`), never by position. 16.1 repaired
  the positional read. **Do not re-introduce an index.**
- **`derive_concentration` is HOISTED** above the conditions tuple (16.1 / AC1.2), so threshold and
  disclosure read ONE set of counts. **The yield arm reads that SAME instance.**
- **The seal floor is RESOLVED from 16.1's, not forked** — `sealed_member_floor` calls
  `contributing_member_floor`. Both = **3**. The yield floor is a **different quantity** with a
  **different source**; it is not resolved from those two and must not be (DN-16-3-2).
- **`MANIFEST_FIELDS` is CLOSED at 9**; the partition is a derived `@property`. **Untouched here.**
- **The 40-hex pin check is hoisted** to every row (16.2). Untouched.
- **`SEAL_COMMIT_SHA` / `PRE_SEAL_MEMBER_IDS` / `SEALED_PARTITION_TABLE`** are frozen. Untouched.
- **`GATE_OUTCOMES` is closed at three; `CONDITION_VERDICTS` at four.** This story invents **no**
  terminal state and **no** verdict. The states it needs already exist.
- **The highest allocated verification id is `TC-ArgusAgent-PRECISION-001-94`.** This story starts
  at **`-95`**.

---

## §1 — WHY THIS STORY EXISTS

### §1.1 The three holes, and which one is left

| hole | closed by | state |
|---|---|---|
| the corpus was never read | 13.5 — `CorpusReadProof` | ✅ closed |
| the corpus was read and **nothing** was promoted | 13.5 — `BLOCKED` + `UNEVALUABLE` | ✅ closed |
| the ratio is drawn from **one repository** | 16.1 — breadth condition | ✅ closed |
| the evidence is one the tool was **tuned against** | 16.2 — seal condition | ✅ closed |
| **the corpus was read and a HANDFUL was promoted, and it scored 100%** | **16.3 — this story** | ⛔ **OPEN, and measured open in §0.1** |

### §1.2 The failure mode, stated concretely

Ratify three sealed members. Run. The detector — conservative by design, and `argus/detectors/vacuous_test.py`
says so in terms (*"the conservative default IS the moat"*) — promotes three findings, one per
member, each an unmistakable case. The named human adjudicates all three TP. `decide_gate` returns
`CLEARED` at precision `1/1`. The record says *"all 6 protocol §5 conditions hold"* and *"Clearing
authorises ATTESTED externalization."* Every guard is green, every disclosure is honest, every
number is derived — **and the claim being published is that a tool was validated at ≥80% precision
by three observations, against a bar it never faced.** §0.1 is that scenario, executed.

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **It does not make the detector yield more.** It makes a low yield say so. That work is
  `DF-16-1-A`'s neighbourhood and is out of the 2026-08-20 authorisation.
- **It does not close the population divergence** between the committed record's LIVE rows and the
  most recent adjudication set's EMITTED population — 16.1 named that as pre-existing and out of
  scope, and it stays out of scope. What is in scope is that the yield sentence, like breadth's,
  **names which population it counted** (AC1.5).
- **It does not gate on rule-class breadth.** `DF-16-1-A` stays unlanded.
- **It does not decide 16.4's outcome.** It decides what a given outcome is allowed to be called.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ `tests/test_gate_decision.py` IS AT 1,191 / 1,200 — SPLIT FIRST. THIS IS TASK 1.

See §0.5. Own commit, before any §5 change, on the `95819bc` (16.2) precedent: a restructuring
inside a story that also amends the protocol makes the one change a reviewer most needs to read
unreviewable. Prove it a pure restructuring — byte-identical moved definitions, collection count
unchanged, suite exit 0 — and record the before/after line counts with `_physical_line_count`.

### §2.2 A seventh §5 condition invalidates the committed gate-decision record

`GateDecision.__post_init__` raises unless the condition ids are **exactly** `SECTION_5_CONDITIONS`
in order. Appending the seventh id makes the committed `gate-decision-record.json` stale, so
`scripts/build_gate_decision.py` must be re-run and `--check` must exit 0 afterwards. Regenerating
it **executes no detector, stages no repository and touches no candidate** — 16.2 verified that and
recorded it; verify it again rather than inheriting the claim.

### §2.3 ⛔ THE AMENDMENT IS ADDITIVE, UNDER V1.3 — NO `V1.4` ROW

A **locked operator decision of 2026-08-20**, already applied twice. The committed
`adjudication-record.json` carries **31 human judgements** (26 FP / 5 BORDERLINE,
`XAgent007 (Engineering Lead)`, 2026-08-17) made under V1.3. A `V1.4` row would re-stamp
`protocol_version` across all 31 — *"a decision folded across an amendment is a re-interpretation of
judgements nobody re-made."* This amendment is additive to §5, touches no §4 rule, no golden-key
semantics and no TP/FP definition, so no judgement's meaning moves. `TC-ArgusAgent-PRECISION-001-45`
/ `-63` stay green and **`adjudication-record.json` is NOT regenerated.**

### §2.4 ⛔ EVERY GUARD THAT ASSERTS A §5 CONDITION COUNT OR POSITION

Enumerated by search at this HEAD; audit each and record one line per guard, none silent:

- `tests/test_gate_breadth.py:590` — `len(decision.conditions) == len(SECTION_5_CONDITIONS) == 6`
  ⛔ **a pinned literal `6`.** It goes to **7**. This is an *intended behaviour change* and must be
  annotated as 16.2 annotated it, not silently bumped.
- `tests/test_gate_breadth.py:595` — `SECTION_5_CONDITIONS[4] == BREADTH_CONDITION_ID`. Must stay
  true (append, never insert) and should be joined by the seal's and the yield's positions.
- `tests/test_gate_condition_lookup.py:161,254,278` — all **derived** from `len(SECTION_5_CONDITIONS)`;
  re-run to confirm, do not edit speculatively.
- `tests/test_gate_decision.py:314,465,489` — all **derived**. Confirm by execution.
- `tests/test_gate_decision.py::-55` (339–451) — ⛔ **must gain the third mirror term.** See §0.5.
- `argus/precision/gate_decision.py:299,314,318,932,955` — counts **derived** from
  `SECTION_5_CONDITIONS`; 16.1 made them so deliberately. Do not re-type any.

### §2.5 The dispatch order is load-bearing and its reason must be written down

16.1 put breadth **after** the empty-denominator branch (*an empty denominator is a stronger, more
specific claim than a narrow one*). 16.2 put the seal **after** breadth (*not enough evidence* is a
different claim from *evidence from the wrong place*, and a population failing both has the first
thing wrong with it). **The yield branch goes AFTER the seal branch**, and the reason is the same
shape and must be stated in the code: yield is a claim about **how much was found**; a population
that fails breadth or seal has something wrong with **where it came from**, which is prior. Reporting
yield first would tell a reader the detector was quiet when in fact the evidence was misprovenanced.

### §2.6 The published figures and the dogfood artifact currency move on any `argus/**` delta

Adding `argus/precision/gate_yield.py` changes the module count and LOC totals that
`tests/test_dogfood_artifact_currency.py` and the dogfood proof assert. Re-run
`scripts/regenerate_dogfood_artifacts.py` in its own declared step and confirm it executes no
detector over any corpus member.

---

## Acceptance Criteria

### AC1 — THE YIELD FLOOR IS A §5 CONDITION, DERIVED AND FROZEN BEFORE 16.4 RUNS

**Given** `UNEVALUABLE` closed the emit-nothing hole for an **empty** denominator, but §0.1 proves
by execution that a **tiny** one clears at 100%
**When** this story completes
**Then**:

1. **AC1.1** A new module `argus/precision/gate_yield.py` carries the constants, the pure predicate,
   and the `requirement` / `measured` / `what_would_close_it` / `unevaluable_reason` /
   `blocked_reason` / `closure_path` **sentences** — the `gate_breadth.py` / `gate_seal.py` shape
   exactly. `gate_decision.py` builds the `ConditionResult` (one direction only; `ConditionResult`
   lives there and the import would otherwise be circular).
2. **AC1.2** The floor is **DERIVED, never typed**, as `ceil(q / (q − p))` over
   `PRECISION_GATE_THRESHOLD = p/q` — *the smallest denominator at which the ≥80% threshold admits a
   single false positive, i.e. at which "80%" is not silently "100%"*. It is a **function of the
   threshold**, taking the threshold as an **argument** (never resolved at module level — `AR8` /
   `DF-9-2-A`). ⛔ **It is NOT written as `threshold.denominator`** (§0.2). The derivation string
   lives beside the function, states the general form, states that it equals `q` only when
   `q − p == 1`, and **discloses the coincidence with `VALIDATION_SET_FLOOR_N = 5` as a coincidence**.
3. **AC1.3** A typed failure (`VacuousYieldFloor`, an `AR10` `ValueError` subclass whose message says
   what a reader must do) is raised when the threshold admits no false positive at any denominator
   (`q − p ≤ 0`), because a floor derived from such a threshold is meaningless.
4. **AC1.4** The condition is **APPENDED** to `SECTION_5_CONDITIONS` as the **seventh** id — the six
   historical ids keep their historical positions — under a dated comment matching the fifth and
   sixth. Id: **`detector-yield-verdict-eligible-population-floor`**.
5. **AC1.5** The count is **READ from the SAME `ConcentrationDisclosure` instance** the decision
   publishes and the breadth and seal arms read (`adjudicated_population`) — **never recounted**,
   never derived from a second source. The `measured` sentence **names which population it counted**
   and carries breadth's divergence caveat verbatim in substance (*counted over the record's LIVE
   rows, NOT over the most recent adjudication set's emitted blocking population, which is a
   different and possibly empty set*).
6. **AC1.6** Below the floor, §5's **precision** condition is `UNEVALUABLE` with the counts that made
   it so and the outcome is `BLOCKED` with a countable closure path. The **yield condition's own
   verdict is `MET` or `FAILED`, never `UNEVALUABLE`** — it *was* counted. `GATE_OUTCOMES` stays
   closed at three, `CONDITION_VERDICTS` at four; **no terminal state and no verdict is invented.**
7. **AC1.7** The dispatch branch sits **after** the seal branch, with §2.5's reason written in the
   code.
8. **AC1.8** ⛔ **The number is frozen in a commit that precedes every commit containing Argus output
   over any bench member**, and this story's landing shas are recorded for 16.4 to cite. It is
   **not** reverse-engineered from any result: no run occurs in this story, and §4.3 of the change
   proposal — *"Numbers to be fixed by the story that implements each, derived and recorded — never
   typed"* — is satisfied by §0.2's executed derivation, which is reproduced in the Dev Agent Record.

> ⚖️ **A wording discrepancy, resolved and recorded.** Change proposal §4.3(3) says *"a run that
> promotes **nothing**"*; the epic's AC1 says *"fewer than **a stated number**"*. **The epic
> governs**: *promotes nothing* is already closed by Story 13.5's empty-emitted-population branch, so
> implementing §4.3's literal wording would produce a condition that cannot fire — the vacuity §0.2
> and this protocol both refuse. Recorded here rather than silently resolved.

### AC2 — ⛔ THE OI1 BULLET IS AMENDED EXPLICITLY, STRUCK-NOT-ERASED, AND NEVER CONTRADICTED IN PASSING

**Given** recall is diagnostic-only by the **OI1 lock**, and a yield floor is adjacent to recall
**Then**:

1. **AC2.1** The **§5 Recall row at `precision-validation-protocol.md:313`** — *"reported as a
   **diagnostic** (not gated in V1) … the externalization gate is **precision** (the OI1 lock)"* — is
   amended **EXPLICITLY**, by **dated addition, struck-not-erased (§3.4)**. The existing sentence is
   **not** rewritten and **not** softened: recall stays ungated and diagnostic. The addition states
   in terms **what the yield floor is** (a floor on the DENOMINATOR of the precision ratio, derived
   from the threshold) and **what it is not** (a floor on recall, on coverage, or on any estimate of
   `FN`), so no future reader can read a recall gate into it.
2. **AC2.2** ⛔ **Line 312's *"Recall over planted defects"* row is NOT touched** — it governs the
   cartridge corpus. ⛔ **§7 is NOT edited** — it carries no recall bullet (§0.4).
3. **AC2.3** The question *"is a yield stated over the gating corpus genuinely not recall, or is it
   recall by another name?"* is **answered in the Dev Agent Record with the measurement behind the
   answer**, not asserted. §0.4 gives the answer and the reasoning; the dev **re-derives it** and
   records agreement or disagreement.
4. **AC2.4** ⛔ **The answer is made MECHANICALLY CHECKABLE, not promised.** A guard asserts —
   **structurally, by an AST walk of `gate_yield.py`'s own imports and names**, on the
   `gate_seal.py` purity-assertion precedent — that the module imports **no** recall symbol
   (`recall`, `recall_ratio`, `recall_den`, `total_fn`, `PrecisionResult`), references **no** `FN`
   term, and references **no** co-occurrence / bench-content quantity. The guard is **driven to red**
   by an adversarial variant that adds such a reference.
5. **AC2.5** ⛔ **ESCALATION, not papering over.** If the dev's own analysis concludes the floor
   **cannot** be stated without an `FN` estimate — i.e. that it *is* recall by another name — the dev
   **HALTS and escalates to the operator** with options, rather than landing it. Re-opening OI1 is an
   operator act.

### AC3 — IT COMPOSES WITH 16.1's BREADTH CONDITION; IT DOES NOT REPLACE IT

**Given** the floor could be satisfied by noise
**Then**:

1. **AC3.1** Both conditions are evaluated independently and **both** appear in the condition set
   with their **own** verdicts. Neither is folded into the other; neither short-circuits the other.
2. **AC3.2** ⛔ **A driven guard, not prose: QUANTITY WITHOUT BREADTH STILL FAILS.** A generated
   population with **yield well above the floor** and **contributing members below the breadth
   floor** is asserted `BLOCKED`, with the breadth condition `FAILED` **and** the yield condition
   `MET` — proving the two are independent terms rather than one wearing the other's name.
   Measured today for the fixture: 40 findings from 1 sealed member → `BLOCKED`, `breadth=False`.
3. **AC3.3** ⛔ **And the converse, which is the story's actual subject: BREADTH WITHOUT QUANTITY
   FAILS TOO.** A generated population with **breadth and seal both MET** and **yield below the
   floor** (sizes **3** and **4**, the two §0.1 measured as wrongly `CLEARED`) is asserted `BLOCKED`
   on **yield**, with breadth `MET` and seal `MET`. This is the guard that would have caught §0.1.
4. **AC3.4** ⛔ **The yield term must be DECISIVE, not lockstep** — the `mixed_population` lesson from
   16.2 and the unreal-guard finding from 16.1's round 2. At least one guard must use a population
   where **breadth and seal are pinned TRUE while yield alone moves**, so a mutation deleting the
   yield clause entirely goes RED. Verify by executing that mutation.
5. **AC3.5** The floor is **not resolved from** `contributing_member_floor` / `sealed_member_floor`
   and does **not** fork them either: it is a different quantity from a different source, and
   `gate_yield.py` states why (DN-16-3-2). The two existing floors are **byte-unchanged** and still
   resolve through one function.

### AC4 — DRIVEN TO BOTH OUTCOMES BY EXECUTED MUTATION, EACH OBSERVED RED

**Given** this project shipped 4 of 35 unreal guards in Epic 14, and 16.1's round 2 shipped a
breadth clause that was unreachable
**Then**:

1. **AC4.1** The new condition is driven to **both** verdicts over **GENERATED** populations — one
   per yield count across the boundary — asserting **where the verdict flips**, not merely that it
   has two values (the `-82`..`-85` / `-87`..`-94` precedent).
2. **AC4.2** Every one of these mutations is **executed** on the shipped code and **observed RED**,
   with the tree restored byte-exact afterwards (`git status --porcelain` clean,
   `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` cleared):
   - the floor forked to a typed literal instead of derived
   - the floor stuck at the breadth/seal floor (3) — must go RED via AC3.3
   - the floor off-by-one in each direction
   - `holds` stuck `True`; `holds` stuck `False`
   - the yield dispatch branch **removed** (must be decisive — AC3.4)
   - the yield term removed from `_precision_condition`
   - the count read from a **second** source instead of the published disclosure
   - the seventh condition id dropped from `SECTION_5_CONDITIONS`
   - AC2.4's AST guard defeated by adding a recall reference
3. **AC4.3** Non-vacuity is asserted, not assumed: every generated population is asserted non-empty
   and asserted to actually straddle the boundary before anything is concluded from it.
4. **AC4.4** Guards live in a **NEW** `tests/test_gate_yield.py` (`tests/test_gate_seal.py` has 65
   lines of headroom — AC8's rule is *"do not shave a file to fit"*), verification ids
   **`TC-ArgusAgent-PRECISION-001-95`..**, registered in the module docstring in this project's
   established form.

### AC5 — IT MAKES CLEARING HARDER, AND TOUCHES NOTHING ELSE

**Given** §5 and Story 13.3 / AC5 forbid any change that makes clearing EASIER
**Then**:

1. **AC5.1** The story records **explicitly** that it makes clearing **harder**, with the executed
   evidence: a population that returns `CLEARED` today at size 3 and 4 returns `BLOCKED` after.
   Every population that cleared before either still clears or is now `BLOCKED`; **no** population
   that failed before can pass because of this condition.
2. **AC5.2** ⛔ **Byte-unchanged, verified by execution:** the ≥80% `Fraction`,
   `VALIDATION_SET_FLOOR_N = 5`, `eligible_member_count() == 5`, the five ratified members,
   `MANIFEST_FIELDS` (**closed at 9**), `GATE_OUTCOMES` (closed at three), `CONDITION_VERDICTS`
   (closed at four), `SEAL_COMMIT_SHA`, `PRE_SEAL_MEMBER_IDS`, `SEALED_PARTITION_TABLE`,
   `contributing_member_floor`, `sealed_member_floor`, and `adjudication-record.json`.
3. **AC5.3** No member is dropped, re-weighted, made ineligible, or re-partitioned. No
   `adjudication_caveat` is edited. **Every finding from every partition stays recorded and stays
   disclosed** — the yield floor governs what may **GATE**, never what is **REPORTED**.
4. **AC5.4** ⛔ **A CONDITION REQUIRES; A FILTER NARROWS.** If any design considered would *filter*
   the population (e.g. counting only sealed rows toward yield), test it by execution, record that
   it `raise`s or that it narrows, and **reject it on that ground** — 16.2's precedent.
5. **AC5.5** The amendment is **INERT ON THE LIVE TREE**, verified **at the producing seam** (16.2 /
   AC6.3): the committed record's population is 31, above the floor of 5, so the yield condition
   reads **`MET`** and the committed decision must still be `BLOCKED` **for the Story 13.5 reason**
   and not for a yield reason. ⛔ **Say so in the `measured` sentence**: 31 is the 2026-08-16
   population produced by the *refuted* pre-Epic-14 corroboration rule; the corrected detector's
   yield over the same corpus is **0**. A reader must not take `MET` as *"the detector currently
   yields 31."*

### AC6 — THE ARTIFACTS ARE CURRENT, ADDITIVE, AND THE ORDERING IS NOT BROKEN

1. **AC6.1** `precision-validation-protocol.md` §5 gains a **THIRD dated block under V1.3** — the
   conjunction sentence is **not** re-wrapped, the fifth and sixth blocks are **byte-unchanged**, and
   the new conjunct is **APPENDED**. ⛔ **No `V1.4` row** (§2.3). Plus AC2's amendment to line 313.
2. **AC6.2** `architecture.md`'s *"Gate-decision enforcement"* registration gains its dated
   `⚖️ AMENDED 2026-08-20 by Story 16.3` addition, **struck-never-erased**, on the 16.1 and 16.2
   precedent (`~~a set that is now SIX~~ **is now SEVEN**`). `TC-ArgusAgent-DOCS-001-77` stays green.
3. **AC6.3** `scripts/build_gate_decision.py` is re-run, `gate-decision-record.json` regenerated,
   `--check` exits 0. ⛔ **`adjudication-record.json` is NOT regenerated** and is asserted
   byte-unchanged. Regeneration is verified to execute **no** detector, stage **no** repository and
   touch **no** candidate.
4. **AC6.4** `scripts/regenerate_dogfood_artifacts.py` re-run in its own declared step; dogfood
   currency guards green.
5. **AC6.5** ⛔ **The BINDING ORDERING CONSTRAINT holds by git ancestry**: this story's commits touch
   **zero** candidate-output paths, and its landing shas are recorded in the story for 16.4's
   ancestry guard to cite — the two-commit pattern 15.1 and 16.2 both used, because a commit cannot
   cite itself.
6. **AC6.6** ⛔ **`DF-16-1-A`'s rule-class arm stays UNLANDED**; no rule-class threshold is written
   anywhere. `DF-13-5-A`'s ONE round stays **UNSPENT**. No ledger entry is disposed of.

### AC7 — SCOPE, ESCALATION AND WHAT MAY NOT BE TOUCHED

1. **AC7.1** ⛔ **NOT AUTHORISED and NOT TAKEN:** running Argus over any bench member; ratifying,
   fetching or staging any candidate; adjudicating any row; spending `DF-13-5-A`'s round; starting or
   preparing **16.4**; acting on, applying or citing as authority
   `sprint-change-proposal-2026-08-20-amendment-A.md` (**registered, UNAPPROVED**).
2. **AC7.2** ⛔ **Locked and not reopenable** (both operator decisions, 2026-08-20): `DF-16-1-A`'s
   rule-class arm stays unlanded; no protocol re-version and no `V1.4` row (the 31 human judgements
   of 2026-08-17 keep V1.3 provenance); set-relative partition rules were rejected on a recorded
   ground.
3. **AC7.3** ⛔ **Out of the write set entirely:** `argus/detectors/**` (in particular
   `vacuous_test.py`, 4 lines of headroom, `DF-15-2-D`), `tests/test_vacuous_density.py`
   (`DF-15-2-E`), `tests/corpus/_manifest.py`, `argus/precision/gate_seal.py`'s rule and table,
   `argus/precision/gate_breadth.py`'s floor.
4. **AC7.4** ⛔ **ESCALATE, do not land, if** (a) §0.3's structural-bound test finds the achievable
   yield capped below the floor **by construction**; or (b) AC2.5's condition fires; or (c) the
   derivation cannot be stated without reference to bench content. Each is an operator decision.
5. **AC7.5** Any deviation from the declared write set is **recorded with its rationale** in the Dev
   Agent Record (16.2 / AC8.5).

### AC8 — GATES AND HAND-OFF

1. **AC8.1** Full suite exit **0** with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` (baseline **1,667**
   collected; the new count is recorded and the delta explained); `mypy argus` Success;
   `bandit -r argus --severity-level medium` clean; module-size ceiling green with **no new
   `_EXEMPT_BY_DESIGN` entry**; both builders `--check` exit 0.
2. **AC8.2** NFR-M1 before/after recorded for **every** touched and adjacent module using
   `_physical_line_count`. ⛔ **No shaving a file to fit** — the remedy is a cohesion split.
3. **AC8.3** Local gates are **Windows-only**; CI runs an ubuntu matrix. If not pushed, record that
   **no CI run covers these shas** as an OPEN item rather than claiming green.
4. **AC8.4** A hand-off section for **16.4** stating: the landing shas, the seventh condition's id,
   the floor and its derivation, the yield condition's verdict on the committed population and why,
   and §0.3's pre-round disclosure **restated in countable terms** so the operator reads it before
   the round is spent.

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

| id | decision | rejected, and why |
|---|---|---|
| **DN-16-3-1** | **The yield floor is `ceil(q/(q−p))` over `PRECISION_GATE_THRESHOLD`** — the smallest denominator at which the ≥80% gate admits one false positive. **= 5.** | **`threshold.denominator`** — equal at `4/5` only because `q−p == 1`; diverges at `5/7` and `7/9` (executed). Writing it that way is a derivation describing something it does not compute — 16.1's *"strict majority"* correction, repeated. |
| **DN-16-3-2** | **NOT derived from `VALIDATION_SET_FLOOR_N`,** though both equal 5 today. The coincidence is **disclosed** in the derivation string. | Deriving from `N_floor` forks the meaning of the one locked floor a **third** time (`N` counts members that EXIST; breadth counts members that CONTRIBUTED; yield counts FINDINGS) and would move a §5 threshold as a side effect of a corpus-floor change. DN-3's one-floor rule is about **not forking one quantity**, not about collapsing three different ones into it. |
| **DN-16-3-3** | **The subject is `ConcentrationDisclosure.adjudicated_population`** — the SAME instance breadth and seal read. | **The most recent adjudication set's emitted count** — a fourth population, forked from the three the decision already reads, and the *entirely*-empty case it would cover is **already closed** by 13.5's branch. **`total_tp + total_fp`** — excludes BORDERLINE rows and would let the yield term disagree with breadth's over one population (26 vs 31 today); the exhaustiveness branch already blocks on residuals, upstream. |
| **DN-16-3-4** | **Own verdict is `MET`/`FAILED`, never `UNEVALUABLE`.** | `UNEVALUABLE` would tell a reader the population's size was **unknown**, when it was counted. 16.1's and 16.2's identical ruling. |
| **DN-16-3-5** | **Dispatch branch AFTER the seal branch.** | Before it: reports *"the detector was quiet"* over a population whose real defect is misprovenanced or too narrow evidence. §2.5. |
| **DN-16-3-6** | **A new `tests/test_gate_yield.py`; the `-55` mirror gains a third REQUIRED keyword term.** | Adding guards to `test_gate_seal.py` (65 headroom) or `test_gate_decision.py` (9) — shaving to fit is what `MAINT-001`'s remedy forbids. A **defaulted** mirror term is how 16.1's breadth clause became unreachable in `-55`. |
| **DN-16-3-7** | **OI1 amended at §5:313 only, by dated addition, struck-not-erased; §7 and line 312 untouched.** | Editing §7 — it carries no recall bullet, and inventing an amendment target is worse than none. Editing line 312 — it governs the **cartridge** corpus, which this condition does not touch. Saying nothing — AC2 forbids contradiction-in-passing. |

### Locked decisions this story CITES rather than reopens

- **`DF-16-1-A`'s rule-class arm stays unlanded** (XAgent007, 2026-08-20). Max verdict-eligible rule
  classes = 1; ≥2 is a shutdown, 1 is vacuous.
- **No protocol re-version, no `V1.4` row** (XAgent007, 2026-08-20).
- **Set-relative partition rules rejected** on the recorded ground that they re-derive to a different
  answer under partial ratification (16.2).
- **`DF-13-5-A`'s pre-registered rule** (XAgent007, 2026-08-17, before any number existed): ONE
  round; zero blocking findings **or** precision below 80% → option (b), FR34 disclosure stands for
  V1.5, *"a materially better detector — NOT a bigger bench."*
- **The 2026-08-20 approval** unblocks 16.1/16.2/16.3 only, authorises **making clearing harder and
  nothing else**, and is **not** approval to ratify, fetch, or spend the round.

### Open ledger entries bearing on this story — verified against `deferred-work.md` on disk, 2026-08-20

| id | bearing |
|---|---|
| `DF-16-1-A` | 🟠 open. **Do not land a rule-class floor.** The count stays disclosed and ungated. |
| `DF-16-1-B` | **Discharged by 16.2** (`95819bc`). `gate_decision.py` is at 986/1200. |
| `DF-15-2-D` | `argus/detectors/vacuous_test.py` at **1,196/1,200**. ⛔ Out of the write set. |
| `DF-15-2-E` | `tests/test_vacuous_density.py` at **1,159/1,200**. ⛔ Out of the write set. |
| `DF-13-5-A` | 🟠 open, ONE round **UNSPENT**. This story neither spends nor prepares it. |
| `DF-12-1-A/B/C` | the three `_EXEMPT_BY_DESIGN` entries; the registry may only **shrink**. |
| **none for `test_gate_decision.py`** | ⛔ **The 9-line trigger is UNFILED.** §0.5. If the split is taken, no entry is needed; if any residual remains, **file it**. |

#### ⛔ Writing rule — `TC-ArgusAgent-DOCS-001-78`

The story record and the ledger must agree. Every ledger edit is an **append** with a date and a
reason; historical text is **struck, never erased** (§3.4). 16.1's review caught an undisclosed
byte-level edit to a Story-15.x ledger entry — verify with
`git diff 1ecf618 -- .../deferred-work.md` that your change is a **pure append, zero deletions**.

### Guard vacuity — this project's signature defect, and the specific obligation here

Epic 14 shipped **4 of 35** unreal guards. 16.1 shipped a breadth clause that no fixture reached and
the review proved it by disabling both branches and observing GREEN. 16.2's `mixed_population` exists
because a sealed-only population makes breadth and seal move in **lockstep**, so deleting the seal
clause left everything green. **The identical trap is here in a third form**: over a population
built only from sealed members, breadth, seal **and** yield all rise together with the fixture size.
AC3.4 is the answer — pin breadth and seal TRUE and move yield alone — and it must be verified by
actually deleting the yield clause and watching it go red.

### Dependencies — none are added, and that is a requirement

No new third-party dependency. `argus` declares its own; a §5 condition is integer and `Fraction`
arithmetic over data the decision already carries. `math.ceil` over integers is exact; **`AR4`
forbids float arithmetic at a threshold boundary** — prefer integer ceiling division
(`-(-q // (q - p))`) or `Fraction`-exact arithmetic to `math.ceil` on a float quotient.

### Standing rules (non-negotiable)

- **`AR4`** exact arithmetic, never a float. **`AR7`** reuse, never fork. **`AR8`** pure — no I/O, no
  clock, no network, no repository-only module-level path (`DF-9-2-A`: this module ships in a wheel).
  **`AR10`** typed failures whose messages say what a reader must do. **`NFR-M1`** ≤1200 lines.
  **`NFR-S1`** no source or secret bytes — counts, ids and ratio strings only. **`NFR-P1`** byte
  stability: when the new term cannot change the answer, return the existing string **byte-for-byte**
  rather than re-rendering (`effective_precision_gate_status` precedent).
- **§3.4 evidence immutability**: amend by dated addition; strike, never erase.
- **Non-vacuity floor** (`AI-E11-1`): assert `> 0` rows before asserting anything about them.

### Files to touch — and the ones that must not move

**Task 1 (own commit) — the split:**
- `tests/test_gate_decision.py` — **UPDATE**, 1,191 → target ≈ 840
- `tests/test_gate_decision_artifact.py` (or a name the AST boundary justifies) — **NEW**

**Then, the story:**
- `argus/precision/gate_yield.py` — **NEW**
- `argus/precision/gate_conditions.py` — **UPDATE** (the seventh id, appended, dated comment)
- `argus/precision/gate_decision.py` — **UPDATE** (`assess_yield` call, `_yield_condition`, the
  dispatch branch, the yield term in `_precision_condition`, the `GateDecision.yield_` field, the
  `CLEARED` sentence)
- `argus/precision/gate_breadth.py` — **UPDATE**, minimal: `effective_precision_gate_status` must
  account for the yield term the same way it accounts for breadth, or an equivalent is added in
  `gate_yield.py` — **decide and record which**, and do not fork the status function (`AR7`)
- `tests/test_gate_yield.py` — **NEW** (`-95`..)
- `tests/test_gate_breadth.py` — **UPDATE** (the mirror's third required term; the pinned `6` → `7`
  with an annotation; the positional assertions extended)
- `tests/test_gate_decision.py` — **UPDATE** (`-55`'s third mirror term)
- `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` — **UPDATE** (§5 third
  dated block; the line-313 OI1 amendment)
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — **UPDATE** (registration addition)
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json` —
  **REGENERATED**
- dogfood artifacts — **REGENERATED**
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **APPEND ONLY**, if anything is filed

**⛔ MUST NOT MOVE:** `argus/detectors/**` · `tests/corpus/_manifest.py` · `argus/precision/gate_seal.py`'s
rule, table and floor · `argus/precision/gate_breadth.py`'s floor · `adjudication-record.json` ·
`argus/precision/replay_harness.py`'s threshold, fold and recall fields · every candidate-output path.

### Previous-story intelligence — 16.1 and 16.2 (both `done`, 2026-08-20)

**From 16.1** (`a20a0ef`, `7323f61`, `0733a33`, `6128466`): the breadth condition in a **separate
module** with `gate_decision` building the `ConditionResult`; `derive_concentration` **hoisted** so
one set of counts serves threshold and disclosure; the positional condition read **repaired** to
`section_5_condition`. Its two hard lessons: **(a)** it escalated rather than landing a shutdown
floor — the disposition is `DF-16-1-A`; **(b)** its round-2 breadth clause was **unreachable** and
its derivation prose **overstated** what the arithmetic computed, both caught by review. §0.2 and
AC3.4 exist because of exactly those two.

**From 16.2** (`95819bc`, `f89f028`, `fd20c32`, `9d7f8b5`, `3243a4a`): the seal condition resolving
its floor **through 16.1's function** rather than forking it; the **SPLIT-FIRST** discipline in its
own commit; the **second dated block under V1.3** with no `V1.4` row; `mixed_population` to make a
clause **decisive** rather than lockstep; the two-commit sha-recording pattern; and the up-front
countable consequence for 16.4 (*sealed ∩ ratified is empty — R2 must ratify ≥3 of six named
sealed candidates*). Its review was a **PASS with zero decision-needed, zero patch, zero defer**
findings — the bar this story is held to.

**From 15.1**: pick-before-you-look; `CRITERIA_COMMIT_SHA`; and the explicit refusal, recorded in
`candidate_selection.py`, to derive a bench floor from the gate arithmetic — *"that reasons backwards
from the number the round is supposed to measure."* ⛔ **That refusal does NOT bar DN-16-3-1, and the
distinction must be recorded:** 15.1 refused to shape the **CORPUS** to the number. This shapes the
minimum **RESOLUTION** below which the number is not the number it claims to be. The directions are
opposite — corpus-shopping moves a number to *produce* a result; this refuses a result of
insufficient resolution — and the discriminator is 16.1's *direction of travel* test, which this
passes: it makes clearing **strictly harder** and is the **highest** of the three floors in §5.

### Git intelligence

Last five commits are all 16.2's record and its landing. `1ecf618` closes 16.2. Working tree clean,
20 ahead of `origin/master`, 0 behind. **No commit in this range touches any candidate-output path**,
so the ordering constraint is intact entering this story and must be intact leaving it.

### References

- `epics.md:3019` (epic header, **binding ordering constraint** and **permitted-failure clause**),
  `epics.md:3127` (Story 16.3)
- `sprint-change-proposal-2026-08-20.md` §4.3(3), §6 (approval and its limits)
- `precision-validation-protocol.md` §5 (lines 305–511: the table, the conjunction, the fifth and
  sixth dated blocks), **line 313 (the OI1 recall bullet)**, §6 (R2), §7 (the OI1 lock)
- `architecture.md` — *Gate-decision enforcement* registration; `NFR-M1` (line 1124)
- `deferred-work.md` — `DF-13-5-A` (the pre-registered rule), `DF-16-1-A`, `DF-16-1-B`, `DF-15-2-D`,
  `DF-15-2-E`
- `validation-corpus/gate-decision-record.json`, `adjudication-set-13-5.json`
- stories `16-1-…`, `16-2-…`, `15-1-…`
- `argus/precision/gate_breadth.py`, `gate_seal.py`, `gate_conditions.py`, `gate_decision.py`
- `scripts/candidate_selection.py` (the co-occurrence proxy and its stated limits)

---

## Tasks & Subtasks

### ⛔ Task 0 — REPRODUCE §0 BEFORE WRITING ANY CODE

- [x] Re-run §0.1's execution and confirm size-3 and size-4 populations return **`CLEARED`**. If they
      do not, **STOP** — the story's premise is false and that is an escalation.
- [x] Re-derive §0.2's floor independently (brute force **and** closed form) and confirm **5**.
- [x] Re-count §0.3's `verdict_eligible: 0` out of `adjudication-set-13-5.json` yourself.
- [x] Re-measure §0.5's line counts with `_physical_line_count`.
- [x] Search for a **structural** cap on promoted findings (AC7.4). Record the result either way.
- [x] Record every re-derivation in the Dev Agent Record, including any disagreement with §0.

### ⛔ Task 1 — SPLIT `tests/test_gate_decision.py` FIRST, IN ITS OWN COMMIT

- [x] Confirm the cohesion boundary by your **own** AST walk; do not take §0.5's table on trust.
- [x] Move byte-for-byte; no function split across the boundary; shared fixtures **imported**.
- [x] Prove a pure restructuring: collection count unchanged, suite exit 0, line counts recorded.
- [x] Commit alone, before any §5 change.

### Task 2 — `argus/precision/gate_yield.py`

- [x] Constants, derivation string, `VacuousYieldFloor`, the pure floor function (AC1.2/AC1.3).
- [x] `YieldAssessment` + `assess_yield` reading the published disclosure (AC1.5), with the sentences.
- [x] `yield_blocked_reason` / `yield_closure_path`, including the *"NOT closable by amending the
      floor"* leg.
- [x] Module docstring: the derivation, the rejected alternatives, the OI1 analysis, the
      `VALIDATION_SET_FLOOR_N` coincidence, and the direction-of-travel statement.

### Task 3 — wire it into the decision

- [x] Append the id to `SECTION_5_CONDITIONS` with its dated comment (AC1.4).
- [x] `assess_yield` call beside `assess_breadth` / `assess_seal`, on the SAME concentration.
- [x] `_yield_condition`, the dispatch branch after the seal branch with §2.5's reason, the yield
      term in `_precision_condition`, the `GateDecision.yield_` field, the `CLEARED` sentence.
- [x] Decide and record the `effective_precision_gate_status` treatment (AR7 — do not fork).

### Task 4 — guards

- [x] `tests/test_gate_yield.py`, `-95`.. : generated populations across the boundary; AC3.2, AC3.3,
      AC3.4; AC2.4's AST guard driven red; non-vacuity assertions throughout.
- [x] `tests/test_gate_breadth.py`: third required mirror term; `6` → `7` **annotated**; positions.
- [x] `tests/test_gate_decision.py`: `-55`'s third mirror term.
- [x] Audit §2.4's guard list, one recorded line each, none silent.

### Task 5 — executed mutations (AC4.2)

- [x] Every mutation in AC4.2, each observed RED, tree restored byte-exact after each.

### Task 6 — protocol and architecture

- [x] §5's **third dated block under V1.3**; the fifth and sixth blocks byte-unchanged; **no `V1.4`**.
- [x] The **line-313 OI1 amendment**, struck-not-erased, saying what the floor is and is not.
- [x] `architecture.md` registration addition, struck-never-erased.

### Task 7 — artifacts, in this order

- [x] `build_gate_decision.py` regenerate → `--check` exit 0; `adjudication-record.json` asserted
      byte-unchanged; verify no detector ran and no candidate was touched.
- [x] `regenerate_dogfood_artifacts.py`; currency guards green.

### Task 8 — gates, record, hand-off

- [x] AC8.1's gates; AC8.2's line counts; AC8.3's CI honesty; AC8.4's hand-off to 16.4 including
      §0.3's pre-round disclosure in countable terms.
- [x] Record the landing shas in a second commit (a commit cannot cite itself).
- [x] Record deviations (AC7.5) and confirm nothing in AC7.1/AC7.2 was taken.

### Review Findings

**Adversarial code review, iteration 1, 2026-08-20 — VERDICT: PASS. Zero decision-needed, zero
patch, zero defer.** Every claim in the Dev Agent Record was independently re-derived by
execution rather than trusted from prose; nothing below is quoted from the story without having
been re-run.

- **Task 1 split, re-verified independently.** Re-extracted the six moved guards
  (`-59`..`-64`) from `1ecf618:tests/test_gate_decision.py` and from
  `HEAD:tests/test_gate_decision_artifact.py` by my own AST walk and compared them as raw source
  strings (not just sha256 prefixes): **byte-identical, all six**. The old file's 20 top-level
  defs partition exactly into the 14 that stayed and the 6 that moved, zero overlap. Full suite
  collection confirmed at **1,673** (see below) = the 1,667 baseline + the six new
  `-95`..`-100` guards, consistent with the split changing nothing.
- **The floor, re-derived and stress-tested.** `verdict_eligible_population_floor` reproduces
  the documented table exactly (`d=1..4 -> 0` FPs affordable, `d=5 -> 1`). Mutated
  `return -(-q // (q - p))` to `return q` (the `.denominator` trap, M5): **RED**
  (`test_...-95` fails exactly where `5/7`/`7/9` diverge). Mutated the floor to a hardcoded `3`
  (M2): **RED** across all six new guards. Ran the inverse the task specifically asked for:
  temporarily mutated `PRECISION_GATE_THRESHOLD` in `replay_harness.py` to `Fraction(5, 7)` and
  confirmed the floor **moves to 4** rather than staying pinned at 5 — the general form is real,
  not a disguised constant.
- **Sizes 3 and 4, measured at both ends myself.** Checked out `1ecf618`'s tree into the working
  directory (HEAD unmoved) and drove `decide_gate` directly: sizes 3–6 all `CLEARED` with all
  six §5 conditions `MET`, reproducing §0.1 exactly. Restored to `HEAD` and re-ran the same
  populations: sizes 3 and 4 now `BLOCKED` (`precision-at-least-80-percent: UNEVALUABLE`,
  yield condition `FAILED`), sizes 5/6 still `CLEARED`. Tree confirmed clean
  (`git status --porcelain` empty) after the round-trip.
- **AC3 composition, both directions, driven directly.** 40 findings from 1 sealed member:
  `BLOCKED`, breadth `FAILED`, yield `MET`, and the outcome reason names BREADTH not yield —
  confirmed the yield floor cannot rescue a breadth-rejected population. The converse (breadth
  and seal pinned `MET`, size below the floor) is `BLOCKED` on yield alone. Mutated the
  dispatch branch out of `decide_gate` entirely (M8/AC3.4 decisiveness): **RED** — the clause is
  decisive, not lockstep. Mutated `precision_evaluable`'s fourth conjunct away (M14): **RED**.
- **AC2 / OI1, verified structurally and by direct attack.** Read `gate_yield.py`'s full source:
  no `FN`, `recall`, or co-occurrence term anywhere in its arithmetic — its only inputs are the
  published `ConcentrationDisclosure.adjudicated_population` and the threshold. Drove the AC2.4
  AST guard red **against the actual production file**, not just the test's internal
  string-patched variants: inserted `total_fn = 431` into `verdict_eligible_population_floor`'s
  body and re-ran `-99` — **RED**, confirming M13 is real. Confirmed via `git diff` that the
  protocol amendment touches **only line 313** (the exact hunk boundaries are the two hunks in
  the whole file's diff): line 312 (cartridge Recall row) and §7 (no hunk touches it) are
  untouched, and the amendment is a byte-for-byte append after the pre-existing sentence
  (verified line-by-line against the base file: 1,408 lines both sides, exactly one line
  differs, and the new line `.startswith()` the old line's full text).
- **"Can only make clearing harder", checked for a counter-path.** Read the refactored
  `precision_gate_status` property line by line against the pre-16.3 version: the new
  `yield_`-check branch only fires when breadth and seal already hold and yield does not —
  every other path is provably identical to before. Mutated `holds = population >= floor` to
  `holds = True` (M6): **RED** across five of the six new guards, confirming the predicate is
  load-bearing in both directions.
- **Byte-unchanged surfaces, verified via `git diff`, not the story's assertion of it**:
  `argus/precision/gate_breadth.py`, `gate_seal.py`, `argus/detectors/**`,
  `tests/test_vacuous_density.py`, `tests/corpus/_manifest.py`, `replay_harness.py`, and
  `validation-corpus/adjudication-record.json` all show **zero diff** against `1ecf618`.
  `architecture.md`'s registration edit is a single-line diff that is a pure append (old line is
  a strict prefix of the new one); `deferred-work.md`'s `DF-16-3-A` entry is `+47/-0`.
- **The pre-round disclosure is re-derived, not asserted**: `test_...-100` reads
  `adjudication-set-13-5.json` and `adjudication-record.json` from disk and asserts the exact
  figures (`4284`, `0`/`0`, `31`, `0 TP / 26 FP / 5 BORDERLINE`) appear in
  `YIELD_PROVENANCE_DISCLOSURE`, plus a **live leg** that drives `assess_yield` directly (not
  through the committed JSON) on both sides of the floor — the M15 repair the dev found in its
  own round is present and does what it claims.
- **Gates, all reproduced independently**: full suite **1,673 passed, 0 failed, 0 skipped, exit
  0** (counted from the raw dot-stream: 1,673 `.` characters, zero `F`/`E`) with
  `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`,
  `__pycache__` cleared before the run; `mypy argus` — Success, 92 source files; `bandit -r argus
  --severity-level medium` — no issues; `tests/test_module_size_ceiling.py` — 6 passed, no new
  exemption; `scripts/build_gate_decision.py --check` and
  `scripts/build_adjudication_record.py --check` — both exit 0. Physical line counts
  (`wc -l`) match the claimed figures exactly for every touched/adjacent module
  (`gate_yield.py` 560, `gate_decision.py` 1084, `gate_conditions.py` 234, `test_gate_yield.py`
  839, `test_gate_decision.py` 865, `test_gate_decision_artifact.py` 451, `test_gate_breadth.py`
  747, `test_gate_seal.py` 1145, `test_release_preflight.py` 1000). `sprint-status.yaml`
  preserves all **107** `development_status` keys and all **7** STATUS DEFINITIONS blocks.
- **Deviations judged.** The two undeclared re-pins (`test_gate_breadth.py`,
  `test_gate_seal.py:818`, both `6 -> 7`) and the `README.md`/`CHANGELOG.md` module-count edits
  are disclosed exactly where they occur, are the minimum edit needed, and are consistent with
  the project's established annotate-rather-than-silently-bump convention. They will need
  re-pinning again at an eighth condition — a known, disclosed, accepted cost of the project's
  own "derive nothing that would hide an insertion" design, not a defect. `DN-16-3-8` (third
  sibling status renderer, `gate_breadth.py` left byte-unchanged) correctly follows the
  `DN-16-2-8` precedent within the story's authority; verified the renderer's predicate against
  `effective_precision_gate_status` / `sealed_precision_gate_status` line by line — same
  NFR-P1 byte-stability shape, no fork. `DF-16-3-A` is a pure append (`+47/-0`, confirmed via
  `git diff --numstat`) with a concrete, non-arithmetic trigger boundary; `gate_decision.py`'s
  own headroom (1,084/1,200, 116 lines) is comfortably above the project's own established
  ~20-line trigger margin, so the absence of a matching ledger entry for it is correct, not an
  omission.
- **No finding rises to Medium or High.** No unresolved `decision-needed` or `patch` item.
  Tree confirmed `git status --porcelain` clean and `git diff` empty at the end of this review's
  own mutation testing.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Claude Opus 5, 1M context), BMAD `dev-story` worker, 2026-08-20.

### Debug Log References

Every figure below was produced by an EXECUTED command on this tree. Nothing is quoted from
§0 without having been re-run first.

#### Task 0 — §0 RE-MEASURED. Four premises reproduced EXACTLY, one search added.

**§0.1 — the hole is REAL.** Driven through the SHIPPED `decide_gate` at `1ecf618` via
`tests/test_gate_seal.py::mixed_population` + `decide_over`, three sealed members:

| size | outcome | precision | population | contributing | sealed contributing | breadth | seal |
|---|---|---|---|---|---|---|---|
| **3** | **`CLEARED`** | `1/1` | 3 | 3 | 3 | `True` | `True` |
| **4** | **`CLEARED`** | `1/1` | 4 | 3 | 3 | `True` | `True` |
| 5 | `CLEARED` | `1/1` | 5 | 3 | 3 | `True` | `True` |
| 6 | `CLEARED` | `1/1` | 6 | 3 | 3 | `True` | `True` |

At size 3 all six conditions read `MET`, in the order §0.1 states, and the outcome sentence
reads *"all 6 protocol §5 conditions hold … Clearing authorises ATTESTED externalization and
NOTHING ELSE."* **§0.1 is reproduced without deviation.**

**§0.2 — the floor, re-derived TWICE, independently.** Brute force (smallest `d` with
`(d−1)/d >= T`) against the closed form `-(-q // (q - p))`, over eight thresholds:

| `T` | brute force | closed form | `q` | agree? |
|---|---|---|---|---|
| **4/5** | **5** | **5** | 5 | ✅ |
| 5/7 | **4** | **4** | 7 | ✅ — and **diverges from `q`** |
| 7/9 | **5** | **5** | 9 | ✅ — and **diverges from `q`** |
| 1/2 | 2 | 2 | 2 | ✅ |
| 2/3 | 3 | 3 | 3 | ✅ |
| 3/4 | 4 | 4 | 4 | ✅ |
| 9/10 | 10 | 10 | 10 | ✅ |
| 99/100 | 100 | 100 | 100 | ✅ |

FPs affordable at `>= 4/5`: `d=1 → 0`, `d=2 → 0`, `d=3 → 0`, `d=4 → 0`, **`d=5 → 1`**,
`d=6 → 1`. **The floor is 5, derived, not typed. §0.2 is reproduced without deviation, and
the `.denominator` trap is confirmed real at two of the eight thresholds.**

**§0.3 — `verdict_eligible: 0`, re-counted myself** out of
`validation-corpus/adjudication-set-13-5.json`: **5 members, 4,284 findings, `verdict_eligible`
0, `blocking` 0**, rule classes `orphan_code` 1,675 · `hardcoded_secret` 1,330 ·
`vacuous_test_heuristic` 1,032 · `cross_partition` 231 · `traceability_not_establishable` 16.
**Every figure matches §0.3 exactly.**

**§0.5 — line counts re-measured with `_physical_line_count` / `_CEILING = 1200`.** All ten
rows of §0.5's table reproduced to the line: `tests/test_gate_decision.py` **1,191 (headroom
9)**, `tests/test_gate_seal.py` 1,135, `gate_decision.py` 986, `gate_seal.py` 777,
`gate_breadth.py` 436, `gate_conditions.py` 220, `tests/corpus/_manifest.py` 1,029,
`tests/test_gate_breadth.py` 704, `vacuous_test.py` 1,196, `tests/test_vacuous_density.py`
1,159. **No deviation.**

**⛔ AC7.4(a) — THE STRUCTURAL-CAP SEARCH, run, and the result recorded either way: NONE
FOUND.** `verdict_eligible == (depth_supported is not None)`
(`replay_harness.finding_match_key`). The only production site passing a non-`None` depth is
`argus/detectors/vacuous_test.py:1067`, and it sits **inside `for definition in
sorted(test_defs)`** — one finding per flagged test function, with `depth` governed by that
function's own `corroborated` boolean. There is **no slice, no `[:k]`, no limit, no early
break** anywhere on that path. The one budget ceiling in the tree
(`argus/cost/budget_governor.py`, `REASON_BUDGET_EXHAUSTED`) caps the **deep/LLM admission**
path, which supplies no depth and is not the verdict-eligibility path; `prosecutor._promote`
is gated on `sign_offs` and the single production `prosecute()` call site supplies none.
**So the achievable yield is UNMEASURED, not BOUNDED BY CONSTRUCTION — 16.1's shutdown shape
does not apply and AC7.4(a) does NOT fire.** I agree with §0.3's disposition, on my own
measurement.

#### Task 1 — the split, proved a PURE restructuring

The §0.5 boundary was confirmed by **my own AST walk before a line moved**, not taken on
trust: the walk enumerated all 20 module-level definitions with their line spans and, per
guard, the module-level names each one reads. `-59`..`-64` are contiguous at **704–1056 (353
lines)** and depend only on `_record`, `_decision_payload`, `_judged`, `_decide`,
`_ADJUDICATOR`, `_REPO_ROOT`, `_DECISION_PATH`, `_PROTOCOL_PATH` — every one of which stayed
put and is now **IMPORTED**. §0.5's table is confirmed.

Purity proved rather than asserted:

- all six moved definitions **BYTE-IDENTICAL** to their originals, compared as AST-extracted
  source slices with sha256 (`cc060851b733`, `44f42807397b`, `6c04c79fdf57`, `42e4f546c1c1`,
  `7c1ed57c4846`, `bb83a546a6fe`);
- **no function split across the boundary**: the origin's 14 remaining definitions and the new
  module's 6 partition the original 20 exactly, with empty intersection, and **none of the 14
  that stayed changed a byte**;
- **collection count 1,667 → 1,667, unchanged**; the two modules collect 8 + 6 = the same 14;
- full suite exit **0** after the move.

Landed **alone**, in `01a2f48`, before any §5 change.

#### Task 5 — AC4.2's mutations: **15 EXECUTED, 15 OBSERVED RED**

Run with `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider` and **every `__pycache__` cleared
before each run** (a stale-bytecode RED is a false RED — 16.2's dev hit exactly that). Each
mutation was applied to the SHIPPED file as **bytes**, run, then restored from the original
bytes, with `git status --porcelain` asserted empty after **every single one**.

| # | mutation | file | exit | guards reddened |
|---|---|---|---|---|
| M1 | floor FORKED to a typed literal (`return 5`) | `gate_yield.py` | 1 **RED** | `-95` |
| M2 | floor STUCK at the breadth/seal floor (`return 3`) | `gate_yield.py` | 1 **RED** | `-95` `-96` `-97` `-98` `-99` `-100` |
| M3 | floor OFF BY ONE, low | `gate_yield.py` | 1 **RED** | `-95` `-96` `-97` `-98` `-99` `-100` |
| M4 | floor OFF BY ONE, high | `gate_yield.py` | 1 **RED** | `-95` `-96` |
| M5 | floor spelled `threshold.denominator` (`return q`) | `gate_yield.py` | 1 **RED** | `-95` |
| M6 | `holds` STUCK `True` | `gate_yield.py` | 1 **RED** | `-96` `-97` `-98` `-99` `-100` |
| M7 | `holds` STUCK `False` | `gate_yield.py` | 1 **RED** | `-54` `-58` `-83` `-84` `-86` `-90` `-96` `-97` `-98` `-99` `-100` |
| M8 | **the yield DISPATCH BRANCH removed** (AC3.4 decisiveness) | `gate_decision.py` | 1 **RED** | `-97` `-98` |
| M9 | yield term removed from `_precision_condition` | `gate_decision.py` | 1 **RED** | `-97` |
| M10 | count read from a SECOND source, not the disclosure | `gate_yield.py` | 1 **RED** | `-54` `-83` `-84` `-86` `-96` `-97` `-98` `-99` `-100` |
| M11 | seventh id DROPPED from `SECTION_5_CONDITIONS` | `gate_conditions.py` | 1 **RED** | 18 guards incl. `-80` `-81` |
| M12 | yield `ConditionResult` never appended | `gate_decision.py` | 1 **RED** | 17 guards incl. `-80` `-81` |
| M13 | **AC2.4's AST guard DEFEATED** by an `FN` reference | `gate_yield.py` | 1 **RED** | `-99` |
| M14 | `precision_evaluable` conjunct dropped | `gate_decision.py` | 1 **RED** | `-97` |
| M15 | pre-round disclosure dropped from the measured sentence | `gate_yield.py` | 1 **RED** | `-100` |

**M5 is the one that matters most for AC1.2** — `return q` is *correct at the shipped 4/5* and
still goes RED, because `-95` drives the derivation over a family containing `5/7` and `7/9`
and asserts the family CONTAINS at least two thresholds where the two spellings differ. The
`.denominator` mistake cannot be made silently.

**M8 is AC3.4's** — deleting the dispatch branch entirely reddens `-97` and `-98` over the
fixture where **breadth and the seal are pinned TRUE and only the population size moves**. The
clause is decisive, not lockstep.

⛔ **M15 CAUGHT ONE OF MY OWN GUARDS BEING UNREAL, and it is recorded rather than quietly
fixed.** On the first run M15 came back **exit 0 — GREEN**. Every assertion about
`YIELD_PROVENANCE_DISCLOSURE` lived in `-100` and every one read the **committed**
`gate-decision-record.json`, which a mutation run does not regenerate: the guard was measuring
a JSON file, not the code that writes it. It would have caught a stale artifact and never a
`measured` sentence that quietly stopped qualifying itself — this project's signature defect,
arrived at from the inside. `-100` gained a **LIVE leg** driving both branches of the sentence
through the shipped `assess_yield` with a non-vacuity assertion that both were observed
(`a0c74ae`), and the **whole 15-mutation set was re-run from scratch afterwards**: all 15 RED.

**Tree after the run**: `git status --porcelain` = `''`, `git diff` = `''`, HEAD unmoved at
`a0c74ae74dc1dff96264f7c1052b2596f94b7d31`.

#### AC5.4 — the FILTER designs, tested BY EXECUTION and rejected on the measured ground

- **"count only sealed rows toward yield"** — over a mixed population (3 sealed + 2 pre-seal
  members, 8 findings) it **narrows the denominator from 8 to 6**. *A CONDITION REQUIRES; A
  FILTER NARROWS* — narrowing the population the ratio is computed over MOVES THE RATIO, which
  protocol §5 and Story 13.3 / AC5 forbid outright. **REJECTED.** It is also redundant: §5's
  SEAL condition already requires sealed provenance, so this is the seal arm re-implemented as
  a denominator edit.
- **`total_tp + total_fp` as the subject** — over the committed population the two **disagree
  by 5**: `adjudicated_population` = 31, `total_tp + total_fp` = 26 (TP 0 / FP 26 /
  BORDERLINE 5). The yield term would disagree with the breadth and seal terms about the size
  of the SAME population, and the residual case it would cover is already blocked UPSTREAM by
  the exhaustiveness branch. **REJECTED (DN-16-3-3).**
- **derive the floor from `VALIDATION_SET_FLOOR_N`** — both are **5 today**, which is the trap.
  **REJECTED (DN-16-3-2)**, and the coincidence is DISCLOSED inside `YIELD_FLOOR_DERIVATION` so
  nobody later simplifies one into the other.

#### AC5.1 — HARDER, never easier, verified by execution

| size | before (`1ecf618`) | after | breadth | seal | yield |
|---|---|---|---|---|---|
| **3** | **`CLEARED`** | **`BLOCKED`** | `MET` | `MET` | **`FAILED`** |
| **4** | **`CLEARED`** | **`BLOCKED`** | `MET` | `MET` | **`FAILED`** |
| 5 | `CLEARED` | `CLEARED` | `MET` | `MET` | `MET` |
| 6 | `CLEARED` | `CLEARED` | `MET` | `MET` | `MET` |
| 7 | `CLEARED` | `CLEARED` | `MET` | `MET` | `MET` |
| 40 from **1** member | `BLOCKED` | `BLOCKED` | **`FAILED`** | — | `MET` |

The condition fires on **exactly the sizes 3 and 4** — the pair §0.1 measured as wrongly
`CLEARED` — and on nothing else. `-98` sweeps the family and asserts that **every** population
that clears after the amendment has `yield MET`, so no path can make clearing easier.

#### §2.4's guard audit — one line per guard, none silent

| site | disposition |
|---|---|
| `tests/test_gate_breadth.py:590` — pinned literal `6` | **`6` → `7`, ANNOTATED** as an intended behaviour change, and joined by `SECTION_5_CONDITIONS[5] == SEAL_CONDITION_ID` and `[6] == YIELD_CONDITION_ID` so an INSERTION reddens it even at the right count |
| `tests/test_gate_breadth.py:595` — `[4] == BREADTH_CONDITION_ID` | **still true, unedited.** Appended, never inserted |
| `tests/test_gate_condition_lookup.py:161,254,278` | **derived** from `len(SECTION_5_CONDITIONS)` — re-run, green, **not edited** |
| `tests/test_gate_decision.py:314,465,489` | **derived** — re-run, green, **not edited**. Now at `:324`/`:475`/`:494` after the Task-1 split; the assertions themselves are byte-unchanged |
| `tests/test_gate_decision.py::-55` (339–451) | **gained the THIRD mirror term**, counted from the record's own live rows and never read out of `assess_yield`, with a non-vacuity floor on that count |
| `argus/precision/gate_decision.py:299,314,318,932,955` | **derived** from `SECTION_5_CONDITIONS` — **not one re-typed**; verified by reading each site |
| ⛔ **`tests/test_gate_seal.py:818` — a SECOND pinned literal `6`, NOT in §2.4's enumeration** | **FOUND BY EXECUTION**, not by the story. `6` → `7`, annotated on the same terms and joined by the seal's positional assertion. Recorded here as a deviation rather than fixed silently (AC7.5) |
| ⛔ `tests/test_release_preflight.py:_MODULES_NAMING_THE_TEST_TREE_IMPORT` | **also not enumerated, also found by execution.** `gate_yield.py` joins the registry with a dated comment saying why — that registry exists to force someone to say it out loud |

#### AC2.3 — is a yield floor recall by another name? **RE-DERIVED, and I AGREE with §0.4**

`recall = TP / (TP + FN)` requires `FN`. Over the repository corpus `FN` is unknowable —
protocol V1.1 records *"a real repository has no golden key"* and `replay_harness` sources its
`FN` term from cartridge golden keys, so over the gating corpus recall degenerates to `1/1`
vacuously. I checked the shipped condition's inputs by reading its call site rather than by
reasoning about it: `assess_yield` takes exactly **(i)** a `ConcentrationDisclosure` and
**(ii)** a `Fraction`. `AdjudicatedPrecision` — the only other object in reach — carries **no
`FN` and no recall field** (checked field by field). There is no term in the derivation that
could carry a claim about what was missed, because there is no input that could supply one.

**The distinction is entirely about WHERE THE NUMBER COMES FROM, and §0.4 has it right.** A
floor from the threshold's own arithmetic is a statement about the RESOLUTION of the
measurement taken. A floor from *"the sealed partition holds 431 co-occurrence files, so expect
at least X"* estimates `FN` from a text proxy and gates on it — that IS recall, it re-opens
OI1, and it is an operator escalation. **AC2.5 does NOT fire**: the floor is stated without any
`FN` estimate, so there is nothing to escalate. **AC7.4(c) does not fire either** — the
derivation needs no reference to bench content and makes none.

AC2.4 makes that structural rather than promised (`-99`), and M13 proves the guard is real.
⛔ The walk covers **imports, names, attributes, parameters and definitions — deliberately NOT
string constants**, because the module must be able to *name what it refuses*: its docstring
and its published `requirement` sentence both say in terms that this is *"NOT a floor on
recall, on coverage, or on any estimate of FN."* A textual grep would forbid exactly the
disclosure AC2.1 requires. What must stay absent is a structural DEPENDENCE, because that is
what it would take for such a quantity to reach the arithmetic. The guard says so in its own
docstring.

#### AC6.3 / AC6.4 — the artifacts, and what regenerating them did NOT do

`adjudication-record.json` **byte-unchanged**, verified twice: md5
`7fe61af357e8900645ad1423fc42c67d` before and after, and `git diff` empty across the whole
story. `build_adjudication_record.py --check` exit **0**. **No `V1.4` row**; the change-log
head is still V1.3 and the 31 human judgements of 2026-08-17 keep their provenance.

Both producers were run **on a CLEAN tree in their own commit** (`d26ffb6`), because both cite
`git rev-parse HEAD` while enumerating the git index — `regenerate_dogfood_artifacts.py`
REFUSES outright on a dirty tree and `build_gate_decision.py` records
`commit_sha_provenance: NOT ESTABLISHED`. The committed record now carries
**`ESTABLISHED`** naming `48e8ea6`.

**Verified again rather than inherited from 16.2's record:** `build_gate_decision.py` does run
the detector — over the **CARTRIDGE** corpus only, whose members are synthetic templates
materialised into a `TemporaryDirectory` by `tests/cartridges/_cartridge.py`, to measure §5's
clean-repo condition. **No fetch, no bench member read, no candidate touched, no
`eligible_for_n` moved.** Files written by the two runs: the gate-decision record and the three
dogfood artifacts, and nothing else.

#### AC6.5 — the BINDING ORDERING CONSTRAINT, checked by git ancestry

`CANDIDATE_OUTPUT_PATHS` was **imported from `tests/test_candidate_selection.py`, never
re-typed**. Over `1ecf618..HEAD` (4 commits):
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/candidates` → **untouched**;
`_bmad-output/audit-reports/candidates` → **untouched**. A control pathspec known to carry
commits in the same range returns them, so the query is not silently empty — the single most
likely way this check could pass vacuously.

### Completion Notes List

- **§5 now carries SEVEN conditions.** `detector-yield-verdict-eligible-population-floor`,
  APPENDED; the six historical ids keep their historical positions; `decide_gate` still reads
  by id and no index was re-introduced.
- **The floor is 5, DERIVED as `ceil(q/(q−p))` and never typed**, taking the threshold as an
  argument, with exact integer ceiling division (AR4) and a typed `VacuousYieldFloor` when
  `q − p <= 0`. The general form is stated, `.denominator` is refused in writing and by M5, and
  the `VALIDATION_SET_FLOOR_N` coincidence is disclosed in the derivation string.
- **Composition, both directions driven** (AC3.2 / AC3.3): 40 findings from one sealed member
  stays `BLOCKED` with breadth `FAILED` and yield `MET`; sizes 3 and 4 with breadth and seal
  `MET` are `BLOCKED` on yield. A population failing both still reports both verdicts —
  nothing short-circuits.
- **DECISIVE, not lockstep** (AC3.4): `-97` pins breadth and the seal TRUE and moves the
  population size alone. M8 deletes the dispatch branch and it goes RED.
- **`DN-16-3-8`, a decision the story left open and I took**: the status renderer is a THIRD
  SIBLING (`yielded_precision_gate_status`) rather than a widened breadth renderer — following
  16.2's `DN-16-2-8` rather than forking it. Consequence: **`argus/precision/gate_breadth.py`
  is BYTE-UNCHANGED**, though the story listed it as a possible UPDATE. All three renderers are
  thin wrappers over ONE shared `precision_gate_status_for`; the fork AR7 forbids would be a
  second renderer, not a third caller. Recorded under AC7.5 as a deviation from the declared
  write set in the safer direction — one fewer file touched.
- **`DF-16-3-A` filed** (append-only, zero deletions): `tests/test_gate_seal.py` at
  **1,145/1,200**, with a stated trigger at 1,180 and a candidate boundary recorded so the next
  author does not have to find it under pressure. Filed because this story was itself handed an
  **unfiled** trigger at nine lines, and that should not happen a fourth time.
- **AC8.3 — OPEN, stated as open rather than claimed green.** I was instructed not to push, so
  **no CI run covers these shas**. The local gates are **Windows-only**; CI runs an ubuntu
  matrix. Nothing here asserts on `os.sep`, a drive letter or a CRLF-sensitive byte count, and
  every path→string boundary uses `.as_posix()` — but that is a design property, not a CI
  result.
- **NOT TAKEN, confirmed:** no Argus run over any bench member; nothing ratified, fetched,
  staged or adjudicated; `DF-13-5-A`'s ONE round **UNSPENT**; `DF-16-1-A`'s rule-class arm
  **UNLANDED** and no rule-class threshold written anywhere; **no `V1.4` row**; set-relative
  partition rules not reopened; `sprint-change-proposal-2026-08-20-amendment-A.md` **not
  approved, not applied, not cited as authority**; 16.4 not started or prepared; no ledger entry
  disposed of.

### File List

**Task 1 — the split (`01a2f48`):**
- `tests/test_gate_decision.py` — UPDATE (1,191 → 846; six guards moved out byte-for-byte,
  nine now-unused imports removed, docstring records the split)
- `tests/test_gate_decision_artifact.py` — **NEW** (451)

**The condition (`48e8ea6`):**
- `argus/precision/gate_yield.py` — **NEW** (560)
- `argus/precision/gate_conditions.py` — UPDATE (220 → 234; the seventh id, appended, dated)
- `argus/precision/gate_decision.py` — UPDATE (986 → 1,084)
- `tests/test_gate_yield.py` — **NEW** (807, then 839)
- `tests/test_gate_breadth.py` — UPDATE (704 → 747)
- `tests/test_gate_seal.py` — UPDATE (1,135 → 1,145)
- `tests/test_gate_decision.py` — UPDATE (846 → 865; `-55`'s third mirror term)
- `tests/test_release_preflight.py` — UPDATE (⚠️ **not in the declared write set** — the module
  registry is a deliberate-decision gate and `gate_yield.py` joins it with its reason)
- `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` — UPDATE
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — UPDATE

**The artifacts (`d26ffb6`):**
- `.../validation-corpus/gate-decision-record.json` — REGENERATED
- `.../minions-dogfood-partition-plan.md`, `.../minions-dogfood-budget-plan.md`,
  `.../minions-dogfood-proof.md` — REGENERATED
- `README.md`, `CHANGELOG.md` — UPDATE (⚠️ **not in the declared write set** — 91 → 92 modules,
  99 → 100 wheel entries, 98 → 99 sdist files; `TC-ArgusAgent-DOCS-001-54` asserts the
  documents against a freshly built wheel in both directions, so leaving them was not an option)

**The unreal-guard repair (`a0c74ae`):**
- `tests/test_gate_yield.py` — UPDATE (807 → 839)

**The record (this commit):**
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **APPEND ONLY** (`DF-16-3-A`;
  `git diff 1ecf618` = 47 insertions, **0 deletions**)
- `_bmad-output/design-artifacts/ArgusAgent/stories/16-3-a-detector-that-finds-nothing-has-not-passed.md`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`

⛔ **BYTE-UNCHANGED, and asserted so:** `argus/precision/gate_breadth.py` ·
`argus/precision/gate_seal.py` · `argus/detectors/**` · `tests/test_vacuous_density.py` ·
`tests/corpus/_manifest.py` · `argus/precision/replay_harness.py` ·
`validation-corpus/adjudication-record.json` · every candidate-output path.

### NFR-M1 (AC8.2) — `_physical_line_count`, every touched and adjacent module

| module | before | after | headroom |
|---|---|---|---|
| `tests/test_gate_decision.py` | 1,191 | **865** | 335 |
| `tests/test_gate_decision_artifact.py` | — | **451** | 749 |
| `argus/precision/gate_yield.py` | — | **560** | 640 |
| `argus/precision/gate_decision.py` | 986 | **1,084** | 116 |
| `argus/precision/gate_conditions.py` | 220 | **234** | 966 |
| `tests/test_gate_yield.py` | — | **839** | 361 |
| `tests/test_gate_breadth.py` | 704 | **747** | 453 |
| `tests/test_gate_seal.py` | 1,135 | **1,145** | 55 ⚠️ `DF-16-3-A` |
| `tests/test_release_preflight.py` | 987 | **1,000** | 200 |
| `argus/precision/gate_breadth.py` | 436 | **436** | unchanged |
| `argus/precision/gate_seal.py` | 777 | **777** | unchanged |
| `tests/corpus/_manifest.py` | 1,029 | **1,029** | unchanged |
| `argus/detectors/vacuous_test.py` | 1,196 | **1,196** | unchanged, untouched |
| `tests/test_vacuous_density.py` | 1,159 | **1,159** | unchanged, untouched |

**No line was shaved to fit and no `_EXEMPT_BY_DESIGN` entry was added** — the registry may only
shrink.

### Gates (AC8.1), all with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`

| gate | result |
|---|---|
| full suite | **1,673 passed · 0 failed · 0 skipped · exit 0** |
| delta vs the 1,667 baseline | **+6** — exactly the new `-95`..`-100`. The Task-1 split moved six guards between modules and changed no total (verified: 1,667 collected before and after the split) |
| `mypy argus` | **Success, 92 source files** |
| `bandit -r argus --severity-level medium` | **No issues identified** |
| module-size ceiling | **6 passed**, no new exemption |
| `build_gate_decision.py --check` | exit **0** |
| `build_adjudication_record.py --check` | exit **0** |
| `git status --porcelain` after all 15 mutations | **empty**; `git diff` empty |

---

## Hand-off to Story 16.4 (AC8.4)

**THE LANDING SHAS — for 16.4's ancestry guard to cite, recorded here because a commit cannot
cite itself** (the Story 15.1 `CRITERIA_COMMIT_SHA` / Story 16.2 `SEAL_COMMIT_SHA` pattern):

| commit | what it froze |
|---|---|
| `01a2f4806c64353176f09ba4dc098e5fa563afdd` | the split-first discharge (`tests/test_gate_decision.py` 1,191 → 846) |
| **`48e8ea6b13cd77a0eb20603e5d9072460a751a18`** | ⛔ **THE YIELD FLOOR — the sha 16.4 cites.** §5's seventh condition, the derivation, the guards, the protocol and architecture amendments |
| `d26ffb67550b7441f6f3ec8075331b6f09f1460c` | the regenerated gate-decision record and dogfood artifacts |
| `a0c74ae74dc1dff96264f7c1052b2596f94b7d31` | the unreal-guard repair to `-100` |

**None of the four touches any candidate-output path**, verified by pathspec against the
imported `CANDIDATE_OUTPUT_PATHS` with a control. The BINDING ORDERING CONSTRAINT is intact
leaving this story exactly as it was entering it.

**THE SEVENTH CONDITION.** Id `detector-yield-verdict-eligible-population-floor`, position 7,
appended. Own verdict `MET` or `FAILED`, never `UNEVALUABLE`. Below the floor, §5's PRECISION
condition is `UNEVALUABLE` and the outcome is `BLOCKED` with a countable closure path.

**THE FLOOR AND ITS DERIVATION.** `ceil(q / (q − p))` over `PRECISION_GATE_THRESHOLD = p/q`
= **5** at the shipped `4/5`. It is the smallest denominator at which the threshold admits a
single false positive — below it, *"≥ 80%"* is silently *"100%"*. Not `q`
(diverges at `5/7` and `7/9`); not `VALIDATION_SET_FLOOR_N` (equal today by coincidence, and
that coincidence is disclosed in code); not the breadth/seal floor of 3 (a different quantity
from a different source). It fires on population sizes **3 and 4** and on nothing smaller that
can reach the branch.

**ITS VERDICT ON THE COMMITTED POPULATION, and why.** **`MET`** — the committed population is
**31**, above the floor of 5. The committed decision is still **`BLOCKED`**, and still for the
**Story 13.5** reason (*"the corpus WAS READ and NOTHING was promoted"*), **not** for a yield
reason. The amendment is INERT on the live tree, verified at the producing seam.

> ⛔ **THE PRE-ROUND DISCLOSURE, IN COUNTABLE TERMS — READ THIS BEFORE SPENDING THE ROUND.**
>
> - The **corrected** detector's verdict-eligible yield over the **entire ratified gating
>   corpus** is **0 of 4,284 findings** across all 5 members (`adjudication-set-13-5.json`,
>   2026-08-18, post-Epic-14). **0 blocking.** Not one promotion.
> - The **only** population that ever exceeded a yield of 5 was the 2026-08-16 set of **31**,
>   produced under the **pre-Epic-14 corroboration rule that Epic 14 REFUTED** — and the named
>   human adjudicated those 31 as **0 TP / 26 FP / 5 BORDERLINE**. **A yield above this floor
>   has been achieved exactly once, and it was achieved entirely by false positives.**
> - `argus/detectors/vacuous_test.py` records the same thing from the other side, in its own
>   comment: *"0 of 4,673 are corroborated at all after 14.1 — an EMPTY DENOMINATOR."*
> - The achievable yield over the **sealed** partition is **UNMEASURABLE** without fetching
>   third-party source, which is a §6 **R2** operator act. The sealed partition's 431
>   co-occurrence files are **a TEXT PROXY and NOT a yield prediction**, and may not be used as
>   one (`scripts/candidate_selection.py`, in its own words).
> - **Unmeasured is NOT bounded-by-construction.** I searched for a structural cap on promoted
>   findings and found **NONE**: the corroboration path emits one finding per flagged test
>   function and admits no *k*. 16.1's shutdown shape does **not** apply, so this was filed as
>   a **disclosure and not a halt** — but the number a reader should hold in mind is **zero**.
> - **On the only evidence that exists, the likely outcome of the ONE round is `BLOCKED` on
>   yield**, and `DF-13-5-A`'s ONE round is spent producing a finding about the DETECTOR rather
>   than a precision figure. ⛔ **That outcome is already pre-registered and is already the
>   answer**: `DF-13-5-A`, answered 2026-08-17 **before any number existed**, routes a round
>   that promotes too little to option **(b)** — *"the FR34 disclosure stands for V1.5 … the
>   next attempt requires a materially better detector — NOT a bigger bench."* The epic header
>   says the same in its own words: *"this epic may not clear the gate, and that is a permitted
>   outcome."*
> - **So this condition is not a new hurdle. It is `DF-13-5-A`'s own stopping rule made
>   arithmetic.** Without it a round yielding **three** would route to `CLEARED` while a round
>   yielding **zero** routes to option (b) — two destinations for a materially identical
>   result. Closing that gap is the whole of this story.

**WHAT 16.4 STILL OPENS ON, unchanged by this story.** The protocol §6 **R2** operator act.
`sealed ∩ ratified` is still **empty** (16.2's hand-off), so R2 must ratify **≥ 3 of the six
named sealed candidates** before any §5 outcome over sealed evidence is reachable at all — and
with this condition, at least **5 verdict-eligible findings** must then come out of them.

**STILL OPEN, and not touched here:** `DF-13-5-A` (ONE round, **UNSPENT**) · `DF-16-1-A` (the
rule-class arm, **unlanded**) · `DF-15-2-D` · `DF-15-2-E` · **`DF-16-3-A`** (new) ·
`sprint-change-proposal-2026-08-20-amendment-A.md` (**registered, UNAPPROVED**) · AC8.3's *no CI
run covers these shas*.

---

## Change Log

| Date | Change | By |
|---|---|---|
| 2026-08-20 | Story contexted at HEAD `1ecf618`. Premises re-measured by execution: the three-finding hole **proved real** (size 3 and 4 return `CLEARED`); the floor **derived** as `ceil(q/(q−p))` = **5** from `PRECISION_GATE_THRESHOLD`, with the vacuity boundary independently measured at 3; the shutdown check **answered as far as it can be** (corrected detector's yield over the gating corpus = **0 of 4,284**) and its unmeasurable remainder recorded as a pre-round disclosure rather than a halt; the OI1 question **answered** (not recall — no `FN` term — conditional on the number's source, made mechanically checkable by AC2.4); the undocumented **9-line SPLIT-FIRST trigger** on `tests/test_gate_decision.py` found and made Task 1. `backlog` → `ready-for-dev`. | create-story (Scrum Master) |
| 2026-08-20 | **Implemented (dev-story).** §0 re-measured by execution and reproduced without deviation on all four premises: sizes 3 and 4 `CLEARED` at `1/1` with six `MET`; the floor **5** re-derived twice (brute force + closed form) over eight thresholds, diverging from `q` at `5/7` and `7/9`; `verdict_eligible: 0` of **4,284** re-counted; §0.5's ten line counts reproduced to the line. **AC7.4's structural-cap search run: NONE found** — unmeasured, not bounded by construction, so no escalation. **Task 1 split taken FIRST and alone** (`01a2f48`), proved a pure restructuring: six definitions byte-identical by sha256, partition of the original 20 exact with no function split, collection 1,667 unchanged. §5's **SEVENTH** condition landed (`48e8ea6`) with `argus/precision/gate_yield.py`; the OI1 Recall row amended explicitly, struck-not-erased, at §5:313 only; §5 gained a **THIRD dated block under V1.3** with **no `V1.4` row**; `adjudication-record.json` byte-unchanged (md5 verified). **15 mutations EXECUTED, 15 observed RED**, bytecode caching disabled, tree restored byte-exact — ⛔ **M15 caught one of my own guards UNREAL** (it read the committed JSON, not the live sentence); `-100` gained a live leg and the whole set was re-run (`a0c74ae`). Artifacts regenerated on a clean tree (`d26ffb6`); no detector ran over any bench member. Full suite **1,673 · exit 0**, mypy 92 files, bandit clean, both builders `--check` 0, ceiling green with no new exemption. `DF-16-3-A` filed (pure append, 0 deletions). AC8.3 recorded **OPEN** — not pushed, so no CI run covers these shas. `in-progress` → `review`. | dev-story (Amelia) |
| 2026-08-20 | **Adversarial code review, iteration 1 — PASS, zero decision-needed/patch/defer.** Every load-bearing claim re-derived by independent execution rather than trusted from prose: the Task 1 byte-identity re-extracted and diffed from both commits (exact match, not just hash comparison); the floor re-derived, and its inverse specifically probed by mutating `PRECISION_GATE_THRESHOLD` itself in a scratch edit (floor moved to 4, confirming the general form is real); sizes 3/4 driven `CLEARED` at a checked-out `1ecf618` tree and `BLOCKED` at `HEAD` in the same process, tree restored clean; AC3's both directions driven directly through `decide_gate`; the AC2.4 AST guard driven RED against the **actual production file** (an inserted `total_fn` reference), not only the test's internal string-patched variants; the OI1 protocol amendment confirmed to touch line 313 only (exactly one of two hunks in the whole-file diff) with a byte-for-byte prefix-preserving append; five independent mutations across `gate_yield.py`, `gate_decision.py` and `gate_conditions.py` (floor forked/stuck, `holds` stuck, dispatch branch removed, `precision_evaluable` conjunct dropped, seventh id dropped) each observed RED with my own eyes; full suite re-run with bytecode caching disabled — **1,673 passed, 0 failed** (counted from the raw dot-stream), mypy 92 files, bandit clean, ceiling 6 passed, both builders `--check` 0; every physical line count and the 107-key/7-STATUS-DEFINITIONS sprint-status shape confirmed by direct measurement. Tree left `git status --porcelain` clean. `review` → `done`. | code-review (QA gate) |
