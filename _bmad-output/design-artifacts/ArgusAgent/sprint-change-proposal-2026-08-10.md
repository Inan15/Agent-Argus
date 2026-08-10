# Sprint Change Proposal — 2026-08-10

**Project:** ArgusAgent (formerly APAA — AI Project Assurance Audit)
**Author:** Correct Course workflow (`bmad-correct-course`), incremental mode
**Requested by:** XAgent007
**Trigger type:** Strategic pivot
**Change scope classification:** **MAJOR** — fundamental replan (PM / Architect involvement)
**Status:** Awaiting operator approval

---

## 1. Issue Summary

### 1.1 What triggered this

Not a story. The trigger is an **operator strategic pivot**, raised 2026-08-10 outside the
story cycle, during a manual verification pass over the deferred-work ledger.

The stated intent:

> *"My intention is to package Argus first for MS Store and other software stores for
> students to download and use this audit tool in their coding agents."*

### 1.2 Problem statement

ArgusAgent's PRD specifies an **internal-first, headless V1** whose externalization is gated
on ≥80% finding-precision, whose primary user is the internal XAgents Engineering Lead /
Delivery Orchestrator, and whose public distribution sits in **V4**. The operator intends a
**first public release to students and independent developers**.

Three specification-level conflicts follow, and one product-level gap that no artifact records:

1. The **≥80% precision gate blocks externalization** — stated five separate times and
   elevated as *the* honesty keystone. It is measurably **not cleared**.
2. **Store compliance was explicitly skipped by name** in the PRD's classification.
3. **Public distribution is V4**, and the V1 primary user is not a student. No journey
   describes a public consumer.
4. **The tool's own provisional status never reaches a user.** Verified: the
   `demo-heuristic-only` grade and the `provisional` gate string exist **only** in
   `argus/dogfood/proof_run.py` and `argus/dogfood/proof_render.py` — the internal dogfood
   artifact. Neither `argus/cli.py` nor anything under `argus/reports/` surfaces either token.

### 1.3 Evidence

**Specification sites (PRD):**

| Site | Text | Conflict |
|---|---|---|
| L118 | *"the honesty keystone is explicit: **APAA must hit ≥80% finding-precision before any externalization conversation**"* | Public release **is** externalization |
| L130 | *"The one bar that gates externalization: ≥80% finding-precision. Everything commercial waits behind it."* | Same |
| L141 | *"Externalization gate cleared: ≥80% finding-precision on the validation set."* | Success criterion unmet |
| L302 | *"The ≥80% finding-precision bar on **N ≈ 5–10 real XAgents repos** … is the gate before any externalization."* | Corpus is N=1 |
| L351 | *"**Tier B is what clears the ≥80%-precision externalization gate.**"* | Same |
| L107 | *"Primary (V1): the **internal XAgents platform owner**"* | Student persona absent |
| L317 | *"Distribution in V1 = the Skill + a committed `.apaa/` convention … a hosted repo-URL runner is **V4**."* | Public channel unphased |
| L340 | *"**Skipped (headless):** `visual_design`, `store_compliance`."* | MS Store needs it |

**Specification sites (architecture):**

- L150-151 — *"the dogfood verdict must carry a hard `grade: demo-heuristic-only` flag and
  **never be presented as externalization evidence** (red-team)."*
- L306-309 — §I Packaging describes a `minions[apaa]` extra and an `apaa` console script.
  **Factually stale since the 2026-08-03 separation.**

**Measured code facts (verified in place on this tree, not inferred):**

| Fact | Evidence |
|---|---|
| The ≥80% gate has never been cleared | `protocol_cleared: bool = False` at `argus/precision/replay_harness.py:223`; never passed `True` at any call site |
| The grade flag is live | `DOGFOOD_GRADE = "demo-heuristic-only"` at `argus/dogfood/proof_run.py:214` |
| The corpus went **backwards**, not forwards | Story 8.5 re-derived the dogfood as a **self-audit of `argus/`** (69 files / 18 206 LOC). The independent Minions run (135 files / 36 712 LOC) survives only at `minions-dogfood-proof-story-7-2-superseded.md` and *"can never be re-derived in this repository"*. The ledger's own words: *"a materially weaker evidence class than the independent run it supersedes, and it is not independent corroboration of anything."* |
| No user surface carries the disclosure | `demo-heuristic-only` / `provisional` grep to `argus/dogfood/**` only |
| No packaging tooling for a desktop store | No MSIX, PyInstaller, Briefcase, Nuitka, cx_Freeze, `.spec` or `.iss` anywhere in the tree |
| The release pipeline has never run | `git tag -l` is **empty**; `release.yml` fires only on `v*.*.*` and **deliberately does not publish to any index** (its own header) |
| README points at a tag that does not exist | *"INTERIM — resolve straight from this repository at a tag."* |
| Privacy posture is clean | Network egress confined to `argus/audit/open_llm_adapter.py` behind the opt-in `[llm]` extra; committed import gates; **no telemetry**; MIT licensed |

---

## 2. Impact Analysis

### 2.1 Epic impact

| Epic | Status | Impact |
|---|---|---|
| **Epics 1–7** | done | **None.** Signed retrospectives; not reopened (§3.4 evidence immutability) |
| **Epic 8** | done | **None** |
| **Epic 9** | done | **None** |
| **Epic 10** | backlog, 0/4 | **Not redefined.** All four stories remain valid and all four are release-relevant. Epic 11 **depends on all four**. One AC **corrected** (10.2, enumeration only — unstarted) |
| **Epic 11** | *new* | **7 stories.** The disclosed public release |
| **Minions Handoff H1–H4** | not epics | **None.** **H0 remains UNOWNED** |

No epic is invalidated. No epic becomes obsolete. Sequencing is unchanged, except that
Story 10.1 (the release-evidence standard) becomes **more** load-bearing: a public release
claim is now imminent, and 10.1 is the control that governs making one.

### 2.2 Story impact

**Corrected — Story 10.2, AC 1 (unstarted, enumeration fix):** the AC named PRD L23 / L180
and architecture L220 / L237 — **4 of 7 sites.** Omitted: PRD **L116** (Executive Summary),
**L398 (FR7 — the binding capability contract)** and **L476 (NFR-P2)**. A pass satisfying the
AC literally would have left the capability contract asserting Python-only while
multi-language ships.

**Added — 7 stories under Epic 11** (detailed in §4.3).

### 2.3 Artifact conflicts

| Artifact | Impact | Sites |
|---|---|---|
| **PRD** | 5 amendments | L107, L130+L141, L133, L317+L340, new J6, new FR34 |
| **Architecture** | 2 amendments | L150-151, L306-309 |
| **UI/UX** | **N/A** | No artifact. Headless classification **retained** |
| **epics.md** | 1 new epic + 1 AC correction | after L1808; Story 10.2 AC1 |
| **sprint-status.yaml** | header note + 8 entries | after L40; after L227 |

### 2.4 Technical impact

| Area | Impact |
|---|---|
| `argus/cli.py`, `argus/reports/**` | **New** — FR34 disclosure surface (Story 11.1) |
| `argus/detectors/vacuous_test.py:198` | Separator fix + near-miss corpus (11.3) |
| `action.yml` | 5 `${{ inputs.* }}` sites → `env:` binding + guard (11.4) |
| `argus/index/ast_index.py` | Runtime `tree-sitter` assertion (11.5); grammar diagnosis (10.4) |
| `argus/precision/replay_harness.py:87-90` | Lazy `_registry` import (11.6) |
| `.github/workflows/release.yml` | Index publish extension (11.7) |
| `README.md`, `CHANGELOG.md` | Install path truth (11.6); `[languages]` extra (10.2) |
| **`argus/pipeline.py`** | ⚠️ **Currently 1331 lines against the NFR-M1 cap of 1200** — see §2.5 |

### 2.5 Pre-existing condition surfaced during analysis (not caused by this change)

**`argus/pipeline.py` breaches NFR-M1 by 131 lines, silently.**

DF-8-2-A recorded the file at **1199 / 1200** and warned *"the next edit of any size breaches
NFR-M1."* Three commits edited it after Epic 9 closed. It is now **1331 lines**, and no gate
caught it: NFR-M1 is enforced **per-module and ad hoc** (`tests/test_cache_invalidation.py:690`,
`tests/test_cartridge_selfaudit.py:472`) with **no repo-wide sweep and no assertion covering
`pipeline.py`.**

This is **not** a release blocker — it is invisible to a user. It is recorded because
Story 10.3's flag work lands in this file, it will tax every fix in Epics 10 and 11, and
three open ledger entries (DF-8-2-A, DF-8-3-A, DF-8-3-C) gate on the extraction that has
never been performed. **Recommended as an enabler, not a gate.** A repo-wide NFR-M1 sweep
test is ~10 lines and would have caught this.

---

## 3. Recommended Approach

### 3.1 Options evaluated

| Option | Effort | Risk | Verdict |
|---|---|---|---|
| **1 — Direct Adjustment** | Medium | Low | **Viable but insufficient.** Carries the code work; cannot amend a PRD contract |
| **2 — Rollback** | — | — | **Not viable.** Nothing to roll back. Epics 1–9 done with signed retros; §3.4 forbids rewriting |
| **3 — PRD MVP Review** | Medium | Medium | **Required.** The MVP is *delivered*; what changes is audience, distribution, and the externalization precondition |

### 3.2 Selected: **Hybrid — Option 3 → Option 1**

Amend the PRD contract first, then carry the work in a new Epic 11 with Epic 10 unchanged.

### 3.3 The keystone decision, and why it is a split rather than a waiver

The operator selected **"amend to allow a disclosed release."** The amendment splits
externalization into two tiers:

- **Attested externalization** — any release in which a verdict is presented as assurance
  evidence (commercial, enterprise, regulated, operated-service). **Still gated on ≥80%.
  Status: NOT CLEARED.**
- **Disclosed externalization** — a free public distribution, permitted pre-gate **if and
  only if** every user-facing verdict surface carries the `demo-heuristic-only` grade and the
  PROVISIONAL gate state, **mechanically enforced** (FR34).

This is a real distinction the codebase already makes — `DOGFOOD_GRADE` and the
`provisional=True` framing exist precisely for it, and Story 8.5's review refused to soften
them. The amendment moves that honesty from an internal artifact to the user's screen.

**Stated plainly: this is still a loosening of the PRD's most-elevated constraint.** The
original wording — *"before any externalization conversation"* — admits no exception. The
2026-08-03 inversion analysis (F1) already flagged the pattern: *"the delta LOOSENS the gate
twice … with every guard pointing only at over-blocking and NOTHING guarding the PRD-fatal
false-`RELEASE_READY` direction."* **FR34's mechanical enforcement is the counterweight, and
Story 11.5 guards the false-green direction specifically.**

### 3.4 Scope narrowed from the original ask

| Channel | Decision |
|---|---|
| **PyPI** | ✅ In scope |
| **GitHub Marketplace** | ✅ In scope — **gated on Story 11.4** |
| **Microsoft Store** | ⏸️ **Deferred** — needs MSIX + bundled runtime + Partner Center identity + privacy policy URL + age rating; none exists |
| **Winget / Chocolatey / Homebrew / Snap** | ⏸️ Deferred |
| **Hosted repo-URL runner** | Remains **V4** |

Deferring desktop stores removed the single hardest conflict: **the `store_compliance` skip
at PRD L340 was re-validated and remains correct.** It must be un-skipped before any
desktop-store channel is scoped.

### 3.5 Timeline and risk

**~11 stories to first public release** (Epic 10's 4 + Epic 11's 7) — not the
package-and-ship the pivot opened with. **Compression option available:** dropping the
marketplace channel removes Story 11.4 entirely and de-scopes 11.7 AC3/AC4, leaving
**PyPI-only at 5 Epic-11 stories.**

**Principal risk:** Story 11.2 may measure that a verdict-blocking finding is **not**
reachable on a default public run. If so, the product's wedge does not fire for a student
the way it fires for a cartridge, and this epic's premise needs re-scoping. **11.2 is
scheduled early and is cheap precisely so this surfaces before listing copy is written.**

---

## 4. Detailed Change Proposals

All nine were reviewed incrementally and **approved by XAgent007 on 2026-08-10**.

### 4.1 PRD (5 edits)

| # | Section | Change |
|---|---|---|
| **1** | §Success Criteria (L130, L141) | Split the gate into **attested** (gated, NOT CLEARED) and **disclosed** (permitted pre-gate under enforced FR34) tiers. Record the gate's status factually |
| **2** | §Exec Summary (L107), §User Success (L133) | Add the **student / independent developer** persona, scoped to the disclosed tier. Add the **"usage is not evidence"** guard — adoption cannot advance the precision gate |
| **3** | §Developer Tool (L317), §Skipped (L340) | Record **V1.5 channels** (index + marketplace); name the **excluded** channels with reasons; re-validate the `store_compliance` skip and pre-commit the condition for reopening it |
| **4** | §User Journeys (after L236) | Add **Journey 6 — Sam, final-year student.** Resolves to `INSUFFICIENT_COVERAGE`, not success. Add 3 rows to the Journey Requirements Summary |
| **5** | §Functional Requirements (after L427) | Add **FR34** — mandatory self-disclosure on every user-facing verdict surface; mechanically enforced; replaced-not-deleted on clearing; scope-bounded against FR17 |

### 4.2 Architecture (2 edits)

| # | Section | Change |
|---|---|---|
| **6** | §Resolved & Flagged Decisions (L150-151) | Clarify the grade describes the **frozen default pipeline** (no LLM, unwired deep-audit seam) — **not** a cut FR7, whose validator is live. Confirm the **proof artifact** remains never externalization evidence. Direct FR34 to **extend** the existing two-sided guard |
| **7** | §I Packaging (L306-309) | Strike-through the stale `minions[apaa]` text with a pointer to handoff H1. Record the measured shipped package. Flag the **load-bearing `tree-sitter <0.26` bound**. Add the V1.5 channel table and the verified privacy posture |

### 4.3 Epics (1 new epic + 1 AC correction)

**Epic 11: The Disclosed Release — ship to the public with the tool's own limits attached**

| Story | Covers | Sev |
|---|---|---|
| **11.1** The tool discloses its own status before it discloses a verdict | FR34 (new) | 🟠 |
| **11.2** A verdict-eligible finding is reachable on a real repository — measured, not assumed | J6 wedge assumption | 🟠 |
| **11.3** A polyglot repository is classified correctly | DF-8-2-B | 🟢→blocking |
| **11.4** The published action cannot execute a consumer's input | DF-9-2-D | 🟢→blocking |
| **11.5** A wrong grammar version cannot silently produce a false green | `tree-sitter` pin | 🟠 |
| **11.6** The published artifact is complete and says only true things | DF-9-2-A, DF-9-2-B | 🟠 |
| **11.7** The release is published, and its status cites the gate that published it | PyPI + Marketplace | 🟠 |

**Dependency flow:** 11.1 **FIRST** → 11.2 **EARLY** → 11.3 / 11.4 / 11.5 independent →
11.6 → 11.7 **LAST**. **Depends on Epic 10 — all four stories.**

**Story 10.2 AC1 corrected** to the full 7-site list including FR7.

### 4.4 sprint-status.yaml (1 edit)

Header DELTA NOTE (2026-08-10) + `epic-11` and 7 story entries. The note restates **H0** and
**DF-7-2-A** as open and unowned, so neither is lost behind a new epic.

---

## 5. Implementation Handoff

### 5.1 Scope classification: **MAJOR**

Amends PRD classification, personas, journeys, success criteria, distribution phasing, and
the capability contract. Routes to **Product Manager / Solution Architect**, not to a
Developer agent.

### 5.2 Recipients

| Role | Deliverable |
|---|---|
| **Product Manager** | Apply PRD edits 1–5; add the 2026-08-10 entry to the PRD frontmatter `amendments` block |
| **Solution Architect** | Apply architecture edits 6–7 |
| **Product Owner / SM** | Apply epics edit 8 (Epic 11 + Story 10.2 AC correction); update `sprint-status.yaml` (edit 9) |
| **Developer agents** | Execute Epic 10 → Epic 11 via the normal SM → Dev → Review cycle. **No Epic 11 story starts before Epic 10 completes** |
| **Named human (unassigned)** | **DF-7-2-A** TP/FP adjudication — the only step that can clear the attested gate. **Not an Epic 11 story** |
| **Named human (unassigned)** | **H0** — filing the Minions handoff H1–H4. **Still UNOWNED** |

### 5.3 Success criteria

1. All 7 PRD/architecture edits applied, dated, and attributed to this proposal.
2. Epic 11 registered; Epic 10 unchanged except the 10.2 AC correction.
3. **FR34 enforced by a committed test before any publish step runs.**
4. Story 11.2's measurement recorded as a yes or a no — **a "no" escalates, it does not soften a journey.**
5. Release status cites an executed CI run id on the released commit, or is recorded **NOT ESTABLISHED**.
6. The marketplace channel does not ship before Story 11.4 lands.

### 5.4 Explicitly out of scope

Desktop application stores · OS package managers · hosted runner · clearing the attested
gate · reopening Epics 1–9 · the `argus/pipeline.py` NFR-M1 extraction (recommended as an
enabler, not gated here).

---

## 6. Approval

| Item | Value |
|---|---|
| **Proposal date** | 2026-08-10 |
| **Edits reviewed** | 9 of 9, incremental mode |
| **Edits approved** | 9 of 9 |
| **Change scope** | MAJOR |
| **Operator approval of the complete proposal** | ⬜ *pending* |

**Approving this proposal authorises:** amending the PRD's ≥80% externalization keystone into
a two-tier gate; adding a third product audience; recording public distribution as V1.5; and
opening a 7-story epic to ship it.

**It does not authorise:** presenting any ArgusAgent verdict as assurance evidence, or
describing the ≥80% precision gate as cleared. **That gate remains NOT CLEARED, and this
proposal does not clear it.**
