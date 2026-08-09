# Changelog

All notable consumer-visible changes to **ArgusAgent** (distribution `argus-agent`, package `argus/`)
are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) loosely;
versioning intent is [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Honesty preamble — read this before you read a version number.**
> `argus-agent` is **still not published to any package index**, and no PyPI publication was attempted.
> What changed with `0.1.0` is that a **release workflow now exists** (`.github/workflows/release.yml`):
> on a `v*.*.*` tag it builds an sdist and a wheel and attaches both to a GitHub Release. The
> distribution **will be resolvable by the VCS pin below — and by nothing else — once that tag is
> created and pushed**:
>
> ```
> pip install "argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0"
> ```
>
> ⚠️ **That command does not resolve today.** Tag `v0.1.0` has **not been created or pushed**
> (`git tag -l` is empty at this commit), so `pip` cannot find the ref. The capability is *prepared*,
> not *exercised* — nobody has run this install against a real tag. Creating and pushing the tag is
> an operator step this repository deliberately did not take.
>
> **What is proven and what is not, stated separately.** The build was proven **locally**: `python -m
> build` produced `argus_agent-0.1.0.tar.gz` and `argus_agent-0.1.0-py3-none-any.whl`, the wheel was
> installed into a fresh virtualenv with the repository absent from `sys.path`, and `argus --help` and
> `argus audit <fixture-repo>` both ran to completion there. The **workflow itself is committed and has
> never executed** — it was added on a feature branch and no tag exists in this repository yet — so
> there is no Actions run id and no release URL to cite. Nothing in this file states or implies that a
> release has been published; when one is, this paragraph gets a URL.
>
> **The VCS pin is INTERIM.** Its exit condition is named in
> [Resolving `argus-agent`](#resolving-argus-agent) below, so "interim" has an end rather than becoming
> permanent by silence.
>
> This is an assurance tool. If it published a release note asserting a release that did not happen, it
> would be committing — about itself — the class of unsupported claim it exists to detect in other
> people's repositories. That is why the two sentences above are separate ones.

---

## Unreleased

*(Nothing yet since `0.1.0`.)*

---

## 0.1.0 — 2026-08-08

**Version note.** `0.1.0` is shipped **un-bumped**: the version this repository has always declared is
the version being released, so `pyproject.toml`, `argus.__version__` and every in-package reference now
state one value reachable from one source (see [Version](#version-one-value-one-source) below). The
maturity marker stays `__status__ = "experimental"`: the public **Python API** is not stable across
versions. The **CLI wire contract** — exit codes and the stdout summary line — is separately frozen and
is unchanged by this release.

### Resolving `argus-agent`

| | |
|---|---|
| **Dependency string** | `argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0` — ⚠️ **does not resolve yet: tag `v0.1.0` has not been created or pushed** (`git tag -l` is empty at this commit). Prepared, not exercised. |
| **Index** | none — `argus-agent` is on no package index |
| **Authentication** | **none required if and only if the repository is public.** ⚠️ Visibility was NOT measured when this line was written; open the URL signed out to check. If it is private, the consuming CI needs a read token and must carry it in the URL. |
| **Status** | **INTERIM.** A git ref is not an immutable index artifact: it depends on the repository staying reachable and the tag staying put. |
| **Exit condition** | When `argus-agent` is claimed on PyPI **and** a PyPI Trusted Publisher (OIDC) is configured for this repository, the publish step is added directly to `.github/workflows/release.yml` — trusted publishing cannot be used from inside a *reusable* workflow — with `permissions: id-token: write` and **no stored token**, and the pin above is replaced by a plain index install of the distribution name. |

PyPI publication is deliberately **not** attempted here: a released name+version on an index can never
be replaced, which makes it an operator decision taken with credentials in hand, not a change a release
automation may make on its own.

**Downstream shape (stated, not executed here).** A consumer that wants Argus as an optional capability
should declare it as an **extra**, never as a base dependency — e.g. `yourpkg[argus]` resolving to the
string above. Making that change in a consumer's repository is out of scope for this repository.

### Version: one value, one source

Before this release the package stated its own version **three times and the three did not agree**:
`pyproject.toml` said `0.1.0`, `argus.__version__` said `0.1.0`, and
`argus.dogfood.proof_run.DOGFOOD_ArgusAgent_VERSION` said `1.43.0` — and the third one was written into
the **signed, content-hashed evidence bundle**, so one persisted `.argus/state/<hash>.json` asserted two
different versions of the same package on its two levels (envelope `0.1.0`, payload `1.43.0`).

`DOGFOOD_ArgusAgent_VERSION` is now sourced from `argus.__version__`. **Consumer impact: the content
hash of the evidence bundle changes**, because `argus_version` is part of the bundle's hashed payload
and the bundle is content-addressed by that hash. This affects the evidence bundle only: for every other
artifact `argus_version` is an *envelope* field and the content hash covers the *payload* alone, so those
files' bytes change but their hashes and filenames do not.

### Behaviour: the composite action distinguishes a crash from an assessment

`action.yml` mapped exit `0 → RELEASE_READY`, `2 → NOT_READY_FOR_RELEASE`, and **everything else** to
`INSUFFICIENT_COVERAGE`. Exit `1` is the typed-failure code meaning *no verdict was produced at all*, so
a crashed audit was being republished as a *ran-and-under-covered* result — an assessment the tool never
made. The map is now explicit over the complete space:

| exit code | `verdict` output | `assessed` output |
|---|---|---|
| `0` | `RELEASE_READY` | `true` |
| `2` | `NOT_READY_FOR_RELEASE` | `true` |
| `3` | `INSUFFICIENT_COVERAGE` | `true` |
| `1` | `AUDIT_FAILED` *(not a verdict)* | `false` |
| anything else | `AUDIT_FAILED` *(not a verdict)* | `false` |

A new `assessed` output lets a gate ask *"did the tool assess this repository at all?"* without
string-matching. **The exit-code wire contract itself is unchanged** — no `0`/`2`/`3`/`1` value moved;
what changed is how the action *labels* them. `strict` remains `"false"` by default: after the FR16/FR4
amendment a first-time consumer is expected to land on exit `3`, which already fails any gate configured
to block, and flipping the default here would pre-empt a policy decision that belongs downstream.

### Packaging: what the distribution contains

`[tool.flit.module] name = "argus"` packages the `argus` Python package and nothing else. Measured on the
built artifacts: the wheel holds 71 modules plus metadata; the sdist adds `pyproject.toml`, `README.md`,
`LICENSE` and `PKG-INFO`. The RAM workflow directories (`audit/`, `phases/`, `adapters/`, `templates/`)
and the installer scripts are **repository-only** — see README.md for the full capability split.

Measured on the built wheel with this repository removed from `sys.path`, one clean subprocess per module:
**66 of the 71 shipped modules import.** Five module files do not — `argus/precision/__init__.py`,
`argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`, `argus/dogfood/proof_render.py` and
`argus/dogfood/proof_run.py` — because the precision harness imports its labelled-cartridge registry from
`tests/`, which is not shipped, and the other four reach that import transitively. Those are Argus's own
self-audit tools; the entire `argus audit` path is unaffected and was executed from the installed wheel.
Tracked as `DF-9-2-A`.

### No assurance claim is made by this release

Argus's flagship dogfood run is a **self-audit** — Argus auditing Argus. It is materially weaker evidence
than an independent-repository run and is **never** independent corroboration of the tool's detection
ability. The ≥80%-precision externalization gate remains **PROVISIONAL** and is **not** cleared; clearing
it requires a human TP/FP adjudication that has not taken place. No statement in this release — here, in
the README, in `action.yml` or in the release workflow — should be read as a claim that Argus has been
externally validated.

### The FR16/FR4 verdict-contract amendment

The sections from here to the end are the consumer contract for this release. They are the substance of
`0.1.0`; everything above states how to resolve it and what the packaging does and does not contain.

The FR16/FR4 **verdict-contract amendment**: *no block without a finding.* Before this change ArgusAgent
could report a repository as `NOT_READY_FOR_RELEASE` when it had found **nothing wrong** — the coverage
shortfall was reported as though it were a defect. It now reports that situation as what it is: *not
enough was examined to vouch*, which is a statement about the audit and not about the code.

**Most pipelines need no change.** The sections below are ordered by what breaks a pipeline soonest;
[Do I need to change anything?](#do-i-need-to-change-anything) at the end is the four-line version.

### Behaviour: exit codes

**Exit-code *values* are unchanged.** `0`, `2`, `3` are the three verdict codes and `1` remains the
reserved code for a typed failure that produced no verdict at all. What changed is **which runs map to
which value** — for exactly one class of run.

| Run shape | Before | After |
|---|---|---|
| ≥1 verdict-blocking finding, coverage at or above the floor | `NOT_READY_FOR_RELEASE` / `2` | `NOT_READY_FOR_RELEASE` / `2` — unchanged |
| assessed deep ratio below the `1/5` floor | `INSUFFICIENT_COVERAGE` / `3` | `INSUFFICIENT_COVERAGE` / `3` — unchanged |
| assessed deep ratio at or above `3/5`, all critical subsystems deep, 0 blocking findings | `RELEASE_READY` / `0` | `RELEASE_READY` / `0` — unchanged |
| **0 blocking findings + an unmet coverage or critical-subsystem gate, at or above the `1/5` floor** | `NOT_READY_FOR_RELEASE` / `2` | **`INSUFFICIENT_COVERAGE` / `3`** ← **the only behaviour change** |

Three consequences, and they are the whole story for a CI integrator:

- **A step branching only on `0` vs non-zero is unaffected.** Nothing that was non-zero became zero.
- **A step distinguishing `2` from `3` now receives the correct one, with no consumer code change.**
  `2` means *Argus found something*. `3` means *Argus did not examine enough to vouch*. Previously the
  fourth row above sent the first message when the second was true. That was the bug; correcting it is
  the amendment.
- **Nothing became a silent pass.** Exit `3` is still non-zero and still fails an unconfigured CI step.
  A pipeline that chooses to treat `3` as success has changed its own risk posture — it did not inherit
  one from this change.

#### The binding FR16 decision table, reproduced so the claim above is checkable

Evaluated **in order**; the first matching row wins. `assessed ratio` is the deep-coverage ratio over the
assessed population (see [Defaults: `--coverage-scope`](#defaults---coverage-scope)).

| # | Condition | Verdict | Exit | `decision_row` |
|---|---|---|---|---|
| 1 | assessed population is empty **or** assessed ratio `< 1/5` (the floor) | `INSUFFICIENT_COVERAGE` | `3` | `row_1_below_floor` |
| 2 | ≥1 verdict-blocking finding | `NOT_READY_FOR_RELEASE` | `2` | `row_2_blocking_findings` |
| 3 | assessed ratio `>= 3/5` **and** every critical subsystem audited deep | `RELEASE_READY` | `0` | `row_3_gates_met` |
| 4 | otherwise — nothing blocking found, a coverage or critical-subsystem gate unmet | `INSUFFICIENT_COVERAGE` | `3` | `row_4_gate_unmet_no_findings` |

Row 1 keeps precedence over row 2 deliberately: below the floor, ArgusAgent has not examined enough to
honestly claim it saw enough to block either.

`INSUFFICIENT_COVERAGE` is a **not-assessed** state, not a blocking verdict. Rows 1 and 4 are both
`INSUFFICIENT_COVERAGE` / exit `3` but they mean different things — row 1: *too little was examined to say
anything*; row 4: *plenty was examined, nothing was found, a gate was not met.*

`1` is not in this table because no verdict produces it. It is what the CLI returns when a typed failure
degrades the run before a verdict exists — see [API](#api-library-consumers) for the one new way that can
now happen.

### Artifacts: schema versions

**Two** schema constants moved from `"1"` to `"2"`. Both are consumer-visible, and their compatibility
behaviour is genuinely different — read both.

| Constant | Before | After | Module |
|---|---|---|---|
| `VERDICT_SCHEMA_VERSION` | `"1"` | `"2"` | `argus/verdict/verdict_gate.py` |
| `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` | `"1"` | `"2"` | `argus/ledger/critical_subsystems.py` |

**`VERDICT_SCHEMA_VERSION` `"1"` → `"2"` — carries the new `decision_row` field.**

`decision_row` records which FR16 row above actually fired. Its four values are exactly
`row_1_below_floor`, `row_2_blocking_findings`, `row_3_gates_met`, `row_4_gate_unmet_no_findings`.

*Compatibility:* **`decision_row` is omitted entirely from a `"1"`-stamped payload** — never emitted as
`"decision_row": null`. A pre-amendment verdict artifact still validates, re-serializes with the same ten
keys it always had, and therefore **round-trips byte-identically and keeps its content hash**. Verdicts
already persisted under `.argus/` are **not rewritten** and keep their `"1"` stamp.

**`CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` `"1"` → `"2"` — carries the new `heuristic_excluded_ineligible`
field, and this one changes every artifact.**

`heuristic_excluded_ineligible` maps a heuristically-designated path to the reason it was ruled ineligible
to be a critical subsystem (`test_file` or `zero_definition_module`).

*Compatibility:* **`heuristic_excluded_ineligible` is emitted unconditionally — even when empty.** It has
no omit-when-unengaged rule. So **every** critical-subsystem artifact changes bytes on **every** run:

```
before:  {"designated_but_unmatched":[],"origins":{},"paths":[],"schema_version":"1"}
after:   {"designated_but_unmatched":[],"heuristic_excluded_ineligible":{},"origins":{},"paths":[],"schema_version":"2"}
```

Populated, the new key looks like `"heuristic_excluded_ineligible":{"tests/test_auth.py":"test_file"}`.

**The consequence the exit-code framing hides:** artifacts under `.argus/` are **content-addressed** — the
file is named for the hash of its own payload (`state/<sha256>.json`). A changed payload therefore means a
**changed filename**. A consumer that pinned a previous artifact path or hash **will not find it**. Every
critical-subsystem artifact is affected; a verdict artifact is affected once it is re-derived under `"2"`.

**A schema bump is not the only thing that moves a filename, and this is the trap.** A run persists more
artifacts than the two whose version changed, and the file name is the hash of the payload — *the whole
payload*, not the `schema_version` in it. So the **negative-assurance artifact moves too**, on any row-4
run, because its `assurance_statement` changed (see [Output: changed strings](#output-changed-strings)) —
and it **keeps its `"1"` stamp**, so nothing in the artifact announces it. If you pin `.argus/` paths or
hashes, re-derive them rather than checking version stamps: **a stamp that did not change is not a promise
that the bytes did not.**

Both bumps are additive: no field was removed, renamed or re-typed. The `schema_version` bump is the
sanctioned signal for an intentional content-hash change.

### Defaults: `--coverage-scope`

**This one predates the amendment above.** `--coverage-scope` already defaulted to `application` before
any of the FR16/FR4 work landed; it is recorded here because it was never announced anywhere, not because
it is part of this delta.

`application` holds test files out of the deep-coverage **denominator**. Test files are graded shallow by
construction — they are the *subject* of the vacuous-test pass, not a target of deep grounding — so in a
well-tested repository they dominate the denominator and manufacture a false negative.

- **A pipeline relying on the whole-repository denominator must now pass `--coverage-scope repository`
  explicitly.**
- **No consumer loses information.** When the assessment is narrowed, both ratios are printed on every
  run and the held-out population is disclosed on the verdict, on stdout and in the report.
- **The floor is still applied *within* the scope.** Narrowing changes *what is claimed*, never the bar
  for claiming it. An application whose own files fall below the `1/5` floor still returns
  `INSUFFICIENT_COVERAGE`. Blocking findings and the critical-subsystem clause are never scoped away.

### Output: changed strings

If you `grep` Argus's human output or its generated `final-verdict.md`, read this section.

**Ship-readiness headline** (stderr, and the first quoted line of `final-verdict.md`) — one row changed.

Every row's **current** headline, one row per line. `N` stands for the run's finding count, not contract
text:

- Headline row 1 unchanged: `NOT ASSESSED — too little of the code was examined deeply to make any call. This is a statement about the audit, not about the code.`
- Headline row 2 unchanged: `BLOCKED — N verdict-blocking finding(s) must be resolved.`
- Headline row 3 unchanged: `READY — no blocking problems found, and enough of the code was examined deeply to say so.`
- Headline row 4 after: `NOT VOUCHED — nothing broken was found, but a coverage or critical-subsystem gate was not met, so no release-readiness claim is made. This is a statement about the audit, not about the code.`

What changed, and from what:

- Headline row 4, before:
  `NOT VOUCHED — nothing broken was found, but a coverage gate was not met, so no release-readiness claim is made. This is a statement about the audit, not about the code.`

  Row 4 also **changed which verdict it wears**: that prose previously appeared under
  `NOT_READY_FOR_RELEASE` / exit `2` and now appears under `INSUFFICIENT_COVERAGE` / exit `3`.
- Row 2's `N` is now always ≥ 1: row 2 is the only producer of `NOT_READY_FOR_RELEASE`, and it requires at
  least one verdict-eligible finding. `BLOCKED — 0 verdict-blocking finding(s)` is no longer reachable.

**`final-verdict.md` callouts** — two changed, and one of them changes the callout **level**.

Every row's **current** callout is published here verbatim, level first, one row per line, so it can be
diffed against a real run without reading the source. The example ratio is `3/10` deep out of `3/5`
required.

**Row 4 renders three different callouts, one per cause** — it names the gates that were actually unmet,
joined by `; `, so a consumer matching the whole sentence must expect all three:

- Row 1 unchanged: `> [!WARNING]` — Repository deep coverage ratio is below the required floor. Additional definitions or tests required.
- Row 2 after: `> [!CAUTION]` — Repository is NOT ready for release — 1 verdict-blocking finding(s).
- Row 3 unchanged: `> [!TIP]` — Repository satisfies all deterministic release readiness criteria. Zero blocking findings emitted.
- Row 4 (coverage) after: `> [!WARNING]` — Release readiness is NOT VOUCHED — Argus found nothing blocking, but deep coverage `3/10` is below the `3/5` release threshold. This is a statement about the audit, not about the code.
- Row 4 (critical) after: `> [!WARNING]` — Release readiness is NOT VOUCHED — Argus found nothing blocking, but at least one critical subsystem is not audited deep (FR16). This is a statement about the audit, not about the code.
- Row 4 (both) after: `> [!WARNING]` — Release readiness is NOT VOUCHED — Argus found nothing blocking, but deep coverage `3/10` is below the `3/5` release threshold; at least one critical subsystem is not audited deep (FR16). This is a statement about the audit, not about the code.

What changed, and from what:

- **Row 4 — the callout LEVEL moved `[!CAUTION]` → `[!WARNING]`, for all three causes.** Before:
  `> [!CAUTION]` / `Repository is NOT ready for release — deep coverage `3/10` is below the `3/5` release threshold.`
  **A tool matching on `[!CAUTION]` to detect a failing audit will stop matching this row.**
- **Row 2 — the appended clauses are gone.** Before, the `[!CAUTION]` line **appended** the coverage and
  critical-subsystem clauses whenever those gates also happened to be unmet — e.g. `… — 1 verdict-blocking
  finding(s); deep coverage `3/10` is below the `3/5` release threshold; at least one critical subsystem is
  not audited deep (FR16).` FR16 short-circuits at row 2, so rows 3 and 4 were never reached and those
  gates were never evaluated — naming them as causes was a false causal claim.
- **Rows 1 and 3 are byte-identical to before**, level and text, as marked above.

**Other rendered text:**

- The `### Critical subsystems below `audited_deep` (N)` section now renders on **every** row that carries
  a non-empty critical set, not only the blocking one. Its lead sentence is row-dependent: only row 4 is
  entitled to a causal one.
- The test-dilution note's caveat changed from `Note that <…> would still block.` to
  `Note that the critical-subsystem clause would still withhold `RELEASE_READY`.` — because that clause
  withholds `RELEASE_READY`, it does not block.

**Persisted negative-assurance statement** (`assurance_statement`, a machine-read string inside
`.argus/state/*.json`) — **the sharpest change in this delta, and the one no schema signal announces.**

Every row's **current** sentence, one row per line. `(…)` stands for the run's scope clause — counts, not
contract text:

- Assurance row 1 unchanged: Assessed coverage is below the floor; no repo-wide verdict was rendered (…).
- Assurance row 2 unchanged: Blocking findings were detected within the assessed scope (…).
- Assurance row 3 unchanged: No blocking findings were detected within the assessed scope (…).
- Assurance row 4 after: No blocking findings were detected within the assessed scope; a coverage or critical-subsystem gate was not met, so release readiness was not vouched for (…).

**Row 4 is the only one that changed, and what it changed FROM is the point of this whole amendment.**
Before, the sentence was selected from the **verdict token alone**, and a row-4 run wore the token
`NOT_READY_FOR_RELEASE` — so it received row 2's sentence:

- Assurance row 4, before:
  `Blocking findings were detected within the assessed scope (…).`

That was written to disk, in a machine-read field, for a run whose `blocking_finding_count` was **`0`**.
The sentence is now selected from the **decision row**, so the single pre-amendment `INSUFFICIENT_COVERAGE`
sentence is split: row 1 keeps it, row 4 gets the wording above. **If you machine-read
`assurance_statement`, this is the field to re-check** — a row-4 run that used to read as a block now reads
as a non-assessment, and the artifact's own bytes were the only place that ever said either.

Note that this before-string was **not replaced**: it is still exactly what row 2 renders today, for a run
that really did find something. Row 4 stopped borrowing it.

**Byte-identical to before — these did *not* change:**

- The ship-readiness headlines for rows 1, 2 and 3 — quoted above and marked *unchanged*. They are stated
  once, there, rather than copied here: a second copy is a second thing that can go stale.
- The row-1 and row-3 `final-verdict.md` callouts — level **and** text — quoted above and marked
  *unchanged*. They are stated once, there, rather than copied here: a second copy is a second thing that
  can go stale.
- The negative-assurance sentences for rows 1, 2 and 3 — quoted above and marked *unchanged*, for the same
  reason as the callouts: stated once, in one place.

### Unchanged on purpose

- **The stdout machine summary line is byte-identical.** Its shape is still
  `verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>`, plus
  `assessed_deep_ratio=<num/den> scope=<id> held_out=<n>` when the assessment was narrowed. **No
  decision-row field was added to it.** This was a deliberate decision: stdout is the wire contract CI
  steps parse positionally, and the row belongs on the artifact.
- **The verdict vocabulary did not grow.** It is still exactly `RELEASE_READY`,
  `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`. Adding a fourth member (`COVERAGE_GATE_UNMET`) was
  considered and rejected — it would have broken every consumer switching on the enum, to express
  something `decision_row` expresses additively.
- **Exit-code values are unchanged**: `0`, `2`, `3`, and `1` for a typed failure.
- **Deriving the row from the unchanged stdout line.** Because the line did not grow, a consumer that
  needs the row can derive it: `INSUFFICIENT_COVERAGE` with assessed ratio `< 1/5` ⇒ row 1;
  `NOT_READY_FOR_RELEASE` ⇒ row 2; `RELEASE_READY` ⇒ row 3; `INSUFFICIENT_COVERAGE` with assessed ratio
  `>= 1/5` ⇒ row 4.
  **Read `assessed ratio` off `assessed_deep_ratio=` when that field is present, and off `deep_ratio=`
  when it is not.** The `assessed_deep_ratio` / `scope` / `held_out` fields are appended **only when the
  assessment was narrowed** — under `--coverage-scope repository` nothing is held out, so the line carries
  `deep_ratio=` alone and that ratio *is* the assessed one.
  **If you need certainty, read `decision_row` on the verdict artifact instead.** The derivation above is
  a partial copy of the decision table, and a second copy of that table that can silently diverge from the
  real one is precisely the fragility this amendment exists to remove. The artifact carries the row
  authoritatively.
- Ratios are exact fractions, printed as `num/den` — never a float, never a percentage. A fully-deep run
  prints `1`, not `10/10`.

### API (library consumers)

For consumers importing `argus.*` rather than shelling out. Added names:

| Name | Kind |
|---|---|
| `DecisionRow` | new `str` enum: `row_1_below_floor`, `row_2_blocking_findings`, `row_3_gates_met`, `row_4_gate_unmet_no_findings` |
| `AuditVerdict.decision_row` | new field, `DecisionRow \| None`, default `None` |
| `AuditVerdict.is_below_floor` | new derived property — the single source of truth for "row 1 or row 4" |
| `ShipReadinessError` | new `ValueError` subclass — **see the behavioural note below** |
| `CriticalIneligibility` | new `str` enum: `test_file`, `zero_definition_module` |
| `CriticalCandidate.ineligibility` | new field |
| `CriticalSubsystemSet.heuristic_excluded_ineligible` | new field, always serialized |
| `ProsecutionResult.verdict_changed` | new field; new rationale token `reclassified:<from>-><to>` |
| `is_test_classification_content_dependent` | newly **exported** from `argus/detectors/vacuous_test.py` |

**`ShipReadinessError` is a behavioural change, not merely an addition.** `render_ship_readiness()` used
to have a terminal branch that always returned prose. For one state — `NOT_READY_FOR_RELEASE` with
`blocking_finding_count == 0` — it now **raises** instead. That state is unreachable from
`evaluate_verdict` after the amendment (row 2 is its only producer and row 2 requires at least one
verdict-eligible finding), so rendering a sentence for it would have meant printing
`BLOCKED — 0 verdict-blocking finding(s)`: an accusation with nothing behind it.

- **If you call `render_ship_readiness()` directly, it can now raise.**
- `ShipReadinessError` subclasses `ValueError`, and the CLI degrades it — like every other typed
  failure — to a secret-safe stderr line and **exit `1`**, never a traceback.

### Do I need to change anything?

- **You branch only on `0` vs non-zero** → **No change.**
- **You distinguish exit `2` from exit `3`** → **No change**, and you now get the correct one: `2` when
  something was found, `3` when not enough was examined to vouch.
- **You validate `schema_version` on an artifact** → **Yes**: update your expected value to `"2"` for the
  verdict artifact and for the critical-subsystem artifact. Old `"1"`-stamped verdicts still validate.
- **You string-match Argus reports, or pin `.argus/` artifact paths or hashes** → **Yes, re-check**: see
  [Output: changed strings](#output-changed-strings) and the content-address note in
  [Artifacts: schema versions](#artifacts-schema-versions).
- **You relied on the whole-repository coverage denominator** → pass `--coverage-scope repository`
  explicitly.
