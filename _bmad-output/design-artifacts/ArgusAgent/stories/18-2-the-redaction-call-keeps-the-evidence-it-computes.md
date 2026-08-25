---
baseline_commit: c288d40
---

# Story 18.2: The redaction call keeps the evidence it computes

Status: done

<!-- Contexted 2026-08-24 at HEAD `c288d40` (branch `docs/merge-strategy-decision`) by the
     create-story workflow (Opus 5).

     ⛔ EVERY FIGURE IN §0 WAS READ OFF THIS TREE BY EXECUTION, not copied from `epics.md`, from
     `sprint-change-proposal-2026-08-24.md`, from `DF-AUD-DETECT-B` or from Story 18.1's record.
     The dead call was proven dead by AST and then by running the shipped `SecretScanDetector.run()`
     over all 251 tracked `*.py` files with `_evidence_for` replaced by a null body, comparing every
     `DetectorResult` field-for-field. The candidate guard was proven RED against the SHIPPED body
     before this story was written. Where an artifact and the tree disagree, §0 says so and THE TREE
     WINS.

     ⛔ NO `argus/`, `tests/`, `scripts/` OR ARTIFACT FILE WAS TOUCHED TO PRODUCE THIS STORY. Every
     simulation was monkeypatching of module attributes inside a throwaway interpreter driven from a
     scratch directory outside the repository.

     ⚠️ THE WORKING TREE WAS ALREADY DIRTY AT CONTEXTING, AND NOT WITH THIS STORY'S WORK: Story
     18.1's review-round record (`deferred-work.md`, `sprint-status.yaml`, `18-1-…md`) is
     modified-but-uncommitted at `c288d40`. See §0.0 and §2.6 — those three files are NOT this
     story's to commit, and `git add -A` would swallow them.

     ⛔ NOTHING HERE SPENDS `DF-13-5-A`. No member is ratified, no protocol row is added, no FR is
     amended, no third-party source is fetched.

     ⚠️ THE EPIC'S STORY TITLE NAMES ONE ARM OF ITS OWN AC AND THE MEASUREMENT SELECTS THE OTHER.
     The AC reads *"either the evidence is retained and used, or the call is deleted — and the choice
     is recorded with its reason."* §0.4 measures the reason. See `DN-18-2-1` and AC7. The title is
     kept verbatim because a story does not edit `epics.md`. -->

## Story

As the **Engineering Lead**,
I want **`run()`'s producer-side redaction call to stop computing evidence it throws away, and the banner above it to stop naming a guarantee that line does not provide**,
so that **a call that reads as load-bearing either is, or is gone — and the redaction guarantee is carried by a guard instead of by a comment.**

### What this story IS

The discharge of **`DF-AUD-DETECT-B`**. One statement decides it:

- `argus/detectors/secret_scan.py:506` — `self._evidence_for(match)`, under the banner
  `# ── PRODUCER-SIDE REDACTION (the keystone) ──` at `:505`. `_evidence_for` is a pure
  `@staticmethod` returning a frozen `SecretFindingEvidence` (`:383`). **The return value is bound
  to nothing.** Measured by AST: it is the module's ONLY expression-statement that discards a
  `_evidence_for` return; the other call site (`:376`, inside `scan_evidence`) uses its return and
  is genuine.

The story **deletes the statement**, **replaces the banner with what is actually true**, corrects
**one measured false sentence** in the same module's docstring, and lands **three guards** that make
the defect unable to recur and pin the FR28 guarantee the entry calls structural.

⛔ **The evidence CARRIER is not deleted.** `SecretFindingEvidence`, `SECRET_EVIDENCE_SCHEMA_VERSION`
and `scan_evidence()` survive unchanged — `tests/test_v1_commitment_closure.py:510` pins **FR28's
delivery** to the literal `class SecretFindingEvidence(` in this very file (§0.6).

### What it is NOT

- ⛔ **NOT a schema widening.** `DetectorResult` does not gain an evidence field; neither does
  `Recording`; neither does `FindingDraft`. §0.4 measures why: **Story 2.5's own record locks the
  opposite** — *"`SecretFindingEvidence` is **NOT** folded into `DetectorResult` and is NOT
  persisted"* (`2-5-…md:613`). Reversing a `done` story's locked decision is **AC7**, an escalation,
  not a story decision.
- ⛔ **NOT a change to any detector OUTPUT.** AC2 requires `run()`'s `DetectorResult` to be identical
  for all 251 tracked `*.py` files, before and after. No finding moves, no count moves, no verdict
  moves.
- ⛔ **NOT a `code_identity` bump.** `FROZEN_DETECTOR_SET`'s `secret_scan.v1`
  (`argus/cache/key.py:187`) stays: bumping it invalidates every cached result for a change that is
  provably output-neutral (AC2.3).
- ⛔ **NOT a touch of `argus/detectors/base.py`.** Its `FindingDraft` docstring names two fields the
  model does not have (§0.3/(c)) — that module is **Story 18.4's** fence, and this story records the
  measurement without fixing it (`AI-E9-8`).
- ⛔ **NOT `argus/detectors/secret_suppression.py`.** Story 18.1 is `done`; its module is not
  reopened and none of `TC-ArgusAgent-SECRET-001-23`..`-27` is edited.
- ⛔ **NOT the regex precision work** (`DF-AUD-DETECT-E` → Story 18.3) and **NOT the `Detector`
  Protocol** (`DF-AUD-DETECT-F` → Story 18.4). Touching either steals a later story's RED.
- ⛔ **NOT a performance story.** §0.2 measures the dead call at **0.4%** of a full sweep.
  `DF-AUD-DETECT-C` is **not** dispositioned by it and no performance claim may be made from it.
- ⛔ **NOT a disclosure feature.** `DF-10-3-B` stays OPEN and untouched.
- ⛔ **NOT a verdict move.** Every `hardcoded_secret` finding is `advisory=True,
  depth_supported=None` by construction. The ≥80% precision keystone stays **NOT CLEARED** and the
  gate stays `BLOCKED`.
- ⛔ **NOT an epic-16-or-earlier reopening.** Epics 1–16 are `done`. Story 2.5's and Story 10.3's
  closed records are cited, never edited.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `c288d40`

⛔ **Task 0 re-derives every row below before a line is written.** Six consecutive epics in this
repository found a stated premise false by executing it; this contexting pass already found **three**
(§0.3/(b), §0.3/(c), §0.4). The figures here were true on 2026-08-24 on a Windows host; **they are a
baseline to re-measure, not a fact to cite.**

### §0.0 The tree, the paths and the baseline

| fact | value at contexting |
|---|---|
| repo root | `d:/ProjectX/XAgents/XAgents/ArgusAgent` |
| HEAD | `c288d40f4550a1ed2365d2c1e5ab230f32bf7016` (`c288d40`) |
| branch | `docs/merge-strategy-decision` |
| last commit touching `argus/` | `ee7e252` — Story 18.1's `feat` |
| `git status --porcelain` | ⚠️ **NOT empty** — three Story-18.1 review-round files (below) |
| python | 3.11.15 (MSC v.1944, 64-bit) |
| tests collected under `tests/` | **1,721** (`--collect-only`, summed per module) |
| full suite | **exit 0** (`python -m pytest tests/ -q`, re-run at this HEAD) |
| the five secret-domain test modules | **58 passed** |
| `python -m mypy argus` | **Success: no issues found in 95 source files** |
| `argus/detectors/secret_scan.py` | **575** lines (NFR-M1 ceiling 1,200) |
| `argus/detectors/base.py` | 204 lines — ⛔ NOT touched (Story 18.4's fence) |
| `argus/detectors/secret_suppression.py` | 301 lines — ⛔ NOT touched (Story 18.1, `done`) |
| `argus/pipeline.py` / `argus/pipeline_stages.py` | **1,111** / 512 lines — ⛔ neither is touched |
| `tests/test_secret_scan.py` | 222 lines |
| `deferred-work.md` | **546,616 bytes**, **0** CRLF, **exactly one** lone `\r` |
| tracked `*.py` (`git ls-files -- '*.py'`) | **251** |

⚠️ **THE TREE IS DIRTY AND IT IS NOT YOURS.** At contexting `git status --porcelain` lists exactly:

```
 M _bmad-output/design-artifacts/ArgusAgent/deferred-work.md
 M _bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml
 M _bmad-output/design-artifacts/ArgusAgent/stories/18-1-the-sentinel-table-...-of-them.md
```

That is Story 18.1's **review-round** record (`+19/-0` on the ledger, the `done` transition, the
Review Findings subsection) — carried by neither this session nor `c288d40`. ⛔ **Stage by explicit
path: `git add -A` / `git add .` would swallow a peer session's uncommitted work into your commit**
(§2.6). Re-check the list at Task 0 — it may have been committed by then, and it may have grown.

⚠️ **`argus/pipeline.py` IS 1,111 LINES, NOT THE 1,331 THE CODE SAYS.** `secret_scan.py:467` records
*"`argus/pipeline.py` is byte-fenced to Story 12.1 (1331 lines against the NFR-M1 cap of 1200)"* as
part of Story 10.3's design rationale. Measured today: **1,111** — under the cap, with headroom. The
comment's *number* is stale. ⛔ **Do not "fix" it**: it is a dated rationale for a decision already
taken, it is not this story's subject, and the decision it justifies is not being reopened. It is
recorded here so nobody re-derives an argument from a stale figure (`AI-E9-7`).

⛔ **`AI-E13-1` — the local suite is Windows-only and CI runs an ubuntu matrix.** A green local run is
recorded as **LOCAL** and never on its own discharges a cross-platform claim.

### §0.1 ⛔ THE DEAD CALL IS DEAD — proven by AST at this HEAD

```
DISCARDED-VALUE CALL STATEMENTS to _evidence_for: [(506, 'self._evidence_for(match)')]
ALL _evidence_for CALL SITES:                     [(506, 'self._evidence_for'), (376, 'self._evidence_for')]
def _evidence_for  -> line 383, decorators ['staticmethod'], returns SecretFindingEvidence
```

`ast.Expr(value=ast.Call(...))` is the exact shape of *a call whose value is thrown away*. There is
**one** in this module for this function, at `:506`, directly under the banner at `:505`. `:376` —
inside `scan_evidence` — **binds** its result. `DF-AUD-DETECT-B`'s citations resolve exactly.

Per match, `_evidence_for` computes `masked` (`"****"`), `value_length`, `kind`, `pattern_id` and a
Shannon `entropy_bits` (an exact `Fraction` over a 1e-6 rational grid) — and at `:506` all five are
discarded by the same statement that computes them.

**The region, verbatim at this HEAD (`:502`–`:518`), so the edit lands in the right place:**

```python
                continue                                                    # :502  (suppressed)

            ast_span = _ast_span_for_line(ast_entry.definitions, match.start_line)   # :504
            # ── PRODUCER-SIDE REDACTION (the keystone) ──                  # :505  ← AC1.2 REPLACES
            self._evidence_for(match)                                       # :506  ← AC1.1 DELETES
            draft = FindingDraft(                                           # :507
                file_path=file_path,
                start_line=match.start_line,
                end_line=match.end_line,
                ast_span=ast_span,
                rule_id=RULE_HARDCODED_SECRET,
                advisory=True,
                coverage_envelope_slice=coverage_envelope_slice,
            )
            findings.append(                                                # :516
                build_recording(draft, depth_supported=None, claim_present=False)
            )
```

⛔ `:502`'s `continue` and `:504`'s `ast_span` binding are **not** yours (`:502` is Story 18.1's
suppression branch). Only `:505` and `:506` move.

### §0.2 ⛔ IT IS UNOBSERVABLE — 251 files, 0 differ. And it is NOT a performance defect.

`SecretScanDetector().run()` driven over **every** file in `git ls-files -- '*.py'` (**251** files)
at HEAD, twice — once with the shipped `_evidence_for`, once with `_evidence_for = lambda m: None` —
comparing the FULL `DetectorResult` (`entries` + `findings` + `degraded`, canonical JSON) per file:

| | `hardcoded_secret` findings | files with ≥1 | files whose `DetectorResult` differs |
|---|---:|---:|---:|
| shipped `_evidence_for` | **88** | **37** | — |
| `_evidence_for` nulled | **88** | 37 | **0** |

⛔ **Zero of 251.** The statement has **no observable effect on any emitted field** — which is
`DF-AUD-DETECT-B`'s own measurement, re-derived here rather than cited.

**`_evidence_for` invocations over that sweep: 88** — exactly one per emitted finding. A suppressed
match `continue`s at `:502`, above the call, so suppressed matches never reach it.

⚠️ **THE COST IS 0.4%, RECORDED SO NOBODY CLAIMS A PERFORMANCE WIN.** Sweep wall time **1.703 s**
shipped vs **1.697 s** nulled — **0.007 s**, **0.4%**. ⛔ **This story is not a performance
improvement, and `DF-AUD-DETECT-C` (detector cost) is NOT dispositioned by it.** Writing *"and it is
faster"* into a commit message is the over-claim this repository keeps catching.

### §0.3 What an emitted finding ACTUALLY carries — and the sentences that say otherwise

Through the shipped `run()` on the non-test path `argus/prod/settings.py` carrying
`API_TOKEN = "AKIAIOSFODNN7EXAMPLE"` (**3** findings — `aws_access_key_id`,
`generic_assigned_secret`, `high_entropy_string`, all at one span), the first emitted `Recording`
serialises to:

```json
{"advisory": true, "cartridge_id": null, "claim_present": false, "coverage_envelope_slice": null,
 "depth_supported": null, "locators": [{"ast_span": null, "end_line": 1,
 "file_path": "argus/prod/settings.py", "start_line": 1}], "partition_id": "root",
 "recording_id": "hardcoded_secret:b8162401…", "rule_id": "hardcoded_secret", "schema_version": "1"}
```

Measured over that payload: **the secret is absent** (as designed), **the mask `"****"` is absent**,
and `value_length` / `entropy_bits` / `kind` / `pattern_id` are **all absent**.

**(a) The models, measured.** `DetectorResult`: `entries`, `findings`, `degraded`. `FindingDraft`:
`file_path`, `start_line`, `end_line`, `ast_span`, `rule_id`, `advisory`, `cartridge_id`,
`coverage_envelope_slice`. `Recording`: `schema_version`, `recording_id`, `partition_id`, `rule_id`,
`cartridge_id`, `advisory`, `depth_supported`, `claim_present`, `locators`,
`coverage_envelope_slice`. `Locator`: `file_path`, `start_line`, `end_line`, `ast_span`. **Not one of
the four has an evidence slot, and all four are `frozen=True, extra="forbid"`.** The structural
redaction guarantee `DF-AUD-DETECT-B` describes is real and holds with `:506` deleted.

**(b) ⛔ FOUND WHILE MEASURING — the module docstring makes a claim that payload falsifies.**
`secret_scan.py:26`–`:27` reads *"The masked indicator + the location are the ONLY things that
survive into a finding."* Measured: **only the location survives.** The masked indicator does not
enter a `FindingDraft`, a `Recording` or a `Locator` — there is nowhere to put it. Same defect class
as `:505`'s banner, same module, so **AC1.3 corrects it here**: leaving it would leave the module
still claiming exactly what this story exists to stop it claiming.

**(c) ⛔ FOUND WHILE MEASURING — and NOT fixed here, because it is another story's module.**
`argus/detectors/base.py:63`–`:72` says `FindingDraft` *"carries … the supported coverage depth (the
verdict-fold input), and the evidence the finding carries WITH it (FR10 'carrying their evidence
counts' — a JSON-primitive dict of fixed-precision/int leaves)."* Measured: `FindingDraft` has
**neither** — no `depth_supported` field, no evidence dict. ⛔ **`base.py` is Story 18.4's fence**
(`DF-AUD-DETECT-F`'s `Detector` Protocol lives in it). Greped: `deferred-work.md` carries **zero**
occurrences of `FindingDraft` outside `DF-AUD-DETECT-B`'s own paragraph, so this is genuinely
un-filed — but filing and scheduling are **`AI-E9-8`**-owned by the Engineering Lead, not by this
story. **Record it; do not fix it; do not file it** (AC4.4).

### §0.4 ⛔ THE ENTRY OFFERS TWO REPAIRS AND CALLS THE SECOND "WHAT STORY 2.5 SAYS". STORY 2.5 SAYS THE OPPOSITE.

`DF-AUD-DETECT-B` ends with this paragraph: *"Two defensible repairs, and they are not equivalent: delete the call and
correct the comment (evidence genuinely is not carried in V1), or widen `DetectorResult` to carry it
(an additive schema change under NFR-M2). ⛔ The second is the one that matches what Story 2.5 says;
the first is the one that matches what ships. Choosing is the Engineering Lead's."*

**Measured against Story 2.5's own record — both halves of it:**

| `2-5-hardcoded-secret-detector-producer-side-redaction.md` | text |
|---|---|
| `:349` (task list) | *"`FindingDraft` → `build_recording`, file graded `audited_shallow`. **Redaction in `_evidence_for`** (value computed→masked→discarded in one step)."* |
| `:613` (locked contract notes) | *"**`SecretFindingEvidence` is NOT folded into `DetectorResult` and is NOT persisted** (the 1.5 `VacuousTestScore` in-memory precedent) — it never reaches `.apaa/`; even its (redaction-safe) fields stay in memory."* |

⛔ **`:613` is a LOCKED decision of a `done` story and it forecloses the widening arm.** The entry's
sentence rests on `:349` alone; `:613`, in the same record, states the widening as a thing Story 2.5
deliberately did **not** do. Shipped code says it a third time at `secret_scan.py:367`: *"detector
evidence travels on a separate frozen model (**NOT** folded into the frozen 1.5 `DetectorResult`,
which has no evidence slot)"*.

⚠️ **This corrects the entry's REASONING, not its finding.** The finding — the call computes evidence
and discards it — is measured and true (§0.1, §0.2). Only the sentence naming the second repair as
Story-2.5-conformant is falsified, and AC4.1 records that in the **append-only** closure note without
rewriting the entry (§3.4).

**What the widening would additionally cost — measured, not asserted:**

- **A field no consumer reads.** Nothing downstream of `DetectorResult` reads evidence. The precedent
  is already filed: `argus/reports/generator.py:421` records that `DetectorResult.degraded` is
  *"recorded and no production code reads it back"* — filed as **`DF-10-4-B`**. Widening would
  reproduce that defect one layer up, in the same model.
- **A second hop to reach an operator.** The report cell is already honest without it:
  `generator.py::_finding_masked_value` (`:151`–`:164`) renders `"**** (value discarded at
  detection — NFR-S2)"`, and it reads serialized `Recording`s. Surfacing evidence therefore requires
  `Recording` to move too — the **frozen 1.2 ledger row** whose module docstring (`recording.py:10`–
  `:15`) reads *"frozen as aggressively as the verdict schema … Every field a downstream consumer
  reads is reserved at birth."*
- **Blast radius beyond one module.** `DetectorResult` is constructed by **four** detectors
  (`secret_scan`, `vacuous_test`, `orphan_code`, `tool_runner`) and consumed by
  `pipeline_stages.py:250`+ and `reports/generator.py`. A one-detector widening is an **AR7** fork; an
  all-detector widening is a different story with a different charter.

### §0.5 The FR arithmetic, measured — and FR10's own detector fails the same clause

`DF-AUD-DETECT-B` says the shipped path fails *FR10's "findings carrying their evidence counts"*.
Measured against `E-PRD/prd.md:527`–`:528` and `:573`:

- **FR10** is the **vacuous-test** FR: *"detect tests that appear vacuous … and report them as
  advisory findings carrying their evidence counts."*
- **FR11** is this detector's FR: *"detect hardcoded secrets and report them with the secret value
  **redacted**."* ⛔ **FR11 requires no evidence to be carried at all.** Deleting `:506` weakens no FR.
- **FR28** is the redaction guarantee, satisfied **structurally** (§0.3/(a)) — which is what the entry
  itself says at 🟡: *"no secret leaks and none can."*

⛔ **AND FR10's OWN DETECTOR DOES NOT CARRY ITS COUNTS EITHER — measured by execution, not read.**
`VacuousTestDetector().run()` over the `test_widget` fixture of `tests/test_vacuous_detector.py:140`
emits one finding whose full payload is `{… "depth_supported": "audited_shallow", "locators":
[{"ast_span": "function:test_widget@1-6", …}], "rule_id": "vacuous_test_ast" …}` — **no
assertion-density, no mock-ratio, no count of anything.** `vacuous_test.py:651` computes a
`VacuousTestScore` and consumes exactly two booleans off it (`heuristically_vacuous`,
`ast_corroborated`); the counts die with the local. Structurally they must: `Recording` has ten
fields and not one can hold a count.

⚠️ **So the evidence-carrying gap is REPOSITORY-WIDE and older than this entry**, and
`tests/test_v1_commitment_closure.py:425` asserts FR10 `wired` with the justification *"Advisory
findings carrying assertion-density and mock-ratio evidence"* — a claim this measurement contradicts.
⛔ **NOT this story's to fix and NOT this story's to file** (`AI-E9-8`; the write set is AC5.1). It is
**disclosed** in the completion notes (AC4.4), and it is the strongest available reason **not** to
widen one detector in isolation: the honest repair is one cross-detector story, or none.

### §0.6 THE GUARDS THAT WILL FIRE, AND THE ONES THAT WILL NOT — measured, not predicted

**WILL FIRE (plan for them):**

- **`tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`**
  (`:202`, asserting `f"**{result.total_loc}**" in text` at `:243`) and
  **`tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`**
  (`:240`, same assertion at `:273`). The three committed dogfood artifacts record **95** source
  files and **33648** total physical LOC; this story changes `secret_scan.py`'s line count, so the
  live derivation moves and these two go RED until the artifacts are regenerated.
  ⚠️ **Story 18.1 measured that `TC-ArgusAgent-DOGFOOD-001-50` did NOT fire** even though its own §0
  predicted it. **Do not chase that id**; watch these two.
- ⛔ **`scripts/regenerate_dogfood_artifacts.py` REFUSES to run on a dirty `argus/` tree** (exit
  **2**, `_refuse_if_argus_is_dirty`). The ordering is therefore forced: **commit `argus/` +
  `tests/` FIRST, then regenerate, then commit the three artifacts separately.** A commit cannot cite
  itself. That is why AC6.2's arc is **four** commits.
- ⛔ **`tests/test_gate_seal.py::test_TC_ArgusAgent_PRECISION_001_94_the_seal_precedes_every_candidate_output`**
  (`:1035`). Verified by importing `argus.precision.gate_seal` at this HEAD:
  `DETECTOR_TUNING_PATHS = ('argus/detectors', 'argus/precision/replay_harness.py')`,
  `SEAL_CITATION_TRAILER = 'Evidence-partition'`, `SEAL_CITATION_VALUES = ('sealed', 'open', 'none')`.
  **This story touches `argus/detectors`, so its `feat` commit MUST carry the whole-line trailer**
  `Evidence-partition: none` — *none* is the honest value: the change was driven by a code audit and
  by executing the shipped `run()`, and **no** corpus finding, sealed or open, informed it. ⛔ Write
  the trailer; never amend the rule. Story 18.1 lost a commit and had to rewrite a sha over exactly
  this.
- ⛔ **`TC-ArgusAgent-DOCS-001-78`** (`tests/test_governance_record_integrity.py:196`) extracts every
  `DF-*` id a **committed story file** claims to have CLOSED and cross-checks `deferred-work.md`. The
  moment this file records a closure for `DF-AUD-DETECT-B`, the ledger must already carry it — so the
  `docs` commit carries **the ledger append and this story's record together, ledger first in the
  diff**. ⚠️ This file as contexted makes **no** closure claim, so contexting leaves the guard green,
  and that was **verified by running the guard's own analyzer over this file**:
  `story_closure_claims()` returns `()`. ⛔ **It is ONE WORD from RED.** `_CLOSURE_VERB` (`:48`)
  matches the bare words `CLOSED` / `Closes` / `closes` on the same LINE as a `DF-*` id, and the
  first draft of §0.4 opened its quotation with the entry id followed by that verb, and the analyzer
  scored the line as a closure claim against a ledger that does not yet carry one. ⛔ **Do not
  reproduce the offending phrasing anywhere in this file, not even to describe it** — the analyzer is
  line-scoped and does not care that you are quoting yourself. **Re-run the analyzer over this file after
  every edit you make to it.** It should return `()` until the ledger note exists, and
  `('DF-AUD-DETECT-B',)` only from the `docs` commit onward — which is exactly why that commit
  carries both. Verify at Task 0:
  `python -m pytest tests/test_governance_record_integrity.py -q`.

**WILL NOT FIRE (verified, so you do not chase them):**

- `tests/test_v1_commitment_closure.py:510` pins **FR28** to the literal `class SecretFindingEvidence(`
  in `secret_scan.py`. It stays green **because the class is not deleted** (AC1.4). ⛔ It is the
  guard that would catch you deleting the carrier along with the call.
- `TC-ArgusAgent-RELEASE-001-11` / `-20` fire on **adding a file under `argus/`**. This story adds
  none — it edits one existing module.
- `tests/test_status_document_registry.py` — `stories/` is `_EXCLUDED_BY_DESIGN` (`:350`, enforced at
  `:471`–`:475`). ⛔ **This story file must NOT be registered there, and neither must the new test
  module**: that registry governs planning records, not code.
- `tests/test_module_size_ceiling.py` — `secret_scan.py` is 575 lines against a 1,200 ceiling
  measured as `len(text.splitlines())` (`:176`–`:183`). This story only removes lines from it. The
  **new test module** is swept by the same guard and must stay ≤1,200.
- `tests/test_command_assets.py`'s publishing corpus declares `_bmad-output/` and `tests/` as
  `_NON_PUBLISHING_PREFIXES`, so neither this story file nor the new test module enters it.

### §0.7 The ledger's byte state and the next free ids — both measured

- `deferred-work.md` at contexting: **546,616 bytes**, **0** CRLF pairs, **exactly ONE** lone `\r`
  (content — a literal `` `\r` `` inside a backtick span discussing line endings), **7,040** LF.
  ⛔ **Edit it in BINARY MODE.** A Windows text-mode write rewrites all 7,040 newlines to CRLF *and*
  eats that CR, producing a 7,000-line diff over a short append.
  ⚠️ The file is **modified-but-uncommitted** at contexting (§0.0). Re-measure at Task 0 and record
  what you find; the invariant, not the byte count, is the thing that must hold after your append.
- ⚠️ **This story file, `epics.md` and `sprint-status.yaml` are CRLF.** They are not the ledger's file
  class. Do not "normalise" in either direction.
- **Next free verification id: `TC-ArgusAgent-SECRET-001-28`.** Measured: the SECRET index in
  `tests/` is continuous `-01`..`-27` and `-27` is the maximum (Story 18.1 added `-23`..`-27`).
  ⛔ **CONTINUE it; renumbering anything invalidates citations in `architecture.md` and
  `deferred-work.md`.**
- **No new `DF-*` entry is expected.** ⛔ **Grep the ledger before filing anything** — **166** `- id:
  DF-` lines at contexting. It already carries this defect (`DF-AUD-DETECT-B`), the unread-field class
  (`DF-10-4-B`), the detector cost (`DF-AUD-DETECT-C`) and the disclosure gap (`DF-10-3-B`). Cite
  prior art rather than re-file: `DF-INV-LEDGER-A` exists because someone filed as new what this
  ledger had recorded the day before.

### §0.8 What is already true and must NOT be re-done

**(a)** `TC-ArgusAgent-SECRET-001-08` (`tests/test_secret_scan.py:118`) already asserts
`SecretFindingEvidence` has no value/secret field, and `TC-ArgusAgent-EVIDENCE-001-04`
(`tests/test_evidence_bundle.py:290`) already asserts the field-name discipline over `Recording` and
`Locator`. **Re-run them; do not rewrite them.** The new guard covers what they do not:
`FindingDraft`, `DetectorResult`, and the emitted result's own canonical bytes.

**(b)** The end-to-end containment property is already CI-blocking:
`tests/test_secret_containment.py` (`TC-ArgusAgent-SECURITY-001-01`+) varies the secret value over a
randomized population and asserts every canary absent from the ledger, every finding, the evidence
bundle, `.argus/**`, the verdict, logs, spans and exception messages. ⛔ **This story does not
reimplement it.** What that suite does **not** assert — and this story's guard does — is that the
redaction *claim in the code* is true, i.e. that nothing in `run()` depends on the discarded
computation.
⚠️ `tests/test_secret_containment.py` cannot be collected on its own (`from _cartridge import
stage_cartridge` resolves only when the whole `tests/` directory is collected). Pre-existing;
re-confirmed at this HEAD. Run it as `python -m pytest tests/ -q`, never as a single-file invocation.

**(c)** Story 18.1 already repaired `secret_suppression.py` and it is `done`. `run()`'s suppression
call at `:451` and the `continue` at `:502` are its territory. ⛔ **Do not touch either.**

**(d)** ⚠️ `secret_scan.py:519`–`:520` already carries a stray double blank line inside `run()`
(measured at this HEAD). **You did not cause it.** Removing it is harmless and optional; claiming it
as part of this story's repair is not.

---

## §1 — WHY THIS STORY EXISTS

### §1.1 A comment that names a keystone the line does not provide is a trap for the next reader

`DF-AUD-DETECT-B` files this at 🟡 rather than deleting it as tidy-up for one reason, and the reason
is measured: **Story 2.5's record describes this call as the redaction step** (`:349`), so *"a reader
checking the AC against the code finds a call that appears to satisfy it"*. That reader is this
repository's own auditor, its own reviewer, and — three times already this month — its own dev agent.
The banner is not decoration; it is the sentence that makes a no-op look load-bearing.

### §1.2 Nothing pins the claim, even though the guarantee itself is pinned

The **guarantee** is pinned end-to-end (§0.8/(b)). What is unpinned is the **claim**: that `run()`'s
redaction is structural rather than performed by that statement. Measured: delete the statement and
**0 of 251** files change (§0.2) — which is the proof, and until this story it lived nowhere.

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **No finding carries evidence afterwards**, and that is the point: V1 findings carry a location and
  flags, and after this story the code says so.
- **FR10's own evidence-count gap survives** (§0.5), disclosed and unfiled.
- **`base.py`'s `FindingDraft` docstring still names two fields it lacks** (§0.3/(c)) — Story 18.4's
  module.
- **`DF-10-3-B` (built-in suppressions are not disclosed) stays OPEN.**
- **`DF-AUD-DETECT-C` (detector cost) stays OPEN**, and the 0.4% figure does not disposition it.
- **The ≥80% precision keystone is still NOT CLEARED and the gate is still `BLOCKED`.**

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ The comment is half the deliverable. Deleting the line silently fails this story.

The entry's own framing is *"delete the call **and correct the comment**"*. A diff that removes two
lines and says nothing leaves Story 2.5's record (`:349`) pointing at a redaction step that no longer
exists anywhere in `run()`. AC1.2 requires the replacement text to state what IS true; AC1.3 requires
the docstring sentence §0.3/(b) falsifies to be corrected in the same change.

### §2.2 ⛔ The RED mechanism is known and was executed before this story was written

With `_evidence_for` monkeypatched to raise, the **shipped** `run()` **propagates the exception** —
verified at this HEAD:

```
PRE-FIX BEHAVIOUR WITH _evidence_for RAISING: run() RAISED Boom -> evidence computed
```

It propagates because `:506` sits **outside** the `try/except` at `:424`–`:432`, which wraps only
`self._scan(source)`. So the behavioural guard (`-28`) is **genuinely RED against the shipped body**
and **GREEN after the deletion**. ⛔ Per the guard-fire rule (architecture, 2026-08-23) that RED is
**author-driven** — it is **vacuity evidence**, proof the case can fail, not *"this guard caught a
defect"*.

### §2.3 ⛔ Guard vacuity — this project's signature defect, and this story's version

`AI-E14-1` / trap E.1. **This story's version:** a guard that patches `_evidence_for` and asserts
"still one finding" while building its input on a `tests/**` path — where step 5's
`DEFAULT_TEST_PATH_PATTERNS` suppresses the match for an entirely unrelated reason and the assertion
says nothing at all. ⛔ **Every case runs on the NON-TEST path `argus/prod/settings.py`**, and
`AI-E11-1` applies: assert the population is non-empty **with the real body** before asserting
anything about the patched one.

### §2.4 ⛔ Do not delete the carrier along with the call

`SecretFindingEvidence` is **FR28's delivery pin** in `tests/test_v1_commitment_closure.py:510`, and
`scan_evidence()` is the in-memory carrier Story 2.5 locked (`:613`). ⛔ Deleting either is **AC7**,
an escalation. `_evidence_for` also keeps its only remaining coverage through
`tests/test_secret_scan.py::test_scan_evidence_carrier_masks_value` (`:135`) — which is why coverage
does not move (AC2.4).

### §2.5 ⛔ The commit arc is FORCED, and it is four commits with a trailer

`chore` (this story file + `in-progress`) → **`feat`** (`argus/` + `tests/`, carrying
`Evidence-partition: none`) → `chore` (regenerate the three dogfood artifacts on a **clean** `argus/`
tree) → `docs` (ledger + this story's record, ledger first in the diff). ⛔ A commit cannot cite
itself, and the regeneration script exits **2** on a dirty `argus/` (§0.6).

⛔ **`DF-INV-MERGE-A` (OPEN, DECIDED-NOT-YET-APPLIED).** Squash and rebase merging orphan the
provenance sha a regenerated dogfood artifact cites, and `TC-ArgusAgent-DOGFOOD-001-49` then reddens
`master` **after** the merge, where no PR check can see it coming. **If the PR lands sha-rewritten,
re-run `python scripts/regenerate_dogfood_artifacts.py` on `master` and commit the result** (AC6.3).

### §2.6 ⛔ The working tree is SHARED and already dirty, and one artifact file has a byte invariant

- **A concurrent session commits to this same branch, and three of its files are uncommitted right
  now** (§0.0). ⛔ **Stage by EXPLICIT PATH. Never `git add -A`, never `git add .`.** Verify the write
  set with `git status --porcelain` — **not** `git diff --name-only`, which cannot see the new
  untracked test module.
- **`deferred-work.md` is LF-only with exactly one content `\r`** (§0.7). ⛔ **Binary-mode edits
  only**, verified after writing.

### §2.7 The idioms the guard needs, so you do not go looking for them

- ⛔ **`run()` is PURE and never opens the file.** `file_path` is a string used for path-glob matching
  and locators only. **`argus/prod/settings.py` does not exist and must not be created** — it is
  chosen because it is a plausible non-test path that `DEFAULT_TEST_PATH_PATTERNS` does not match.
- The entry the detector needs is constructed directly, no tree-sitter:
  `AstIndexEntry(file_path=<same string>, ast_eligible=True, definitions=())` from
  `argus.index.ast_index` — the `tests/test_secret_scan.py::_entry` precedent.
- Findings are counted as `[f for f in result.findings if f.rule_id == RULE_HARDCODED_SECRET]`;
  ⛔ de-duplication is on `(start_line, end_line, pattern_id)` (`:441`), so one source line can
  legitimately yield more than one finding — the `API_TOKEN = "AKIA…"` line yields **3** (§0.3).
- The AST guard reads the module's own source with `ast.parse` and looks for
  `ast.Expr(value=ast.Call(func=… "_evidence_for" …))`. ⛔ It must NOT be a blanket *"no bare call
  statements"* rule: `matches.append(...)`, `seen.add(...)` and `findings.append(...)` are legitimate
  discarded-value statements in the same file.
- Test function names follow the area convention exactly:
  `def test_TC_ArgusAgent_SECRET_001_28_<snake_case_claim>() -> None:` — the id is *in the function
  name*, which is how `tests/conftest.py`'s guard-fire recorder attributes a RED.
- Non-blocking-ness, where asserted, uses `blocking_finding_count` / `is_verdict_blocking` from
  `argus.verdict.verdict_gate` (the `-22` precedent).

---

## §3 — AC ↔ TASK MAP

*(There to be checked, not trusted. Every AC is named by at least one task; every task cites the AC it
discharges. Stories 16.5 and 16.6 each failed a readiness validation where an AC was repaired on one
side of the file and its mirror left defective in the task list.)*

| AC | discharged by |
|---|---|
| AC1 — the dead call is gone and the code stops claiming otherwise | Task 3 |
| AC2 — the change is output-neutral, proven by execution | Task 0, Task 1, Task 4 |
| AC3 — the guarantee and the non-recurrence are asserted by guards | Task 2, Task 3 |
| AC4 — the choice is recorded with its reason, append-only | Task 5 (AC4.4), Task 6 (AC4.1–AC4.3, AC4.5, AC4.6), Task 8 |
| AC5 — scope, paths, portability, ceilings | Task 2 (AC5.2), Task 3 (AC5.1, AC5.3), Task 7 (AC5.4, AC5.5), Task 8 (AC5.1) |
| AC6 — gates, dogfood regeneration, the commit arc, the trailer | Task 0 (AC6.1 baseline), Task 7, Task 8 |
| AC7 — escalate, do not decide | all tasks |

---

## Acceptance Criteria

### AC1 — THE DEAD CALL IS GONE, AND THE MODULE STOPS CLAIMING WHAT IT DOES NOT DO

- **AC1.1** — the expression-statement `self._evidence_for(match)` at `secret_scan.py:506` is
  **DELETED**. ⛔ Not commented out, not bound to `_`, not guarded by a flag: binding it to a
  throwaway name keeps the computation and keeps the lie.
- **AC1.2** — the banner `# ── PRODUCER-SIDE REDACTION (the keystone) ──` at `:505` is **REPLACED,
  not merely removed**, by text stating what is true and measurable: the redaction is **structural**
  — no emitted model has a field that could hold the value (`FindingDraft` / `Recording` / `Locator`
  / `DetectorResult`, all `frozen`, all `extra="forbid"`) — so the value is dropped by never being
  carried; `scan_evidence()` remains the in-memory evidence carrier and the pipeline does not call
  it. ⛔ The replacement must not assert anything §0 did not measure.
- **AC1.3** — the module docstring's sentence at `:26`–`:27` (*"The masked indicator + the location
  are the ONLY things that survive into a finding"*) is **corrected** to the measured fact: only the
  location survives; the masked indicator is computed by `scan_evidence()`'s carrier and never enters
  a finding. ⛔ **No other sentence in that docstring is reflowed, reordered or trimmed** — a
  whitespace-only churn over a 104-line docstring hides the one change that matters.
- **AC1.4** — ⛔ **`SecretFindingEvidence`, `SECRET_EVIDENCE_SCHEMA_VERSION`, `_evidence_for` and
  `scan_evidence()` all SURVIVE**, unchanged in name, signature, purity and behaviour.
  `__all__` is unchanged. (`tests/test_v1_commitment_closure.py:510` pins FR28 to the literal
  `class SecretFindingEvidence(` in this file.)
- **AC1.5** — `run()`'s signature, purity (AR8) and control flow are otherwise unchanged; in
  particular the suppression call at `:451` and the `continue` at `:502` are **byte-unchanged**
  (Story 18.1's territory).

### AC2 — THE CHANGE IS OUTPUT-NEUTRAL, AND THAT IS PROVEN BY EXECUTION

- **AC2.1** — ⛔ **NOTHING MOVES.** Re-derive §0.2's sweep at the story's own HEAD: `run()` over every
  file in `git ls-files -- '*.py'`, comparing the FULL `DetectorResult` (`entries` + `findings` +
  `degraded`) per file, before and after. **The set of differing files must be EMPTY**, and the
  finding total must be unchanged. Baseline at `c288d40`: **251 files, 88 findings, 37 files with
  ≥1, 0 differing.**
- **AC2.1a** — ⛔ **BOTH SIDES ARE TAKEN OVER ONE IDENTICAL FILE POPULATION.** This is the exact
  shape of Story 18.1's only review finding: its sweep was computed over the population that
  *predated* its own new test module, so the tracked population had already grown by one when the
  claim was made. Once `tests/test_secret_evidence_contract.py` is tracked, `git ls-files -- '*.py'`
  is **252**. Run the comparison **engine-vs-engine over the SAME list** (pre-change module body vs
  post-change module body), not HEAD-vs-worktree over two different lists, and **state which
  population count the pair was taken over**.
- **AC2.1b** — if the new test module itself reports any `hardcoded_secret` finding (18.1's did, at
  its own PEM fixture), that finding is **DISCLOSED by path, line and cause** in the completion
  notes and proven **non-blocking** with `blocking_finding_count` / `is_verdict_blocking`. ⛔ **It is
  NOT suppressed, annotated, relocated or edited away** — that is `DF-8-5-B`'s forbidden move.
- **AC2.2** — the full suite is green at or above its baseline (**1,721** collected, exit 0), with
  **no test's assertion loosened**. The five secret-domain modules (**58 passed**) pass with **no
  edit to any assertion, docstring or fixture in them**.
- **AC2.3** — ⛔ **`FROZEN_DETECTOR_SET`'s `code_identity="secret_scan.v1"` (`argus/cache/key.py:187`)
  is NOT bumped**, and `argus/cache/**` is not touched. AC2.1 proves no cached result is stale;
  bumping would invalidate every cached result for a provable no-op. If you believe it must move,
  that is **AC7**.
- **AC2.4** — coverage stays at or above the `--cov-fail-under=80` floor. `_evidence_for` keeps its
  coverage through `tests/test_secret_scan.py::test_scan_evidence_carrier_masks_value`; record the
  measured percentage either way.

### AC3 — THE NON-RECURRENCE AND THE GUARANTEE ARE ASSERTED BY GUARDS, NOT BY A COMMENT

- **AC3.1** — a new module `tests/test_secret_evidence_contract.py` opens
  **`TC-ArgusAgent-SECRET-001-28`** and continues upward. ⛔ **CONTINUE the index; renumber nothing.**
  Its module docstring states the defect, the measurement (§0.1, §0.2) and the RED evidence, in the
  register of `tests/test_secret_suppression_recording.py`.
- **AC3.2 — `-28`, the BEHAVIOURAL guard.** With `SecretScanDetector._evidence_for` monkeypatched to
  **raise**, `run()` on the non-test path still emits **exactly the same findings** it emits with the
  real body. ⛔ The case first asserts the real-body population is **non-empty** (`AI-E11-1`), then
  compares the two results. **Measured RED against the shipped body: the exception propagates**
  (§2.2).
- **AC3.3 — `-29`, the NON-RECURRENCE guard.** An AST assertion over `argus/detectors/secret_scan.py`
  that **no `_evidence_for` call site is an expression-statement whose value is discarded**, and that
  the module still contains **at least one** `_evidence_for` call site (so the guard cannot pass by
  the function having vanished). ⛔ Scoped to `_evidence_for` only — a blanket "no bare calls" rule
  would fire on `findings.append(...)` (§2.7).
- **AC3.4 — `-30`, the FR28 STRUCTURAL guard.** Over a `DetectorResult` produced by `run()` on a
  synthetic secret: (i) the canonical serialization of the WHOLE result contains **neither the secret
  value nor any evidence field name** (`masked`, `value_length`, `entropy_bits`, `kind`,
  `pattern_id`); (ii) **no field name** of `FindingDraft` or `DetectorResult` matches the forbidden
  token set `("source", "secret", "value", "body", "excerpt", "content", "raw")` — extending
  `TC-ArgusAgent-EVIDENCE-001-04`'s discipline to the two models it does not cover. Population
  asserted non-empty first.
- **AC3.5** — ⛔ **THE RED IS OBSERVED AND ITS EXACT TEXT RECORDED**, driven against the **shipped**
  module body (monkeypatch from a pre-fix copy held outside the repository, or
  `git stash push -- argus/detectors/secret_scan.py` — **explicit pathspec only**). ⛔ **Never by
  weakening an assertion.** Per `AI-E14-1` an author-driven RED is **vacuity evidence**, not "this
  guard caught a defect"; record it as such. A case that stays GREEN against the shipped body is
  **not a guard** — fix the case, not the assertion, and record that you found it.
- **AC3.6** — every key value is **built in the module**; ⛔ **no secret is planted in a committed
  fixture file**, and no assertion is on a secret value — only on counts, rule ids, field names and
  absence (NFR-S1 / NFR-S2, the `-15`..`-27` precedent).

### AC4 — THE CHOICE IS RECORDED WITH ITS REASON, APPEND-ONLY

- **AC4.1** — **`DF-AUD-DETECT-B`** gains a **dated append-only closure note** naming this story, the
  fix sha, the new guard ids, the measured output-neutrality (**251 files, 0 differing**), and — 
  explicitly — **which of the two offered repairs was taken and why**, including that the entry's own
  sentence *"the second is the one that matches what Story 2.5 says"* is **falsified by Story 2.5's
  own record at `:613`** (§0.4). ⛔ **The original entry above the note is NOT rewritten** (§3.4
  evidence immutability — the `DF-1-3-A` / `DF-AUD-DETECT-A` notes are the form).
- **AC4.2** — ⛔ **Story 2.5's record is NOT edited**, and neither is Story 10.3's or Story 18.1's.
  They are `done`. The correction lives in the ledger, dated (§3.4).
- **AC4.3** — ⛔ **Binary-mode edit only.** Verify after writing: `deferred-work.md` still has **0**
  CRLF pairs and **exactly one** lone `\r`, and `git diff --stat` over it shows **insertions only**.
- **AC4.4** — ⛔ **Grep before filing. Nothing new is filed by this story.** The two measured gaps —
  `base.py`'s `FindingDraft` docstring (§0.3/(c)) and FR10's un-carried evidence counts (§0.5) — are
  **DISCLOSED in the completion notes with their measurements** and **NOT fixed, NOT filed, NOT
  asserted onto Story 18.4** (`AI-E9-8`: filing and scheduling are the Engineering Lead's).
- **AC4.5** — ⛔ **`architecture.md`, `E-PRD/prd.md` and `epics.md` are NOT edited.** Measured:
  `architecture.md`'s only reference is a directory-tree comment (`:1176`,
  *"secret_scan.py # FR11 — regex/entropy + producer-side redaction"*) which stays true, and
  `sprint-change-proposal-2026-08-24.md` §2 records `prd.md: None` / `architecture.md: None`. If you
  judge one must move, that is **AC7**.
- **AC4.6** — ⛔ **`DF-10-3-B`, `DF-10-3-C`, `DF-AUD-DETECT-C` / `-D` / `-E` / `-F` and `DF-13-5-A`
  are NOT dispositioned.** Naming one in prose without doing its work is the `AI-E12-3` defect.

### AC5 — SCOPE, PATHS, PORTABILITY AND CEILINGS

- **AC5.1** — ⛔ **THE WRITE SET IS EXACTLY:**
  1. `argus/detectors/secret_scan.py` — UPDATE
  2. `tests/test_secret_evidence_contract.py` — NEW
  3. `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — APPEND-ONLY
  4. the three regenerated dogfood artifacts (`minions-dogfood-partition-plan.md`,
     `minions-dogfood-budget-plan.md`, `minions-dogfood-proof.md`) — by their own renderer only
  5. this story file
  6. `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — status transitions only

  ⛔ **NOT in it:** `argus/detectors/base.py`, `argus/detectors/secret_suppression.py`,
  `argus/cache/key.py`, `argus/pipeline.py`, `argus/pipeline_stages.py`, `argus/reports/generator.py`,
  any `done` story's record, and **anything under `minions_core/apaa/`** — that tree is dead; `argus/`
  is the only live one.
- **AC5.2** — NFR-M1: `secret_scan.py` is 575 lines and only shrinks; the new test module must be
  ≤ **1,200**. **Split, never shave, never exempt.**
- **AC5.3** — no new dependency and no new import in `secret_scan.py`. AR8 purity preserved: no I/O,
  no clock, no randomness, no network on any decision path.
- **AC5.4** — `AI-E13-1`: the local run is Windows-only and is recorded as **LOCAL**. The
  cross-platform claim belongs to the CI ubuntu matrix, and only after it is green at the pushed sha.
- **AC5.5** — ⛔ stage by **explicit path**; never `git add -A` / `git add .` (§2.6, and the tree was
  already dirty with a peer session's work at contexting). Verify with `git status --porcelain`.

### AC6 — GATES, DOGFOOD REGENERATION AND THE COMMIT ARC

- **AC6.1** — green at the end, **every exit code recorded**: the full suite (`python -m pytest
  tests/ -q`, and again with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`), coverage `--cov-fail-under=80`,
  `mypy argus`, `bandit -r argus --severity-level medium`, `tests/test_module_size_ceiling.py`,
  `tests/test_release_preflight.py`, `tests/test_dogfood_artifact_currency.py`,
  `tests/test_dogfood_plan.py`, `tests/test_dogfood_proof.py`,
  `tests/test_governance_record_integrity.py`, `tests/test_v1_commitment_closure.py`,
  `tests/test_gate_*.py`. ⛔ Run with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared — Story
  16.5's dev lost a commit to a **false RED from stale bytecode**.
- **AC6.2** — the commit arc is **four** commits, in this order, for §0.6's forced reason:
  **`chore`** (this story file + `sprint-status` → `in-progress`) → **`feat`** (`argus/` + `tests/`)
  → **`chore`** (regenerate the three dogfood artifacts on a clean `argus/`) → **`docs`** (ledger +
  this story's record, **ledger first in the diff**). ⛔ Commit messages **pure ASCII** (`DF-16-6-F`),
  and the **`feat`** commit carries the whole-line trailer **`Evidence-partition: none`** (§0.6).
- **AC6.3** — ⛔ `DF-INV-MERGE-A`: if the PR lands squashed or rebased, re-run
  `python scripts/regenerate_dogfood_artifacts.py` on `master` and commit, or
  `TC-ArgusAgent-DOGFOOD-001-49` reddens `master` after the fact.
- **AC6.4** — the final write set equals AC5.1 exactly, verified with `git status --porcelain`
  (**not** `git diff --name-only` — the new test module is untracked and `git diff` is blind to it),
  and the three Story-18.1 files listed in §0.0 are **not** in any of this story's commits unless
  they were already committed by their own session.

### AC7 — ESCALATE, DO NOT DECIDE

⛔ **STOP and escalate — do not decide — if any of these becomes necessary:**

- the evidence must be **RETAINED** after all — i.e. `DN-18-2-1` must be reversed. ⛔ That reverses
  **Story 2.5's locked `:613` decision** and widens a frozen contract; it is the Engineering Lead's
  call, not the dev's, and §0.4 is the measurement to put in front of them;
- `DetectorResult`, `Recording`, `FindingDraft` or `Locator` must gain **any** field;
- `SecretFindingEvidence`, `SECRET_EVIDENCE_SCHEMA_VERSION`, `scan_evidence()` or `_evidence_for`
  must be **deleted** or have its signature changed;
- `code_identity` (`secret_scan.v1`) must be bumped, or anything under `argus/cache/` must be touched;
- **any** file's `DetectorResult` differs before vs after (AC2.1's differing set is non-empty), or the
  finding total moves off **88**;
- `argus/detectors/base.py`, `argus/detectors/secret_suppression.py`, `argus/pipeline*.py` or
  `argus/reports/generator.py` must be touched;
- any assertion in the five secret-domain test modules must be edited;
- `architecture.md`, `E-PRD/prd.md`, `epics.md` or any `done` story's record must be edited;
- a **new** `DF-*` entry looks necessary (§0.3/(c), §0.5) — `AI-E9-8`: recording is this story's job,
  filing is the Engineering Lead's;
- `DF-13-5-A` must be spent, a member ratified, a protocol row added, or an FR amended;
- a finding must become **verdict-eligible**, or a threshold must move;
- any `DN-*` must be reopened. ⛔ **A `DN-*` you disagree with is an escalation, not a story
  decision.**

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

- **`DN-18-2-1` — DELETE THE CALL; DO NOT WIDEN THE SCHEMA.** The entry offers two repairs and leaves
  the choice open; this story takes the first, on four measured grounds: (i) **Story 2.5's `:613`
  locks non-folding** and the widening would reverse a `done` story's decision (§0.4); (ii) **no FR
  requires it** — FR11 asks for redacted reporting, and the entry's FR10 citation is the
  *vacuous-test* FR (§0.5); (iii) widening produces **a field no consumer reads**, which is exactly
  `DF-10-4-B`'s already-filed defect class, one layer up in the same model; (iv) reaching an operator
  additionally requires moving the **frozen 1.2 `Recording`** and the report renderer — a
  cross-detector schema story, not this one.
  *Rejected: widen `DetectorResult` (the entry's second arm).* Cost measured in §0.4; foreclosed by
  `:613`; **available by escalation** (AC7) if the Engineering Lead reads `:613` differently.
  *Rejected: bind the call to `_` or keep it behind a comment.* That keeps the computation and keeps
  the claim; the entry's complaint is not the CPU, it is the appearance of load-bearing-ness.
  *Rejected: delete `scan_evidence()` / `SecretFindingEvidence` as well.* FR28's delivery pin
  (`test_v1_commitment_closure.py:510`) and Story 2.5's locked in-memory carrier both say no.
- **`DN-18-2-2` — THE COMMENT IS CORRECTED, NOT DELETED (AC1.2).** A silent removal leaves a reader
  who checks Story 2.5's `:349` against the code with a redaction step that exists nowhere.
  *Rejected: delete the banner and say nothing.* That trades one wrong impression for a second one.
- **`DN-18-2-3` — THE MODULE'S OWN FALSE SENTENCE IS FIXED HERE; `base.py`'s IS NOT.** §0.3/(b) is in
  the file this story already edits and is the same claim class as the banner; §0.3/(c) is in
  Story 18.4's module.
  *Rejected: fix both.* Crosses another story's fence and steals its diff.
  *Rejected: fix neither.* Leaves the module still claiming what this story exists to stop it
  claiming.
- **`DN-18-2-4` — THREE GUARDS IN A NEW MODULE `tests/test_secret_evidence_contract.py`.** One
  module, one subject (the `DN-18-1-4` precedent): the subject here is *what a finding carries*, not
  suppression and not detection precision. The module docstring carries the measurement and the RED
  evidence, as `-15`..`-27` do.
  *Rejected: appending to `tests/test_secret_scan.py`.* That module's subject is detection + the
  evidence carrier's own shape (`-01`..`-14`); the RED evidence and the AST guard do not belong to it.
  *Rejected: one guard instead of three.* The behavioural guard alone cannot stop the statement
  coming back (nothing would go red if a future edit re-added a discarded call in a place `run()`
  tolerates); the AST guard alone asserts syntax, not behaviour.
- **`DN-18-2-5` — `code_identity` IS NOT BUMPED (AC2.3).** AC2.1 proves output-neutrality, so no
  cached result is stale.
  *Rejected: bump it "for hygiene".* It would invalidate every cached result for a no-op — the cache
  canary's cost with none of its benefit.
- **`DN-18-2-6` — THE 251-FILE SWEEP IS AN INSTRUMENT, NOT A COMMITTED TEST.** Its numbers are
  recorded in the completion notes and the ledger note; it is not added to the suite.
  *Rejected: committing it as a guard.* It re-reads the whole tree on every run, it duplicates what
  `tests/test_secret_containment.py` already gates, and a whole-repo sweep in the suite is the kind of
  slow, environment-coupled test this project has removed twice.

### Locked decisions this story CITES rather than reopens

- **Story 2.5 / `:613`** — `SecretFindingEvidence` is **not** folded into `DetectorResult` and **not**
  persisted; the carrier is in-memory by design. `DN-18-2-1` rests on it.
- **Story 2.5 / the structural guarantee** — redaction is the **absence** of a value field on
  `Recording` / `Locator` / `FindingDraft`. True before and after this change.
- **Story 10.3 / AC4.5** — built-in suppressions emit **no** `operator_suppressed_secret` record. ⛔
  This story must not start emitting one.
- **Story 18.1 / `DN-18-1-1`..`-7`** — the length-gated sentinel match and everything around it.
  `done`; not reopened.
- **architecture §G** — the suppression threat model; read, not edited (AC4.5).

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| entry | bearing |
|---|---|
| **`DF-AUD-DETECT-B`** | **THE SUBJECT.** This story is chartered to discharge it (AC4.1). Its finding is re-measured in §0.1/§0.2; its *reasoning* about Story 2.5 is falsified in §0.4 and corrected append-only. |
| **`DF-10-4-B`** | Prior art for *"a `DetectorResult` field recorded and never read back"* — the defect the widening arm would recreate (§0.4). Cited, **not** dispositioned. |
| **`DF-AUD-DETECT-C`** | ⛔ OPEN. The 0.4% figure in §0.2 does **not** disposition it. |
| **`DF-AUD-DETECT-E` / `-F`** | Stories 18.3 / 18.4. Do not pre-empt them; `base.py` is `-F`'s file. |
| **`DF-AUD-DETECT-D`** | Story 17.3. Not this story. |
| **`DF-10-3-B` / `DF-10-3-C`** | ⛔ OPEN, untouched, out of scope. |
| **`DF-INV-MERGE-A`** | OPEN, DECIDED-NOT-YET-APPLIED. Governs how this PR may land (§2.5, AC6.3). |
| **`DF-INV-WHEEL-A`** | OPEN. Running Argus inside its own repo reddens `TC-ArgusAgent-DOCS-001-54` for an unrelated reason. If you hit that red, it is **not yours**. |
| **`DF-INV-REFS-A`** | OPEN. Six referenced ids do not resolve. Do not "fix" one in passing. |
| **`DF-13-5-A`** | ⛔ **OPEN and UNSPENT.** Nothing here spends it. |
| **`DF-8-5-B`** | *"Do not close it by loosening an assertion."* The standing rule over AC2.2 and AC7. |
| **`DF-INV-LEDGER-A`** | Why AC4.4 says grep before filing. |

### Dependencies — none are added, and that is a requirement

`secret_scan.py` imports `math`, `re`, `Counter`, `Fraction`, `Sequence`, `pydantic`, and four
first-party modules. **This story adds none and removes none.** ⛔ Nothing here requires web research:
there is no third-party API surface involved, the models are this repository's own, and the change is
a deletion plus two comment corrections. `pydantic`'s frozen/`extra="forbid"` behaviour is already
exercised by 1,721 tests at this HEAD.

### Standing rules (non-negotiable)

- **AR7** — one arithmetic, one vocabulary, never forked. Two ways for a finding to carry evidence is
  that fork.
- **AR8** — pure/impure separation. `secret_scan.py` is PURE and stays PURE.
- **NFR-P1** — no clock, randomness, network or host-dependent comparison on any decision path.
- **NFR-S1 / NFR-S2** — no source byte, no secret value, no absolute host path in any artifact,
  message or test assertion.
- **NFR-M1** — 1,200 physical lines per module. **Split, never shave, never exempt.**
- **NFR-M2** — frozen, additive-only contracts. ⛔ *Additive-only* is a permission, not an
  instruction: it does not make an unread field free.
- **`AI-E11-1`** — every guard asserts its population is non-empty before asserting anything about it.
- **`AI-E13-1`** — the local suite is Windows-only; CI runs an ubuntu matrix.
- **`AI-E12-3` / `AI-E12-6`** — *a disposition recorded in prose and not in the ledger is not a
  disposition.*
- **`AI-E14-1`** — an author-driven RED is vacuity evidence, not "this guard caught a defect".
- **`AI-E9-8`** — do not assert a new finding onto an existing story to give it a home.

### Previous-story intelligence

**Story 18.1 (`done`, this epic, immediately before) — what it hands you:**

1. ⛔ **It deliberately did NOT touch `secret_scan.py`**, naming the dead `_evidence_for` as *"18.2"*
   in its own "what this story did NOT do" list. **The RED is intact and it is yours.**
2. **Its §0 predicted the wrong guard.** `TC-ArgusAgent-DOGFOOD-001-50` did **not** fire; the two
   dogfood *derivation* tests did (§0.6). This story's §0.6 is written from that measurement, not
   from the same prediction.
3. **Its gate list missed `TC-ArgusAgent-PRECISION-001-94`**, which reddened the `feat` commit for a
   missing `Evidence-partition` trailer and forced a **sha rewrite** — commit 2 amended, the dogfood
   artifacts regenerated a second time. ⛔ **Write the trailer on the `feat` commit the first time**
   (AC6.2).
4. **Its review found one Low finding**, and it was a **disclosure** gap: a sweep re-derived over the
   population that predated its own new test module. ⛔ **Take AC2.1's sweep over the population that
   INCLUDES your new test module**, and disclose anything it reports (your module builds no secret
   material by design — the guards construct values in-line — but measure, do not assume).
5. **Its ledger note is the FORM for yours**: dated, append-only, entry above unrewritten, measured
   before/after, guards named, and the things it does **not** disposition listed explicitly.
6. **Two commits, not one, when a sha must be cited** — a commit cannot cite itself. Four commits
   here, same as 18.1.

**Story 2.5** built this detector, this carrier and this comment. Its record is the source of both
`DN-18-2-1`'s justification (`:613`) and the trap that made the entry worth filing (`:349`). ⛔ Read
both; edit neither.

### Git intelligence

Recent arc (last 8 commits): `8b6c304` → `ee7e252` → `fa5e463` → `c288d40` is Story 18.1's four-commit
arc, preceded by four `docs(gov)` commits from the 2026-08-24 self-audit (`DF-INV-MERGE-A`,
`DF-INV-LEDGER-A`, a provenance re-cite after a rebase-merge, and a delivery record).

- **`argus/` is quiet again.** The last change to it is `ee7e252` (Story 18.1's `feat`), and the three
  dogfood artifacts were regenerated for exactly that sha at `fa5e463`. **Your `feat` commit moves
  past it, so those artifacts go stale and must be regenerated** (§0.6).
- **`3a9e100` had to re-cite provenance after a rebase-merge orphaned the old sha** — the lived
  instance of `DF-INV-MERGE-A`. AC6.3 is not theoretical.
- **The culture this week is: measure, then withdraw what the measurement does not support** — three
  claims and one attribution were withdrawn by their own authors on 2026-08-24. §0.4 does the same to
  a sentence in the entry this story discharges. Do it again in your completion notes if Task 0
  disagrees with any row of §0.

### References

- [epics.md](../epics.md) — `## Epic 18` (line ~3609) and `### Story 18.2` (~3672). ⛔ Its *"AWAITING
  OPERATOR APPROVAL"* paragraph and the append-only approval note beneath it are **left as written**
  (§3.4 / the Epic 16 precedent). **Not a blocker; not to be edited.**
- [sprint-change-proposal-2026-08-24.md](../sprint-change-proposal-2026-08-24.md) — §1 (the audit),
  §2 (impact: `prd.md` **None**, `architecture.md` **None**), §4 (Epic 18's four stories).
  **APPROVED 2026-08-24 by XAgent007 (Engineering Lead).**
- [deferred-work.md](../deferred-work.md) — `DF-AUD-DETECT-B` (~§6416), `DF-AUD-DETECT-A`'s closure
  note (~§6300+, the FORM for yours), the Epic 17/18 scheduling table (~§6630). ⛔ **Line numbers
  drift; grep by id.**
- [2-5-hardcoded-secret-detector-producer-side-redaction.md](2-5-hardcoded-secret-detector-producer-side-redaction.md)
  — `:349` and `:613`. ⛔ **Read; never edit** (`done`).
- [18-1-the-sentinel-table-matches-values-not-substrings-of-them.md](18-1-the-sentinel-table-matches-values-not-substrings-of-them.md)
  — §0.6 (the guard/commit-arc analysis), completion note 5 (which gates actually fired). ⛔ **Read;
  never edit** (`done`).
- [E-PRD/prd.md](../E-PRD/prd.md) — **FR10** (`:527`), **FR11** (`:528`), **FR28** (`:573`). ⛔ None is
  amended.
- [architecture.md](../architecture.md) — §G *Security & Governance*; `:1176` names this module in the
  directory tree. ⛔ **Read, do not edit** (AC4.5).
- `argus/detectors/secret_scan.py` — the module under change. **Read the whole docstring (`:1`–`:104`)
  before touching a line.**
- `argus/detectors/base.py`, `argus/ledger/recording.py` — the models. **Read; do not edit.**
- `tests/test_secret_scan.py` (`-01`..`-14`), `tests/test_secret_suppression_recording.py`
  (`-15`..`-22`), `tests/test_secret_sentinel_matching.py` (`-23`..`-27`) — the register the new
  module should be written in. **Read; do not edit.**

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC2.1, AC2.2, AC6.1)

- [x] `git status --porcelain` — record it. ⚠️ **Expect it to be non-empty** (§0.0: three Story-18.1
      files). Record which files are not yours **before** you stage anything.
- [x] Clear `__pycache__`; export `PYTHONDONTWRITEBYTECODE=1`. **Story 16.5 lost a commit to a false
      RED from stale bytecode.**
- [x] Re-run §0.1's AST proof. **Expect exactly one discarded-value `_evidence_for` statement, at
      `:506`.** If it is gone or there are two, **STOP and report** — the premise is false.
- [x] Re-run §0.2's sweep. **Expect 251 files, 88 findings, 37 files with ≥1.** Record the pair; it is
      the only baseline you will ever be able to take.
- [x] Re-run §0.3's single-file payload check. **Expect 3 findings and a payload with no mask, no
      evidence field and no secret.**
- [x] Re-run the five secret-domain modules (**expect 58 passed**) and the full suite (**expect 1,721
      collected, exit 0**). Record both.
- [x] Re-measure §0.7's ledger byte state and the max `TC-ArgusAgent-SECRET-001-NN` (**expect `-27`**).
- [x] `python -m pytest tests/test_governance_record_integrity.py -q` — **expect green** (this file
      claims no closure yet).
- [x] Record every figure that came out different. **Expect at least one.**

### Task 1 — THE EQUIVALENCE INSTRUMENT, BUILT BEFORE THE CHANGE (AC2.1)

- [x] Write the sweep as a throwaway script **outside the repository** (scratch dir) that drives
      `run()` over `git ls-files -- '*.py'` and emits a `{path: canonical DetectorResult}` map.
- [x] Capture the **pre-change** map to a scratch file. ⛔ Do not commit the instrument
      (`DN-18-2-6`).

### Task 2 — THE GUARD, WRITTEN AGAINST THE SHIPPED BODY (AC3)

- [x] Create `tests/test_secret_evidence_contract.py`, opening `TC-ArgusAgent-SECRET-001-28` and
      continuing upward. Docstring in the `-15`..`-27` register: the defect, the measurement, the RED
      evidence, and *"key material is synthetic and built in the module"*.
- [x] `-28` — the **behavioural** guard: real-body population non-empty, then `_evidence_for`
      monkeypatched to raise, then the two results compared (AC3.2).
- [x] `-29` — the **non-recurrence** AST guard over `secret_scan.py`, scoped to `_evidence_for`
      (AC3.3). ⛔ Not a blanket "no bare call statements" rule.
- [x] `-30` — the **FR28 structural** guard over the emitted result and the two models
      `TC-ArgusAgent-EVIDENCE-001-04` does not cover (AC3.4).
- [x] Every case asserts its population non-empty first (`AI-E11-1`); no assertion on a secret value
      (AC3.6).
- [x] Confirm the new module is ≤ **1,200** physical lines (AC5.2) — `len(text.splitlines())`, the
      same arithmetic `tests/test_module_size_ceiling.py:176`–`:183` uses.

### Task 3 — DRIVE IT RED, THEN MAKE THE CHANGE (AC3.5, AC1)

- [x] Run the new module **against the shipped `secret_scan.py`**. **Record the exact failure text of
      every case that goes RED, and which do not.** ⛔ A case that stays GREEN pre-change is not a
      guard — fix the case, not the assertion, and record that you found it.
- [x] ⛔ **Two safe mechanisms, one unsafe.** SAFE: (a) monkeypatch from a pre-change copy of the
      module held outside the repository; (b) `git stash push -- argus/detectors/secret_scan.py` —
      **explicit pathspec**, and only after `git status --porcelain -- argus/detectors/secret_scan.py`
      confirms the only change there is yours. ⛔ UNSAFE: `git stash` with no pathspec — a peer
      session's three files are in this tree (§0.0).
- [x] Delete `:506` (AC1.1); replace the `:505` banner with the measured truth (AC1.2); correct the
      docstring sentence at `:26`–`:27` (AC1.3). ⛔ Nothing else in the docstring is reflowed.
- [x] Confirm `SecretFindingEvidence` / `SECRET_EVIDENCE_SCHEMA_VERSION` / `scan_evidence` /
      `_evidence_for` / `__all__` are untouched (AC1.4) and `:451`/`:502` are byte-unchanged (AC1.5).
- [x] Re-run the new module. **Record GREEN.**

### Task 4 — PROVE THE CHANGE MOVES NOTHING (AC2)

- [x] Re-run Task 1's sweep post-change and diff the two maps. ⛔ **The differing set must be EMPTY**
      and the totals must be unchanged (**88 / 37**). If one file differs, that is **AC7**.
- [x] ⛔ Take **both** sides over the SAME file list — **252** files once the new test module is
      tracked (AC2.1a). Record which population the pair was taken over, and disclose any
      `hardcoded_secret` finding the new module itself carries, with its non-blocking proof
      (AC2.1b). **This is the one finding 18.1's review raised; do not repeat it.**
- [x] Re-run the five secret-domain modules **with no edit to any assertion, docstring or fixture in
      them** (AC2.2).
- [x] Full suite, green, **no assertion loosened**. ⛔ `tests/test_secret_containment.py` must be run
      as part of the whole-directory collection (§0.8/(b)).
- [x] Coverage with `--cov-fail-under=80`; record the percentage (AC2.4).
- [x] Confirm `argus/cache/key.py` is **unmodified** (AC2.3) — `git status --porcelain` must not list
      it.

### Task 5 — THE DISCLOSURES (AC4.4)

- [x] Re-derive §0.3/(c) (`base.py`'s `FindingDraft` docstring) and §0.5 (FR10's un-carried counts) at
      your own HEAD. **Record both measurements in the completion notes.**
- [x] ⛔ **Do not fix either. Do not file either.** Name `AI-E9-8` and the Engineering Lead as the
      owner of the filing decision.

### Task 6 — THE LEDGER (AC4.1–AC4.3)

- [x] ⛔ **Grep first** (`DF-INV-LEDGER-A`). Then append, **in binary mode**, `DF-AUD-DETECT-B`'s
      dated closure note: the repair taken, the reason (§0.4, including the `:613` falsification of
      the entry's own sentence), the guard ids, the 251-file/0-differing measurement, and an explicit
      list of what this closure does **not** disposition.
- [x] Verify afterwards: **0** CRLF pairs, **exactly one** lone `\r`, and a `git diff` confined to the
      appended lines.
- [x] ⛔ Confirm `architecture.md`, `E-PRD/prd.md`, `epics.md`, `2-5-…md` and `18-1-…md` are
      **unmodified** (AC4.2, AC4.5) — `git status --porcelain` must not list any of them as *yours*.

### Task 7 — GATES, DOGFOOD REGENERATION AND THE COMMIT ARC (AC5.5, AC6.1, AC6.2)

- [x] Commit `argus/` + `tests/` **by explicit path**, with the trailer **`Evidence-partition: none`**
      as a whole line in the commit message (§0.6). ⛔ Never `git add -A`.
- [x] `python -m pytest tests/test_gate_seal.py -q` immediately after that commit — this is where
      Story 18.1 lost a sha.
- [x] `python scripts/regenerate_dogfood_artifacts.py` on the now-clean `argus/` tree; commit the
      three artifacts separately. ⛔ Exit 2 means the tree is dirty — fix the tree, never pass
      `--allow-dirty-argus`.
- [x] Run the full AC6.1 gate list. **Record every exit code.** Mark the run **LOCAL / Windows-only**
      (AC5.4).

### Task 8 — HAND-OFF (AC6.3, AC6.4)

- [x] `git status --porcelain` — the write set equals AC5.1 exactly, and no Story-18.1 file rode along.
- [x] Completion notes: every re-measured §0 figure, the observed REDs with their exact text, the
      pre/post sweep pair, the two disclosures from Task 5, every exit code, and **any §0 premise
      found false**.
- [x] ⛔ If the PR lands squashed or rebased, re-run the regeneration on `master`
      (`DF-INV-MERGE-A`, AC6.3).

### Review Findings

**Code review complete (2026-08-25, iteration 1, Sonnet 5).** 0 `decision-needed`, 0 `patch`, 0
`defer`, 0 dismissed. Every load-bearing claim was RE-DERIVED BY EXECUTION rather than read back
from the dev's notes, per this repository's standing review method:

- **AST single-discarded-statement claim** — re-parsed `argus/detectors/secret_scan.py` at the
  reviewed HEAD independently: zero discarded-value `_evidence_for` expression statements, one
  remaining (bound) call site at `:378`. MATCH.
- **Docstring-stripped AST whole-module diff** — independently re-derived comparing the pre-change
  body (`git show 58821c3:argus/detectors/secret_scan.py`) against the reviewed HEAD: the ONLY
  semantic difference is the removal of the one `Expr(Call(self._evidence_for(match)))` statement.
  MATCH — confirms AC1.1/AC1.4/AC1.5 by construction, not by reading the diff.
- **Output-neutrality sweep (AC2.1/AC2.1a)** — independently re-implemented the engine-vs-engine
  sweep (pre-change module loaded from a scratch copy outside the repo via
  `importlib.util.spec_from_file_location`, tree never stashed) over the SAME 252-file
  `git ls-files -- '*.py'` population: **91 findings / 38 files with ≥1 on both sides, 0 of 252
  `DetectorResult`s differing, `_evidence_for` invocations 91 → 0**. Exact match to the story's own
  figures.
- **RED/GREEN guard evidence (AC3.5, item 4 of the review brief)** — reproduced `-28`'s behavioural
  assertion and `-29`'s AST assertion directly against the pre-change engine (no tracked file was
  touched — an attempt to swap the tracked file was correctly blocked by the sandbox as an
  unsafe shared-tree mutation, and the safer in-memory technique the dev used was applied
  instead): `-28` RED (`AssertionError` propagates out of `run()`, confirming `:506` sat outside
  the `try/except`), `-29` RED (discarded call found at `:506`), `-30` GREEN pre-change *and*
  post-change — independently confirmed to be a contract pin (a guarantee already true, not a
  defect witness), exactly as disclosed. No finding here.
- **`sprint-status.yaml` not staged (`DN-DEV-18-2-A`)** — verified: at committed HEAD (`62fd1b9`)
  line 512 reads `18-1-...: review` and line 513 reads `18-2-...: backlog`; in the current working
  tree both lines carry further content (18-1 now shows a peer session's own iteration-2
  code-review pass to `done`, appended concurrently while this review ran). The two development-
  status lines are genuinely inseparable from the peer's concurrent edits without either
  swallowing work this session did not write or publishing an inconsistent state. The reasoning
  holds and is endorsed; this reviewer's own status write (below) follows the same
  write-but-do-not-stage discipline for the same reason.
- **AC5.2 deviation (575 → 594 lines)** — accepted as a legitimate reading, not a defect. AC1.2
  unambiguously requires the banner to be REPLACED (not merely removed) by a substantive,
  measured-fact block; AC5.2's "only shrinks" was a pre-implementation prediction that assumed
  pure deletion. The two ACs are in direct textual tension; AC1.2 (an explicit content
  requirement) is correctly treated as binding over AC5.2's predictive clause, and the governing
  NFR (NFR-M1's 1,200-line ceiling) is met with wide headroom (594 vs. 1,200, independently
  measured via `wc -l`). Disclosed prominently in three places (commit message, ledger closure
  note, completion note 8); nothing here required an AC7 escalation — the escalation list does not
  cover this class of in-story AC tension.
- **§0.7's "166 vs 169" `DF-` line-count discrepancy (item 3)** — independently reproduced all
  three counting methods against the on-disk ledger: unanchored substring `- id: DF-` → 169;
  indentation-tolerant anchored `^[[:space:]]*- id: DF-` → 169; strict column-0-anchored
  `^- id: DF-` → 3 (an artifact of the ledger's entries being indented under a YAML list key, not
  a real count). Confirms the dev's explanation: a counting-method artifact, not a moved fact —
  the ledger's byte state (546,616 → 556,678 bytes after this story's own +98/-0 append; 0 CRLF,
  exactly one lone `\r`) is otherwise exactly as claimed.
- **Ledger closure note** — read in full on disk (`deferred-work.md:6416`–`:6543`). The original
  `DF-AUD-DETECT-B` entry above the note is untouched; the append-only closure note correctly
  states the repair taken, falsifies only the entry's own Story-2.5 sentence (not Story 2.5's
  record, which is cited, never edited), records the measured before/after, names the guards, and
  lists what the disposition does NOT touch. `TC-ArgusAgent-DOCS-001-78`'s closure-claim analyzer
  was re-run and is green; the story's own "`DF-AUD-DETECT-B` is CLOSED..." sentence (completion
  note 15) is a real closure claim by the analyzer's own rule, but it is correctly backed by the
  ledger note landing in the SAME commit, ledger first in the diff — verified consistent, not a
  finding.
- **Write set / commit arc** — `git diff c288d40..HEAD --stat` matches AC5.1 exactly (7 paths, no
  extras); `git status --porcelain` at review time shows only the three pre-existing peer-owned
  files, none of this story's making. Four commits (`57a278f` chore → `2cc5128` feat → `25ff87f`
  chore → `62fd1b9` docs), all pure ASCII, `feat` carries `Evidence-partition: none` as a whole
  line. Matches AC6.2 exactly.
- **Independently executed gates**, all green at this HEAD: full suite (1,724 collected via
  summed per-module `--collect-only`, 0 `F`/`E` markers, exit 0), the four independently
  collectible secret-domain modules plus `test_secret_evidence_contract.py` (30 passed;
  `test_secret_containment.py` reconfirmed uncollectable standalone, pre-existing, and green as
  part of the full-directory run), `mypy argus` (clean, 95 files), `bandit -r argus
  --severity-level medium` (clean), coverage `--cov-fail-under=80` (95.69%, matches exactly),
  `test_module_size_ceiling.py`, `test_release_preflight.py`, `test_dogfood_*.py` (×3),
  `test_governance_record_integrity.py`, `test_v1_commitment_closure.py`, `test_gate_seal.py`. All
  LOCAL / Windows-only (`AI-E13-1`); no cross-platform claim is made here, consistent with the
  standing rule that a green local suite is not cross-platform proof.
- No SOLID/DRY/coupling/testability concerns: the change is a single dead-statement deletion, two
  comment/docstring corrections stating only measured facts, and three well-scoped, single-subject
  guards (`AI-E11-1` non-vacuity checks present in all three, no assertion on a secret value, no
  planted fixture secret — the AWS documentation example key is the established repo-wide
  precedent).

No unresolved issues. All ACs independently reconfirmed met except AC5.2's literal "only shrinks"
clause, which is superseded by AC1.2 as reasoned above and does not block this review.

---

## Dev Agent Record

### Agent Model Used

Opus 5 (`claude-opus-5[1m]`), BMAD `bmad-dev-story` workflow, 2026-08-24. Single implementation
round; no review iteration preceded it.

### Debug Log References

- **Task 0 re-measurement** (before any line was written) - AST proof, 251-file sweep,
  single-file payload, five secret modules, full suite, ledger byte state, DOCS-001-78 analyzer.
- **RED run** of `tests/test_secret_evidence_contract.py` against the SHIPPED `secret_scan.py`.
- **Engine-vs-engine sweep** over one identical 252-file list, pre-change body vs post-change body.
- Instruments were throwaway scripts held OUTSIDE the repository (`DN-18-2-6`); none is committed.
  The shared working tree was never stashed or reverted - the pre-change body was driven by loading
  a copy of the module from the scratch directory via `importlib.util.spec_from_file_location`.

### Completion Notes List

**1. Every Section 0 premise was re-measured by execution and every one reproduced.** One figure
came out different and it is a counting-method artifact, not a moved fact - see note 9.

| Section 0 row | expected | measured | verdict |
|---|---|---|---|
| discarded-value `_evidence_for` statements | exactly 1, at `:506` | `[(506, 'self._evidence_for(match)')]` | MATCH |
| all `_evidence_for` call sites | `:376`, `:506` | `[(376, ...), (506, ...)]` | MATCH |
| `_evidence_for` def | `:383`, `['staticmethod']`, returns `SecretFindingEvidence` | identical | MATCH |
| tracked `*.py` | 251 | 251 | MATCH |
| sweep, shipped body | 88 findings / 37 files / 88 invocations | 88 / 37 / 88 | MATCH |
| sweep, `_evidence_for` nulled | 88 / 37, **0 differing** | 88 / 37, **0 differing** | MATCH |
| `argus/prod/settings.py` payload | 3 findings, no mask, no evidence field, no secret | 3 findings; `****`, `masked`, `value_length`, `entropy_bits`, `kind`, `pattern_id` and the value ALL absent; `recording_id` `hardcoded_secret:b8162401...` | MATCH |
| `secret_scan.py` | 575 lines | 575 | MATCH |
| five secret-domain modules | 58 passed | 58 passed | MATCH |
| full suite | 1,721 collected, exit 0 | 1,721 collected, exit 0 | MATCH |
| `mypy argus` | clean, 95 source files | `Success: no issues found in 95 source files` | MATCH |
| `deferred-work.md` | 546,616 bytes, 0 CRLF, exactly one lone `\r`, 7,040 LF | identical | MATCH |
| max `TC-ArgusAgent-SECRET-001-NN` | `-27` | `-27` | MATCH |
| DOCS-001-78 analyzer over this file | `()` | `()` | MATCH |
| `git status --porcelain` | non-empty, three Story-18.1 files | the same three, plus this story file untracked | MATCH |

**2. THE OBSERVED REDs, verbatim, driven against the SHIPPED module body** (`AI-E14-1`: these are
AUTHOR-DRIVEN, therefore **vacuity evidence** - proof the cases can fail - **not** "these guards
caught a defect"). The RED was taken with `secret_scan.py` still pristine on disk, before any edit:

- `TC-ArgusAgent-SECRET-001-28` - **RED**:

  ```
  E       AssertionError: _evidence_for must not be on run()'s path (TC-ArgusAgent-SECRET-001-28)
  tests\test_secret_evidence_contract.py:177: AssertionError
  ```

  The exception PROPAGATED OUT OF `run()` exactly as Section 2.2 predicted: `:506` sat outside the
  `try/except` at `:424`-`:432`, which wraps only `self._scan(source)`.

- `TC-ArgusAgent-SECRET-001-29` - **RED**:

  ```
  E       AssertionError: secret_scan.py calls _evidence_for and DISCARDS the return value at
          line(s) [506]. That computes the masked indicator, the length, the kind, the pattern id
          and an exact-Fraction entropy and throws all five away in the statement that computes
          them, while reading as the load-bearing redaction step (DF-AUD-DETECT-B). ...
  E       assert not [506]
  tests\test_secret_evidence_contract.py:249: AssertionError
  ```

- `TC-ArgusAgent-SECRET-001-30` - **GREEN pre-change, BY DESIGN, and recorded as such.** It pins
  FR28's structural guarantee, which was true before this story and stays true after it; it exists
  so a future widening of `FindingDraft` / `DetectorResult` cannot land silently. Per Task 3 a case
  that stays GREEN pre-change "is not a guard" - this one is deliberately a CONTRACT PIN rather than
  a defect witness, which is why it is disclosed here rather than strengthened into a false RED.

All three are **GREEN post-change** (exit 0).

**3. THE PRE/POST SWEEP PAIR, taken engine-vs-engine over ONE identical population** (AC2.1a - the
exact shape of Story 18.1's only review finding, deliberately not repeated). Both sides were driven
over the SAME file list, which **includes** this story's own new test module, rather than
HEAD-vs-worktree over two lists that differ by one file:

| population **252** (identical list both sides) | `hardcoded_secret` findings | files with >=1 | `_evidence_for` invocations | `DetectorResult`s differing |
|---|---:|---:|---:|---:|
| pre-change engine (module copy from outside the repo) | 91 | 38 | 91 | - |
| post-change engine (the tree) | 91 | 38 | **0** | **0 of 252** |

Over the 251-file population that predates the new module, the same instrument re-derives Section
0.2's own figures: **88 / 37 / 0 differing**. The `91 - 88 = 3` delta is entirely the new test
module's own findings (note 4). The `91 -> 0` invocation count is the direct proof the call left
`run()`'s path; the `0 differing` is the proof nothing observable moved.

**Cost, recorded so nobody claims a performance win:** 1.462 s pre-change vs 1.455 s post-change;
and on the separate shipped-vs-nulled pair the NULLED side was the *slower* of the two (1.467 s vs
1.477 s). The difference is inside the noise. **`DF-AUD-DETECT-C` is NOT dispositioned by it.**

**4. AC2.1b - THE NEW TEST MODULE'S OWN FINDINGS, DISCLOSED BY PATH, LINE AND CAUSE.**
`tests/test_secret_evidence_contract.py` reports **3** `hardcoded_secret` findings against itself,
all at **line 111**, its `_SYNTHETIC_SECRET` module constant - the published AWS documentation
access-key example, which the guards must build in-module to have a detectable subject at all
(AC3.6 forbids planting it in a committed fixture file). **Cause:** three scan patterns
(`aws_access_key_id`, `generic_assigned_secret`, `high_entropy_string`) hit that one span, and
`run()` de-duplicates on `(start_line, end_line, pattern_id)`, so one line legitimately yields
three. **Proven non-blocking by execution:** each is `advisory=True`, `depth_supported=None`,
`is_verdict_blocking` **False**, and `blocking_finding_count` over the whole result is **0**;
`degraded` is `()`. They appear identically under BOTH engine bodies and so cancel out of the
pre/post delta. They were **NOT** suppressed, whitelisted, annotated, relocated or edited away
(`DF-8-5-B`).

**5. AC1 verified MECHANICALLY, not by reading the diff.** A docstring-stripped AST comparison of
the whole module before vs after reports **exactly one difference**:

```
AST-level (docstring-stripped) differences: 1
   -            self._evidence_for(match)
```

So AC1.1 (the statement is DELETED, not commented out and not bound to a throwaway name), AC1.4
(`SecretFindingEvidence`, `SECRET_EVIDENCE_SCHEMA_VERSION`, `_evidence_for`, `scan_evidence` and
`__all__` all survive - re-confirmed by name, and `_evidence_for` is still a decorated
`@staticmethod`) and AC1.5 (`run()`'s signature, purity and control flow otherwise unchanged;
`:451` and `:502`, Story 18.1's territory, byte-unchanged) are all discharged by one measurement.
AC1.2's banner replacement and AC1.3's docstring correction are the only other edits in the file
and both are comment/docstring text. No import was added or removed (AC5.3).

**6. TASK 5 DISCLOSURES - re-derived at this HEAD, and deliberately NOT fixed and NOT filed**
(`AI-E9-8`: recording is this story's job, filing and scheduling are the Engineering Lead's).

- **(a) `argus/detectors/base.py:63`-`:72`.** The `FindingDraft` docstring says it carries *"the
  supported coverage depth (the verdict-fold input), and the evidence the finding carries WITH it
  (FR10 'carrying their evidence counts' - a JSON-primitive dict of fixed-precision/int leaves)"*.
  Measured at this HEAD, `FindingDraft.model_fields` is exactly `['advisory', 'ast_span',
  'cartridge_id', 'coverage_envelope_slice', 'end_line', 'file_path', 'rule_id', 'start_line']` -
  **neither** a `depth_supported` field **nor** any evidence field. Same claim class as the banner
  this story repaired. `base.py` is Story 18.4's fence and was left **byte-unchanged**.
- **(b) FR10's own detector does not carry its counts either.** `VacuousTestDetector().run()` over
  the `test_widget` fixture of `tests/test_vacuous_detector.py:140` emits **1** finding whose FULL
  payload is `{"advisory":true, ..., "depth_supported":"audited_shallow", "locators":[{"ast_span":
  "function:test_widget@1-6", ...}], "rule_id":"vacuous_test_ast", ...}` - **no assertion-density,
  no mock-ratio, no count of anything**; the tokens `assertion`, `density`, `mock`, `ratio` and
  `count` are all absent from it. Structurally they must be: `Recording`'s ten fields
  (`advisory, cartridge_id, claim_present, coverage_envelope_slice, depth_supported, locators,
  partition_id, recording_id, rule_id, schema_version`) include none that could hold a count. So the
  evidence-carrying gap is **repository-wide and older than `DF-AUD-DETECT-B`**, and it is the
  strongest available reason NOT to widen one detector in isolation: the honest repair is one
  cross-detector story, or none.

Both are recorded in the ledger's closure note as well, under "RECORDED HERE, NOT FILED". **No new
`DF-*` entry was filed** (AC4.4); the ledger was greped first (`DF-INV-LEDGER-A`) and already
carries this defect, the unread-field class (`DF-10-4-B`), the detector cost (`DF-AUD-DETECT-C`) and
the disclosure gap (`DF-10-3-B`).

**7. EVERY EXIT CODE - LOCAL / Windows-only** (`AI-E13-1`; `PYTHONDONTWRITEBYTECODE=1` exported and
`__pycache__` cleared before each full run, per AC6.1 and Story 16.5's lost commit).

| gate | result | exit |
|---|---|---|
| `pytest tests/ -q` (baseline, pre-change) | 1,721 collected, all passed | **0** |
| `pytest tests/ -q` (post-change, pre-regeneration) | 2 failed - the two PREDICTED dogfood derivation guards | 1 |
| `pytest tests/ -q` (post-regeneration, final) | 1,724 collected, all passed | **0** |
| `pytest tests/ --cov=argus --cov-fail-under=80` | `Required test coverage of 80% reached. Total coverage: 95.69%` (TOTAL 7315 stmts, 315 miss, 96%) | **0** |
| the six secret-domain modules | 61 passed (58 baseline + the 3 new) | **0** |
| `mypy argus` | `Success: no issues found in 95 source files` | **0** |
| `bandit -r argus --severity-level medium` | 0 medium, 0 high at the medium threshold | **0** |
| `pytest tests/test_gate_seal.py` (run immediately after the `feat` commit) | 9 passed | **0** |
| `pytest tests/test_module_size_ceiling.py test_release_preflight.py test_governance_record_integrity.py test_v1_commitment_closure.py test_status_document_registry.py test_command_assets.py` | 59 passed | **0** |
| `pytest tests/test_dogfood_plan.py test_dogfood_proof.py test_dogfood_artifact_currency.py` (post-regeneration) | 48 passed | **0** |
| `python scripts/regenerate_dogfood_artifacts.py` | 3 artifacts rewritten, provenance sha `2cc5128`, 95 files, 33667 LOC | **0** |

**Which guards actually fired, versus which Section 0.6 predicted.** Section 0.6 was RIGHT: the two
that fired are `test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
and `test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`, both on the
live-LOC derivation (`33648 -> 33667`, exactly this module's `575 -> 594`). Both went green after
regeneration, with **no assertion loosened** (`DF-8-5-B`). `TC-ArgusAgent-DOGFOOD-001-50` did **not**
fire, as Section 0.6 warned. `TC-ArgusAgent-PRECISION-001-94` did **not** fire, because the
`Evidence-partition: none` trailer was written on the `feat` commit **the first time** - Story
18.1's lost sha was not repeated. `tests/test_v1_commitment_closure.py:510` stayed green because
`class SecretFindingEvidence(` was not deleted.

**8. AC5.2 - A DEVIATION FROM A PREDICTED FIGURE, DISCLOSED.** AC5.2 says `secret_scan.py` "is 575
lines and **only shrinks**". It did **not** shrink: it is **594** lines, `+19`. The deletion removes
2 lines, and AC1.2 requires the banner to be **REPLACED, not merely removed**, by text stating what
is true and measurable - which is a substantive comment block, not a one-liner. The two
requirements are in tension and AC1.2 is the binding one; the block follows this module's own
established idiom (the Story 10.3 suppression-branch comment at `:451` is a comparable block in the
same function). **The governing NFR is satisfied with wide headroom:** NFR-M1's ceiling is 1,200
physical lines measured as `len(text.splitlines())`, and `secret_scan.py` is 594 while the new test
module is **344**. `tests/test_module_size_ceiling.py` is green. Recorded rather than silently
absorbed, because the `+19` is also the whole cause of the dogfood regeneration in note 7.

**9. THE ONE SECTION 0 FIGURE THAT CAME OUT DIFFERENT, and why it is not a moved fact.** Section 0.7
records **166** `- id: DF-` lines in the ledger; measured here, **169**. The ledger's byte state was
simultaneously verified **byte-identical** to Section 0.7 (546,616 bytes, 0 CRLF, exactly one lone
`\r`, 7,040 LF), so **the file did not move between contexting and this round** - the difference is
in how the two counts were taken (line-anchored `^- id: DF-` returns 3; unanchored `- id: DF-`
returns 169). Section 0.7 itself says the invariant, not the count, is the thing that must hold. No
action taken.

**10. TWO PRE-EXISTING OBSERVATIONS, recorded and NOT acted on.**

- `tests/test_secret_containment.py` still cannot be collected on its own (`ModuleNotFoundError: No
  module named '_cartridge'`) and was run only as part of whole-directory collection, exactly as
  Section 0.8/(b) requires. Pre-existing; re-confirmed at this HEAD.
- The DOCS-001-78 ledger extractor reports `DF-13-5-A` among its closed ids **at HEAD, before this
  story's append** (36 closed ids at HEAD, of which `DF-13-5-A` is one), even though `DF-13-5-A` is
  OPEN and UNSPENT. That is a pre-existing extractor imprecision, the guard is green at HEAD with
  it, and it is **not this story's** to fix or file. Verified that this story's append adds
  **exactly one** id to that set - `DF-AUD-DETECT-B` - and leaks no false closure onto
  `DF-10-3-B`, `DF-10-4-B`, `DF-AUD-DETECT-C`, `-E` or `-F`.

**11. AC5.1 / AC6.4 - THE WRITE SET, AND A FORCED DECISION ABOUT THE SHARED TREE (`DN-DEV-18-2-A`).**
Section 0.0 warned the tree is shared and already dirty with three Story-18.1 files. Measured at
Task 0, that was still true - and two of those three files are files **this story must also write**:

- `deferred-work.md` - the peer's hunk is `@@ -6376,0 +6377,19 @@` and this story's is
  `@@ -6426,0 +6446,98 @@`. **Two disjoint, pure-insertion hunks**, so they separate cleanly: the
  blob committed here is HEAD's ledger plus **only** this story's 98 lines, verified to be a pure
  insertion (every HEAD line surviving in order) with the byte invariants intact.
- `sprint-status.yaml` - **does NOT separate.** At HEAD `18-2` is `backlog`; the SM's
  `ready-for-dev` transition is itself part of the peer's uncommitted delta, and line **236**
  (`last_updated`) is a **single physical line** carrying the peer's 18-1 REVIEW comment and this
  story's comments together, while line 512 (18-1) is purely the peer's and sits adjacent to line
  513 (18-2) in one hunk. There is no way to commit this story's transition without either
  swallowing the peer's uncommitted 18-1 record (forbidden by Section 2.6 / AC5.5 / AC6.4) or
  publishing a state inconsistent with it. **Decision: the file is WRITTEN on disk - `18-2` reads
  `in-progress` then `review`, with dated status-line comments in the established style and all
  comments and the STATUS DEFINITIONS block preserved - but is deliberately NOT staged in any of
  this story's commits.** It therefore remains a working-tree modification for the peer session (or
  the next orchestrator step) to commit along with its own 18-1 record. `epic-18` was left at
  `in-progress` and no other entry was touched.

**Committed write set, by explicit path, four commits, never `git add -A`:**

| commit | paths |
|---|---|
| `57a278f` `chore` | this story file (new) |
| `2cc5128` `feat` | `argus/detectors/secret_scan.py`, `tests/test_secret_evidence_contract.py` - carries `Evidence-partition: none` |
| `25ff87f` `chore` | the three regenerated dogfood artifacts |
| `docs` | `deferred-work.md` (ledger first in the diff), then this story file |

Verified with `git status --porcelain` (not `git diff --name-only`, which is blind to the untracked
test module): `argus/cache/key.py`, `argus/detectors/base.py`,
`argus/detectors/secret_suppression.py`, `argus/pipeline.py`, `argus/pipeline_stages.py`,
`argus/reports/generator.py`, `architecture.md`, `E-PRD/prd.md`, `epics.md`, the five shipped
secret-domain test modules and every `done` story's record are **all unmodified**, and nothing under
`minions_core/apaa/` was touched.

**12. AC6.3 / `DF-INV-MERGE-A` - STANDING INSTRUCTION FOR WHOEVER LANDS THIS.** The three dogfood
artifacts cite provenance sha `2cc5128`. **If this PR lands squashed or rebased, that sha is
orphaned and `TC-ArgusAgent-DOGFOOD-001-49` reddens `master` after the merge, where no PR check can
see it coming.** Re-run `python scripts/regenerate_dogfood_artifacts.py` on `master` and commit the
result.

**13. NOTHING ESCALATED (AC7).** No `DetectorResult` / `Recording` / `FindingDraft` / `Locator`
field was added; no survivor was deleted or had its signature changed; `code_identity` was not
bumped and `argus/cache/` was not touched; the differing set is empty and the finding total held;
no fenced module was touched; no assertion in the five secret-domain modules was edited; no
`architecture.md` / `prd.md` / `epics.md` / `done`-story record was edited; no new `DF-*` was filed;
`DF-13-5-A` stays OPEN and UNSPENT; no finding became verdict-eligible and no threshold moved; no
`DN-*` was reopened. The >=80% precision keystone stays **NOT CLEARED** and the gate stays
**BLOCKED**. No new dependency and no new import.

**14. WHAT THIS STORY DID NOT FIX, named so it is not mistaken for fixed.** No finding carries
evidence afterwards, and that is the point. FR10's evidence-count gap survives (note 6b).
`base.py`'s `FindingDraft` docstring still names two fields it lacks (note 6a). `DF-10-3-B`,
`DF-10-3-C`, `DF-AUD-DETECT-C`, `-D`, `-E` and `-F` and `DF-10-4-B` all stay OPEN. The 0.4%-class
cost figure dispositions nothing.

**15. THE LEDGER DISPOSITION.** `DF-AUD-DETECT-B` is CLOSED by this story at fix sha `2cc5128`.
The disposition lives in `deferred-work.md` as a dated, append-only note whose original entry is
NOT rewritten (§3.4 evidence immutability), because a disposition recorded in prose and not in the
ledger is not a disposition (`AI-E12-3` / `AI-E12-6`). That note and this record land in the SAME
`docs` commit, ledger first in the diff, so `TC-ArgusAgent-DOCS-001-78` never observes a story
claiming a closure the ledger does not yet carry. Verified with the guard's own analyzers: the
ledger extractor gains **exactly one** id, and no false closure leaks onto any entry this story
merely cites.

### File List

| path | change |
|---|---|
| `argus/detectors/secret_scan.py` | UPDATE - deleted the discarded-value `self._evidence_for(match)` statement; replaced the `PRODUCER-SIDE REDACTION (the keystone)` banner with the measured truth; corrected the module docstring's false "masked indicator + the location are the ONLY things that survive" sentence |
| `tests/test_secret_evidence_contract.py` | NEW - `TC-ArgusAgent-SECRET-001-28`..`-30` (344 lines) |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | APPEND-ONLY - `DF-AUD-DETECT-B`'s dated closure note (+98 lines, pure insertion; 0 CRLF and exactly one lone `\r` re-verified) |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` | REGENERATED by `scripts/regenerate_dogfood_artifacts.py` |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` | REGENERATED by the same renderer |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` | REGENERATED by the same renderer |
| `_bmad-output/design-artifacts/ArgusAgent/stories/18-2-the-redaction-call-keeps-the-evidence-it-computes.md` | this record |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | status transitions only - **written on disk, deliberately NOT staged** (`DN-DEV-18-2-A`, note 11) |

⛔ Not touched: `argus/detectors/base.py`, `argus/detectors/secret_suppression.py`,
`argus/cache/key.py`, `argus/pipeline.py`, `argus/pipeline_stages.py`, `argus/reports/generator.py`,
`architecture.md`, `E-PRD/prd.md`, `epics.md`, any `done` story's record, and anything under
`minions_core/apaa/`.

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-24 | 1.0 | Implemented. Section 0 re-measured by execution first and every premise reproduced (one figure differed by counting method only, ledger bytes identical - completion note 9). `self._evidence_for(match)` DELETED from `run()`; the `PRODUCER-SIDE REDACTION (the keystone)` banner REPLACED with the measured truth (redaction is the absence of a value field on four frozen `extra="forbid"` models); the module docstring's false *"masked indicator + the location are the ONLY things that survive"* sentence corrected. Carrier untouched - a docstring-stripped AST comparison of the whole module reports the removal of that ONE statement as the only semantic difference. Output-neutrality proven ENGINE-VS-ENGINE over one identical 252-file population (91 findings / 38 files both sides, **0 differing**, `_evidence_for` invocations 91 -> 0); the 251-file population re-derives Section 0.2's 88 / 37 / 0. Three guards added in `tests/test_secret_evidence_contract.py` continuing the SECRET index at `-28`..`-30`; `-28` and `-29` observed RED against the shipped body with their text recorded, `-30` GREEN before and after by design and disclosed as a contract pin. `DF-AUD-DETECT-B` given a dated append-only closure note recording the DELETE arm, the four grounds, and the falsification of the entry's own "matches what Story 2.5 says" sentence by `2-5-...md:613`. The new module's 3 self-findings and both Task 5 gaps disclosed, none fixed and none filed (`AI-E9-8`). Suite 1,724 exit 0, coverage 95.69%, mypy clean over 95 files, bandit clean, gate-seal green with `Evidence-partition: none` on the `feat` commit first time. `secret_scan.py` 575 -> 594 lines, a disclosed deviation from AC5.2's "only shrinks" forced by AC1.2 (note 8). `sprint-status.yaml` written but NOT staged - its delta is inseparable from a peer session's uncommitted 18-1 record (`DN-DEV-18-2-A`, note 11). Status `review`. | dev-story (Opus 5) |
| 2026-08-24 | 0.1 | Story contexted at HEAD `c288d40`; §0 measured by execution (AST proof of the single discarded-value call at `:506`; 251-file sweep 88 findings / 37 files with `_evidence_for` nulled → **0 files differ**; cost 0.007 s = 0.4%; emitted-`Recording` payload shows no mask and no evidence field; the behavioural guard proven RED against the shipped body; suite 1,721 collected exit 0, five secret modules 58 passed, mypy clean over 95 files). Three premises found false while measuring: the module docstring's *"masked indicator + location survive"* sentence, `base.py`'s `FindingDraft` docstring naming two absent fields, and — the decisive one — `DF-AUD-DETECT-B`'s claim that widening `DetectorResult` *"matches what Story 2.5 says"*, which Story 2.5's own record forecloses at `:613`. `DN-18-2-1` therefore takes the delete-and-correct arm. Contexting-side guards verified green with this file on disk: `tests/test_governance_record_integrity.py`, `tests/test_status_document_registry.py` and `tests/test_command_assets.py` (18 passed), and the DOCS-001-78 analyzer returns `()` closure claims over this file - after a first draft that did claim one and was corrected. Status `ready-for-dev`. | create-story (Opus 5) |
