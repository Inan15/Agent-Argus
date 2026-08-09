# Sprint Change Proposal — Specification Debt from the Separation

**Date**: 2026-08-09
**Project**: ArgusAgent (`argus-agent`)
**Trigger**: Execution of the Repository Audit Execution Protocol against ArgusAgent itself.
Four findings survived story-traceability validation: three capabilities that entered the
shipped contract without passing a story gate, and a release status asserted over a CI
workflow that had never executed.
**Author**: correct-course analysis
**Status**: PROPOSED — no planning artifact is amended by this document. Epic 10 carries the
work. Two code repairs referenced here (the `audit-ci.yml` gate breaks) were already landed
on `fix/honest-verdict-reporting` 2026-08-09; the *evidence standard* that should have caught
them is what remains open.

---

## 1. Issue Summary

### 1.0 How this differs from the 2026-07-28 proposal

This document is, in part, about that one. `sprint-change-proposal-2026-07-28.md` recorded
real and valuable work — a large coverage expansion, a complexity refactor, a security fix,
and the first CI workflow. It also carried three capabilities into the shipped contract
without a story, and closed with a release-readiness verdict its own evidence could not
support. Nothing here disputes the engineering; the finding is about the **gate**, and it is
recorded factually rather than as fault. The separation collapsed the history in which a gate
would have run, and nothing was in place to notice.

### 1.1 A release status was asserted over a gate that had never executed *(DF-AUD-APAA-C, 🟠)*

`sprint-change-proposal-2026-07-28.md:63` records:

> **Release Status**: Upgraded from `NEEDS TARGETED REWORK` to **READY FOR RELEASE**!

Its evidence (`:55`) is a **local** run: *"916 PASSED … 93% coverage"*. Item 6 of that same
proposal **created** `.github/workflows/audit-ci.yml`. That workflow's only run on `master`
(`30774175196`) is `failure`, and the log ends:

```
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'StoreIntegrityError'
459	        token = "StoreIntegrityError"
##[error]Process completed with exit code 1.
```

It died at `bandit` in 40s — before `pytest` was ever reached — because `bandit -r argus`
exits 1 on **any** severity and this tree carries 18 benign Low findings (subprocess calls for
`git`; constants named `token`/`secret` holding rule ids). A second, independent break:
`pytest --cov` was invoked while `pytest-cov` was absent from the `[dev]` extra, so the
`--cov-fail-under=80` gate could not have run either.

Both were repaired 2026-08-09, and a clean-venv reproduction of every workflow step now
passes on 3.12 (`mypy` clean over 71 files; bandit gate PASS at medium+; `1219 passed`;
coverage 94.96%). **The repair is not the deferred item — the evidence standard is.**

### 1.2 Multi-language grounding shipped in V1 while every spec says V2 *(DF-AUD-APAA-D, 🟡)*

The capability entered via `sprint-change-proposal-2026-07-28.md:18` — *"user intent requested
evaluating and implementing multi-language auditing capability"* — with no story and no
amendment. The specs were never updated:

| Artifact | Says | Reality |
|---|---|---|
| `prd.md:23` | `[Python V1, multi-language V2]` | 10 languages in V1 |
| `prd.md:180` | V2 roadmap lists *"**multi-language** AST grounding"* | Delivered |
| `architecture.md:220` | *"Deferred (post-V1): multi-language AST…"* | Delivered |
| `architecture.md:237` | *"V1 deep = Python only"* | 10 languages parse |

Three consequences: the V2 roadmap **double-counts delivered work**; the `[languages]` extra
is documented in neither README nor CHANGELOG, so a consumer cannot discover it; and
`index/ast_index.py:311` records **one** `grammar_version` resolved from `tree-sitter-python`
for a 10-language index — so a Go/Rust/JS grammar change would not move the R3 cache key.
That is the identical silent-cache-staleness class **DF-5-1-A** already flags for
`prompt_template_version`. The architecture's R3 key (`:77-78`, `:201`) was *designed* for a
single grammar, which makes this a **design change, not a defect fix**.

**Direction matters:** this is an *undersell*. Every consumer-facing document says
Python-only, so no false capability claim reached a buyer. The debt is internal and
forward-looking.

### 1.3 Four CLI flags are accepted and specified nowhere *(DF-AUD-APAA-E, 🟡)*

FR30 and `architecture.md:226` specify `repo + commit + budget + materiality_bar`; Story 1.7
declares the flag names **LOCKED**. The shipped parser accepts **13** flags. Traceability:

```
--commit  --budget  --materiality-bar  --critical-subsystem
--exclude-critical  --coverage-scope  --report-dir  --reports  --strict   → story-backed
--passes   --skip-pass   --ignore-path   --ignore-pattern                 → ZERO coverage
```

Zero occurrences across epics, stories, PRD, addendum, both prior change proposals, CHANGELOG
and README. They entered in the root commit `084c6a7` (the 426-file separation seed) and
`b05fa4c`. Two of them — `--ignore-path`, `--ignore-pattern` — suppress **security** findings
with no threat model.

They were also **entirely inert** until 2026-08-09: every production call site dropped the
`request` argument, so `--skip-pass security` still ran the scanner and still emitted a
`hardcoded_secret` finding, while the report printed *"Secret Scan Status: SKIPPED (Pass
Deselected)"*. No consumer can depend on their behaviour, so **neither blessing nor removal is
a behavioural break**.

### 1.4 A grammar that fails to load is reported as missing *(DF-AUD-APAA-F, 🟢)*

`index/ast_index.py:266` catches `(ImportError, Exception)` and returns `None`, so an
uninstalled grammar and an installed-but-broken one (ABI mismatch, corrupt build) both surface
as `grammar_missing_<lang>` — and the remedy the report gives ("install the package") is wrong
in the second case. The tuple is redundant (`Exception` subsumes `ImportError`), hiding that
the catch is total. It is the only bare `except: …pass` in `argus/`, a shape AR10 and Story
4.3 explicitly forbid. Degradation itself is correct — the file is recorded
`ast_eligible=False`, never a false deep claim — so this is **diagnosis quality, not
correctness**.

---

## 2. Impact Analysis

### 2.1 Epic impact

**All 9 epics are `done` with retrospectives complete; Epic 9's entry reads "FINAL epic and
FINAL retro of the plan". There is no epic in flight.** The change therefore lands on a
*closed* plan.

- **New epic required** — Epic 10, following the Epic 8/9 delta precedent (both were post-hoc
  deltas created after an amendment or a separation, carrying corrective work *without*
  rewriting closed epics).
- **Explicitly rejected: modifying Epics 1, 4 or 6 in place.** Their retrospectives are signed
  and dated; editing their scope now would falsify the record — the same class of error as
  §1.1. Forward-pointing amendment notes are the honest mechanism.
- **Forward plan affected** — the PRD V2 roadmap double-counts delivered work (§1.2).

### 2.2 Story impact

No existing story changes status. Four new stories under Epic 10. Story 1.7's LOCKED flag list
is *referenced* by Story 10.3 and updated there, not edited retroactively.

### 2.3 Artifact conflicts

| Artifact | Edits | Nature |
|---|---|---|
| `epics.md` | +1 epic, +4 stories | Addition only |
| `prd.md` | 6 (2 frontmatter, dateline, FR30, 3 multi-language) | Amendment, house 4-part mechanism |
| `addendum.md` | +2 sections (A2, A3) | Addition |
| `architecture.md` | 5 | Amendment — **includes the R3 design change**; requires introducing an `amendments:` mechanism this document does not have |
| `README.md` | 2 | Addition (extras table) + one description correction |
| `CHANGELOG.md` | +1 `## Unreleased` entry | Addition |
| `deferred-work.md` | +4 entries (DF-AUD-APAA-C…F) | Addition |
| `sprint-status.yaml` | header + Epic 10 block | Addition |

### 2.4 Technical impact

- **Code:** one change only — `ast_index.py:266`, ~4 lines (Story 10.4). Everything else is
  specification.
- **CI/CD:** already repaired; Story 10.1 adds the *standard*, not the fix.
- **Determinism:** the R3 key change is free **now** because the Epic-5 memoization store is
  unwired — no cached result exists to invalidate. After wiring it would need a
  `CACHE_KEY_SCHEMA_VERSION` bump and a migration.
- **No capability is withdrawn.** No consumer-visible behaviour changes except whichever
  outcome Story 10.3 chooses for four inert flags.

---

## 3. Recommended Approach

**HYBRID — Direct Adjustment as the vehicle, absorbing an MVP re-baseline, holding Rollback
open as an explicit decision for §1.3 only.**

| Option | Assessment |
|---|---|
| **1 — Direct Adjustment** *(chosen vehicle)* | New delta Epic 10 + amendment notes. **Effort Medium / Risk Low.** Additive; one code change. |
| **2 — Rollback** | **Not viable for §1.2** — deleting working, 95%-covered, CI-gated capability to make prose true is inverted cost (**High/High**). **Viable for §1.3** — the flags were inert, so removing the CLI surface while keeping the internal `enabled_passes` model field is **Low/Low**. Held open inside Story 10.3. |
| **3 — MVP Review** | MVP is delivered and *exceeded*. Scope needs **recognising**, not reducing. Absorbed into 10.2 rather than run as an alternative. **Medium/Low.** |

**Rationale.** The corrective work is overwhelmingly prose; the single code change is four
lines. Rollback of §1.2 is the only high-risk move available and buys nothing amendment cannot
achieve for far less. Most importantly, §1.1 fixes the **control** rather than a symptom —
without it, the next separation or ad-hoc request reproduces all of this.

**Sequence is gate-first:** 10.1 → 10.2 → 10.3 → 10.4 (10.4 independent, may land anytime).

**Deliberately not decided here:** Story 10.3's bless-vs-remove ruling on the four flags. Both
are defensible; removal is cheaper and restores the locked contract, blessing keeps useful
function. 10.3 is written to *present* that choice with a threat model requirement, not to
pre-empt it.

---

## 4. Detailed Change Proposals

Seven proposals were drafted and reviewed individually. They are reproduced in the working
record of this session; each carries OLD → NEW text and a rationale.

| # | Artifact | Change | Story |
|---|---|---|---|
| 1 | `epics.md` | Add Epic 10 + Stories 10.1–10.4 (full ACs, Given/When/Then house format) | — |
| 2 | `prd.md` + `addendum.md` | FR30 bound to the parser; amendment entry; addendum **A2** | 10.3 |
| 3 | `prd.md` + `addendum.md` | Multi-language re-baselined V2→V1; **removed from the V2 roadmap**; addendum **A3** | 10.2 |
| 4 | `architecture.md` | `amendments:` mechanism introduced; L220/L237 corrected; tech pins extended; **R3 key → per-grammar** | 10.2 |
| 5 | `README.md` + `CHANGELOG.md` | Document the `[languages]` extra, its effect on coverage grades, and (honestly) that `[llm]` is inert | 10.2 |
| 6 | `deferred-work.md` | Entries **DF-AUD-APAA-C … F** | all |
| 7 | `sprint-status.yaml` | Header counts + DELTA NOTE + Epic 10 block at `backlog` | — |

**Three items flagged for the approver's explicit attention:**

1. **Proposal 4 amends a document marked `status: 'complete'`** and introduces an amendment
   mechanism it lacks. The alternative is a separate `architecture-addendum.md`.
2. **Proposal 4's R3 edit is the only genuine design decision** in the set. It may warrant its
   own ADR rather than an inline amendment.
3. **Proposal 7 re-opens a plan Epic 9 declared FINAL.** If preserving that closure matters,
   the work can be tracked as a post-closure maintenance line outside epic numbering.

---

## 5. Implementation Handoff

**Scope classification: MODERATE.** Backlog reorganisation plus contract amendments; not a
fundamental replan (no goal, architecture pattern or technology choice changes), and not Minor
(six planning artifacts and two contract documents are touched).

| Recipient | Responsibility |
|---|---|
| **Product Owner / PM** | Approve Proposals 2, 3 (PRD + addendum). Rule on whether the V2 roadmap removal is accepted — the highest-value, easiest-to-skip edit. |
| **Solution Architect** | Approve Proposal 4, in particular the **R3 per-grammar cache-key change** and whether it lands as an inline amendment or an ADR. |
| **Governance Owner** | Own Story 10.3. Produce or refuse the threat model for `--ignore-path` / `--ignore-pattern`; absent one, the flags are removed rather than blessed. |
| **Delivery Orchestrator** | Own Story 10.1. Adopt the evidence standard; correct the 2026-07-28 record in place, dated and reasoned. Confirm CI green on `master` (3.10 leg and the Ubuntu runner remain unproven locally). |
| **Developer agent** | Story 10.4 only (~4 lines + tests). May land independently of the rest. |

### Success criteria

1. `audit-ci.yml` passes on `master`, and its run id is cited by 10.2–10.4.
2. No PRD or architecture statement contradicts shipped behaviour; a test pins
   parser-vs-contract equality.
3. The V2 roadmap contains no delivered work.
4. `grammar_version` names the grammar that parsed — landed **before** the Epic-5 store is
   wired.
5. Each of the four flags is either specified with ACs and a CHANGELOG entry, or absent.
6. A missing grammar and a broken grammar report distinct reasons, both pinned by tests.
7. Every entry DF-AUD-APAA-C…F is closed or explicitly re-deferred with a reason.

### Not closed by this proposal

- **DF-AUD-APAA-A** (orphan `cache/`, open since 2026-07-04) — Story 10.2 fixes the *key*;
  A asks for a *wire-or-mark-permanent* decision. Different questions; conflating them would
  let A be silently marked done.
- **F-14** — `argus/shared/budget_guardrails.py` is a vendored copy of another product's
  module on the wired budget path, carrying a `datetime.now()` call in a tree whose AR4 forbids
  clocks. Story 3.1's *"reuse BY IMPORT, never fork"* premise expired when the separation
  vendored the file. Stale provenance claims were corrected 2026-08-09; the **extraction**
  needs its own story.
- **Config drift** — `_bmad/bmm/config.yaml` sets `planning_artifacts` to a non-existent
  directory, and `architecture.md` frontmatter `inputDocuments` cites a path inside it.
- **Audit coverage** — this audit read ~29.5% of `argus/` by eye (100% by tool and AST sweep).
  Per the protocol's confidence rule that supports subsystem-level conclusions only.
