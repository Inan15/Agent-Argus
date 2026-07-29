# Story 6.3: Orphan / dead-code detector — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability).
>
> **This is the THIRD story of Epic 6** (Trust Substrate — Self-Audit, Prosecutor & Precision, Tier-B). It
> builds on the fully-done Epics 1+2+3+4+5 and on **done Stories 6.1** (the `LLMDispatchPort` +
> `MinionsLLMAdapter` + `FakeDispatch` + the thin `DeepAuditSeam`) and **6.2** (the FR7 deep-claim
> AST-grounding validator `audit/grounding.py::is_deep_claim_grounded`, which CLOSED DF-1-7-B). `epic-6`
> is already `in-progress`.
>
> **THIS STORY DELIVERS FR12 (orphan / dead-code detection, `[Tier B]`) and CONSUMES the long-carried 🟢
> `DF-1-4-A`** (the 1.4 edge set is unresolved-name only — its `target_story` is literally
> `epic-6-orphan-dead-code-detector`, i.e. THIS story). It adds a detector that, over the 1.4
> whole-repo AST index (`definitions` per file + the call/reference `edges`), flags definitions that are
> never referenced (orphans / dead code) as **advisory** findings — each with a verifiable locator — using
> the standard 1.5 detector base (`detectors/base.py`). Because the 1.4 edge set is **unresolved-name only**
> (DF-1-4-A: bare callee identifier / trailing attribute, NO name binding / scope resolution), the detection
> rule MUST be **CONSERVATIVE**: an unestablishable / ambiguous reference makes a definition NOT-orphan —
> the detector NEVER makes a false dead-code accusation. It mirrors the 1.5 advisory-by-contract moat.

## Story

As an **Engineering Lead** who wants unreachable code surfaced — a function or class that no caller and no
referencing requirement reaches, the classic dead-code that inflates a "we looked at the code" claim while
adding only risk — but who is far more harmed by a FALSE dead-code accusation (deleting live code) than by a
missed orphan,
I want **a pure orphan / dead-code detector** (`detectors/orphan_code.py`) that, given the 1.4 whole-repo AST
index (each file's `definitions` + the call/reference `edges`), flags a `function`/`class` `Definition` as an
orphan finding ONLY when it has **no caller and no referencing requirement that can be ESTABLISHED** from the
available (unresolved-name) edge set — emitting each orphan via the EXISTING 1.5 `build_recording` finding
builder (`finding_id` + ≥1 verifiable locator from the `Definition.ast_span` + `rule_id` + `advisory: true` +
coverage-envelope slice), and routing every un-analyzable / degraded condition to a recorded
`DegradedCondition` rather than a crash,
so that **FR12 is delivered and DF-1-4-A is CONSUMED honestly**: dead code surfaces as an advisory finding
the operator can act on, the CONSERVATIVE rule (an unresolved/ambiguous reference ⇒ NOT-orphan) means APAA
never cries wolf on the unresolved-name edge substrate, and the detector plugs into the existing detector
registry/base with MINIMAL pipeline change — which (given `pipeline.py` is at the 1200-line hard limit)
requires a cohesion split of `pipeline.py` FIRST so the file stays under 1200 lines (NFR-M1).

## Story Context

This is **Story 3 of Epic 6** (Trust Substrate, Tier-B — the "proven, not asserted, depth" moat). It delivers
**FR12 (orphan / dead-code detection, `[Tier B]`)** over the determinism spine (Epics 1–5) and CONSUMES the
🟢 **DF-1-4-A** carry-forward (origin: story 1-4; target_story: `epic-6-orphan-dead-code-detector` = THIS
story; recorded in the 1-4 story file as "the edge set is unresolved-name only … recorded only so the
downstream 1.5/Epic-6 consumers know the edge set is unresolved").

**The substrate already exists — REUSE it, do NOT re-parse (the no-fork keystone, §3.3 / AR7).** The 1.4
tree-sitter AST index (`index/ast_index.py`) already produces, per file, an `AstIndexEntry` carrying
`definitions: tuple[Definition, ...]` (function/class defs with `kind`/`name`/`start_line`/`end_line` + an
`ast_span` token) and `edges: tuple[CodeEdge, ...]` (call/reference edges with `callee`/`line`). The whole
`AstIndex.entries` tuple is exactly the cross-file substrate orphan detection needs. **6.3's detector consumes
the SAME pre-built `definitions`/`edges` — it does NOT re-parse source, does NOT add a second tree-sitter
call, does NOT add a `radon`/`ast`-stdlib parse.** The 1.4 index docstring already states the edge set is
"enough for the Story 1.5 vacuous-path reachability check and the **Epic-6 orphan/dead-code detector**" — this
is the story that consumes it.

**The DF-1-4-A landmine — the edge set is UNRESOLVED-NAME only (the conservative-detection crux).** The 1.4
`CodeEdge` captures only the bare callee identifier or trailing attribute name (`_callee_name` →
`identifier` text or `attribute` trailing name) at a line — there is **NO name binding, NO scope resolution,
NO import resolution, NO method-vs-function disambiguation** (architecture/1.4: "name binding / scope
resolution is deliberately not done here … NOT a full call-graph resolver (that is Epic-6 depth)"). This means
the reference graph is a NAME-MATCH graph, not a resolved call graph. The detector MUST therefore treat
"establishable reference" as: **the definition's `name` appears as a `callee` in SOME edge anywhere in the
repo index** (a name-match). A definition whose name matches no edge `callee` is a *candidate* orphan; but
because the graph is unresolved, any name-collision, dynamic dispatch, decorator/registry reference, dunder
hook, or entrypoint reachability that the unresolved edges cannot see could make it live. **The CONSERVATIVE
rule (locked DN-CONSERVATIVE below): flag an orphan ONLY when the definition's name appears in NO edge
`callee` AND the definition is not covered by an EXCLUSION set of names the unresolved substrate cannot
reason about (dunders, `__all__`/export hooks, test entrypoints, known framework hooks). When in doubt,
NOT-orphan.** A false `audited_shallow` is cheaper than a false 🔴 (1.5/6.2 register); a false dead-code
deletion is the most expensive error this detector could cause — so the bar is asymmetric toward silence.

**Advisory-by-contract (CC #6 / FR33 / the 1.5 moat).** An orphan finding is `advisory=True` — it carries its
evidence (the def's `ast_span`, its kind/name, the "no establishable caller" reason) but, on the
unresolved-name substrate, it can NEVER move the verdict to 🔴 on its own. The verdict-moving promotion of an
advisory finding is the 6.4 Prosecutor's job (AST corroboration AND Prosecutor sign-off); 6.3 EMITS the
advisory finding only. This mirrors the 1.5 vacuous detector exactly: a heuristic finding that informs but
does not, alone, block.

**The standard detector base — REUSE `detectors/base.py` (the registry/Protocol keystone, §3.3).** Every
APAA detector emits the SAME finding row (the 1.2 `Recording`) via the SAME locator-or-reject builder
(`build_recording`, FR13) and satisfies the `Detector` `Protocol` (`rule_id: str` + a pure `run(...) ->
DetectorResult`). The orphan detector is a NEW concrete detector satisfying this Protocol structurally — it
reuses `FindingDraft` → `build_recording` → `Recording` VERBATIM and returns a `DetectorResult` (its
`findings` + `degraded` tuples). **It produces NO `entries` (coverage grades): orphan detection does not grade
file depth — it is a finding-only detector over already-graded files (the SAME additive-findings,
no-double-count pattern Story 2.5's secret detector uses; a no-orphan repo is byte-identical to the pre-6.3
ledger + verdict).**

**The cross-file shape — orphan detection is a WHOLE-INDEX pass, not per-file (the wiring decision).** Unlike
the per-file `VacuousTestDetector` / `SecretScanDetector` / `ToolRunnerDetector` (each scores one file at a
time inside `_detect_per_file`), orphan detection is INHERENTLY cross-file: a definition in file A is "not an
orphan" because file B references it. The detector therefore consumes the WHOLE `AstIndex.entries` (or the
whole `(definitions-by-file, all-edges)` it derives once) in a single `run(index=...)` pass. **Decision
(DN-WHOLE-INDEX, locked below):** wire it as a single whole-index detector pass in the pipeline AFTER
`_detect_per_file` (in `run_audit_detailed` and the resume path), appending its `findings` to the existing
`findings` accumulation — NOT inside the per-file loop. This keeps `_detect_per_file` (per-file) and the
orphan pass (cross-file) cleanly separated and is the minimal, cohesive wiring. On a halted/partial run the
orphan pass runs over the ASSESSED entries only (consistent with `_detect_per_file` running over assessed
entries — no analysis of skipped remainder; document this).

**THE SIZE CONSTRAINT — `pipeline.py` is at the 1200-line hard limit; SPLIT FIRST (NFR-M1, the carry-forward
from the 6-2 review).** `minions_core/apaa/pipeline.py` is currently **1190/1200 lines** — at the §3.2 hard
limit. Adding the orphan detector import + the whole-index pass call + the findings append would push it OVER
1200. **Decision (DN-PIPELINE-SPLIT, locked below): this story MUST first extract a cohesive module out of
`pipeline.py` into a sibling under `apaa/` (documented in both module docstrings) so the file drops well below
1200 BEFORE the orphan wiring is added.** Candidate cohesive seams (pick the cleanest, lowest-blast-radius
one; record the choice + rationale in Dev Notes): (a) the per-file detection orchestration
(`_detect_per_file` + `_grade_non_test_python` + `_read_source` + `_is_python`) → `apaa/pipeline_detect.py`;
(b) the assemble/persist helpers (`_assemble_and_persist` + the `_persist_*` family) →
`apaa/pipeline_persist.py`; (c) the resume shell (`resume_audit_detailed` + its helpers) →
`apaa/pipeline_resume.py`. The extraction is a PURE refactor — NO behavior change, every existing test stays
green byte-identically, the public `run_audit` / `run_audit_detailed` / `resume_audit_detailed` entrypoints
keep their signatures and import locations (re-export from `pipeline.py` if needed so existing imports do not
break). The split is documented in the extracted module's docstring AND `pipeline.py`'s docstring (§3.2 "split
documented in the module docstring"). **The orphan detector itself lives in its OWN new module
`detectors/orphan_code.py` (≤1200 lines, trivially) — the split is about making ROOM in `pipeline.py` for its
WIRING, not about housing the detector.**

**Scope vs the rest of Epic 6 (explicit deferrals — do NOT pull forward).**
- **6.4 adversarial Prosecutor + cut-edge pass (FR19)** — the PROMOTION of an advisory finding to a
  verdict-moving 🔴 (AST corroboration AND Prosecutor sign-off), the ledger-justifies-the-verdict challenge,
  and the `cross_partition` cut-edge re-read are 6.4. 6.3 EMITS advisory orphan findings only; it does NOT
  build the Prosecutor and does NOT make an orphan finding verdict-blocking.
- **6.5 defect-cartridge self-audit harness + holdout + clean controls (FR20)** — the orphan cartridge
  (#3) + the CI-asserted golden-key harness + the clean true-negative controls are 6.5. 6.3 may ship a
  minimal in-test fixture to prove the detector, but it does NOT build the cartridge self-audit harness.
- **6.6 precision replay harness + validation protocol (FR20/OI1 N=5)** — not 6.3.
- **6.7 HITL STOP/PROCEED + decision record (FR23/FR24)** — not 6.3.
- **A RESOLVED call graph / name binding / scope resolution / import resolution** — explicitly OUT OF SCOPE
  (it is the deferred V2 / Epic-6-depth work DF-1-4-A names). 6.3 works over the UNRESOLVED-name edge set and
  is CONSERVATIVE because of it. It does NOT add resolution.
- **A "referencing requirement" traceability resolver** — FR12's full text is "no referencing requirement or
  caller". V1 has no requirement-traceability graph (that is the Story 2.6 "traceability not establishable"
  honesty register). 6.3's "referencing requirement" half is satisfied CONSERVATIVELY: where requirement
  traceability cannot be established, a def is NOT flagged solely on caller-absence if it is on the
  exclusion/entrypoint set — i.e. 6.3 does NOT invent a requirement graph; it stays conservative. Record this
  honest-limitation in the detector docstring + Dev Notes.

**Carry-forward action items (CLAUDE.md §9.1 / L1-E11 — each 6.x story cites its AI-E5-* item).**
- **DF-1-4-A (other 🟢) — THE consumed defer.** This story is DF-1-4-A's `target_story`. The unresolved-name
  edge set is consumed CONSERVATIVELY. Back-fill DF-1-4-A into `_bmad-output/design-artifacts/APAA/
  deferred-work.md` (it currently lives ONLY in the 1-4 story file's `[Review][Defer]` line) AND append the
  consumption note (CONSUMED 2026-… by story 6.3; the conservative rule; what the unresolved substrate can
  and cannot prove) — per AI-E5-4's "keep story-file copies as evidence; back-fill + close in the central
  register". If 6.3 files a NEW defer (e.g. "resolved call graph for higher orphan recall — Epic-6-depth/V2"),
  file it append-only with the six CC-3 fields.
- **AI-E5-1 (test-infra 🟠) — the COMPLETE-THE-DECLARED-SET keystone-adequacy checklist.** Applied to 6.3's
  orphan-classification input set: enumerate the full set of `(definition, edge-graph)` shapes the detector
  must classify — **a referenced def (name appears as an edge callee → NOT-orphan), an unreferenced def with
  no name-match (→ orphan finding), a dunder/`__init__`/`__all__`/test-entrypoint def (excluded → NOT-orphan
  even with no caller), a name-collision (two defs share a name; one is called → BOTH NOT-orphan,
  conservative), a non-Python / parse-failed / `ast_eligible=False` entry (no defs to analyze → skipped, no
  finding), an empty-`definitions` / empty-`edges` index, and a non-ASCII-bearing `Definition.name`** — and
  demonstrate EACH member covered (RED-first where applicable). The retro names this pattern explicitly.
- **AI-E5-1 no-crash leg (AR10 / NFR-R1).** The detector must NEVER raise out of the pipeline: a
  malformed / empty / None index, an entry with `parse_failed=True`, a `definitions`/`edges` tuple in any
  shape, a `Definition` with a `None`/empty name → a recorded `DegradedCondition` or a NOT-orphan
  classification, never an uncaught raise. NAMED handling, no bare `except`, no `print()`.
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** A def with a
  non-ASCII identifier (`Definition.name`) / a non-ASCII file path must classify + (when orphan) build a
  finding + serialize + derive a stable `recording_id` under `PYTHONIOENCODING=utf-8` (the single serializer
  is `ensure_ascii=False`). ≥1 fixture carries a non-ASCII value.
- **AI-E5-4 (governance 🟢) — central defer register.** Back-fill + consume DF-1-4-A in `deferred-work.md`
  (above); any NEW defer carries the six CC-3 fields, append-only.
- **AI-E5-7 (process 🟢) — keep the structural gates green + partial-reuse docstring precision.** The new
  detector must keep the no-web-imports gate (`apaa.* ⊬ fastapi/uvicorn/starlette`) and the single-serializer
  AST gate green — it is PURE (no provider import; the only serializer touch is the EXISTING `build_recording`
  → `canonical` id-hash, no new `json.dumps`/hasher/parse). When reuse is PARTIAL (consumes
  `definitions`/`edges`, composes `build_recording`), narrate it precisely ("consumes the 1.4 pre-built AST
  index; computes a pure name-reachability fact; composes the EXISTING `build_recording`", not "reuses the AST
  index wholesale").
- **AI-E5-3 (process 🟠) — committed pre-`review` test-existence guard.** NOT 6.3's primary deliverable, but
  6.3 MUST honor the in-session test-existence discipline (the detector + its tests + the pipeline-split
  green-everything proof EXIST + pass before the `review` flip).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 6.3) + the architecture (FR12 orphan/dead-code; the 1.4 edge
> set is the substrate; CC #6 advisory-by-contract) + the PRD (FR12 + FR13 locator-or-reject) + DF-1-4-A
> (unresolved-name edges → conservative detection). Drivers: **APAA-FR-12** (detect orphan / dead code — no
> referencing requirement or caller), **APAA-FR-13** (every finding carries ≥1 verifiable locator or is
> rejected, not emitted — via the EXISTING `build_recording`), **APAA-FR-33-support / CC #6** (advisory-by-
> contract: the orphan finding is `advisory=True` and cannot alone move the verdict to 🔴; the Story 6.4
> Prosecutor owns promotion), **APAA-NFR-D2** (the detector is a pure, zero-LLM-token scorer over recorded
> inputs), **APAA-AR10 / NFR-R1** (a malformed / empty / parse-failed input → a recorded `DegradedCondition`
> or NOT-orphan, NEVER an uncaught raise), **APAA-AR7 / §3.3** (REUSE the 1.4 `definitions`/`edges` BY IMPORT
> — no re-parse, no second tree-sitter/ast/radon call; compose the EXISTING `build_recording` — no finding
> fork), **APAA-AR8** (the detector is PURE — no I/O, no clock, no LLM, no provider import, no float),
> **APAA-AR4** (single canonical serializer; content-derived ids; no clock/uuid/random/iteration-order),
> **APAA-NFR-S1** (no source/secret bytes — cite `Definition` names/spans/counts, never source excerpts),
> **APAA-NFR-M1** (≤1200-line files — the `pipeline.py` split), **APAA-NFR-M2** (frozen Epic-1..6 contracts
> unchanged; additive-only).
>
> **SCOPE FENCE — Tier-B, single-purpose, the FR12 orphan detector + DF-1-4-A consumption.** This story
> delivers ONLY: (1) the pure orphan/dead-code detector (`detectors/orphan_code.py`) satisfying the 1.5
> `Detector` `Protocol`, computing the CONSERVATIVE name-reachability fact over the whole 1.4 AST index and
> emitting `advisory=True` orphan findings via the EXISTING `build_recording` (FR13 locator-or-reject); (2)
> the **`pipeline.py` cohesion split** (DN-PIPELINE-SPLIT — a pure no-behavior-change refactor extracting a
> cohesive sibling so `pipeline.py` < 1200 lines) FIRST; (3) the minimal pipeline wiring (a single
> whole-index orphan pass after `_detect_per_file`, appending findings — DN-WHOLE-INDEX); (4) the
> complete-the-declared-set + no-crash + non-ASCII tests; (5) the DF-1-4-A back-fill + consumption note. It
> does NOT build, and MUST NOT pull forward: the **adversarial Prosecutor + verdict-moving promotion of an
> advisory finding** (6.4); the **cartridge self-audit harness + holdout + clean controls** (6.5); the
> **precision replay harness** (6.6); the **HITL STOP/PROCEED + decision record** (6.7); a **resolved call
> graph / name binding / scope resolution / import resolution** (DF-1-4-A V2/Epic-6-depth — 6.3 stays on the
> unresolved-name substrate); a **requirement-traceability graph**; a **second tree-sitter / `ast` / `radon`
> parse** (REUSE the 1.4 index); an **edit to the frozen `coverage_ledger.py` / `recording.py` / `base.py`
> contracts** (compose them as-is); a **live provider-backed LLM call** (the detector is pure + zero-token);
> a **new `.github/workflows` CI job**; a **new HTTP route / FastAPI surface / UI** (§3.7); a **new `cli.py`
> flag**.

**AC1 — `pipeline.py` is split into a cohesive sibling FIRST so it stays < 1200 lines, with NO behavior change (NFR-M1 / DN-PIPELINE-SPLIT / §3.2)**
**Given** `minions_core/apaa/pipeline.py` is at the 1190/1200-line hard limit and the orphan wiring would push
it over
**When** the story lands
**Then** BEFORE the orphan wiring is added, a cohesive seam is extracted from `pipeline.py` into a new sibling
under `minions_core/apaa/` (e.g. `pipeline_detect.py` / `pipeline_persist.py` / `pipeline_resume.py` — the
chosen seam + rationale recorded in Dev Notes), `pipeline.py` drops well below 1200 lines, and the public
`run_audit` / `run_audit_detailed` / `resume_audit_detailed` entrypoints keep their signatures AND their
existing import locations (re-export from `pipeline.py` if a symbol moved, so no existing import breaks)
**And** the split is a PURE refactor: the FULL existing `tests/apaa/` suite passes BYTE-IDENTICALLY (no
fixture/golden change attributable to the split — any orphan-detection re-grade is AC4, not the split), and
both the extracted module's docstring AND `pipeline.py`'s docstring document the split (§3.2 "split documented
in the module docstring") and every resulting file is ≤1200 lines.

**AC2 — A pure orphan / dead-code detector flags an unreferenced definition as an advisory finding over the 1.4 AST index (FR12 / FR13 / AR8 / §3.3 no re-parse)**
**Given** a new detector `detectors/orphan_code.py` satisfying the 1.5 `Detector` `Protocol` (a `rule_id: str`
+ a pure `run(...) -> DetectorResult`), consuming the WHOLE pre-built 1.4 AST index (`AstIndex.entries` /
the `definitions` + `edges` it derives once)
**When** it runs over a repo where a `function`/`class` `Definition` is referenced by NO establishable caller
(its `name` appears as NO `CodeEdge.callee` anywhere in the index) and is not on the exclusion/entrypoint set
**Then** it emits an `advisory=True` orphan `Recording` for that definition via the EXISTING
`build_recording` (`detectors/base.py`) — carrying a `finding_id` (content-derived id, AR4), ≥1 verifiable
`Locator` built from the def's file + line span + `Definition.ast_span` (FR13 locator-or-reject — a
locator-less finding is rejected, not emitted), a stable `rule_id` (e.g. `orphan_code`), and a
`coverage_envelope_slice`
**And** it consumes the PRE-BUILT `definitions`/`edges` (the 1.4 substrate the 1.5 subset already reads) — it
does NOT re-parse source, add a second tree-sitter call, or import `ast`/`radon` for a second parse (AR7 /
§3.3 no-fork); it is PURE (no I/O, no clock, no LLM, no provider import, no float — AR8); the finding cites
the `Definition` name / `ast_span` / counts only, NEVER a source excerpt (NFR-S1); and the detector produces
NO coverage `entries` (orphan detection does not grade depth — the additive-findings, no-double-count pattern
of the 2.5 secret detector).

**AC3 — Detection is CONSERVATIVE on the unresolved-name edge set — NEVER a false dead-code accusation (DF-1-4-A / CC #6 / FR12)**
**Given** the 1.4 edge set is UNRESOLVED-NAME only (DF-1-4-A: bare callee identifier / trailing attribute, no
name binding / scope resolution / import resolution)
**When** the detector decides whether a definition is an orphan
**Then** it flags an orphan ONLY when the definition's name appears in NO edge `callee` across the whole index
AND the definition is not covered by the locked EXCLUSION set (dunder methods `__init__`/`__call__`/etc.,
`__all__`/export-hook names, test-entrypoint names like `test_*`/`setUp`/`tearDown`, and a small locked set of
known framework/registry/decorator hook names the unresolved substrate cannot reason about) — and on ANY
ambiguity (a name-collision where two defs share a name and ANY one is referenced → BOTH are NOT-orphan; a
def reachable only via dynamic dispatch / decorator the edges can't see) the detector resolves to NOT-orphan
**And** the conservative rule + its HONEST limitation ("grounds REACHABILITY over an unresolved-name graph —
it can miss an orphan a resolved graph would catch (low recall), but it does NOT falsely accuse live code
(high precision is the asymmetric priority); requirement-traceability is not established in V1") is documented
in the detector docstring + Dev Notes, in the SAME honesty register as the 1.5 vacuous detector; the finding
is `advisory=True` and CANNOT alone move the verdict to 🔴 (the 6.4 Prosecutor owns promotion).

**AC4 — Minimal, cohesive pipeline wiring: a single whole-index orphan pass after `_detect_per_file`; a no-orphan repo is byte-identical to pre-6.3 (DN-WHOLE-INDEX / NFR-M2)**
**Given** the per-file detectors run inside `_detect_per_file` but orphan detection is INHERENTLY cross-file
**When** the pipeline runs
**Then** the orphan detector runs as a SINGLE whole-index pass AFTER `_detect_per_file` (in
`run_audit_detailed` and the resume path), appending its `findings` to the EXISTING `findings` accumulation
(NOT inside the per-file loop); on a halted/partial run it runs over the ASSESSED entries only (consistent
with `_detect_per_file`; documented), and its `degraded` conditions fold as the existing detectors' do
**And** a repo with NO orphans produces NO new findings and NO coverage entry → the resulting `.apaa/` ledger
+ verdict + persisted artifacts are BYTE-IDENTICAL to the pre-6.3 path (the regression-safe property — only
an actual orphan adds an advisory finding); the frozen Epic-1..6 contracts (`coverage_ledger.py`,
`recording.py`, `detectors/base.py`, `index/ast_index.py`, `store/*`, `verdict/*`, `cache/*`, `models.py`)
show NO working-tree diff (the detector COMPOSES `build_recording`; it does not edit the base).

**AC5 — Complete-the-declared-set + no-crash matrix over the orphan-classification input set, each RED-first where applicable (AI-E5-1 / AR10)**
**Given** the full DECLARED set of `(definition, edge-graph)` shapes the detector must classify
**When** the detector is tested
**Then** EACH member is covered: (a) a def whose `name` appears as an edge callee → NOT-orphan (no finding);
(b) an unreferenced def with no name-match and not excluded → an `advisory` orphan finding (the FR12 happy
path); (c) a dunder / `__init__` / `__all__` / `test_*` entrypoint def with no caller → EXCLUDED → NOT-orphan
(the conservative exclusion); (d) a name-collision (two defs share a `name`, one is referenced) → BOTH
NOT-orphan (the conservative ambiguity rule — the DF-1-4-A unresolved-name guard, RED-first against a naive
"each def checked independently" implementation that would false-flag the uncalled twin); (e) a non-Python /
`parse_failed` / `ast_eligible=False` entry (no defs) → no finding, NEVER a crash; (f) a malformed / empty /
None index / a `Definition` with a `None`/empty name → a recorded `DegradedCondition` or NOT-orphan, NEVER an
uncaught raise (the no-crash leg — NAMED handling, no bare `except`); (g) a non-ASCII `Definition.name` /
non-ASCII path → classifies + (when orphan) builds a finding + serializes + derives a stable `recording_id`
under `PYTHONIOENCODING=utf-8` (AI-E1-1)
**And** the enumeration is explicit in the test module (the complete-the-declared-set discipline — the
practice that caught 3.4 / 4.2 / 5.1 / and the 6.2 construct set).

**AC6 — Determinism, purity, secret-containment, and the frozen contracts hold; ≤1200 lines; mypy (NFR-D1/D2 / AR8 / NFR-S1 / NFR-M1/M2)**
**Given** the new detector + the pipeline split + the orphan wiring
**When** the suite runs under `PYTHONIOENCODING=utf-8`
**Then** the detection path stays PURE + deterministic + ZERO-token (no LLM — NFR-D1/D2); orphan findings are
emitted in a SORTED, deterministic order (by file_path then start_line then name — AR11, no set/dict-order
reliance); the detector imports NO provider code and NO FastAPI (the no-web-imports gate stays green); no
source/secret bytes enter any finding (cite `Definition` names / `ast_span` / counts, NEVER source excerpts —
NFR-S1); any count/ratio-shaped value is `int`/`Fraction`/str, never float (AR4 — though 6.3's orphan fact is
a boolean over a name-set membership, no ratio); content-derived `recording_id` via the EXISTING
`build_recording` (no `uuid4`/counter/arrival order)
**And** each new/modified file is ≤1200 lines (NFR-M1 — `pipeline.py` is now well under after the split,
`detectors/orphan_code.py` is small); `mypy` is clean on the new/modified modules; the frozen Epic-1..6
contracts show NO working-tree diff beyond the documented AC1 split re-exports + the AC4 wiring.

**AC7 — No regression / no scope creep; structural gates green; mypy clean; the pre-`review` test-existence precondition (AI-E5-7 / AI-E5-3 / the thin-slice discipline)**
**Given** the new detector + the pipeline split + the orphan wiring + their tests
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the prior green baseline + the new 6.3 orphan tests, with the split changing NO fixture/golden and a
no-orphan repo byte-identical), and the import-isolation gate (web-stack), the single-serializer AST gate (the
detector adds NO `json.dumps`/hasher/second parse — it composes `build_recording` only), and the file-size
gate stay green; `mypy` is clean
**And** NO new `.apaa/` write path is introduced (orphan findings flow through the EXISTING findings persist
fold), NO `cli.py` flag, NO HTTP route, NO new CI job, NO live LLM call
**And** the new test files cite their `APAA-FR-12` / `APAA-FR-13` / `APAA-AR10` / DF-1-4-A drivers in the
module docstring + the locked test area / index; the mandatory artifacts EXIST + pass + the DF-1-4-A
back-fill/consumption note is filed BEFORE the story flips to `status: review` (AI-E5-3 / AI-E2-1
test-existence discipline). **Test area `APAA-ORPHAN`** (`TC-APAA-ORPHAN-001-NN` — start at `-01`; lock the
area + index in the module docstring); the pipeline-split assertions may use the existing `APAA-PIPELINE`
area.

## Tasks / Subtasks

- [x] **Task 0 — Re-read the REAL surfaces; LOCK the conservative rule, the detector shape, the whole-index wiring, and the pipeline split seam** (AC: 1, 2, 3, 4)
  - [x] Re-read `minions_core/apaa/index/ast_index.py` (`Definition` = `name/kind/start_line/end_line` +
        `ast_span`; `CodeEdge` = `callee/line` — UNRESOLVED-name; `AstIndexEntry` = `file_path/ast_eligible/
        parse_failed/definitions/edges`; `AstIndex.entries`). LOCK: the detector CONSUMES the pre-built
        index — NO re-parse (§3.3 / AR7); the reference graph is a NAME-MATCH graph (DF-1-4-A), so the rule
        is conservative.
  - [x] Re-read `minions_core/apaa/detectors/base.py` (`Detector` `Protocol`, `FindingDraft`,
        `build_recording`, `DetectorResult`, `DegradedCondition`). LOCK: the orphan detector satisfies the
        Protocol structurally, composes `build_recording` (FR13), returns `findings` + `degraded` and NO
        `entries` (no coverage grade — the 2.5 additive-findings pattern).
  - [x] Re-read `minions_core/apaa/detectors/secret_scan.py` + `detectors/vacuous_test.py` (the standard
        detector idiom: a frozen evidence model, advisory framing, the "what it can/cannot prove" register,
        named degradation, content-derived id). REUSE the idiom; do NOT fork the finding model.
  - [x] Re-read `minions_core/apaa/pipeline.py` — measure the current line count (≈1190), the `_detect_per_file`
        per-file loop (lines ≈370-456), the `run_audit_detailed` + resume call sites, `_assemble_and_persist`,
        the `_persist_*` family, and the module docstring/cost section. LOCK the split seam (DN-PIPELINE-SPLIT)
        + the whole-index orphan pass site (DN-WHOLE-INDEX — after `_detect_per_file`, over assessed entries on
        a halt). Record the chosen seam + rationale.
  - [x] Re-read the 1-4 story file's DF-1-4-A `[Review][Defer]` line + `_bmad-output/design-artifacts/APAA/
        deferred-work.md` header. LOCK: 6.3 is DF-1-4-A's `target_story`; back-fill + consume it (Task 5).
  - [x] Enumerate + LOCK the EXCLUSION set (dunders, `__all__`/export hooks, `test_*`/`setUp`/`tearDown`
        entrypoints, a small locked framework/registry/decorator hook list). Record the set + its conservative
        rationale in Dev Notes — it is the false-accusation moat, frozen for 6.5's clean controls.
- [x] **Task 1 — Split `pipeline.py` into a cohesive sibling FIRST (pure refactor, NO behavior change)** (AC: 1, 6)
  - [x] Extract the chosen cohesive seam (Task 0) into a new `minions_core/apaa/pipeline_<seam>.py`. Keep the
        public `run_audit` / `run_audit_detailed` / `resume_audit_detailed` signatures + import locations
        stable (re-export from `pipeline.py` if a symbol moved). Document the split in BOTH docstrings (§3.2).
  - [x] Run the FULL `tests/apaa/` suite — it must pass BYTE-IDENTICALLY (no fixture/golden change from the
        split). Confirm `pipeline.py` < 1200 lines and the new module ≤1200 lines.
- [x] **Task 2 — Build the pure orphan / dead-code detector** (AC: 2, 3, 6)
  - [x] `detectors/orphan_code.py`: a concrete detector (`rule_id = "orphan_code"`) with a pure
        `run(*, index: AstIndex) -> DetectorResult` (or `run(*, entries=...)`). Derive ONCE the set of all
        edge `callee` names across the index + the locked EXCLUSION set. For each `Definition` in each
        ast-eligible entry: orphan iff its `name` is in NO callee set AND not excluded AND not part of a
        name-collision where any twin is referenced (DN-CONSERVATIVE). Emit an `advisory=True` orphan finding
        via `build_recording` (locator from file + span + `ast_span`); produce NO coverage `entries`.
  - [x] PURE, no I/O / clock / LLM / provider import / float; NEVER raises on a degraded entry (AR10 — a
        malformed/None/parse-failed entry → a recorded `DegradedCondition` or NOT-orphan). Findings sorted
        deterministically (AR11). Docstring: the conservative rule + its HONEST limitation (low recall / high
        precision; unresolved-name substrate; requirement-traceability not established in V1), the `APAA-FR-12`
        / `APAA-FR-13` / DF-1-4-A drivers, the `APAA-ORPHAN` area + index `-01`.
- [x] **Task 3 — Wire the whole-index orphan pass into the pipeline (minimal, after `_detect_per_file`)** (AC: 4, 7)
  - [x] In `run_audit_detailed` (and the resume path): after `_detect_per_file`, run a single
        `OrphanCodeDetector().run(index=...)` (over assessed entries on a halt — consistent with
        `_detect_per_file`), and `findings.extend(orphan_result.findings)` + fold `degraded` as the existing
        detectors do. NO change to `_grade_non_test_python` / the per-file loop / the verdict math / the
        persist order. A no-orphan repo stays byte-identical (AC4).
- [x] **Task 4 — Tests: complete-the-declared-set + no-crash + non-ASCII + the conservative name-collision guard** (AC: 2, 3, 5)
  - [x] New `tests/apaa/test_orphan_code_detector.py` (area `APAA-ORPHAN`, `TC-APAA-ORPHAN-001-NN`): the full
        declared set (referenced→not-orphan / unreferenced→orphan / excluded-entrypoint→not-orphan /
        name-collision→both-not-orphan / non-Python-or-parse-failed→no-finding / malformed-no-crash /
        non-ASCII). The (d) name-collision member is the DF-1-4-A conservative guard: RED against a naive
        per-def check, GREEN under the collision-aware rule.
  - [x] A pipeline-level assertion (area `APAA-PIPELINE`): a repo with a planted orphan def yields the advisory
        orphan finding end-to-end (whole-index pass wired); a no-orphan repo is byte-identical to pre-6.3
        (ledger + verdict + persisted locators unchanged).
- [x] **Task 5 — Run + mypy + gates + the DF-1-4-A back-fill/consumption + the pre-`review` precondition** (AC: 6, 7)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
        all pass (prior baseline + the new 6.3 tests; the split changed NO fixture/golden; no-orphan repo
        byte-identical). `mypy` clean on the new/modified modules.
  - [x] Confirm NO working-tree diff to the frozen Epic-1..6 surfaces beyond the AC1 split re-exports + the
        AC4 wiring (`coverage_ledger.py`/`recording.py`/`detectors/base.py`/`ast_index.py`/`verdict/*`/`cache/*`
        byte-identical). Confirm the no-web-imports + single-serializer + file-size gates green. NO
        `cli.py`/HTTP/CI-job change.
  - [x] **DF-1-4-A / AI-E5-4 / AI-E5-7:** back-fill DF-1-4-A into `_bmad-output/design-artifacts/APAA/
        deferred-work.md` (the central register — it currently lives only in the 1-4 story line; keep the
        story-file copy as evidence) AND append the consumption note (CONSUMED 2026-… by story 6.3; the
        conservative rule; the unresolved-name limitation). If a NEW defer is filed (e.g. resolved call graph
        for higher recall — Epic-6-depth/V2), the six CC-3 fields.
  - [x] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (the detector + the pipeline split + the wiring +
        the new tests incl. the conservative name-collision guard + the pipeline-level assertion) EXIST + pass
        BEFORE the `review` flip; the Dev Agent Record is filled completely (no blank placeholders), incl. the
        chosen split seam + rationale and the locked exclusion set.

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **FR12 = detect orphan / dead code (no referencing requirement or caller), each with a verifiable locator
  (FR12 + FR13, epic Story 6.3 AC).** "It flags functions/classes with no caller and no referencing
  requirement as orphan findings, each with a verifiable locator." V1's orphan fact is DETERMINISTIC and
  STRUCTURAL: a `function`/`class` `Definition` whose `name` appears as NO `CodeEdge.callee` across the whole
  1.4 index AND is not on the exclusion/entrypoint set is a candidate orphan; the requirement half is
  satisfied conservatively (no V1 requirement-traceability graph — that is the 2.6 "traceability not
  establishable" register).
- **CONSERVATIVE on the unresolved-name edge set — NEVER a false dead-code accusation (DN-CONSERVATIVE —
  DF-1-4-A, the false-accusation moat).** The 1.4 edges are unresolved-name only (no binding/scope/import
  resolution). So the graph is a NAME-MATCH graph. The asymmetric harm — a false dead-code deletion is far
  worse than a missed orphan — locks the bar toward silence: a name-collision where any twin is referenced ⇒
  BOTH not-orphan; any def reachable via dynamic dispatch / decorator / registry the edges can't see ⇒
  not-orphan (covered by the exclusion set); when in doubt ⇒ not-orphan. The finding is `advisory=True` (CC
  #6) — it informs, it does not, alone, block (6.4 Prosecutor owns promotion). Honest limitation: low recall,
  high precision — documented in the detector docstring (the 1.5 register).
- **REUSE the 1.4 AST index — NO re-parse (§3.3 / AR7 / the no-fork keystone).** The detector consumes the
  pre-built `AstIndex.entries` (`definitions` + `edges`) — the SAME substrate the 1.5 subset + the 6.2
  grounding validator read. It does NOT call tree-sitter again, NOT import `ast`/`radon` for a second parse.
  One grammar version, one parse — determinism + the single-serializer discipline intact.
- **REUSE the 1.5 detector base — compose `build_recording`, satisfy the `Detector` `Protocol` (§3.3).** The
  orphan detector is a NEW concrete detector satisfying the `Detector` `Protocol` structurally; it builds its
  finding via the EXISTING `build_recording` (FR13 locator-or-reject, content-derived id) and returns a
  `DetectorResult`. It edits NOTHING in `detectors/base.py` / `ledger/recording.py`. It produces NO coverage
  `entries` (orphan detection is finding-only — the 2.5 secret-detector additive-findings pattern; a no-orphan
  repo is byte-identical to pre-6.3).
- **Whole-index, not per-file (DN-WHOLE-INDEX — the wiring decision).** Orphan detection is inherently
  cross-file (a def is live because another file references it). The detector consumes the WHOLE index in one
  `run` pass; the pipeline wires it as a SINGLE pass AFTER `_detect_per_file` (NOT inside the per-file loop),
  appending findings. On a halt it runs over the ASSESSED entries only (consistent with `_detect_per_file`).
- **The `pipeline.py` SPLIT FIRST (DN-PIPELINE-SPLIT — NFR-M1, the 6-2-review carry-forward).** `pipeline.py`
  is at 1190/1200. Extract a cohesive seam (the per-file detection orchestration, OR the assemble/persist
  helpers, OR the resume shell) into a new `apaa/pipeline_<seam>.py` BEFORE adding the orphan wiring, so the
  file stays < 1200. PURE refactor — no behavior change, every existing test byte-identical, public
  entrypoints + import locations stable (re-export if a symbol moved). Document the split in both docstrings.
- **No-crash matrix → recorded condition / NOT-orphan, NEVER an uncaught raise (AR10 / NFR-R1 / AI-E5-1).** A
  malformed / empty / None index, a `parse_failed` entry, a `Definition` with a `None`/empty name → a recorded
  `DegradedCondition` or a NOT-orphan classification. NAMED handling, no bare `except: pass`, no `print()`.
- **No source/secret bytes (NFR-S1 / CC #5).** An orphan finding cites the `Definition` name / `ast_span` /
  counts — NEVER source excerpts. No new `.apaa/` write path (findings flow through the EXISTING persist fold).
- **PURE + deterministic + zero-token (NFR-D1/D2 / AR8).** The detector is a pure fold over the AST index —
  no I/O, no clock, no LLM, no provider import, no float. Findings sorted deterministically (AR11). A
  non-ASCII def name derives a stable id under `PYTHONIOENCODING=utf-8` (`ensure_ascii=False` single
  serializer — AI-E1-1).
- **Frozen contracts unchanged (AR8 / NFR-M2).** Verify NO working-tree diff to `store/{canonical,envelope}.py`,
  `cache/key.py`, `ledger/recording.py`, `ledger/coverage_ledger.py`, `detectors/base.py`, `index/ast_index.py`,
  `verdict/*`, `models.py` — beyond the AC1 split re-exports + the AC4 wiring.

### Project Structure Notes

- **The detector lives in a NEW `minions_core/apaa/detectors/orphan_code.py`** (small, ≤1200 lines trivially).
  It is PURE-of-providers (the no-web-imports gate) and consumes the 1.4 `AstIndex`.
- **The pipeline split** produces a new `minions_core/apaa/pipeline_<seam>.py` (chosen seam recorded in the
  Dev Agent Record). The orphan WIRING is a single whole-index pass in `run_audit_detailed` + the resume path.
- **Test area `APAA-ORPHAN`** (`TC-APAA-ORPHAN-001-NN`, start `-01`) for the detector; the pipeline-split /
  whole-index wiring assertions may use `APAA-PIPELINE`. New test: `tests/apaa/test_orphan_code_detector.py`.
  Lock the area + index in the module docstring.
- **DO NOT** add a `cli.py` flag, an HTTP route, a `.github/workflows` CI job, a second parser, or any
  `.apaa/` write path. DO NOT build 6.4 Prosecutor / 6.5 cartridge-harness / 6.6 precision / 6.7 HITL. DO NOT
  add name binding / scope resolution / a resolved call graph (DF-1-4-A V2). DO NOT make the orphan finding
  verdict-blocking (it is `advisory=True`; 6.4 owns promotion). DO NOT wire a live LLM call.

### DF-1-4-A consumption notes (AC3 — read before writing the detector)

- DF-1-4-A (`index/ast_index.py:186-231`): the `CodeEdge` set is unresolved-name only — the bare callee
  identifier / trailing attribute, no name binding / scope resolution. It is the AC-sanctioned V1 substrate
  (the 1.4 story explicitly recorded it "so the downstream 1.5/Epic-6 consumers know the edge set is
  unresolved"). Its `target_story` is `epic-6-orphan-dead-code-detector` = THIS story.
- The consumption is HONEST: 6.3 builds reachability over a NAME-MATCH graph, not a resolved call graph. It is
  conservative (high precision, low recall) by design. Back-fill DF-1-4-A into `deferred-work.md` and append
  the consumption note; if higher recall (a resolved call graph) is wanted later, file it as a NEW defer
  targeting Epic-6-depth / V2 with the six CC-3 fields.

### References

- [Source: _bmad-output/design-artifacts/APAA/epics.md#Story-6.3] — the FR12 orphan/dead-code AC (flag functions/classes with no caller and no referencing requirement; each with a verifiable locator).
- [Source: _bmad-output/design-artifacts/APAA/architecture.md] — FR12 orphan/dead-code (Epic 6, Tier B); the 1.4 edge set as the structural substrate; CC #6 advisory-by-contract (no cry-wolf).
- [Source: minions_core/apaa/index/ast_index.py] — `Definition` / `CodeEdge` (UNRESOLVED-name, DF-1-4-A) / `AstIndexEntry` / `AstIndex.entries` — the pre-built substrate the detector REUSES (no re-parse).
- [Source: minions_core/apaa/detectors/base.py] — the `Detector` `Protocol` + `FindingDraft` + `build_recording` (FR13 locator-or-reject, content-derived id) + `DetectorResult` / `DegradedCondition` — the standard detector base the orphan detector composes (no fork).
- [Source: minions_core/apaa/detectors/secret_scan.py] — the standard detector idiom (advisory framing, frozen evidence model, named degradation, "what it can/cannot prove" register, additive-findings/no-double-count) to mirror.
- [Source: minions_core/apaa/detectors/vacuous_test.py] — the 1.5 advisory-by-contract moat the orphan finding mirrors (a heuristic finding that informs but does not, alone, block).
- [Source: minions_core/apaa/pipeline.py] — `_detect_per_file` (the per-file loop; orphan is cross-file → wired AFTER it), `run_audit_detailed` + the resume path (the wiring sites), `_assemble_and_persist` + `_persist_*` (the split candidates); the file is at 1190/1200 → split FIRST (NFR-M1).
- [Source: _bmad-output/design-artifacts/APAA/stories/1-4-tree-sitter-ast-index-repo-intake-python-stack-detection.md] — the DF-1-4-A `[Review][Defer]` line (the defer this story consumes) + its CC-3 fields.
- [Source: _bmad-output/design-artifacts/APAA/stories/6-2-full-python-ast-grounding-of-audited-deep-claims.md] — the Epic-6 precedent (REUSE 1.4, compose the keystone, pure detector, complete-the-declared-set, no-crash, non-ASCII, scope-fence vs 6.4/6.5/6.6/6.7) this story mirrors.

## Dev Agent Record

### Context Reference

- Story spec: this file (`6-3-orphan-dead-code-detector.md`).
- Substrate reused (no re-parse / no fork): `minions_core/apaa/index/ast_index.py`
  (`Definition`/`CodeEdge`/`AstIndexEntry`/`AstIndex`), `minions_core/apaa/detectors/base.py`
  (`Detector` Protocol / `FindingDraft` / `build_recording` / `DetectorResult` / `DegradedCondition`),
  the 2.5 `detectors/secret_scan.py` idiom (advisory framing, frozen evidence, named degradation,
  additive-findings/no-coverage-entry).
- Consumed defer: DF-1-4-A (`epic-6-orphan-dead-code-detector` = this story).

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement).

### Debug Log References

- Initial split + wiring caused 2 resume byte-identity failures
  (`test_e2e_resume_reaches_identical_verdict_and_ledger_as_uninterrupted_run`,
  `test_e2e_chained_partial_then_complete_resume_reaches_identity`). Root cause: orphan findings
  are CROSS-FILE; a prior PARTIAL run computed them over a SUBSET (smaller referenced-name universe ⇒
  more apparent orphans), and carrying those forward diverged from an uninterrupted run. Fix: on
  resume, DROP prior `orphan_code` findings and RECOMPUTE the whole-index orphan pass over the resumed
  assessed set (`carried_forward ∪ resume_target` from the current index). Both tests green after.

### Completion Notes List

- **AC1 (pipeline split FIRST, pure refactor).** Chosen seam (DN-PIPELINE-SPLIT): the cohesive
  `.apaa/` PERSIST family — extracted `_persist` + the `_persist_*` helpers VERBATIM into the new
  sibling `minions_core/apaa/pipeline_persist.py` (renamed to public `persist_*` + the producer-token
  constants as the single source of truth). Rationale: lowest blast radius (leaf persistence helpers,
  no detection/verdict/cost logic), most cohesive (one concern: write a built artifact through the 1.3
  writer), and the four producer tokens the resume-discovery path still reads are re-imported (aliased
  to the historical private names) so the resume code is untouched. `pipeline.py` dropped 1190 → 1071
  lines; new module 268 lines. The split changed NO fixture/golden — the full pre-6.3 `tests/apaa/`
  suite stayed byte-green (735 passed before the new tests landed). Split documented in BOTH docstrings.
- **AC2/AC3 (the conservative detector).** `detectors/orphan_code.py::OrphanCodeDetector` (rule_id
  `orphan_code`), pure `run(*, index: AstIndex) -> DetectorResult`. ONE whole-index pass derives the
  global callee-name set + a name→def-count histogram; a def is orphan iff (name not in any callee) AND
  (not excluded) AND (not a name-collision twin). The locked EXCLUSION set: structural dunders (`__x__`),
  `test_*`/`test` entrypoints, + `ORPHAN_EXCLUSION_NAMES` (setUp/tearDown/setUpClass/…, pytest hooks,
  main/handler/lambda_handler/setup/teardown/startup/shutdown/on_startup/on_shutdown). Findings via the
  EXISTING `build_recording` (FR13 locator-or-reject, content-derived id), `advisory=True`,
  `depth_supported=None`. NO coverage entry. Findings sorted (file_path, start_line, rule_id, recording_id).
- **AC4 (wiring, no-orphan byte-identity).** `_orphan_findings(index, assessed_entries)` runs the single
  cross-file pass AFTER `_detect_per_file` in BOTH `run_audit_detailed` (over assessed entries on a halt)
  and `resume_audit_detailed` (over carried∪target). Findings appended only; no coverage entry ⇒ a
  no-orphan repo is byte-identical (proven TC-APAA-PIPELINE-001-52 + the unchanged signature-demo goldens).
- **AC5 (complete-the-declared-set + no-crash + non-ASCII).** TC-APAA-ORPHAN-001-01..17 cover (a)
  referenced→not-orphan, (b) unreferenced→orphan, (c) excluded entrypoints (parametrized), (d) the RED-first
  name-collision guard (both referenced + neither-referenced), (e) non-Python/parse-failed→no-finding,
  (f) None index → typed `OrphanCodeError`, empty-named def + malformed entry → recorded `DegradedCondition`
  (via `model_construct` to bypass validation, AR10 — NEVER an uncaught raise), (g) non-ASCII name+path.
- **AC6/AC7 (purity/determinism/gates/sizes/mypy).** Detector is PURE (no I/O/clock/LLM/provider/float);
  the no-web-imports gate extended (not forked) to cover both new modules + the strict zero-token check
  (orphan_code ⊬ providers/web; pipeline_persist ⊬ web); single-serializer gate untouched (the detector
  composes `build_recording` only — no new json.dumps/hasher/parse). All files ≤1200 (1071/268/306).
  mypy clean on the new modules. Frozen Epic-1..6 contracts show NO working-tree diff
  (coverage_ledger/recording/base/ast_index/store/verdict/cache/models byte-identical).
- **DF-1-4-A consumed honestly** + a NEW defer DF-6-3-A (resolved call graph for higher recall →
  `epic-6-resolved-call-graph`) filed append-only with the six CC-3 fields in `deferred-work.md`.

### File List

NEW source:
- `minions_core/apaa/detectors/orphan_code.py` — the pure conservative orphan/dead-code detector (FR12).
- `minions_core/apaa/pipeline_persist.py` — the `.apaa/` persist family extracted from `pipeline.py`
  (DN-PIPELINE-SPLIT, pure no-behavior-change refactor).

MODIFIED source:
- `minions_core/apaa/pipeline.py` — split (persist helpers moved + re-imported); the whole-index orphan
  pass wired after `_detect_per_file` in `run_audit_detailed` + `resume_audit_detailed`; docstring updated.

NEW tests:
- `tests/apaa/test_orphan_code_detector.py` (area APAA-ORPHAN, TC-APAA-ORPHAN-001-01..17).
- `tests/apaa/test_orphan_pipeline_wiring.py` (area APAA-PIPELINE, TC-APAA-PIPELINE-001-50..52).
- `tests/apaa/cartridges/orphan_basic/src/calc.py.txt` + `tests/apaa/cartridges/orphan_basic/tests/test_calc.py.txt`
  — the planted-orphan cartridge (one live `add`, one dead `unused_helper`).

MODIFIED tests:
- `tests/apaa/test_no_web_imports.py` — guard extended to `detectors.orphan_code` + `pipeline_persist`.

MODIFIED governance:
- `_bmad-output/design-artifacts/APAA/deferred-work.md` — DF-1-4-A back-filled + consumed; DF-6-3-A filed.

## Senior Developer Review (AI)

**Reviewer:** XAgentsLabs007 (BMAD code-review gate, adversarial)
**Date:** 2026-06-29
**Iteration:** 1
**Outcome:** PASS → status `done`

### Verdict rationale

A clean, conservative, no-behavior-change slice that delivers FR12 and honestly consumes DF-1-4-A. The
keystone risk — a FALSE dead-code accusation on the unresolved-name (DF-1-4-A) edge substrate — is held
off by three independent guards in `OrphanCodeDetector._is_orphan` (name-match miss AND not-excluded AND
not-a-name-collision-twin), each empirically proven RED-first. The pipeline split is a verified pure
refactor and the no-orphan byte-identity property holds. All ACs met; full suite green; mypy clean on the
modules under review; ≤1200-line and headless invariants preserved.

### What was verified (evidence, not assertion)

- **AC1 (pipeline split, pure refactor).** `pipeline_persist.py` (268 lines) is a verbatim lift of the
  `.apaa/` persist family (renamed to public `persist_*` + the producer-token constants as a single
  source of truth, re-imported into `pipeline.py` so resume-discovery is untouched). `pipeline.py` is
  **1071 lines** (well under 1200). Split documented in BOTH docstrings (§3.2). No verdict/persist-order/
  producer-token change. Full pre-existing `tests/apaa/` suite stays green (no fixture/golden delta).
- **AC2/AC3 (conservative detector — the no-false-accusation moat).** Adversarial hunt for a false dead
  accusation: (i) attribute calls `obj.method()` → the 1.4 `CodeEdge` captures the trailing attribute
  name as `callee` → `method` lands in `referenced_names` → NOT-orphan; (ii) dunders matched structurally
  (`__x__`), `test_*`/`test`, and the locked `ORPHAN_EXCLUSION_NAMES` (unittest/pytest/framework hooks)
  excluded; (iii) name-collision counts ALL named defs (any kind) for a name → `>1` makes BOTH twins
  NOT-orphan even when one is uncalled (errs toward silence, never accusation). `ast_span` is an
  index-validated computed property so the FR13 locator is always buildable (no silent reject path).
  Advisory-by-contract confirmed: `advisory=True`, `depth_supported=None`, and TC-APAA-PIPELINE-001-51
  empirically proves the finding is not verdict-eligible (6.4 owns promotion).
- **AC4 / DN-WHOLE-INDEX (byte-identity).** Finding-only detector (NO coverage entry); single cross-file
  pass wired AFTER `_detect_per_file` in both `run_audit_detailed` (assessed entries on halt) and resume.
  The resume cross-file fix is correct: prior `orphan_code` findings are DROPPED and RECOMPUTED over
  `carried_forward ∪ resume_target` from the CURRENT index (still-skipped excluded), mirroring the
  uninterrupted assessed set — the two named byte-identity tests
  (`test_e2e_resume_reaches_identical_verdict_and_ledger_as_uninterrupted_run`,
  `test_e2e_chained_partial_then_complete_resume_reaches_identity`) both PASS; the 28-test resume suite
  is green.
- **AC5/AC6/AC7 (complete-the-declared-set / no-crash / non-ASCII / gates).** TC-APAA-ORPHAN-001-01..17
  cover every declared shape incl. the RED-first name-collision guard (-05/-06), non-Python/parse-failed,
  the no-crash leg (typed `OrphanCodeError` only on a non-`AstIndex`; empty-named def + malformed entry →
  recorded `DegradedCondition` via `model_construct`, never an uncaught raise), and non-ASCII name+path
  with stable `recording_id`. Detector is PURE (no I/O/clock/LLM/provider/float), findings sorted (AR11).
  no-web-imports gate extended (not forked) to `detectors.orphan_code` + `pipeline_persist`;
  single-serializer gate untouched (composes `build_recording` only). All files ≤1200 (1071/268/306).
  mypy clean on the two new modules (the only mypy noise is pre-existing `radon` stub warnings in
  `tool_runner.py`, not under review). No `cli.py`/HTTP/CI-job change; no live LLM.
- **Suite:** `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
  **1112 passed, 1 skipped, 4 subtests passed** (100.4s).
- **Governance:** DF-1-4-A back-filled + CONSUMED (2026-06-29 append-only note; original 1-4 story line
  retained as evidence, §3.4); DF-6-3-A (resolved call graph → `epic-6-resolved-call-graph`) filed — both
  carry the six CC-3 fields and valid `target_story` values.

### Notes (non-blocking, no action required)

- The frozen Epic-1..6 surfaces are git-untracked (the whole `minions_core/apaa/` subtree is new), so
  the "no working-tree diff" claim cannot be diffed against a committed baseline; it is instead verified
  empirically by the unchanged fixtures/goldens and the byte-identity tests. Acceptable for this slice.
- The detector counts name-collisions across ALL definition kinds (a `variable foo` shadows a
  `function foo`), which is strictly MORE conservative than required — consistent with the asymmetric
  silence bar. Not a defect.

### Action Items

None. No unresolved decision-needed or patch findings; no deferrable Low items warranting a follow-up.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-29 | 0.1.0 | create-story: full context-filled spec for Story 6.3 (orphan/dead-code detector, FR12, Tier B). Locks DN-CONSERVATIVE (unresolved-name edge set → conservative name-match reachability, never a false dead-code accusation — consumes DF-1-4-A), DN-WHOLE-INDEX (cross-file detector wired as a single pass after `_detect_per_file`, additive findings, no coverage entry, no-orphan repo byte-identical), and DN-PIPELINE-SPLIT (pipeline.py at 1190/1200 → cohesion split FIRST as a pure no-behavior-change refactor before the orphan wiring). Advisory-by-contract (6.4 Prosecutor owns promotion). Scope-fenced vs 6.4/6.5/6.6/6.7 + resolved-call-graph/requirement-graph V2. Status → ready-for-dev. | Scrum Master (claude-opus-4-8) |
| 2026-06-29 | 1.0.0 | code-review iter-1 PASS → done. Adversarial review of the conservative orphan detector (no-false-accusation moat held by 3 guards: name-match miss + exclusion set + name-collision twin guard), the pure pipeline split (1071 lines), the no-orphan byte-identity property + the resume drop+recompute cross-file fix (both named byte-identity tests green). 1112 passed/1 skipped, mypy clean on new modules, gates green, ≤1200, headless, DF-1-4-A consumed + DF-6-3-A filed (6 CC-3 fields). No action items. | Reviewer (claude-opus-4-8) |
