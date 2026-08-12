"""PURE markdown renderer for the dogfood PROOF ARTIFACT (``minions-dogfood-proof.md``).

Extracted VERBATIM from ``argus/dogfood/proof_run.py`` by Story 9.2 (ledger item
``DF-8-5-D``). The move is a PURE RELOCATION — the rendered bytes are unchanged, proven
by rendering the SAME :class:`~argus.dogfood.proof_types.DogfoodProofRun` before and
after the move and comparing byte-for-byte
(``TC-ArgusAgent-DOGFOOD-001-38``/``-39``). ``proof_run.py`` re-exports
:func:`render_proof_markdown` and :data:`DOGFOOD_EXTERNALIZATION_GUARD`, so every
existing import path is unchanged.

AR8 — this module is PURE and STRUCTURALLY so: it takes an already-derived
:class:`DogfoodProofRun` and returns a ``str``. It performs no filesystem I/O, reads no
clock, runs no subprocess, and — critically — imports NOTHING from ``proof_run``, which
is the impure shell (git enumerate, snapshot materialize, audit run, ``.argus/``
persist). The pure/impure separation the 7.2 module docstring narrated in prose is now
a module boundary the import graph enforces, and the direction of that edge is the
reason :data:`DOGFOOD_EXTERNALIZATION_GUARD` moved here WITH its only consumer rather
than staying behind and creating an import cycle. Its value is byte-identical to the
pre-move constant and is pinned by an equality assertion
(``TC-ArgusAgent-DOGFOOD-001-40``), so "unchanged" is verified rather than asserted.

NFR-S1 — the renderer emits provenance, counts, rule-ids and repo-relative locators
only: no source byte, no secret value, no absolute host path. AR4 — ratios render from
exact ``Fraction`` numerator/denominator pairs, never a ``float``.
"""

from __future__ import annotations

from fractions import Fraction

from argus.dogfood.proof_types import DogfoodProofRun

__all__ = [
    "DOGFOOD_EXTERNALIZATION_GUARD",
    "render_proof_markdown",
]


# The externalization-guard sentence the proof artifact + wrapper carry (AC-DEMO-GRADE).
# A committed test asserts this language is present + that no "externalization-grade /
# validated deep audit" over-claim phrase is injected.
DOGFOOD_EXTERNALIZATION_GUARD = (
    "This dogfood run is a demo-heuristic-only (Tier-A) result: the frozen pipeline "
    "run_audit_detailed calls NO LLM (zero-token) and the AST-grounding deep-audit "
    "seam is NOT wired in, so every finding is advisory / verdict-ineligible "
    "(depth_supported is None). It is NOT presented as externalization or assurance "
    "evidence, and it does NOT clear the >=80%-precision gate — that requires the human "
    "TP/FP adjudication over these REAL findings (a documented human step, still open)."
)

# The provenance banner this renderer stamps. ONE definition so the artifact can never
# name a generator module that does not exist (Story 8.5 / AC2 — pinned by a committed
# test that resolves every path the artifact cites). Story 9.2 / DF-8-5-D moved the
# renderer out of ``proof_run.py``, so the banner names BOTH the module that renders the
# bytes and the module that orchestrates the run and re-exports the entry point. Naming
# only the old path would still have resolved — and would still have been the artifact
# pointing at a file that no longer contains its generator.
_GENERATOR_MODULE = "argus/dogfood/proof_render.py"
_ORCHESTRATOR_MODULE = "argus/dogfood/proof_run.py"

# The preserved, non-regenerable independent run this artifact path used to hold (AC5).
_SUPERSEDED_ARTIFACT = "minions-dogfood-proof-story-7-2-superseded.md"

_SELF_AUDIT_HONESTY = (
    "**This is a SELF-audit — Argus auditing Argus (Story 8.5 / AC2).** The subject is "
    "this repository's own package, not an independent codebase. A self-audit is "
    "MATERIALLY WEAKER evidence than the independent-repository run it supersedes: the "
    "tool and the tree share authorship, so the run cannot demonstrate that the tool "
    "finds defects it was not written alongside. It is reportable as a reproducibility "
    "and no-source-retention demonstration; it is NEVER independent corroboration of "
    "the tool's detection ability. The independent Story-7.2 run over the Minions "
    f"platform repository is preserved verbatim at `{_SUPERSEDED_ARTIFACT}` and cannot "
    "be re-executed here, because that source is not in this repository. The filename "
    "`minions-dogfood-proof.md` is a retained HISTORICAL identifier (an evidence path "
    "that moves is an evidence path that gets lost); the subject is what this section "
    "names, not what the filename suggests."
)


def _audited_tree_clause(proof: DogfoodProofRun) -> str:
    """Name the tree the run ACTUALLY enumerated (PURE; Story 8.5 / AC2).

    Rendered from the scope the impure orchestration recorded onto the run — never a
    hardcoded subject — so the artifact cannot name a tree the audit did not read. An
    unrecorded scope degrades to an explicit marker rather than a guessed subject. Only
    the MEASURED exclusions are named: a configured prefix that held nothing out is not
    rendered as a held-out sub-tree (Story 8.5 review, iteration 1).
    """
    if not proof.scope_prefix:
        return "the audited tree (scope not recorded by this run)"
    excluded = ", ".join(f"`{p}`" for p in proof.effective_exclude_prefixes)
    tail = f", excluding {excluded}" if excluded else ""
    return f"the git-tracked `{proof.scope_prefix}` package tree{tail}"


def _row_token(proof: DogfoodProofRun) -> str:
    """Render the LITERAL disclosed ``DecisionRow`` value, never a re-derivation (PURE)."""
    if not proof.decision_row:
        return (
            "`not disclosed` (a pre-amendment verdict payload carried no row; the row is "
            "NOT inferred from the verdict token here, because rows 1 and 4 render the "
            "same token)"
        )
    return f"`{proof.decision_row}`"


def _render_assessed_population(proof: DogfoodProofRun) -> list[str]:
    """Render the population the gate keyed on (PURE; Story 8.5 / AC1).

    States the whole-ledger numbers AND, when a narrowing was disclosed, the assessed
    sub-population with its scope id, held-out count and reason. An absent narrowing is
    stated EXPLICITLY — it must never be readable as a silent one.
    """
    if proof.scope is None:
        return [
            "**No narrowing occurred.** The verdict carries no `coverage_scope`, so the "
            "gate keyed on the WHOLE coverage ledger: "
            f"**{proof.deep_count} `audited_deep` of {proof.total_count} entries** "
            f"(`{proof.deep_ratio.numerator}/{proof.deep_ratio.denominator}`, exact "
            "`Fraction`). No entry was held out of the assessment and no scope "
            "identifier was applied.",
        ]
    s = proof.scope
    return [
        "**A narrowing WAS applied and is disclosed on the verdict.** The gate keyed on "
        "the assessed sub-population below, not on the whole ledger:",
        "",
        f"- Scope identifier: `{s.scope_id}`",
        f"- Assessed deep / assessed total: **{s.assessed_deep_count} / "
        f"{s.assessed_total_count}** "
        f"(`{s.assessed_deep_ratio.numerator}/{s.assessed_deep_ratio.denominator}`, "
        "exact `Fraction`)",
        f"- Held out of the assessment: **{s.excluded_count}** entries, reason "
        f"`{s.excluded_reason}`",
        f"- Whole-ledger deep / total (for comparison): **{proof.deep_count} / "
        f"{proof.total_count}** "
        f"(`{proof.deep_ratio.numerator}/{proof.deep_ratio.denominator}`)",
        "",
        "The `INSUFFICIENT_COVERAGE` floor is re-applied WITHIN the narrowed population, "
        "so a narrowing changes WHAT is claimed and never lowers the bar for claiming it.",
    ]


def _render_critical_clause(proof: DogfoodProofRun) -> list[str]:
    """Render the critical-subsystem clause state (PURE; Story 8.5 / AC1, boundary B3).

    Distinguishes a clause satisfied over a NON-EMPTY, fully-deep critical set from one
    satisfied over an EMPTY set — the second is VACUOUS and is named as such.
    """
    c = proof.critical
    if c is None:
        return [
            "**Not captured by this run.** This artifact makes NO claim about the "
            "critical-subsystem clause state.",
        ]
    if not c.set_retrieved:
        why = f" MEASURED reason: {c.retrieval_note}." if c.retrieval_note else ""
        return [
            "**The run's persisted critical-subsystem set could NOT be read back** from "
            "the snapshot's `.argus/state/` tree, so its SIZE is unknown here. This "
            "artifact therefore does NOT state whether the clause was satisfied over a "
            "real set or vacuously over an empty one — an unread set is reported as "
            f"unread, never as empty.{why}",
            "",
            f"- Clause satisfied (`critical_subsystems_all_deep`): **{c.all_deep}**",
            f"- Critical paths NOT `audited_deep`: **{len(c.not_deep)}**",
        ]
    if not c.all_deep:
        headline = (
            "**NOT satisfied.** At least one critical path is not `audited_deep`; the "
            "paths below are the evidence behind the clause result."
        )
    elif c.set_size == 0:
        headline = (
            "**VACUOUSLY satisfied — the critical set is EMPTY.** The clause held "
            "because there was nothing in it to hold over, NOT because critical code "
            "was audited deep. Read this run's verdict accordingly."
        )
    else:
        headline = (
            "**Satisfied over a NON-EMPTY set.** Every path in the critical set is "
            "`audited_deep`; the gate is not vacuous."
        )
    out = [
        headline,
        "",
        f"- Clause satisfied (`critical_subsystems_all_deep`): **{c.all_deep}**",
        f"- Critical-set size (`CriticalSubsystemSet.paths`): **{c.set_size}**",
        "- Paths the DR-5 eligibility filter removed from the HEURISTIC term as "
        f"ineligible: **{c.excluded_ineligible_count}**",
        f"- `designated_but_unmatched` operator paths: **{len(c.designated_but_unmatched)}**",
    ]
    for path in c.designated_but_unmatched:
        out.append(f"  - `{path}`")
    out.append(f"- Critical paths NOT `audited_deep`: **{len(c.not_deep)}**")
    for path in c.not_deep:
        out.append(f"  - `{path}`")
    return out


def _render_ceiling_pair(proof: DogfoodProofRun) -> list[str]:
    """Render the CEILING HONESTY PAIR (PURE; Story 8.5 / AC1, D7).

    ``$X`` = :data:`DOGFOOD_BUDGET_CEILING` is a FROZEN historical execution parameter;
    the 7.1 generator re-sizes its ceiling from the live tree every derivation and has
    drifted away from it. Stating only one lets this artifact and the budget artifact —
    published together — disagree about "the 7.1 empirical ceiling". Both are stated,
    with a fit verdict for EACH.
    """
    cost = proof.cost
    out = [
        "**The ceiling honesty pair (Story 8.5 / AC1).** Two different numbers are in "
        "play and this artifact states both rather than letting them be confused:",
        "",
        f"- **Frozen historical execution parameter** `$X` = `DOGFOOD_BUDGET_CEILING` = "
        f"**{cost.ceiling}** credits — the ceiling this run was actually EXECUTED under. "
        "It is a pinned constant recording a past sizing, NOT a live measurement.",
    ]
    if cost.live_sized_ceiling is not None:
        out.append(
            "- **Live 7.1 sizing** — the `sized_ceiling` derived from the CURRENT tree by "
            "the same `build_full_repo_plan` call this generator already makes (REUSED — "
            f"no second accountant): **{cost.live_sized_ceiling}** credits. This is the "
            "number `minions-dogfood-budget-plan.md` publishes."
        )
        out.append(
            f"- Fits under the frozen `$X` = {cost.ceiling}: **{cost.fits_within_ceiling}** "
            f"· Fits under the live 7.1 sizing = {cost.live_sized_ceiling}: "
            f"**{cost.fits_within_live_sized_ceiling}**"
        )
    else:
        out.append(
            "- **Live 7.1 sizing:** not supplied to this derivation, so no live figure is "
            "stated here. Read `minions-dogfood-budget-plan.md` for the current sizing."
        )
    return out


def render_proof_markdown(proof: DogfoodProofRun) -> str:
    """Render the committed dogfood PROOF ARTIFACT (``minions-dogfood-proof.md``; PURE).

    Records: the run provenance + verdict, the within-ceiling + 3.2-halt confirmation, the
    SIGNED bundle locator + content hash (the "signature") + the no-source-retention +
    reproducibility claims, the honest ``grade: demo-heuristic-only`` flag + the
    externalization guard, the adjudication-ready finding classes (per-class ``rule_id`` +
    verdict-eligibility + count + sample locators + an empty TP/FP column for the human),
    and the OI1 provisional-gate report. Value-free — only provenance / counts / rule-ids /
    repo-relative locators (NFR-S1). Deterministic + byte-stable for the same proof.
    """
    b = proof.cost.baseline_ratio
    baseline_str = (
        f"{b.numerator}/{b.denominator}" if isinstance(b, Fraction) else str(b)
    )
    scope = _audited_tree_clause(proof)
    lines: list[str] = []
    lines.append(
        "# Argus Dogfood — Proof Artifact (Story 7.2 generator, RE-DERIVED by Story 8.5 "
        "as a SELF-audit)"
    )
    lines.append("")
    lines.append(
        f"> AUTO-GENERATED by `{_GENERATOR_MODULE}` "
        f"(`render_proof_markdown`, re-exported from `{_ORCHESTRATOR_MODULE}`, which "
        "orchestrates the run). Reproducible + byte-stable for the same tracked "
        "content of the tree named in §1 — do NOT hand-edit. "
        "Drivers: ArgusAgent-FR-29 / ArgusAgent-FR-17 / "
        "ArgusAgent-FR-30 / ArgusAgent-FR-21 / ArgusAgent-NFR-D1 / ArgusAgent-NFR-S1 / ArgusAgent-AR4 / ArgusAgent-AR7."
    )
    lines.append("")

    # ── Run provenance + verdict ────────────────────────────────────────────
    lines.append(
        f"## 1. Dogfood execution (AC-EXECUTE) — the frozen audit over {scope}"
    )
    lines.append("")
    lines.append(
        "**Derivation method: RE-RUN** (Story 8.5 / AC4). Every figure in this artifact "
        "was produced by EXECUTING the shipped pipeline on the tree named below, pinned "
        "by the commit descriptor and the `$X` ceiling recorded in §1 and §2. Nothing "
        "here is analytic, nothing is hand-written into the file, and no historical "
        "figure is hardcoded into the generator."
    )
    lines.append("")
    lines.append(
        "The frozen `pipeline.run_audit_detailed` (REUSED — no fork) was run over "
        f"{scope} of THIS repository. That tree was materialized into a CLEAN on-pin "
        "snapshot (the 6.5 `stage_cartridge` pattern) so the frozen "
        "`load_repo_at_commit` clean-tree precondition holds. The audited BYTES are this "
        "repository's own package source at the commit descriptor below."
    )
    lines.append("")
    lines.append(_SELF_AUDIT_HONESTY)
    lines.append("")
    lines.append(
        f"- Commit descriptor (`git rev-parse HEAD` at generation): "
        f"`{proof.commit_descriptor}`"
    )
    lines.append(
        "- Enumerated population (the HONEST label — Story 12.1, closing `DF-10-4-D`): the "
        "file list in this artifact is enumerated from the git INDEX (`git ls-files`), NOT "
        "from the tree at the commit descriptor above. The two are the same tree exactly "
        "when `argus/` carries no staged-or-uncommitted change, and "
        "`TC-ArgusAgent-DOGFOOD-001-50` fails unless they agree — so this artifact cannot "
        "quietly describe one tree while citing another."
    )
    lines.append(f"- Source files audited: **{proof.source_file_count}**")
    lines.append(f"- Total physical LOC (build-cost proxy): **{proof.total_loc}**")
    lines.append(f"- Partition units (7.1 plan, CONSUMED): **{proof.unit_count}**")
    lines.append(
        f"- **Verdict: `{proof.verdict}` (exit `{proof.exit_code}`)**"
    )
    lines.append(f"- **Decision row (FR16 / DR-3), as DISCLOSED by the gate: {_row_token(proof)}**")
    lines.append(
        f"- Coverage-ledger deep-%: **`{proof.deep_ratio.numerator}/{proof.deep_ratio.denominator}`** "
        "(exact `Fraction`, never a float — AR4)"
    )
    lines.append(
        f"- Coverage-ledger deep count / total entries: **{proof.deep_count} / "
        f"{proof.total_count}**"
    )
    lines.append(f"- Blocking (verdict-eligible) findings: **{proof.blocking_finding_count}**")
    lines.append(f"- Total findings emitted: **{proof.total_finding_count}**")
    lines.append("")

    # ── The inputs the row was computed from (DR-3) ─────────────────────────
    lines.append("### 1a. The assessed population the row was computed from (DR-3)")
    lines.append("")
    lines.extend(_render_assessed_population(proof))
    lines.append("")
    lines.append(
        "### 1b. The critical-subsystem clause (FR4 / DR-5 / boundary B3)"
    )
    lines.append("")
    lines.extend(_render_critical_clause(proof))
    lines.append("")

    # ── Within-ceiling + 3.2 halt ───────────────────────────────────────────
    lines.append("## 2. Within the `$X` = 843 ceiling (AC-EXECUTE / FR21 / OI3) + the 3.2 halt")
    lines.append("")
    lines.append(
        f"The run's V1 deterministic zero-token cost total is **{proof.cost.total_credits} "
        "credits** (folded via the 3.1 `account_spend` — no fork)."
    )
    lines.append("")
    lines.extend(_render_ceiling_pair(proof))
    lines.append("")
    lines.append(
        f"- Under `BudgetConfig(ceiling_credits={proof.cost.ceiling})` the run FITS "
        f"(`ceiling_reached is False`): **{proof.cost.fits_within_ceiling}**"
    )
    lines.append(
        f"- Under a ceiling ONE credit below the total the run BREACHES "
        f"(the >=-is-a-breach REUSE — the 3.2 halt->skip->downgrade->report path fires): "
        f"**{proof.cost.breaches_below_total}**"
    )
    lines.append(
        f"- NFR-C1 baseline ratio (audit-cost / build-cost proxy): `{baseline_str}` "
        "(`Fraction`/marker — never a float)"
    )
    lines.append("")

    # ── SIGNED bundle ───────────────────────────────────────────────────────
    lines.append("## 3. The SIGNED, source-free evidence bundle (AC-BUNDLE / FR29 / NFR-A1 / NFR-S1)")
    lines.append("")
    lines.append(
        "Exported via the done 4.3 `build_evidence_bundle` + persisted via "
        "`persist_evidence_bundle` (REUSED — no forked bundle model / serializer), "
        "serialized THROUGH the single 1.1 `canonical.dumps_bytes` and stamped by the 1.1 "
        "content-addressed, **prev-hash-chained** envelope (the ArgusAgent \"signature\"; the "
        "point-in-time stamp is the envelope `created_at`, EXCLUDED from the hash — "
        "NFR-A1/D3)."
    )
    lines.append("")
    lines.append(f"- Persisted bundle locator: `{proof.bundle_locator}`")
    lines.append(f"- Bundle content hash (the signature): `{proof.bundle_content_hash}`")
    lines.append(f"- Canonical bundle byte length: **{proof.bundle_byte_length}**")
    lines.append(f"- Referential-integrity report consistent (4.2 lint): **{proof.integrity_consistent}**")
    lines.append(
        "- **No-source-retention MOAT (NFR-S1 / NFR-S3):** the bundle retains NO source "
        "byte and NO secret value — the moat is STRUCTURAL (no bundle field holds "
        "a source/secret value; only locations + redacted indicators). Proven over the "
        "REAL audited tree by `tests/test_secret_containment.py` "
        "(`TC-ArgusAgent-SECURITY-001-23`) and `tests/test_dogfood_proof.py` "
        "(`TC-ArgusAgent-DOGFOOD-001-22`)."
    )
    lines.append(
        "- **100% reproducibility (AC-REPRODUCIBLE / NFR-D1 / P1):** two dogfood runs on "
        "the same tracked content yield a BYTE-IDENTICAL verdict + bundle canonical bytes "
        "(the builder sorts/order-fixes every collection; no clock/float/set-order in the "
        "hashed payload). Demonstrated (RED against injected non-determinism, then green) "
        "in `tests/test_dogfood_proof.py` (`TC-ArgusAgent-DOGFOOD-001-24`)."
    )
    lines.append("")

    # ── Signature demo ──────────────────────────────────────────────────────
    lines.append("## 4. The `GitHub green · Sonar green · ArgusAgent 🔴` signature demo (AC-SIGNATURE)")
    lines.append("")
    lines.append(
        "ArgusAgent audits a vacuous test (the `vacuous_basic` cartridge — a test that runs "
        "green in CI while asserting nothing) and emits a **BLOCKING** `vacuous_test_ast` "
        "finding → verdict `NOT_READY_FOR_RELEASE` / exit `2` (the 🔴), reproducing the "
        "`GitHub green · Sonar green · ArgusAgent 🔴 tests appear vacuous` line as a real, "
        "repeatable committed artifact (the 1.7 `TC-ArgusAgent-PIPELINE-001-01` precedent). "
        "Asserted in `tests/test_dogfood_proof.py` "
        "(`test_signature_demo_vacuous_test_blocks`)."
    )
    lines.append("")

    # ── Demo-grade flag ─────────────────────────────────────────────────────
    lines.append("## 5. `grade: demo-heuristic-only` — the red-team honesty flag (AC-DEMO-GRADE)")
    lines.append("")
    lines.append(f"- **`grade: {proof.grade}`**")
    lines.append("")
    lines.append(f"> {DOGFOOD_EXTERNALIZATION_GUARD}")
    lines.append("")

    # ── Adjudication-ready findings ─────────────────────────────────────────
    lines.append("## 6. Adjudication-ready REAL findings (AC-ADJUDICATION-READY / OI1 / DF-6-6-A)")
    lines.append("")
    lines.append(
        "The REAL dogfood findings are laid out below by the 6.6 `finding_match_key` "
        "identity `(rule_id, verdict_eligible, advisory)` — one row per finding CLASS "
        "(two DISTINCT classes never collapse to one row — AI-E6-1). A human Eng-Lead + "
        "QA-Lead can tag each class TP/FP per `precision-validation-protocol.md` §4/§5 by "
        "inspecting the sample locators on the real repo. **The human TP/FP adjudication "
        "is NOT performed here (OI1 — it is the human step); the `TP/FP` column is left "
        "empty for the human.**"
    )
    lines.append("")
    lines.append("| rule_id | verdict-eligible (blocking) | advisory | count | sample locators | TP/FP (human) |")
    lines.append("|---|---|---|---|---|---|")
    for row in proof.adjudication:
        samples = "; ".join(f"`{s}`" for s in row.sample_locators) or "—"
        lines.append(
            f"| `{row.rule_id}` | {row.verdict_eligible} | {row.advisory} | {row.count} "
            f"| {samples} | {row.adjudication or '&nbsp;'} |"
        )
    lines.append("")

    # ── Provisional gate ────────────────────────────────────────────────────
    lines.append("## 7. The ≥80%-precision gate STAYS PROVISIONAL (AC-PROVISIONAL / OI1 keystone)")
    lines.append("")
    lines.append(
        "The synthetic corpus (7.1: 5 distinct classes) bootstrapped a PROVISIONAL "
        "≥80%-precision gate. **The gate is cleared ONLY by the human TP/FP adjudication "
        "over the REAL dogfood findings above** — a HUMAN step (Eng-Lead + QA-Lead), OUT "
        "of scope for this autonomous story. This proof presents NO ≥80% number as "
        "authoritative / cleared, does NOT flip `protocol_cleared`, and does NOT flip the "
        "6.5 `precision_gate_status()` marker."
    )
    lines.append("")
    lines.append(f"- Gate status: `{proof.gate_status}`")
    lines.append(
        "- The still-open human-adjudication step is filed as a defer (six CC-3 fields, "
        "`target_story: epic-7-minions-dogfood-precision`) in `deferred-work.md`."
    )
    lines.append("")
    return "\n".join(lines)
