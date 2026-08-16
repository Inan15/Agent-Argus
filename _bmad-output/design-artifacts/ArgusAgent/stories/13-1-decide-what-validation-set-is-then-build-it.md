---
baseline_commit: bc55e361d46b1a33672d0214c7d8e1a97190d0dc
---

# Story 13.1: Decide what the validation set is, then build it

Status: review

<!-- Created 2026-08-16 by create-story. Every premise below was re-measured by execution on
     HEAD bc55e36 before this file was written; see §0. Validation is optional — run
     bmad-create-story:validate for a second pass before dev-story. -->

## Story

As the Argus maintainer,
I want one definition of the validation set and a corpus that satisfies it,
So that the gate is cleared against the thing the PRD actually specified.

This is the first story of **Epic 13 — Earn the Gate**, the only work in the plan that can remove
the tool's provisional status. It is a **decision + construction** story, not a feature story. It
ends with: one governing corpus definition, the losing definition amended (not deleted), the
architecture's last OPEN input closed **by decision** rather than by implementation, and a corpus
that 13.2 can adjudicate.

### What it is NOT

- **It does not adjudicate anything.** No finding is judged TP or FP here. That is 13.2, and it
  requires the named human (XAgent007). A story that adjudicates its own corpus has proven nothing.
- **It does not compute or flip the gate.** `protocol_cleared` stays `False`. The `precision_gate_status()`
  marker is not flipped. Any change that makes a cleared gate *possible* to state without 13.2 having
  run is a defect, not progress.
- **It does not delete the cartridge registry.** The cartridges measure **recall against known plants**
  (FR20, delivered and CI-asserted). They keep doing that. The decision below reassigns what they are
  *evidence of*, and reassigns nothing else.
- **It does not soften a threshold.** ≥80% exact `Fraction`, 0 clean-repo blocking FP, N ≥ 5. If the
  corpus turns out to be hard to build, that is a fact to record, never a reason to move a number.
- **It publishes nothing outward-facing.** No tag, no push beyond ordinary commits, no release, no
  visibility change. `DF-12-9-A` remains unauthorised and untouched by this story.

## Acceptance Criteria

### AC1: One definition governs, the other is amended — dated, reasoned, and recorded in both documents

**Given** the PRD specifies *"N ≈ 5–10 **real** XAgents repos, starting with **Minions**"*
(`prd.md:196`) and *"🔴 judged genuinely real by an **independent senior engineer**"* (`prd.md:191`),
while `precision-validation-protocol.md` §5 specifies *"N ≥ 5 distinct labeled **planted-defect
cartridges**"* with `VALIDATION_SET_FLOOR_N = 5` (`tests/cartridges/_registry.py:57`) — **two
different corpora, never reconciled**

**Then** exactly one governs, and the decision carries a date and a reason in **both** documents.

**The recommendation of record — adopt it or overturn it explicitly, never silently:** **the PRD
governs.** The reason is that the two specify different *quantities*, not two opinions about one
quantity:

| | Cartridge corpus | Real-repository corpus |
|---|---|---|
| Measures | **Recall** against known plants — did we find what we hid? | **Precision** on unplanted code — is a blocking finding real? |
| Denominator | Golden keys the team authored | Findings the tool emitted on code nobody planted |
| Gates externalization? | **No** | **Yes** — this is the ≥80% gate |
| Status | Delivered, CI-asserted (FR20) | **Does not exist yet** — this story builds it |

**And** the protocol is amended, not replaced: §1, §4, §5 and §6 gain the corpus distinction, the
cartridge rows keep their recall role, and the amendment is appended to the protocol's change log
(§3.4 evidence immutability — **strike, never erase**).

### AC2: The architecture's last OPEN input is closed BY DECISION, at every site that states it

**Given** the architecture states *"This is the one open input that gates an ARCHITECTURE choice, not
merely scope"* — and states it in **two places that do not agree**:

| Site | What it says today |
|---|---|
| `architecture.md:203-208` | *"✅ **CLOSED 2026-08-10b — assigned, not answered.**"* |
| `architecture.md:800-807` | *"**Still open**, and the 'resolve before harness build' condition was not met … **Owned by Story 13.1**"* |

**Then** this story closes it **at both sites, with the same words**, in the established
strike-not-delete form, recording *which* definition won and *why* — and the "Gap Analysis"
mention at `architecture.md:1244` is corrected in the same pass so a third site does not survive
saying something else.

**And** a committed guard asserts the resolution text is present, in the `TC-ArgusAgent-DOCS-001-23`
pattern (*"a rule that lives only in a test is not a rule and a rule that lives only in prose is not
enforced"*, `architecture.md:921-922`). An architecture decision with no guard is how this one drifted
for three epics.

### AC3: The corpus is specified, and it is built from repositories Argus did not author

**Given** the corpus went **backwards**: Story 8.5 re-derived the dogfood as a **self-audit of
`argus/`**, the independent Minions run survives only at
`minions-dogfood-proof-story-7-2-superseded.md` and *"can never be re-derived in this repository"*
(`deferred-work.md:832-836`), and the ledger calls the replacement *"a materially weaker evidence
class … not independent corroboration of anything"*

**AC3a — the specification (fully autonomous).** A committed, machine-readable **validation-set
manifest** defines membership. Each member carries, at minimum: repository URL, **pinned commit sha**,
licence, primary language, provenance (`independent` | `self` | `superseded`), and an
`eligible_for_n: bool` with a **reason string when false**. The manifest is the one named place; a
member that is not in it is not in N.

**And** the exclusions are recorded **in the manifest itself**, not in prose elsewhere:
- the **Argus self-audit** is `eligible_for_n: False`, reason: self-authored;
- the **superseded Minions run** is `eligible_for_n: False`, reason: not re-derivable in this repository;
- the **cartridges** are not manifest members at all — different corpus, different quantity (AC1).

**And** the floor is derived from the manifest, never transcribed: a function returning the count of
`eligible_for_n` members, compared against `VALIDATION_SET_FLOOR_N` — reusing the existing constant,
never forking a second floor.

**AC3b — the build (gated on one explicit operator act — see ESCALATION).** The manifest is populated
to **N ≥ 5** independent repositories, each staged at its pinned sha and audited through the
**unmodified** `pipeline.run_audit_detailed`, producing an **adjudication-ready** finding set for 13.2
in the shape 13.2 expects: per-finding `rule_id`, verdict-eligibility, advisory flag, and ≥1 locator —
the 6.6 `finding_match_key` identity `(rule_id, verdict_eligible, advisory)`.

**And** no third-party source byte is committed, and no source byte reaches any artifact (NFR-S1) —
manifest metadata and locators only, exactly as `minions-dogfood-proof.md` already does for `argus/`.

### AC4: "Usage is not evidence" is enforced, not just restated

**Given** the PRD's guard — *"**usage is not evidence** — adoption cannot advance the precision gate,
only adjudicated findings can"* (`prd.md:159`)

**Then** the manifest may **source** repositories from anywhere, including public users, and the
sourcing rule is recorded; but a member contributes to N **only** once its findings are adjudicated in
13.2. Install counts, run counts, stars and download figures are **never** eligible fields — and the
manifest schema is closed such that adding one is a failure, not a silent extension (the
`DF-10-4-E` exhaustive-dispatch shape: an unregistered member **raises**).

### AC5: `DF-8-5-C` — the published figure is DERIVED from the registry, not written by hand

**Given** `argus/dogfood/proof_run.py:643-644` passes `precision=Fraction(0, 1)` and `n=0` as
**literals, not a measurement**, rendering *"precision=0/1 … N=0 labeled cartridges populated, floor
N=5"* into `minions-dogfood-proof.md:88` — while the shipped registry, measured live on `bc55e36`,
returns `populated_planted_defect_count() == 7` across `distinct_rule_class_count() == 5` classes

**Then** the figure is **derived**, the artifact is **regenerated** so the corpus it reports is the
corpus that exists, and a guard asserts the rendered figure equals the derived figure — so the next
hand-written number fails before it is published.

**And** the correction is recorded **as a correction**: the literal **understated** the corpus, so it
never made a gate look cleared — but *a hand-written number in a proof artifact about the very gate
this epic measures* is the defect class Epic 8 exists to delete, and it survived five epics inside the
generator that exists to prevent it.

⚠️ **The derivation must not break the wheel.** `tests/cartridges/` is **repository-only and absent
from the built distribution** (`DF-9-2-A`). `argus/precision/replay_harness.py:93-99` already declares
the single lazy impure edge (`_registry_module()`). **Reuse it.** A module-level import of the registry
from `argus/dogfood/proof_run.py` ships a wheel that cannot import, and
`tests/test_built_distribution.py` `-20` is the guard that will catch you.

### AC6: Every document this story falsifies is CORRECTED, never loosened

1. **The protocol's file paths are stale in three places** — §1 names
   `minions_core/apaa/precision/replay_harness.py`, `tests/apaa/cartridges/_registry.py` and
   `tests/apaa/test_precision_replay.py`. Measured: all three moved to `argus/` / flat `tests/` in the
   2026-08-03 separation. Correct them in the same pass that amends §5; a protocol that cannot locate
   its own substrate cannot govern an adjudication.
2. **`deferred-work.md` is append-only** — `git diff --numstat` on it must be `+n / -0`.
   `DF-8-5-C` is closed here **against evidence**. `DF-6-6-A`, `DF-6-6-A-P1`, `DF-6-6-A-P2` and
   `DF-7-2-A` are **not** closed by this story (they are 13.2's human half) — but each gets a
   progress note naming which corpus it now adjudicates, because 8.5 already moved that target once
   without telling them (`deferred-work.md:813-839`).
3. **`DF-10-2-A` gets its dated decision here or an explicit re-home.** Four consecutive
   retrospectives have named it critical-path (`AI-E10-4` → `AI-E11-7` → `AI-E12-9`) and its
   `target_story` is still `NONE`. C/C++/Ruby/Rust ground cleanly and extract **zero** definitions —
   which directly shapes AC3's `primary_language` eligibility. Decide it as part of the corpus
   specification or re-home it with a named owner; `AI-E9-8` forbids `target_story: NONE` without one.
4. **No guard is narrower than its AC** (`AI-E8-6`), and every new guard satisfies the
   **GUARD-ADEQUACY CLAUSE** (`AI-E11-1`): (i) its observable is named, (ii) the defect is demonstrated
   to move it **at the real seam**, (iii) at least one adversarial variant is **generated** from the
   registry it closes over.
5. **NFR-M1**: no module or test file crosses **1200 lines**. Headroom is measured in §0.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (this project's create-story control, nine-for-nine since Epic 11)

Measured **2026-08-16 on `bc55e36`** (HEAD; `origin/master` == HEAD, 0 ahead / 0 behind), by
**execution**. Per the Epic-11 retro §3.2 refinement and `AI-E12-10`, **confirmations are recorded as
well as divergences.**

| Premise, as `epics.md:2504-2549` states it | Re-measured on `bc55e36` | Consequence |
|---|---|---|
| *"PRD **L161** specifies N ≈ 5–10 real XAgents repos"* | ⚠️ **TRUE CLAIM, STALE CITATION.** The text is at **`prd.md:196`**. `prd.md:161` is the heading `### User Success` | **Locate by content, never by the epic's line numbers.** Every PRD/architecture line cite in this epic predates the frontmatter that shifted them |
| *"PRD **L156** requires findings judged genuinely real by an independent senior engineer"* | ⚠️ **TRUE CLAIM, STALE CITATION.** Text at **`prd.md:191`** | AC1 |
| *"PRD **L118/L130/L141/L302** carry NOT CLEARED"* (13.3's premise, verified early because AC1 amends the same file) | ⚠️ **STALE.** `NOT CLEARED` / the gate status live at **`prd.md:139`, `:176`, `:373`, `:475`** | Recorded now so 13.3 does not rediscover it |
| *"the architecture records at **L152-154** that the validation-set input is OPEN"* | ⚠️ **STALE CITATION, AND THE SITE SPLIT IN TWO.** The sentence is at **`architecture.md:205`**; a second, **disagreeing** statement is at **`:800-807`**; a third mention at **`:1244`** | **AC2 — and the divergence is the point.** One site says CLOSED-as-assigned, one says still open. Closing one leaves the plan contradicting itself, exactly as before |
| *"`precision-validation-protocol.md` §5 specifies N ≥ 5 labeled planted-defect cartridges with `VALIDATION_SET_FLOOR_N = 5`"* | ✅ **HOLDS.** Protocol §5 row 3; `tests/cartridges/_registry.py:57` → `VALIDATION_SET_FLOOR_N = 5` | AC1. The conflict is real, not a misreading |
| *"the shipped registry measures **5 distinct rule classes across 7 populated rows**"* | ✅ **CONFIRMED BY EXECUTION.** `populated_planted_defect_count()` → **7**; `distinct_rule_class_count()` → **5** (`cross_partition`, `hardcoded_secret`, `orphan_code`, `vacuous_test_ast`, `vacuous_test_heuristic`); 10 registry rows: 5 `planted_defect`, 2 `holdout`, 1 each `clean_control` / `trap` / `no_crash` | **AC5.** The epic's arithmetic is right |
| *"`proof_run.py:643-644` passes `precision=Fraction(0, 1), n=0` as literals"* | ✅ **EXACT — line numbers still true.** `L643: precision=Fraction(0, 1),` · `L644: n=0,` inside the `precision_gate_status_for(...)` call at `L642-647` | **AC5.** The one citation in this epic that did not drift |
| *"…rendering `N=0 … floor N=5` into `minions-dogfood-proof.md:87`"* | ⚠️ **OFF BY ONE.** The rendered line is **`:88`**; `:87` is blank. Content confirmed: `precision=0/1 … N=0 labeled cartridges populated, floor N=5` | AC5 |
| `sprint-status.yaml:415` cites the same literals at **`proof_run.py:764-765`** | ❌ **A THIRD, DIFFERENT CITATION for one defect.** The file is **611 lines** — `:764` does not exist. `epics.md` says `:643-644`; the tree agrees with `epics.md` | **Three documents, three line numbers, one defect.** Confirms DN-«locate by content»: fix the tracker's cite when you close `DF-8-5-C` |
| *"`argus/precision/replay_harness.py:223` is where `protocol_cleared` is passed"* (13.3's premise) | ⚠️ **DRIFTED BY 3.** `compute_precision` is defined at **`:222`**; the parameter `protocol_cleared: bool = False` is at **`:226`**. Confirmed never passed `True` anywhere in the tree | Recorded for 13.3 |
| The protocol can locate its own substrate | ❌ **DIVERGES — three dead paths.** §1 names `minions_core/apaa/precision/replay_harness.py`, `tests/apaa/cartridges/_registry.py`, `tests/apaa/test_precision_replay.py`. **None exists.** Live: `argus/precision/replay_harness.py`, `tests/cartridges/_registry.py`, `tests/test_precision_replay.py` | **AC6.1.** The document governing the gate has stale pointers to every instrument it governs |
| *"the adjudicator is named"* (epic start condition) | ✅ **HOLDS.** `sprint-status.yaml:414` / `:416` name **XAgent007** in the Engineering Lead / protocol §2 primary role | ESCALATION. The QA-Lead second and external tie-break stay unfilled until a borderline finding requires them (§4) |
| The corpus regression is as the epic describes | ✅ **HOLDS, and it is worse than one line.** `deferred-work.md:823-830` records the measured collapse: `cross_partition` 332→**2**, `hardcoded_secret` 2289→**22**, `orphan_code` 285→**77**; 2906→**101** findings; verdict `NOT_READY_FOR_RELEASE` (exit 2) → **`RELEASE_READY` (exit 0)** | **AC3.** The self-audit is not a thinner version of the Minions run — it is a *different verdict* |
| Nothing has been published | ✅ **HOLDS.** `git tag -l` → **empty**. `origin/master` == `bc55e36` == HEAD | This story stays inside that. `DF-12-9-A` is untouched |
| `AI-E10-8` — *"`argus/pipeline.py` is 1331 lines against NFR-M1"* | ❌ **ALREADY FIXED, LEDGER NOT TOLD.** Measured: **1111** (under the 1200 limit). Story 12.1 closed it; the action item still reads open | Do not "fix" it again. Flag it in the Dev Agent Record |
| `AI-E12-1` — *"register `epic-12-retro-2026-08-15.md` in `_STATUS_DOCUMENTS`"* | ❌ **REGISTRATION ALREADY DONE.** `tests/test_evidence_citation.py:125`. The *second* half (make it part of the retrospective step's DoD) is unverified | Do not re-register. Same class as the row above |
| Test-case id high-water marks | Measured: `PRECISION-001-**20**` · `CARTRIDGE-001-**15**` · `DOGFOOD-001-**52**` · `DOCS-001-**72**` | New ids continue from these. **Open no new area** — see §Testing |
| NFR-M1 headroom (files this story touches) | `argus/dogfood/proof_run.py` **679** · `argus/precision/replay_harness.py` **391** · `tests/cartridges/_registry.py` **332** · `tests/test_precision_replay.py` **513** · `tests/test_dogfood_proof.py` **1106** (94 left) · `tests/test_evidence_citation.py` **1199** | 🚨 **`test_evidence_citation.py` has ONE line of headroom.** AC2's guard **cannot** land there — apply the cohesion-split remedy 12.8 used, do not shave. `test_dogfood_proof.py` at 94 left will not take AC5's guard plus its adversarial variants either |

### §0.1 — THE INVENTORY: what exists to measure precision with, and what it actually proves

| Instrument | Lives at | Measures | Counts toward the ≥80% gate? |
|---|---|---|---|
| Cartridge registry (10 rows, 5 classes) | `tests/cartridges/_registry.py` | **Recall** vs. planted golden keys | ❌ No — AC1's decision |
| Precision replay harness | `argus/precision/replay_harness.py` | TP/FP/FN fold, exact `Fraction` | ✅ The arithmetic — **reuse, do not fork** |
| Argus self-audit dogfood | `minions-dogfood-proof.md` (101 findings) | Argus on Argus | ❌ No — self-authored (AC3a exclusion) |
| Minions run (Story 7.2, 2906 findings) | `minions-dogfood-proof-story-7-2-superseded.md` | Argus on an independent repo | ❌ No — *"can never be re-derived in this repository"* |
| **The real-repository corpus** | **does not exist** | **Precision on unplanted code** | ✅ **This story builds it** |

**Read the last two rows together.** The only independent evidence the project ever had is
preserved-but-unrepeatable, which is why AC3 is a build and not a re-run.

### Files to touch

**NEW** — the corpus substrate. It is **repository-only**, like `tests/cartridges/`, for the same
reason (`DF-9-2-A`): it must not ship in the wheel.

| Path (indicative) | Purpose |
|---|---|
| `tests/corpus/_manifest.py` | AC3a. The pinned manifest + the derived eligible-N function. Mirror `_registry.py`'s frozen-tuple-of-specs shape — a `CorpusMemberSpec` beside `CartridgeSpec`, **not** a second registry with new idioms |
| `tests/test_validation_corpus.py` | AC3/AC4 guards. Manifest shape, closed schema, derived floor, exclusion reasons present |
| a guard for AC2's architecture text | 🚨 **It must be a new module.** The natural home, `tests/test_evidence_citation.py`, is at **1199/1200** — one line. Do not shave it to fit; **record the choice and the reason**, and follow 12.8's cohesion-split precedent if you split instead |

**UPDATE** — read each completely before editing. What it does today and what must be preserved is
stated so the change is a modification, not a rewrite.

| Path | What it does today | What must be preserved |
|---|---|---|
| `argus/dogfood/proof_run.py` (679) | Builds `DogfoodProofRun`; `L642-647` calls `precision_gate_status_for` with **literal** `Fraction(0,1)` / `n=0`; `L638-641` explains why the gate stays provisional | ⚠️ **The OI1 comment at `L638-641` stays true after your edit.** Derive the numbers; do **not** pass `protocol_cleared=True`, and do **not** compute an authoritative precision here. Reach the registry only through `replay_harness._registry_module()` — never a module-level import |
| `argus/precision/replay_harness.py` (391) | `compute_precision` (`:222`), `protocol_cleared` default `False` (`:226`), the lazy `_registry_module()` edge (`:93-99`), `precision_gate_status_for` (`:356`) | The **single declared impure edge**. Adding a second way to reach the registry is the fork this codebase keeps refusing. `Fraction` only — never a float (AR4) |
| `tests/cartridges/_registry.py` (332) | `VALIDATION_SET_FLOOR_N = 5`; `populated_planted_defect_count()`; `distinct_rule_classes()`; `precision_gate_status()` | **Reuse `VALIDATION_SET_FLOOR_N`.** Do not fork a second floor constant for the repo corpus — one floor, two populations |
| `precision-validation-protocol.md` (175) | §1 substrate, §2 roles, §3 budget, §4 method, §5 thresholds, §6 phased plan, §7 OI1 invariants, change log | §7 is **not softened** — it says so in its own heading. §3.4 immutability: **append to the change log**, strike in place, never erase. The §2 role table and §4 borderline ladder are 13.2's contract — amend the *corpus*, not the *method* |
| `_bmad-output/…/architecture.md` (1280) | `:203-208` and `:800-807` (disagreeing), `:1244` gap analysis, §Enforcement (`:897+`) | Strike-not-delete. §Enforcement entries take the established form: **rule text + enforcing module + test ids** (`:916-922` is the model). `-23` asserts §H's text is present — do not reword it away |
| `_bmad-output/…/E-PRD/prd.md` (616) | `:191`, `:196` (Validation Approach), `:159`, `:176`, `:373`, `:475` | **Strike-not-delete amendment form**, matching the `*(Amended 2026-08-10b.)*` convention already in the file. `:475` already says *"Assigned, not answered — owned by Story 13.1"* — **this story is what fills it in** |
| `_bmad-output/…/deferred-work.md` (289KB) | Append-only ledger | `+n / -0`. Close `DF-8-5-C`; progress-note `DF-6-6-A`/`-P1`/`-P2`/`DF-7-2-A`; rule on `DF-10-2-A` |
| `minions-dogfood-proof.md` (89) | Generated artifact; `:88` carries the hand-written gate line | **Regenerated by its generator, never hand-edited.** The `DF-8-5-B` / `DF-10-4-D` bootstrap applies — see Testing |

### Locked decisions this story must cite rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **OI1 — N is LOCKED at 5; precision measured over FINDINGS not repos; no over-claim** | protocol §7 | The floor does not move because a corpus is hard to build |
| **The gate flips only when all four §5 conditions hold AND the adjudication run is recorded** | protocol §5, §6.4 | This story satisfies **none** of them. It makes 13.2 possible |
| **`protocol_cleared=True` is passed by the harness *caller*, never defaulted** | `replay_harness.py:226` | Untouched here |
| **Precision is an exact `Fraction`, rendered `"num/den"`** | AR4; `_ratio_string` (`:212`) | No float, no rounding, no percentage literal |
| **NFR-S1 — no source or secret bytes in any artifact** | architecture §G; 4.3/4.4 CI-blocking canary suite | Third-party corpus: metadata + locators only. **Never commit third-party source** |
| **`DF-9-2-A` — `tests/` is absent from the built distribution** | `replay_harness.py:85-88` | AC5's derivation and AC3a's manifest both live behind the lazy edge |
| **`DF-10-4-E`** — an exhaustive dispatch **raises** on an unregistered member | 12.5 `_downgrade_sentence`; 12.8 AC4 | AC4's closed manifest schema takes the same shape |
| **`AI-E9-7` / single-source** — never publish a prose copy of a pinned constant | architecture §Enforcement | Why AC5 derives and why AC3a's floor is computed |
| **`AI-E9-8`** — never `target_story: NONE` without a named human | Epic-9 retro | AC6.3 |
| **`AI-E8-6`** — a guard narrower than its own AC is a breach, not a satisfaction | Epic-8 retro | AC6.4 |
| **`AI-E11-1` GUARD-ADEQUACY CLAUSE** — observable named, defect moved **at the real seam**, adversarial variant **generated** from the registry | Epic-11 retro §3.1 | Every new guard here |
| **`DF-8-5-B` / `DF-10-4-D` bootstrap** — commit the `argus/` delta → regenerate artifacts → commit separately | 12.5-12.8 Debug Logs | **AC5 changes `argus/dogfood/proof_run.py`, so this applies.** See Testing |
| **§3.4 evidence immutability** — supersede, strike, never erase | architecture §3.4 | Every amendment in AC1, AC2, AC6 |
| **Nothing outward-facing** | `DF-12-9-A`; `AI-E12-2` | No tag, no release, no visibility change |

### Decisions taken by this story (record each in the Dev Agent Record with its rejected alternative)

- **DN-1 — The PRD governs; the protocol is amended.** Rejected alternative: let the protocol govern
  and amend the PRD down to cartridges. That would make the externalization gate clearable by a corpus
  the team authored and planted, which is the "measure your own homework" failure the epic exists to
  avoid. The cartridges are not demoted — they are **re-labelled as the recall instrument they always
  were** (FR20).
- **DN-2 — The cartridge registry is not touched except to be reused.** Rejected alternative: extend
  `CartridgeSpec` with a `real_repo` kind. That fuses two corpora into one table and would let a
  clean-control cartridge silently enter the precision denominator.
- **DN-3 — One floor constant, two populations.** `VALIDATION_SET_FLOOR_N = 5` is reused for the
  repository corpus. Rejected alternative: a second constant. Two floors is how two corpora happened.
- **DN-4 — The corpus is pinned by commit sha and fetched, never vendored.** Rejected alternative:
  commit the third-party source. It would breach NFR-S1's spirit, bloat the repository, and make the
  licence position of every member the maintainer's problem.
- **DN-5 — Guards over the corpus must be network-free.** They assert the *manifest* and the
  *derivation*; where a staged corpus is genuinely absent, the outcome is **`Unevaluable`, recorded —
  never a silent skip** (the `test_release_preflight.py` three-outcome discipline). A green CI run that
  silently skipped the corpus guard is worse than a red one.
- **DN-6 — `DF-10-2-A` is decided as a corpus-eligibility rule, not as a detector story.** C/C++/Ruby/
  Rust ground cleanly but extract **zero** definitions, so a member whose `primary_language` is one of
  them cannot support `audited_deep` and must not silently count toward N. Record it as an explicit
  eligibility rule with its reason, or re-home the ledger entry with a named owner — but do not leave
  it `NONE` for a fifth retrospective.

### Toolchain and external facts, verified on this machine 2026-08-16

- HEAD `bc55e36`; `origin/master` identical (0 ahead / 0 behind); `git tag -l` empty; working tree
  carries six untracked non-source artifacts (`.bmad-drift-audit/`, `argusdemo/`,
  `bmad-dev-loop-pack/`, three `_bmad-output/audit-reports/` folders) — `AI-E12-12` owns them;
  **do not sweep them as part of this story**, and do not let them enter the corpus.
- Python **3.11** via `uv run --python 3.11`. Gates are **local** — `architecture.md` §H: a local run
  is necessary, never sufficient, and is labelled LOCAL. **CI evidence: NOT ESTABLISHED** for any
  Epic-10/-11/-12/-13 sha (`audit-ci.yml`'s latest run covers `00c8d1b`, 2026-08-09).
- ⚠️ **Local gates are Windows-only here; CI runs an ubuntu matrix.** A green local suite has already
  shipped POSIX-only bugs to master. Anything path-shaped in the manifest (URLs, staging dirs,
  locators) gets `pathlib` and forward-slash normalisation, not string concatenation.
- No `project-context.md` exists in this repository (searched `**/project-context.md`). The
  architecture + this file are the context.

### Previous story intelligence — traps already paid for, do not pay again

From Story 12.9 (the immediately preceding story, clean-pass review) and Epics 10-12:

1. **The premise re-measurement in §0 is not ceremony.** It has caught a materially wrong premise in
   every story since Epic 11 — including, this time, four stale citations and two action items that
   are already done. Re-measure on *your* implementation baseline (Task 1) — §0 was measured before
   you started.
2. **The artifact-currency bootstrap bites whenever `argus/**` moves.** `AI-E12-11`: ten of Epic 12's
   28 commits hit this. Sequence: commit the `argus/` delta → regenerate the artifacts → commit the
   regeneration separately. AC5 changes `argus/`, so plan for it from the first commit.
3. **Commit each story's delta as the story closes** (`AI-E10-7`). Do not implement into one dirty
   working tree — six untracked artifacts are already sitting there from previous rounds.
4. **A story record that claims a ledger closure the ledger never received is the live defect class**
   (`AI-E12-3`, `AI-E12-6` — four such claims from Stories 12.4/12.5 are still being dispositioned).
   If you write "closed `DF-8-5-C`" in the Completion Notes, the ledger must show it, in the same commit.
5. **The resumed-session integrity check** (`AI-E11-11` / `AI-E12-8`): if this session resumed after a
   transport error, re-derive state from the tree before continuing. A dev agent already died mid-story
   once and left a partially-applied change.
6. **12.6 / DN-7** — need a helper from a `_`-prefixed API? **Promote it to public**; never reach through.
7. **12.6 / DN-8** — a false registry entry is worse than a coy docstring.

### Testing requirements

- **Framework/gates, all run locally before hand-off:** `pytest` (full suite — the baseline on
  `bc55e36` is **1543 passed / 0 failed / 0 skipped**; a *skip* appearing is a regression signal),
  `mypy` (clean, 83 files), `bandit` (19 Low / 0 Medium / 0 High). Report each with its actual numbers
  in the Dev Agent Record — never "all green".
- **Test ids continue from the measured high-water marks.** `PRECISION-001-21+`, `CARTRIDGE-001-16+`,
  `DOGFOOD-001-53+`, `DOCS-001-73+`. **Open no new area** — a new area is a decision that needs a
  reason recorded, not a convenience.
- **RED-then-green is mandatory evidence, at the real seam** (`AI-E11-1` clause ii). For each new
  guard, capture in the Debug Log: the observable, the planted defect, the RED output, the fix, the
  GREEN output. Specifically —
  - **AC5**: revert `proof_run.py` to the literals → the derivation guard must go RED. A guard that
    stays green against `Fraction(0,1)`/`n=0` is vacuous and is the whole point of `DF-8-5-C`.
  - **AC2**: delete the resolution paragraph from `architecture.md` → the presence guard goes RED.
  - **AC3a/AC4**: add a manifest member with a `stars` field, and one with `eligible_for_n: False` and
    **no reason** → both must fail. Generate at least one adversarial variant **from the manifest
    itself**, not hand-written.
- **Non-vacuity**: any guard that walks a registry asserts it extracted **> 0** rows first (the `-39`
  argparse-internals precedent). A guard that silently iterates an empty manifest passes forever.
- **Determinism precondition (protocol §4)**: adjudication is only valid over a byte-reproducible run.
  If AC3b stages and audits a corpus, prove byte-identical results across two runs before recording
  anything — reusing the existing reproducibility check, not a new one.
- **The suite must not reach the network.** DN-5.

---

## Tasks & Subtasks

- [x] **Task 1 — Re-measure every §0/§0.1 premise on your implementation baseline (AC: all)**
  - [x] Re-run each measurement by execution; record confirmations *and* divergences in Debug Log §1
  - [x] If a premise has moved since 2026-08-16, say so before acting on it
- [x] **Task 2 — Take and record the governing-corpus decision (AC1)**
  - [x] Adopt DN-1 or overturn it with a stated reason; date it
  - [x] Amend `precision-validation-protocol.md` §1/§4/§5/§6 for the corpus split; append to its change log
  - [x] Amend `prd.md` at `:191`, `:196`, `:475` in strike-not-delete form
- [x] **Task 3 — Close the architecture's OPEN input, at all three sites (AC2)**
  - [x] `architecture.md:203-208`, `:800-807`, `:1244` — same words, no site left disagreeing
  - [x] Register the rule in §Enforcement (rule text + enforcing module + test ids)
  - [x] Guard asserting the resolution text is present; RED-then-green evidence
- [x] **Task 4 — Specify the validation set (AC3a, AC4)**
  - [x] `tests/corpus/_manifest.py`: `CorpusMemberSpec`, frozen tuple, closed schema that **raises** on an unregistered field
  - [x] Derived eligible-N function reusing `VALIDATION_SET_FLOOR_N`
  - [x] Record the three exclusions (self-audit, superseded Minions run, cartridges) with reasons
  - [x] Record the sourcing rule and the never-eligible fields (usage/stars/installs)
  - [x] `tests/test_validation_corpus.py` with the adversarial variants from §Testing
- [x] **Task 5 — Fix `DF-8-5-C` by derivation (AC5)**
  - [x] Derive `precision` / `n` in `proof_run.py:642-647` via the existing lazy registry edge
  - [x] Guard: rendered figure == derived figure; RED against the reverted literals
  - [x] Regenerate `minions-dogfood-proof.md` via its generator; **bootstrap sequence** per §Previous story intelligence
  - [x] Record the correction as a correction, including that it understated
- [x] **Task 6 — Populate the corpus to N ≥ 5 (AC3b — see ESCALATION)** — ✅ **RATIFIED AND EXECUTED**
  - [x] Escalate to the named operator (XAgent007) rather than self-authorising
  - [x] Operator RATIFIED 2026-08-16 and named five repositories
  - [x] Measure every candidate before admission — pin, language mix, licence
  - [x] Stage each at its pinned sha, audit through unmodified `run_audit_detailed`
  - [x] Prove byte-reproducibility across two runs — **5 of 5 reproducible**
  - [x] Emit the adjudication-ready finding set in the `finding_match_key` shape for 13.2
- [x] **Task 7 — Ledger and documents (AC6)**
  - [x] Close `DF-8-5-C` with its evidence; `+n / -0` on `deferred-work.md`
  - [x] Progress-note `DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A` with the corpus they now adjudicate
  - [x] Rule on `DF-10-2-A` or re-home it with a named owner
  - [x] Correct the protocol's three stale substrate paths
  - [x] Note the two already-satisfied action items (`AI-E10-8`, `AI-E12-1` first half) rather than redoing them
- [x] **Task 8 — Gates and hand-off**
  - [x] `pytest` / `mypy` / `bandit` with actual numbers, labelled **LOCAL**
  - [x] NFR-M1 re-measured on every touched file
  - [x] Nothing outward-facing performed; re-assert by execution (`git tag -l`, remote unmoved)

---

## ⛔ ESCALATION — the one act this story cannot give itself (AC3b)

**AC3a is fully autonomous. AC3b is not, and the boundary is deliberate.**

Populating the corpus means **fetching third-party source onto the operator's machine** and asserting
that a given repository is a legitimate member of the corpus that will clear Argus's externalization
gate. Both are operator acts:

1. **Which repositories.** Licence, provenance and independence are judgement calls with an
   accountable owner. The manifest is a *proposal* until ratified.
2. **Fetching.** Cloning external code is a network act against third-party hosts.

**The named human already exists** — `sprint-status.yaml:414`/`:416` name **XAgent007** as Engineering
Lead / protocol §2 primary adjudicator — so this is a *single explicit ratification*, not an
open-ended block.

**If ratification is not obtained in this session:** complete AC1, AC2, AC3a, AC4, AC5 and AC6 in
full, record the proposed manifest in the Dev Agent Record, and mark AC3b **HALTED — awaiting
operator ratification**, following the Story 12.9 / AC9 precedent where a halt is the *designed*
terminal state and does not block the story's pass. **Do not** populate the manifest with plausible
repository names to make a count look met — a fabricated corpus in the story that defines the corpus
is the worst available outcome.

---

## Dev Agent Record

### Agent Model Used

Claude Opus 5 (`claude-opus-5`), via the `bmad-dev-story` workflow, 2026-08-16.

### Debug Log

#### §1 — Task 1: every §0/§0.1 premise re-measured on the implementation baseline, by execution

Baseline `bc55e36` — **identical to the sha §0 was measured on**, and `origin/master == HEAD`
(0 ahead / 0 behind), so §0 was measured on the implementation baseline and no premise had time
to move. Re-measured anyway, by execution.

| Premise | Re-measured | Verdict |
|---|---|---|
| `populated_planted_defect_count()` = 7 across `distinct_rule_class_count()` = 5 | **7 / 5**, classes `cross_partition`, `hardcoded_secret`, `orphan_code`, `vacuous_test_ast`, `vacuous_test_heuristic` | ✅ CONFIRMED by import + call |
| `proof_run.py:643-644` carries the `Fraction(0, 1)` / `n=0` literals | exact, at those lines | ✅ CONFIRMED |
| `minions-dogfood-proof.md:88` renders the gate line (`:87` is blank) | exact | ✅ CONFIRMED |
| Protocol §1's three substrate paths are dead | `minions_core/apaa/precision/replay_harness.py`, `tests/apaa/cartridges/_registry.py`, `tests/apaa/test_precision_replay.py` — **none exists** | ✅ CONFIRMED |
| `architecture.md` states the OPEN input at two disagreeing sites + a third mention | `:205-212` CLOSED-as-assigned · `:800-807` "Still open" · `:1244` gap analysis | ✅ CONFIRMED |
| `VALIDATION_SET_FLOOR_N = 5` at `tests/cartridges/_registry.py:57` | exact | ✅ CONFIRMED |
| `compute_precision` at `:222`, `protocol_cleared` at `:226`, never passed `True` | exact | ✅ CONFIRMED |
| Test-id high-water marks `PRECISION-20 · CARTRIDGE-15 · DOGFOOD-52 · DOCS-72` | exact, by regex sweep over `tests/*.py` | ✅ CONFIRMED |
| NFR-M1 headroom figures (679 / 391 / 332 / 513 / 1106 / **1199**) | **all exact** | ✅ CONFIRMED |
| `git tag -l` empty; nothing published | empty | ✅ CONFIRMED |
| `AI-E10-8` — `pipeline.py` 1331 lines | **1111** — already fixed by Story 12.1 | ❌ STALE, not re-fixed |
| `AI-E12-1` first half — retro registration | already at `test_evidence_citation.py:125` | ❌ STALE, not redone |

**One measurement-method divergence found, and it matters more than it looks.** `sprint-status.yaml`
records `pipeline.py` at **1005** lines while §0 records **1111**. Neither is a typo: **1005 is what
`Get-Content <f> | Measure-Object -Line` returns**, because that idiom scores an empty line as *zero
lines*, and the file has 106 blank ones. The true physical count — `len(text.splitlines())`, which is
what `tests/test_module_size_ceiling.py` uses — is **1111**. I hit this myself on the first pass and
briefly recorded nine files as ~10% smaller than they are. Both figures are under the ceiling so no
conclusion changes, but a silently-undercounting measurement idiom is a live hazard for a project
whose maintainability standard *is* a line ceiling. Filed in the ledger under `AI-E10-8`.

#### §2 — RED evidence, captured at the real seam (AI-E11-1 clause ii), before or during each guard

| Guard | Observable | Planted defect | RED | GREEN |
|---|---|---|---|---|
| `PRECISION-001-21`..`-30` | the manifest module resolves | (none needed — written first, module absent) | `ModuleNotFoundError: No module named '_manifest'` at collection | 13 passed after `tests/corpus/_manifest.py` landed |
| `DOCS-001-73` | count of resolution paragraphs in `architecture.md` | deleted the resolution from **one of the three** sites | `AssertionError: the validation-set resolution appears at 2 site(s); it must appear at exactly 3` | restored → passed |
| `DOGFOOD-001-54` | committed artifact vs live derivation | reverted the call site to `precision=Fraction(0, 1), n=0` | artifact no longer carries the derived string → FAILED | `git checkout` → passed |
| `DOGFOOD-001-55` | `ast` read of the call site + the contract | same revert | `ast.Call`/`Fraction` detected at the `precision=` keyword → FAILED | restored → passed |

The AC5 revert was performed against the **committed** `59a2ad4`, so the RED was produced by the real
seam in the real module and restored by `git checkout`, not by editing a copy.

**A RED I did not plant, and did not weaken.** `TC-ArgusAgent-DOGFOOD-001-30` went red because my new
`derive_gate_status` **docstring** quoted the literal `protocol_cleared=True` while explaining that the
function never passes it. That guard is a deliberate substring scan over the whole `argus/dogfood/`
package. The fix was to reword the prose, not to teach the guard about docstrings — and the docstring
now says so, so the next person to trip it knows which way to fix it.

#### §3 — findings this story did not expect, and corrected rather than papered over

1. **`DF-10-2-A`'s premise is wrong about Rust**, and four retrospectives repeated it. The entry says
   C, C++, Ruby **and Rust** *"ground cleanly and extract zero definitions"*. Measured by running
   `build_ast_index` over a probe per language: **three hold, Rust does not** — Rust extracts its
   `struct_item` and misses only functions, because the extractor's vocabulary entry is `fn_item`,
   **a node type `tree-sitter-rust` does not emit** (the real one is `function_item`), so it matches
   nothing. C/C++ fail differently again: `function_definition` *is* in the vocabulary, but those
   grammars carry the name under a `declarator` field while `_node_name` reads `name` only, so every
   definition is matched and then dropped for having no name. Ruby is a pure vocabulary gap
   (`method`/`class` vs `method_definition`/`class_definition`). Rust **stays ineligible** on the
   narrower correct ground, and `AST_INELIGIBILITY_REASONS` now records the mechanism per language
   instead of the slogan. `-30` re-measures the set on every run, in both directions, so the ruling
   cannot rot. **The detector gap itself is NOT fixed here** — no AC owns it and it would change
   grounding across four languages.
2. **Closing `DF-8-5-C` the way the ledger specified would have made the artifact worse.** Its close
   condition said to pass `populated_planted_defect_count()` — i.e. publish `N=7 … floor N=5`, which
   reads as **floor MET** for a gate the cartridges do not gate. That condition predates this story's
   own DN-1 decision. Resolved as DN-7 below; the ledger records the divergence explicitly rather
   than quietly following or quietly ignoring it.
3. **`TC-ArgusAgent-DOGFOOD-001-45` blocked a legitimate additive export.** Its `len(surface) == 17`
   line is labelled *non-vacuity*, but the no-shrink rule it protects is already asserted six lines
   above; the equality also froze the shim against any new public name. Replaced with a **registry**
   (`_ADDED_SINCE_SPLIT`) that closes both directions — an unrecorded addition fails, and a stale
   entry for a name no longer exported fails too. The guard's stated intent is preserved and its
   population is now shrinking-by-construction, following `_EXEMPT_BY_DESIGN`.
4. **Two of my own guards were too narrow and were tightened, not relaxed.** `-25` originally
   rejected the *substring* `VALIDATION_SET_FLOOR_N = ` and so failed on the manifest's own prose
   explaining DN-3; it now reads the module with `ast` and forbids a second **binding**. `-76`
   originally permitted the dead protocol paths only inside a `>` blockquote and so failed on the
   append-only change-log row that must name what it corrected; the permitted record contexts are
   now enumerated **with reasons**, plus a direct assertion that no §1 substrate *bullet* points at
   a dead path — which is the surface the defect actually lived on.

#### §4 — measured environment facts that changed the design

- **`build_dogfood_proof` is reachable only from `scripts/regenerate_dogfood_artifacts.py`**, never
  from the CLI (measured by import sweep). So the corpus substrate is always resolvable when the
  proof runs, and the built-distribution branch of `measure_validation_corpus()` is defensive.
  It still **records** unavailability rather than zeroing, because a zero meaning "not consulted"
  and a zero meaning "measured, and it is zero" are different facts — which is the whole content
  of `DF-8-5-C`.
- **The ten tree-sitter grammars are core dependencies**, not the `[languages]` extra (Story 12.5
  moved them). So `-30` **asserts** the grammar imports instead of using the `importorskip` idiom
  its twenty sibling files use: after 12.5 their absence is a packaging regression, and DN-5 forbids
  a silent skip where the honest outcome is a recorded failure. The deviation is deliberate.
- **The NFR-M1 sweep reads the git INDEX**, so every new file was `git add`-ed on creation.
- **`_ratio_string` / `Fraction` only** — no float was introduced anywhere (AR4).

#### §5 — gates, all LOCAL (architecture.md §H: a local run is necessary, never sufficient)

| Gate | Result | Baseline |
|---|---|---|
| `pytest` (full suite) | **1560 passed / 0 failed / 0 failed-errors / 0 skipped**, 338.3s, exit 0 | 1543 → **+17** (13 `PRECISION-001-21..-30` + `DOGFOOD-001-53..-55`; 4 `DOCS-001-73..-76`) |
| `mypy argus` | **Success: no issues found in 83 source files** | 83 files, clean — unchanged |
| `bandit -r argus` | **19 Low / 0 Medium / 0 High** (confidence 0 Low / 6 Med / 13 High) | identical to baseline |
| NFR-M1 (≤1200) | replay_harness **575** · proof_run **741** · `_manifest` **406** · `test_validation_corpus` **719** · `test_validation_set_decision` **340** · `test_dogfood_module_split` **331** | no file within 400 lines of the ceiling |
| `deferred-work.md` append-only | `git diff --numstat` → **166 / 0** | `+n / -0` satisfied |

**CI evidence: NOT ESTABLISHED.** No CI run covers any Epic-10/-11/-12/-13 sha; `audit-ci.yml`'s
latest run covers `00c8d1b` (2026-08-09). ⚠️ **These gates ran on Windows only**; CI runs an ubuntu
matrix, and a green local suite has previously shipped POSIX-only bugs to master. Every path in the
new code is `pathlib`-based; the manifest stores URLs and shas, not filesystem paths.

**Nothing outward-facing was performed**, re-asserted by execution at hand-off: `git tag -l` is
**empty**, and `origin/master` is still **`bc55e36`** — unmoved. No push, no tag, no release, no
visibility change. `DF-12-9-A` is untouched.

#### §6 — decisions taken, with their rejected alternatives

- **DN-1 — ADOPTED as recommended. The PRD governs; the protocol is amended.** Rejected: let the
  protocol govern and amend the PRD down to cartridges — which makes the externalization gate
  clearable by a corpus the team authored, planted and wrote the answers to. The cartridges are
  re-labelled as the recall instrument they always were (FR20); nothing in `tests/cartridges/`
  changed.
- **DN-2 — ADOPTED. The cartridge registry is reused, never extended.** Rejected: a `real_repo`
  kind on `CartridgeSpec`. `-24` asserts the two id spaces are disjoint in both directions.
- **DN-3 — ADOPTED. One floor, two populations.** `validation_floor_n()` resolves the 6.5 constant
  through the declared lazy edge. Rejected: a second constant — which is how two corpora happened.
- **DN-4 — ADOPTED. Pinned and fetched, never vendored.** Enforced at construction: an eligible
  member without a 40-hex sha raises. `-28` asserts `tests/corpus/` holds no third-party file.
- **DN-5 — ADOPTED. Guards are network-free**, proven by an `ast` closure over the manifest's
  imports rather than by assertion.
- **DN-6 — ADOPTED, with a measured correction to its premise.** See §3.1. Ruled as a
  corpus-eligibility rule enforced in `__post_init__`, not as a detector story.
- **🆕 DN-7 — `DF-8-5-C`'s published `n` is the REPOSITORY corpus, not the cartridge count.**
  Rejected: the ledger's literal close condition, `n = populated_planted_defect_count()` = 7, which
  would publish *"N=7 … floor N=5"* — reading as **floor met** for a gate the cartridges do not
  gate, a worse statement than the one it replaced and in the **over-claiming** direction. Under
  DN-1 the gate's `N` is the repository corpus, measured at 0. **The published number is the same
  `0` it always was; what changed is that it is a measurement of a named population instead of a
  literal, and it now says which population it counts.**
- **🆕 DN-8 — `precision` is `None` ("NOT COMPUTED BY THIS RUN"), not `Fraction(0, 1)`.** Rejected:
  keeping a zero ratio, and rejected: computing a real precision inside the dogfood generator. This
  generator audits a repository and never invokes the replay harness, so `precision=0/1` claimed a
  measurement that had not been made. `precision=None` with `provisional=False` now **raises**: a
  run that computed no number is structurally incapable of reporting a cleared gate.
- **🆕 DN-9 — `population_label` is a parameter, defaulting to the existing wording.** Rejected:
  changing the noun globally, which would have altered `compute_precision`'s output bytes and broken
  NFR-P1 byte-stability for a surface that legitimately *does* count cartridges. Rejected also:
  leaving the noun alone, which would have published a repository count described as "cartridges" —
  a new false statement introduced by the change that removed an old one.
- **🆕 DN-10 — the AC2 guard is a new module, not four assertions in `test_evidence_citation.py`.**
  That file measured **1199/1200**. The sanctioned remedy is a cohesion split, never shaving; and
  splitting a load-bearing guard file belongs to a story that says so. Recorded in the new module's
  docstring, per AC3's instruction to record the choice and the reason.

### Completion Notes

**AC1 ✅** — DN-1 adopted and dated. `precision-validation-protocol.md` amended at §1 (corpus
distinction + the new gate ground truth), §4 (method applies to both corpora; a real repository has
no golden key, so every blocking finding is adjudicated individually), §5 (the cartridge-floor row
**struck in place**, replaced by the validation-set floor; a recall row added), §6 (the repository
corpus's R1–R4 plan added beside the retained cartridge history), with a **V1.1 change-log entry**.
§2 roles, §3 budget and §7 invariants deliberately unchanged. `prd.md` amended at `:191`, `:196`,
`:373` and `:475` in strike-not-delete form.

**AC2 ✅** — the architecture's last OPEN input is closed **by decision**, in the **same words at all
three sites** (§Architectural Decisions, §Still OPEN, §Gap Analysis), each stating which definition
won, why, and that closing the input does not clear the gate. Registered in §Enforcement with rule
text, both enforcing modules and test ids. Guarded by `TC-ArgusAgent-DOCS-001-73`..`-76`, which
**count** occurrences rather than checking presence — a presence check would pass with one site fixed
and two contradicting, which is exactly what happened in 2026-08-10b.

**AC3a ✅** — `tests/corpus/_manifest.py`: a frozen `CorpusMemberSpec` tuple mirroring `_registry.py`'s
shape, each member carrying URL, pinned sha, licence, primary language, provenance and
`eligible_for_n` with a required reason when false. The floor is **derived**
(`eligible_member_count()` against the reused `VALIDATION_SET_FLOOR_N`), never transcribed. The three
exclusions are recorded **in the manifest**: the self-audit (`provenance: self`), the superseded
Minions run (`provenance: superseded`), and the cartridges — which are not members at all, asserted
in both directions.

**AC3b ✅ RATIFIED AND EXECUTED** — escalated rather than self-authorised; the operator (XAgent007)
ratified on 2026-08-16 and named five repositories. Each was **measured before admission**, not
accepted on description. **N = 5, floor MET.**

| Member | Pin | Language (measured) | Verdict | Blocking | Total | Deep | Repro |
|---|---|---|---|---|---|---|---|
| `ai-body-runtime` | `4480ffd` | python 15 | `RELEASE_READY` | 0 | 13 | 2/3 | ✅ |
| `agent-markovich` | `a561668` | python 65 | `INSUFFICIENT_COVERAGE` | 0 | 272 | 24/65 | ✅ |
| `minions` | `ec63b72` | python 591 | `NOT_READY_FOR_RELEASE` | **24** | 2946 | 74/197 | ✅ |
| `xagents-webapp` | `33a8652` | typescript 810 | `INSUFFICIENT_COVERAGE` | 0 | 1507 | 513/862 | ✅ |
| `agent-smith` | `9ab774d` | ts 226 / py 168 / rust 34 | `NOT_READY_FOR_RELEASE` | **7** | 1280 | 72/145 | ✅ |

**31 blocking findings — the precision denominator 13.2 adjudicates — and every one is
`vacuous_test_ast`,** the moat detector. 5987 advisory findings are recorded but are not false
accusations and do not enter the denominator (protocol §4, as amended). Delivered as
`validation-corpus/adjudication-set.json` (machine, 2 MB) plus `blocking-worklist.md` (the 31 a
human actually judges — a 2 MB JSON is a machine artifact, and an adjudication list nobody can read
is an adjudication that does not happen).

**Three things AC3b did NOT do.** It pre-adjudicated nothing — every TP/FP field is `null` and
`-31` asserts they stay null. It cloned nothing — fetching is the operator act the escalation
exists for, so the runner reads existing checkouts and **verifies each against its pin, refusing on
mismatch**. And it fabricated nothing: `ai_body_runtime` was not a git repository at ratification and
was therefore unpinnable and unadjudicable, which was **escalated rather than worked around** —
`git init` was performed only on the operator's explicit instruction, and the manifest row records
that the pin has content but no history.

**The corpus's honest limitations, recorded per member rather than in a footnote.** `minions`
carries the strongest caveat: **Argus was developed against it** — it began life inside that repo as
`minions_core/apaa/` and Story 7.2 ran over it — so a high precision score there is the least
transferable evidence in the corpus, and the repository corpus has no author-blind holdout mechanism
to offset it the way the cartridges do. `xagents-webapp` is the opposite and the most valuable: 810
TypeScript files against a detector suite written almost entirely for Python. And `independent` here
means **not the tool auditing itself** — not third-party; all five are XAgents repos and four are
agent-authored, which is exactly what the PRD specifies and is still the corpus's main limitation.

**AC4 ✅** — "usage is not evidence" is a **schema property**: `MANIFEST_FIELDS` is closed and checked
in both directions, `NEVER_ELIGIBLE_FIELDS` enumerates the ban (stars, installs, downloads, …), and
an unregistered member **raises** (`UnregisteredCorpusMember`, the `DF-10-4-E` shape). The sourcing
rule is recorded: source from anywhere, admit only on adjudication.

**AC5 ✅** — `DF-8-5-C` closed by derivation. `derive_gate_status()` reads both corpora through the
declared lazy edges; the artifact was regenerated through its own renderer via the `DF-8-5-B` /
`DF-10-4-D` bootstrap (commit `argus/` at `59a2ad4` → regenerate → commit separately at `2e2e089`).
The correction is recorded **as a correction**, including that the literal *understated* and
therefore never made a gate look cleared — and including why the ledger's own close condition was
not followed literally (DN-7).

**AC6 ✅** — `deferred-work.md` `+166 / -0`. `DF-8-5-C` closed against evidence; `DF-6-6-A`/`-P1`/
`-P2`/`DF-7-2-A` progress-noted with the corpus they now adjudicate and why `DF-7-2-A` is
unperformable as written; `DF-10-2-A` **ruled** with a dated decision and a named owner, its premise
corrected by measurement; the protocol's three dead substrate paths corrected; `AI-E10-8` and
`AI-E12-1`'s first half recorded as already-satisfied rather than redone. No guard is narrower than
its AC, every new guard names its observable, moves at the real seam and generates at least one
adversarial variant from the registry it closes over.

**The gate did not move, and could not have.** `protocol_cleared` is still `False` and still never
passed `True` anywhere in the tree; `precision_gate_status()` is unflipped; the validation set
reports `N = 0` **derived**; and the harness now *raises* if asked to render a cleared gate from a
run that computed no precision. This story makes 13.2 possible; it satisfies none of the four §5
clearing conditions and does not try to.

### File List

**NEW**

| Path | What |
|---|---|
| `tests/corpus/_manifest.py` | AC3a/AC4 — the validation-set manifest: `CorpusMemberSpec`, `VALIDATION_CORPUS`, the closed schema, the derived floor, the DN-6 language ruling |
| `tests/test_validation_corpus.py` | `TC-ArgusAgent-PRECISION-001-21`..`-30`, `TC-ArgusAgent-DOGFOOD-001-53`..`-55` |
| `tests/test_validation_set_decision.py` | `TC-ArgusAgent-DOCS-001-73`..`-76` — the decision is recorded at every site that states it |

**MODIFIED**

| Path | What |
|---|---|
| `argus/precision/replay_harness.py` | `registry_module()` promoted public (12.6/DN-7) with `_registry_module` kept as an alias; `corpus_manifest_module()` added; `ValidationCorpusMeasurement` + `measure_validation_corpus()`; `precision_gate_status_for` takes `precision: Fraction \| None`, `corpus_note` and `population_label`, and raises on a not-computed precision with `provisional=False` |
| `argus/dogfood/proof_run.py` | `derive_gate_status()` replaces the `DF-8-5-C` literals; `PRECISION_PROTOCOL_PATH` declared once; `__all__` + imports updated |
| `tests/test_dogfood_module_split.py` | `-45`: the `len(surface) == 17` freeze replaced by the `_ADDED_SINCE_SPLIT` registry, closing both directions (§3.3) |
| `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` | AC1/AC6.1 — §1, §4, §5, §6 amended; three dead substrate paths corrected; V1.1 change-log entry |
| `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` | AC1 — `:191`, `:196`, `:373`, `:475` amended strike-not-delete |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | AC2 — the resolution at all three sites + the §Enforcement registration |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | AC6 — append-only `+166 / -0` |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` | AC5 — regenerated by its own renderer |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` | regenerated in the same pass (provenance sha + LOC) |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` | regenerated in the same pass |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | status transitions |
| `_bmad-output/design-artifacts/ArgusAgent/stories/13-1-…md` | this file |

### Review Findings

<!-- The reviewer writes findings HERE, in this file, not only into sprint-status.yaml (AI-E12-10). -->

#### code-review 2026-08-16 (iteration 1) — 3 layers on Sonnet, 9 findings, 1 dismissed

Layers: Blind Hunter (adversarial general) · Edge Case Hunter (path-walking) · Acceptance Auditor
(diff vs this spec). All three ran with **no** conversation context and were told that the author's
own Completion Notes are not evidence. **All three independently raised R1 as High** — the strongest
possible signal, since none could see the others' output.

**Verdict: CHANGES REQUESTED.** Every AC is *structurally* satisfied — the Auditor verified AC1,
AC2, AC3a, AC3b, AC4, AC5, AC6 and every "What it is NOT" red line as met — but the story shipped a
**stale published figure that a guard now freezes**, which is the exact defect class the story
exists to delete.

- [ ] **[Review][Patch] R1 (HIGH) — the corpus count is stale at `N = 0` in every hand-written decision document, and `-75` FREEZES it** [`tests/test_validation_set_decision.py:86`, `:203`]
      Live truth: `eligible_member_count() == 5`, `meets_validation_floor() == True`. Still asserting
      zero: `prd.md:196` (*"Measured 2026-08-16: N = 0 eligible members … awaiting operator
      ratification"* — the ratification happened the same day), `precision-validation-protocol.md:191`
      + its V1.1 change-log row, `architecture.md:227`/`:839`/`:1318` (all three resolution sites),
      and `deferred-work.md:4036`/`:4044` (`DF-13-1-A`, *"it was **not performed**"* — flatly false).
      Also stale in four docstrings: `tests/corpus/_manifest.py:25`/`:302`,
      `argus/dogfood/proof_run.py:615` (*"measured, and currently 0"* — the function returns 5),
      `tests/test_validation_corpus.py:23`/`:113`.
      **Root cause:** AC1/AC2/AC6 were written when the corpus genuinely was empty; AC3b then
      populated it, and only the *derived* surfaces followed. The derived artifact
      (`minions-dogfood-proof.md`) is correct **because** it is derived — which is the story's own
      thesis proving itself, and the prose proving the converse.
      **Worst part:** `-75` requires the literal string `` `N = 0` eligible members `` to be present
      in `prd.md`, so a guard written to protect the record now *enforces the falsehood* and keeps
      the suite green. `deferred-work.md` is append-only, so `DF-13-1-A` needs a correcting appended
      entry, never an edit.
- [ ] **[Review][Patch] R2 (HIGH) — `measure_validation_corpus()` conflates two independent resolutions: it mislabels which substrate failed and publishes a real `n` beside "NOT CONSULTED"** [`argus/precision/replay_harness.py:478-484`]
      `validation_floor_n()` routes through `registry_module()`, so if the manifest resolves but the
      cartridge registry does not, the single `try` reports `validation_set_n=5` **and**
      `validation_set_available=False`, and `corpus_note()` renders *"the repository corpus manifest
      was NOT CONSULTED by this run"* — blaming the wrong substrate while publishing a number it
      claims not to have read. Self-contradictory output from the module written to stop exactly
      that (`DF-8-5-C`). Confirmed by probe. Second half: the bare `except Exception` also swallows
      `ValueError` from `CorpusMemberSpec.__post_init__`, so a genuinely broken manifest row reports
      as ordinary absence. Both branches are `pragma: no cover`.
- [ ] **[Review][Patch] R3 (HIGH) — a non-reproducible member renders as "0 blocking — nothing to adjudicate" and is persisted before the failure fires** [`scripts/audit_validation_corpus.py:263-266`, `:347-360`, `:366-374`]
      Findings are withheld when `reproducible=False` (correct), but the worklist builder then folds
      an empty list and writes *"## member — 0 blocking / No blocking finding. Nothing to adjudicate
      for this member."* to `blocking-worklist.md` — byte-identical to a genuinely clean member — and
      writes it to disk **before** the `non_repro` check returns exit 2. A human reading the artifact
      rather than the exit code is actively misled about the corpus that gates externalization.
      *(Reviewer rated Med; raised to High — an artifact that cannot distinguish "clean" from
      "withheld" is the honesty defect this epic exists to remove.)*
- [ ] **[Review][Patch] R4 (MED) — `floor_n=None` crashes with a re-raised `ImportError` instead of the degradation its docstring promises** [`argus/precision/replay_harness.py:554`]
      `measure_validation_corpus()` documents that an unresolvable substrate is *recorded*, not
      fatal; `precision_gate_status_for` then does `registry_module().VALIDATION_SET_FLOOR_N if
      floor_n is None`, re-raising uncaught. Failing loudly is the right behaviour here — but the
      docstring must say so, and the failure should be typed and explained rather than a bare import
      error surfacing from a second lookup.
- [ ] **[Review][Patch] R5 (MED) — the documented exit-code contract is wrong; the `SystemExit` handler is dead code** [`scripts/audit_validation_corpus.py:184-195`, `:284-290`]
      `SystemExit` derives from `BaseException`, so `except (DogfoodProofError, Exception)` never
      catches it and `if isinstance(exc, SystemExit): raise` can never run. `raise SystemExit(<str>)`
      exits **1**, while the module docstring documents **2** for a pin mismatch or a missing
      checkout. Verified by probe. Raised independently by two layers.
- [ ] **[Review][Patch] R6 (MED) — `--map id=<absolute path>` silently escapes `--checkout-root`** [`scripts/audit_validation_corpus.py:267`, `:290`]
      `Path("C:/root") / "D:/elsewhere"` → `D:\elsewhere` (pathlib discards the left operand on an
      absolute right). The metavar promises `RELATIVE_PATH` and nothing enforces it. The pin check
      still runs, so a wrong tree is usually caught — but the audited location is unconstrained.
- [ ] **[Review][Patch] R7 (MED) — `.git`-as-a-file checkouts (git worktrees, submodules) are refused as "no git checkout"** [`scripts/audit_validation_corpus.py:279`]
      `(checkout / ".git").is_dir()` is `False` for a worktree or submodule, both fully valid
      repositories. Would have blocked the operator for a legitimate layout.
- [ ] **[Review][Patch] R8 (LOW) — `--map` without `=` dumps a raw traceback** [`scripts/audit_validation_corpus.py:267`]
      `dict(pair.split("=", 1) ...)` raises `ValueError: dictionary update sequence element #0 has
      length 1`. Every other failure path in this script prints a clean `REFUSED —`.
- [ ] **[Review][Patch] R9 (LOW) — `head.stdout.decode()` lacks `errors="replace"`** [`scripts/audit_validation_corpus.py:184`]
      Inconsistent with `_tracked_sources`, which tolerates bad bytes. Only bites on corrupted git
      state, but the inconsistency is the kind that outlives the reason for it.

**Dismissed as noise (1):** `architecture.md` at 1354 lines against NFR-M1's 1200-line ceiling —
NFR-M1's population is `git ls-files -- '*.py'` (`tests/test_module_size_ceiling.py:156`); markdown
is outside its stated scope. The Auditor flagged and self-cleared this.

**Explicitly cleared by the Auditor, verified against the tree rather than the story's prose:** the
resolution paragraph is byte-identical at all three architecture sites; the floor is derived, never
forked (checked by `ast` walk); `deferred-work.md` is `+166/-0`; `tests/cartridges/_registry.py` is
untouched; 0 of 6018 findings are pre-adjudicated; no source byte appears under `tests/corpus/` or
`validation-corpus/`; `protocol_cleared=True` appears in no production module; thresholds unmoved;
`git tag -l` empty and nothing pushed. The Blind Hunter separately re-verified the DN-6 grammar
claims against the real `tree-sitter-rust`/`-c` grammars and confirmed them accurate, not overstated.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-08-16 | v0.4 | **AC3b RATIFIED AND EXECUTED — all 7 ACs complete; status -> review.** Operator named five repositories; each measured before admission. N=5, floor MET. All five byte-reproducible across two runs. 31 blocking findings (24 minions + 7 agent-smith, all `vacuous_test_ast`) emitted adjudication-ready for 13.2, nothing pre-adjudicated. `ai_body_runtime` was unpinnable (no git) and was escalated, not worked around. Gates LOCAL: pytest **1561/0/0**, mypy clean 83 files. | Developer (dev-story) |
| 2026-08-16 | v0.2 | AC1–AC6 implemented. DN-1 adopted: the PRD governs, the protocol amended not replaced. The architecture's last OPEN input closed **by decision** at all three sites with a counting guard. Validation-set manifest built with a closed schema and a derived floor. `DF-8-5-C` closed by derivation + artifact regeneration (DN-7/DN-8: the gate's `N` is the repository corpus and `precision` is *not computed*, not zero). `DF-10-2-A` ruled with its premise corrected by measurement — Rust extracts structs, so the ledger's "zero definitions" was wrong for one of its four languages. Gates LOCAL: pytest **1560/0/0**, mypy clean 83 files, bandit 19 Low / 0 Med / 0 High. Nothing outward-facing. | Developer (dev-story) |
| 2026-08-16 | v0.1 | Story contexted. Premises re-measured on `bc55e36`; four stale epic citations, one off-by-one, two already-satisfied action items and three dead protocol paths recorded in §0. | Scrum Master (create-story) |
