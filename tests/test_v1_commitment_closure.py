"""Story 10.5 / AC5 — a V1 commitment is delivered, or it is explicitly not V1.

Verification area ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-30``..``-41``, CONTINUING the index
locked by Story 8.4; ``-20``..``-23`` belong to ``tests/test_evidence_citation.py`` **and**
``tests/test_status_document_registry.py`` — *(amended 2026-08-17 by Story 13.4: that range has TWO
hosts since the cohesion split; the derivation stayed, ``-21``/``-22`` and the governed population
moved, and no id was renumbered)* — ``-24``..``-27``
to ``tests/test_spec_claim_scope.py``, ``-28`` to ``tests/test_invocation_contract.py`` and ``-29``
to ``tests/test_grammar_diagnosis.py``).

**The rule this file enforces**, established by Story 10.5 and registered in ``architecture.md``
§Enforcement: *a V1 commitment is delivered only when a production call site reaches it — mapping to
a module is not delivery, and a commitment with neither a call site nor a dated reclassification is
a defect.*

**The defect class.** Epic 10 repaired four claims that outran the product: a status claim citing no
gate (10.1), a scope claim naming the wrong languages (10.2), an invocation claim naming the wrong
flags (10.3), a degradation claim naming the wrong cause (10.4). Underneath all four sits one class:
*the specification commits to a thing the product does not have.* That class was filed **four times
over five weeks** — ``DF-AUD-APAA-A`` and ``DF-AUD-APAA-B`` (2026-07-04), ``DF-6-7-A``,
``DF-10-4-B`` — and **swept zero times**. Each filing recorded an *instance*; none triggered a sweep.
``implementation-readiness-report-2026-08-03.md:400`` even scored the blind spot — *"the requirement-ID
pass scores 100%; the unnumbered-obligation pass scores 68%"* — and the score was never acted on.
This file is what makes a fifth filing impossible.

**Two closures that meet in the middle, because neither closes the class alone.**

1. *Forward* — the commitment side is prose and **cannot be enumerated from a section heading.**
   Measured 2026-08-11: the ``standards_refs[]`` + CWE-on-security commitment was named by the epic
   AC, the change proposal and the sprint-status annotation as **one** site in §Product Scope. It
   lives at **three** PRD coordinates, and the second — inside §Compliance & Regulatory, in a
   different sentence shape (``**V1:**`` in a domain-requirements bullet, not a ``·``-separated scope
   list) — **had been named in no planning document since 2026-08-03.** A sweep anchored on the
   ``## Product Scope`` heading would not have seen it. So the population is derived by **claim
   SHAPE across the whole document**.
2. *Reverse* — the delivery side is code and **can be walked exactly.** ``architecture.md:905``
   certifies *"All 33 FRs of the base contract map to a concrete module … No FR is unsupported"* over
   a module-**placement** table. Measured on this tree, four of the seven FRs in one row of that
   table (FR23, FR24, FR26, FR29) have no production call site reachable from ``argus/cli.py``. The
   sentence is true and useless. ``-34``/``-35`` make a ``wired`` disposition **mechanically
   refutable**, in both directions.

**The asymmetry that keeps this guard honest.** *Module unreachable* is **not** *FR undelivered*, and
a guard that equated them would manufacture false accusations — the failure mode this product exists
to prevent. FR27 is the worked example: the memoization *mechanism* is unwired, but the default run
is zero-token and deterministic, so *"the same verdict for the same repository and version"* holds
**by determinism**. The reachability walk is the **closure device that forces a classification**; it
is never the classifier. It may **refute** a ``wired`` claim mechanically. It may never **assign** a
disposition. Assignment is a dated, reasoned human decision recorded in the registries below.

**Why the graph is built by reading source as TEXT and never by ``import argus`` (Story 10.5 DN-6).**
Three measured reasons: lazy imports exist and would defeat a runtime walk
(``argus/precision/replay_harness.py`` inserts onto ``sys.path`` inside a function); importing
``argus`` would make the result depend on which optional extras are installed, so CI's three legs and
a developer host could disagree about delivery; and a test that executes **no** ``argus`` line cannot
perturb the coverage figure the ledger cites. Precedent: 10.1's guard is pure ``pathlib`` + ``re``,
10.4's is pure ``ast``. **No new dependency, stdlib only.**

**Both closures go green by finding nothing** — a heading rename, a section move, a package rename,
an ``ast.parse`` failure. Non-vacuity is therefore mandatory and is ``-39``: every floor below is a
named constant carrying the reason its number is what it is.

Every file is opened ``encoding="utf-8"`` explicitly: the artifact tree carries ``~~``, ``⚠️``, ``🚩``
and ``·``, and an inherited host locale is the exact defect class that turned run ``31322881580`` red.

No network, no LLM, no subprocess, no ``.argus/`` write, no ``argus`` import.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_PRD = _ARTIFACT_DIR / "E-PRD" / "prd.md"
_ARCHITECTURE = _ARTIFACT_DIR / "architecture.md"
_LEDGER = _ARTIFACT_DIR / "deferred-work.md"
_PACKAGE_ROOT = _REPO_ROOT / "argus"

_GUARD_FILE = "tests/test_v1_commitment_closure.py"


def console_entry_modules(pyproject: str) -> tuple[str, ...]:
    """Every MODULE that ``[project.scripts]`` names as an entry point (PURE).

    CORRECTED 2026-08-15 by Story 12.6. This file used to carry
    ``_ENTRY_POINT = "argus.cli"`` and asserted, in prose at its own non-vacuity floor,
    *"It is the ONLY entry point — pyproject.toml ships three console aliases and all three
    are argus.cli:main"*. Story 12.6 shipped a FOURTH alias, ``argus-mcp =
    argus.mcp.server:main``, and **that sentence became false with nothing red** — the
    reachability walk simply went on being computed from one of the two entry points, so
    every `wired` disposition in this file was being proven against a graph that no longer
    described the product. A hand-written entry point is a fact about the distribution
    stored in the wrong place; this reads it from the distribution metadata, so the next
    entry point is covered on the day it is declared (AI-E11-1 clause (iii): the population
    is a closure, never a hand-list).

    Returns the module halves of the ``module:function`` targets, deduplicated and sorted.
    An empty result is impossible-by-assertion at `-39`, because a walk from no entry point
    reaches nothing and every reachability assertion here would pass vacuously.
    """
    match = re.search(r"^\[project\.scripts\]\n(.*?)(?=\n\[|\Z)", pyproject, re.S | re.M)
    if match is None:
        return ()
    targets = re.findall(r'^[\w.-]+\s*=\s*"([^"]+)"', match.group(1), re.M)
    return tuple(sorted({target.split(":", 1)[0] for target in targets}))


_ENTRY_POINTS: tuple[str, ...] = console_entry_modules(
    (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
)
#: How the entry-point set is named in a failure message. A set, because there are two.
_ENTRY_POINT_LABEL = " ∪ ".join(_ENTRY_POINTS) or "<no entry point>"

# The date this story's dispositions were taken and its amendments landed. Every amendment this
# guard pins must carry it, so a future reader can tell a 10.5 edit from an older one.
_DISPOSITION_DATE = "2026-08-11"
_DISPOSITION_STORY = "Story 10.5"

# ─────────────────────────────────────────────────────────────────────────────
# Non-vacuity floors (`-39`). Each is BELOW the figure measured on 2026-08-11 by enough slack that
# an ordinary amendment does not trip it, and ABOVE zero by enough that a rename, a move or a parse
# failure cannot pass silently. A guard that goes green by finding nothing is the failure mode.
# ─────────────────────────────────────────────────────────────────────────────

# Measured 2026-08-11: 20 V1 claim atoms across `**V1 Core:**` (10), `**V1 Differentiator:**` (3),
# `**Proof:**` (1), the `### V1 Design Invariants` bullets (5) and §Compliance's `**V1:**` (1).
# Floor 15: three whole shapes could be merged away before this stops meaning anything.
_MIN_CLAIM_ATOMS = 15

# Measured 2026-08-11: FR1..FR37, all 37 present. The contract only ever grows (NFR-A1 additive
# only), so a floor of 30 catches a section move or a shape rename without pinning the count — the
# count itself is pinned exactly by `-32`'s both-direction closure against the registry.
_MIN_FR_IDS = 30

# RE-MEASURED 2026-08-15 by Story 12.7 against the tree it produced. Measured: **83** modules under
# `argus/`, **401** intra-package import edges (submodule edges plus the ancestor-package edges a
# submodule import implies), **68** modules reachable from the union of the `[project.scripts]`
# entry modules. The five new modules are `argus.assets`, `argus.assets.commands`, `argus.commands`,
# `argus.commands.hosts` and `argus.commands.installer`, and ALL FIVE are reachable — the installer
# is reached from `argus.cli` through the `install-commands` sub-command, which is what makes FR35's
# second half `wired` rather than a library seam. No entry point was added: `install-commands` is a
# SUB-COMMAND (DN-1), so the entry-point set is unchanged and the reachability walk starts where it
# started.
# ~~Measured 2026-08-15 by Story 12.6: 78 / 390 / 63, of which 60 from `argus.cli` alone.~~
# ~~Measured 2026-08-11: 72 / 318 / 53 from `argus.cli` alone.~~ (§3.4 — the earlier measurements
# stay legible so the trend is readable rather than remembered.)
# Floors still sit ~25% low, and they RISE with the measurement rather than being left where they
# were: a floor that stops tracking the tree is a floor that stops meaning anything. A package split
# may move modules between files, but a walk that finds 61 modules or 299 edges has stopped seeing
# the package.
_MIN_PACKAGE_MODULES = 62
_MIN_IMPORT_EDGES = 300
_MIN_REACHABLE_MODULES = 51

# ─────────────────────────────────────────────────────────────────────────────
# The two CLOSED disposition vocabularies (Story 10.5 DN-4). A hit that fits none of these is a
# HALT for the dev, never a new label invented mid-sweep: an open vocabulary is how "maps to a
# module" became a certification of coverage in the first place.
# ─────────────────────────────────────────────────────────────────────────────

_FORWARD_VOCABULARY = frozenset(
    {
        "fr-backed",  # carried by a numbered FR; names it
        "nfr-backed",  # carried by an NFR — SPECIFIED, not a gap (DN-5)
        "constraint",  # a forward-compatibility invariant, not a capability
        "reclassified-v2",  # decided out of V1 on a date, at the destination too
        "specified-not-built",  # the deliverable IS a specification; residual named
        "delivered-differently",  # delivered, not in the promised form; divergence named
    }
)

_REVERSE_VOCABULARY = frozenset(
    {
        "wired",  # production call site reachable from argus/cli.py — PROVEN by `-34`
        "delivered-differently",  # holds by another mechanism; named mechanism deferred
        "library-seam",  # built, correct, test-proven, no reachable production call site
        "not-built",  # specified for V1.5+; names the owning story
    }
)

# `library-seam` and `not-built` are the two dispositions that admit a gap. Both must name where the
# gap goes, or the sweep has produced a shrug rather than a disposition.
_MUST_NAME_A_FORWARD_TARGET = frozenset({"library-seam", "not-built"})


@dataclass(frozen=True)
class _Commitment:
    """One V1 commitment atom's disposition. `anchor` must match EXACTLY ONE atom in the PRD."""

    anchor: str
    disposition: str
    evidence: str  # the FR/NFR/module/story that carries it, named BY ANCHOR never by line number
    reason: str


@dataclass(frozen=True)
class _Delivery:
    """One FR's delivery disposition. `module` is a repo-relative path; `anchor` lives inside it."""

    fr: str
    disposition: str
    module: str
    anchor: str
    reason: str
    # Story 12.2 / AC7.2 — the DEDICATED seam modules a `not-built` FR would be delivered
    # THROUGH, so the disposition can be REFUTED once they become reachable. Without it
    # `not-built` was unrefutable in the one direction that matters: wiring FR36 turned
    # nothing red, and the registry would have asserted "not built" about something built,
    # forever. NOT the same as `module` (which claims delivery, and `-33` rightly forbids
    # here): this claims only *if these become reachable, this disposition has expired*.
    # Name ONLY modules that exist for THAT FR — a shared module going reachable proves
    # nothing, and naming one would manufacture a false accusation.
    seam_modules: tuple[str, ...] = ()


# ─────────────────────────────────────────────────────────────────────────────
# FORWARD REGISTRY — every V1 commitment atom, disposed 2026-08-11 by Story 10.5.
# Measured on 2026-08-11: 20 atoms, 20 entries, matched one-to-one in both directions by `-30`.
# By disposition: fr-backed 11 · constraint 3 · nfr-backed 2 · reclassified-v2 2 ·
# specified-not-built 1 · delivered-differently 1.
# ⚠️ That tally is a COMMENT and comments drift. `-30` recomputes the matching every run and is the
# only statement of it that cannot be wrong: the parser wins over any hand count, which is the whole
# lesson of this story (§A.1 — one site was named, three were measured).
# ─────────────────────────────────────────────────────────────────────────────

_FORWARD_REGISTRY: tuple[_Commitment, ...] = (
    _Commitment(
        anchor="shared **envelope** (schema_version + content-hash determinism",
        disposition="fr-backed",
        evidence="FR25 — `argus/store/envelope.py::class EnvelopeWriter`",
        reason="The content-hashed, schema-versioned envelope is FR25 and is on the live write "
        "path; redaction is FR28.",
    ),
    _Commitment(
        anchor="schemas **finding ① / severity.rubric ②",
        disposition="fr-backed",
        evidence="FR5 (coverage_ledger), FR13 (finding), FR15/FR17 (verdict), FR24 "
        "(decision_record — a library seam, see the reverse registry)",
        reason="Each named schema is carried by a numbered FR. That decision_record ④ is only a "
        "library seam is a DELIVERY fact recorded in the reverse registry, not a commitment gap.",
    ),
    _Commitment(
        anchor="`standards_refs[]` field + **CWE-required-on-security findings**",
        disposition="reclassified-v2",
        evidence="§Product Scope §Growth Features (V2) — the existing *standards mapping "
        "(CWE/ASVS/ISO 25010/SLSA)* item, which now records the merge",
        reason="Decided V2 on 2026-08-11 by Story 10.5 (DN-1). The 2026-08-03 case FOR shipping "
        "was explicitly *cheaper now than after the finding schema is frozen*; the schema is now "
        "frozen, content-hashed and shipped, so the premise expired. A persisted standards field "
        "widens the redaction surface (NFR-S1/S2) for an audience — Journey 4, attested use — the "
        "≥80% precision gate holds NOT CLEARED regardless.",
    ),
    _Commitment(
        anchor="**pure-function verdict gate**",
        disposition="fr-backed",
        evidence="FR15 — `argus/verdict/verdict_gate.py::def evaluate_verdict`",
        reason="Delivered and reachable from the CLI; the reverse registry proves it.",
    ),
    _Commitment(
        anchor="**referential-integrity lint**",
        disposition="fr-backed",
        evidence="FR26 — carried by a numbered FR, disposed `library-seam` in the reverse registry",
        reason="The COMMITMENT is FR-backed. Whether the FR is reachable is the reverse sweep's "
        "question, and there it is a library seam — the two registries deliberately answer "
        "different questions about the same item.",
    ),
    _Commitment(
        anchor="**human STOP/PROCEED escalation** with **R1 pattern-matched",
        disposition="fr-backed",
        evidence="FR23 — carried by a numbered FR, disposed `library-seam` in the reverse registry",
        reason="Same split as the integrity lint: the commitment is numbered; the delivery is a "
        "seam with no reachable call site, amended into FR23's own text on 2026-08-11.",
    ),
    _Commitment(
        anchor="crude **budget ceiling**",
        disposition="fr-backed",
        evidence="FR21/FR22 — `argus/cost/budget_governor.py`, `argus/cost/exhaustion.py`",
        reason="Ceiling, halt, skip, downgrade and honest report are all on the live path.",
    ),
    _Commitment(
        anchor="stack detection + partitioning",
        disposition="fr-backed",
        evidence="FR2/FR3 — `argus/intake/stack_detect.py`, `argus/index/partitioner.py`",
        reason="Both reachable from `argus.cli`; the ≤40 files / 15k LOC limits are "
        "`PartitionLimits`.",
    ),
    _Commitment(
        anchor="`work_manifest` **concept**",
        disposition="nfr-backed",
        evidence="NFR-S4 — the manifest read boundary; `argus/index/partitioner.py::class "
        "WorkManifest`",
        reason="RECORDED AS SPECIFIED, NOT AS A GAP (DN-5). The FR preamble binds *capabilities*; "
        "the permission boundary is an NFR and the architecture validates NFRs separately. The "
        "genuine hit here is the REACHABILITY of `read_in_scope`, which is already `DF-AUD-APAA-B` "
        "and is re-targeted by this story rather than re-filed.",
    ),
    _Commitment(
        anchor="**Python AST-grounded `audited_deep` claims**",
        disposition="fr-backed",
        evidence="FR6/FR7 — `argus/audit/grounding.py::def is_deep_claim_grounded`",
        reason="Delivered, and delivered wider than promised: Story 10.2 recorded that grounding "
        "ships for every language in `argus/shared/source_languages.py`, not Python alone.",
    ),
    _Commitment(
        anchor="heuristic **vacuous-test detector**",
        disposition="fr-backed",
        evidence="FR10 — `argus/detectors/vacuous_test.py::class VacuousTestDetector`",
        reason="On the live detector path, advisory-framed and evidence-carrying as promised.",
    ),
    _Commitment(
        anchor="**defect-cartridge framework**",
        disposition="fr-backed",
        evidence="FR20 — `tests/cartridges/_registry.py`, asserted in CI",
        reason="The commitment is FR-numbered. Its delivery mechanism is a CI-asserted corpus "
        "rather than a runtime module, which the reverse registry records as "
        "`delivered-differently` rather than pretending to a call site.",
    ),
    _Commitment(
        anchor="**lightweight Prosecutor**",
        disposition="fr-backed",
        evidence="FR19 — `argus/verdict/prosecutor.py::def prosecute`",
        reason="One pass at the final verdict gate, exactly as scoped.",
    ),
    _Commitment(
        anchor="dogfood run against **Minions itself**",
        disposition="delivered-differently",
        evidence="Story 8.5 — the self-audit of `argus/`, artifacts `minions-dogfood-*.md`",
        reason="The promised proof was a run against the Minions repository. What was delivered is "
        "a SELF-audit of `argus/`, which `deferred-work.md` itself calls *a materially weaker "
        "evidence class … not independent corroboration of anything*. Recorded, not re-opened: "
        "RS-1 fences this repository and a Minions run is out of scope for every Epic-10 story.",
    ),
    _Commitment(
        anchor="**Envelope determinism** is golden-tested",
        disposition="nfr-backed",
        evidence="NFR-D3/NFR-A1 — the determinism golden-tests over `store/canonical.py` and "
        "`store/envelope.py`",
        reason="A forward-compatibility invariant carried by binding NFRs, validated by the "
        "architecture's own NFR pass. Specified, not a gap (DN-5).",
    ),
    _Commitment(
        anchor="**Grounded-claim validation is a stack-agnostic interface**",
        disposition="constraint",
        evidence="Enforced by `argus/shared/source_languages.py` + "
        "`tests/test_multilanguage_audit.py`",
        reason="A forward-compatibility constraint on HOW grounding is built, not an added "
        "capability. Already amended 2026-08-10 by Story 10.2 to record that the additive "
        "implementations shipped in V1.",
    ),
    _Commitment(
        anchor="**Reserve `partition_id`**",
        disposition="constraint",
        evidence="Enforced by `argus/index/partitioner.py` — `partition_id` is always `\"root\"` "
        "in V1",
        reason="A reserved field for the V2 seam auditor. A constraint on the ledger shape, not a "
        "capability the operator can invoke.",
    ),
    _Commitment(
        anchor="**Frozen invariant declared now:** curated memory",
        disposition="constraint",
        evidence="Enforced by absence — no `argus/**` module reads a curated-memory source on the "
        "verdict path, and the verdict is a pure function of the ledger (FR15)",
        reason="A negative invariant: G3 ships V4 and never touches the verdict/decision path. "
        "Enforced by the pure-function verdict gate, which takes the ledger and nothing else.",
    ),
    _Commitment(
        anchor="**APAA specifies the cost/memory consumption-contracts**",
        disposition="specified-not-built",
        evidence="Specified in PRD §Dependencies / Cross-product Boundary — layers (a), (d), (e). "
        "The FILING of the handoff into the Minions tracker is **H0**",
        reason="The deliverable is a SPECIFICATION and the specification exists. The residual is "
        "the filing: `deferred-work.md` records H0's *ownership* closed on 2026-08-10b by the "
        "operator electing option (b), and in the same breath records that this **does not mean "
        "H1–H4 have been filed** and that assumption A5 remains UNSUPPORTED. This disposition is "
        "`specified-not-built` with the filing OPEN — never `done`. Pinned by `-38`.",
    ),
    _Commitment(
        anchor="format-validated, e.g. `^CWE-",
        disposition="reclassified-v2",
        evidence="§Product Scope §Growth Features (V2) — merged into the existing *standards "
        "mapping* item alongside the §Product Scope site",
        reason="THE SECOND, INDEPENDENTLY-BINDING V1 SITE, invisible to every planning document "
        "since 2026-08-03 because it lives in §Compliance & Regulatory in a different sentence "
        "shape. It carries a FORMAT commitment (`^CWE-\\d+$`) the §Product Scope site never made, "
        "so it is amended in its own right, not by reference. Amending only the first site would "
        "leave the PRD self-contradicting — the exact state this story exists to end.",
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# REVERSE REGISTRY — FR1..FR37, disposed 2026-08-11 by Story 10.5.
# `wired` is PROVEN by `-34`, never trusted: the named module must exist, the named anchor must be
# in it, and the module must be in the transitive import closure from `argus/cli.py`.
# `library-seam` is PROVEN too, symmetrically, by `-35`: if 12.1 or 12.3 wires a seam, this file
# goes RED until the disposition is updated. That red is the guard working.
# ─────────────────────────────────────────────────────────────────────────────

_REVERSE_REGISTRY: tuple[_Delivery, ...] = (
    _Delivery("FR1", "wired", "argus/intake/repo_loader.py", "def load_repo_at_commit(",
              "Headless submission at a pinned commit; reached from `cli.main` through the "
              "pipeline's intake step."),
    _Delivery("FR2", "wired", "argus/intake/stack_detect.py", "def detect_stack(",
              "Stack and toolchain probed with no operator configuration."),
    _Delivery("FR3", "wired", "argus/index/partitioner.py", "class PartitionLimits(",
              "Bounded audit units within the declared ≤40 files / 15k LOC limits."),
    _Delivery("FR4", "wired", "argus/ledger/critical_subsystems.py",
              "def identify_critical_subsystems(",
              "Detected by content and designatable by the operator; feeds the coverage gate."),
    _Delivery("FR5", "wired", "argus/ledger/coverage_ledger.py", "class CoverageLedger(",
              "Fixed-enum depth recorded for every file."),
    _Delivery("FR6", "wired", "argus/ledger/depth_semantics.py", "def classify_depth(",
              "Silence downgrades to `audited_shallow`; the classifier is on the live path."),
    _Delivery("FR7", "wired", "argus/audit/grounding.py", "def is_deep_claim_grounded(",
              "Claim validated against source structure; delivered for every language in "
              "`argus/shared/source_languages.py` (amended 2026-08-10, Story 10.2)."),
    _Delivery("FR8", "wired", "argus/verdict/verdict_gate.py", "def evaluate_verdict(",
              "`inferred` can never satisfy a gate — enforced inside the pure verdict function."),
    _Delivery("FR9", "wired", "argus/ledger/coverage_report.py", "def build_coverage_report(",
              "The operator reads exactly what was examined at each depth."),
    _Delivery("FR10", "wired", "argus/detectors/vacuous_test.py", "class VacuousTestDetector:",
              "Advisory findings carrying assertion-density and mock-ratio evidence."),
    _Delivery("FR11", "wired", "argus/detectors/secret_scan.py", "class SecretScanDetector:",
              "The ONE security-category finding producer in V1 — hence the Journey 4 note that "
              "names it as the exact scope of the missing standards reference."),
    _Delivery("FR12", "wired", "argus/detectors/orphan_code.py", "class OrphanCodeDetector:",
              "Tier B; orphan / dead code with no referencing requirement or caller, detected on "
              "the live detector path."),
    _Delivery("FR13", "wired", "argus/detectors/base.py", "def build_recording(",
              "A finding without a verifiable locator is rejected at construction."),
    _Delivery("FR14", "wired", "argus/detectors/tool_runner.py", "class ToolRunnerDetector:",
              "Tool failure becomes a finding, never a crash."),
    _Delivery("FR15", "wired", "argus/verdict/verdict_gate.py", "def evaluate_verdict(",
              "The verdict is a pure function of the ledger, 0 LLM tokens."),
    _Delivery("FR16", "wired", "argus/verdict/verdict_gate.py", "class DecisionRow(",
              "The amended decision table: findings before coverage, INSUFFICIENT_COVERAGE never a "
              "default NOT_READY."),
    _Delivery("FR17", "wired", "argus/verdict/negative_assurance.py",
              "def build_negative_assurance_verdict(",
              "Scope statement, materiality bar, disclaimer and point-in-time stamp on every "
              "verdict."),
    _Delivery("FR18", "wired", "argus/verdict/verdict_gate.py", "def exit_code_for_verdict(",
              "Deterministic exit code plus the machine-readable verdict artifact."),
    _Delivery("FR19", "wired", "argus/verdict/prosecutor.py", "def prosecute(",
              "Tier B; the adversarial pass runs at the final verdict gate."),
    _Delivery("FR20", "delivered-differently", "tests/cartridges/_registry.py",
              "class GoldenFinding:",
              "DELIVERED, but not by a runtime module: the cartridge corpus and its golden keys "
              "are a CI-asserted test surface (`tests/cartridges/`, `tests/"
              "test_cartridge_selfaudit.py`, `audit-ci.yml`), so there is no production call site "
              "to reach and none is owed. Recorded rather than dressed as `wired`."),
    _Delivery("FR21", "wired", "argus/cost/budget_governor.py", "def account_spend(",
              "The operator's ceiling is accounted against real spend."),
    _Delivery("FR22", "wired", "argus/cost/exhaustion.py", "def build_halt_report(",
              "Halt, mark the remainder skipped, downgrade, report honestly."),
    _Delivery("FR23", "library-seam", "argus/governance/escalation.py", "def escalation_fires(",
              "LOCKED `library-seam` (Story 10.5 DN-3), owner XAgent007 (Governance Owner), "
              "target_story NONE — unscheduled until Story 12.1 lifts the NFR-M1 gate. Built, "
              "typed and test-proven by `tests/test_hitl_escalation.py`, and reachable from "
              "NOTHING: `argus/governance/escalation.py` has exactly one importer in the package "
              "(`governance/decision_record.py`, itself unreachable). The reason has two halves "
              "and both are load-bearing: (a) every call site lands in `argus/pipeline.py`, which "
              "is 1331 lines against the NFR-M1 cap of 1200 and is byte-fenced to Story 12.1; and "
              "(b) the V1 default path is unattended CI (Journeys 3 and 5) with no human to answer "
              "a default-STOP gate, so a naive wiring would deadlock every automated audit. THE "
              "COST THIS INCURS, STATED RATHER THAN HIDDEN: the PRD cut-order marks FR23 "
              "non-negotiable core — only FR24 is [Tier B] — and "
              "`implementation-readiness-report-2026-08-03.md:365` already flagged FR23 as "
              "stranded in a slippable epic. A de-scope that hides its own cost is the defect this "
              "epic closes."),
    _Delivery("FR24", "library-seam", "argus/governance/decision_record.py",
              "class DecisionRecordWriter:",
              "NEVER FILED BEFORE 2026-08-11. Tier B, built and test-proven, with NO importer at "
              "all inside `argus/` — its only mention in the package is a prose reference in "
              "`store/integrity.py`. Follows FR23: the record has nothing to record until the gate "
              "it records for is invoked. Filed as `DF-10-5-A`; owner Governance Owner; "
              "target_story NONE — unscheduled, to be scheduled with FR23 once 12.1 lifts the "
              "`pipeline.py` gate."),
    _Delivery("FR25", "wired", "argus/store/envelope.py", "class EnvelopeWriter:",
              "Every artifact is wrapped content-hashed and schema-versioned on the live write "
              "path."),
    _Delivery("FR26", "library-seam", "argus/store/integrity.py",
              "def lint_referential_integrity(",
              "NEVER FILED BEFORE 2026-08-11. Tier B / NFR-A2, built and test-proven by "
              "`tests/test_store_integrity_lint.py`, but importable only from "
              "`dogfood/proof_run.py` and `evidence/bundle.py` — both themselves unreachable from "
              "`argus.cli`, so no audit an operator can run lints its own on-disk state. Filed as "
              "`DF-10-5-B`; owner Governance Owner; target_story NONE — unscheduled; the call site "
              "lands in `pipeline.py`, fenced to 12.1."),
    _Delivery("FR27", "wired", "argus/cache/memo_store.py", "class MemoStore:",
              "RE-DERIVED 2026-08-13 by Story 12.3, which WIRED the mechanism this entry had "
              "disposed as absent. `argus/pipeline.py` now consults `MemoStore` through a key "
              "derived by `argus.cache.key.derive_cache_key` around the deterministic "
              "detect/grade stage, so this module is in the import closure from `argus.cli` and "
              "a re-run over an unchanged closure is SERVED the recorded result. Proven, not "
              "asserted: `TC-ArgusAgent-CACHE-001-81` proves the warm run does not execute the "
              "stage, and `-82` poisons the slot and proves the served value reaches the verdict "
              "— byte-identity alone could not, since it is green with no cache at all. "
              "SUPERSEDED (not deleted, §3.4): this entry previously read `delivered-differently` "
              "on the grounds that *the memoization MECHANISM is unwired (`DF-AUD-APAA-A`) … "
              "Mechanism deferred to Story 12.3*, the property holding BY DETERMINISM rather "
              "than by cache. Both halves of that sentence are now false. That the registry "
              "could not SEE them become false is the hole `delivered_differently_refutations` "
              "closes (AC6.3); scoped honestly, the memoization covers the DETERMINISTIC stage "
              "only — the `--deep-audit` component is not served from the store (`DF-12-3-A`)."),
    _Delivery("FR28", "wired", "argus/detectors/secret_scan.py", "class SecretFindingEvidence(",
              "Excerpts are redacted before storage; no source or secret bytes reach ledger, "
              "evidence, logs or traces (NFR-S1)."),
    _Delivery("FR29", "library-seam", "argus/evidence/bundle.py", "def build_evidence_bundle(",
              "NEVER FILED BEFORE 2026-08-11, and the sharpest of the four: FR29's text reads "
              "*\"An operator CAN export an evidence bundle\"* and **no operator can** — there is "
              "no CLI subcommand and the only importer in the package is `dogfood/proof_run.py`. "
              "An FR whose text is operator-invocable while no operator can invoke it is amended, "
              "not silently re-read. Filed as `DF-10-5-C`; owner Governance Owner; target_story "
              "NONE — unscheduled; needs a CLI surface, which is 12.8's fence."),
    _Delivery("FR30", "wired", "argus/cli.py", "def build_parser(",
              "The accepted invocation surface, pinned in both directions by "
              "`tests/test_invocation_contract.py` (Story 10.3)."),
    _Delivery("FR31", "wired", "argus/cost/resume.py", "def build_resume_plan(",
              "Resume from on-disk `.argus/` state, reached through `pipeline.resume_audit`."),
    _Delivery("FR32", "wired", "argus/store/canonical.py", "def dumps_bytes(",
              "Byte-identical on-disk state on the sequential host: one serializer, no host "
              "dependence."),
    _Delivery("FR33", "wired", "argus/verdict/verdict_gate.py", "def order_findings(",
              "Verdict-blocking findings surface before non-blocking ones."),
    _Delivery("FR34", "not-built", "", "",
              "Specified for V1.5 and owned by Story 11.1 (mandatory self-disclosure of "
              "unvalidated precision). ⛔ Not amended by Story 10.5: the PRD already dates it and "
              "the plan already names its story."),
    _Delivery("FR35", "wired", "argus/mcp/server.py", "def serve(",
              "DELIVERED IN PART 2026-08-15 by Story 12.6, and the SCOPE OF `wired` IS STATED SO "
              "IT CANNOT BE OVER-READ — this is the disposition's load-bearing half here. What is "
              "delivered: a coding agent can invoke the audit and consume the verdict through a "
              "local agent-integration surface with no human relaying it. `pyproject.toml` ships "
              "`argus-mcp = argus.mcp.server:main` in the SAME distribution, this module's "
              "stdin→stdout loop speaks JSON-RPC 2.0 over stdio in both protocol eras, and its one "
              "`audit_repository` tool reaches `run_audit` through `argus.cli`'s OWN request "
              "projection, so the surface is reachable from a declared entry point and the verdict "
              "is the CLI's by construction (`TC-ArgusAgent-MCP-001-07`). Reachability is proven "
              "by `-34` above against the union closure, which from this date starts at the SET of "
              "`[project.scripts]` entry modules rather than at `argus.cli` alone. "
              "COMPLETED 2026-08-15 by Story 12.7, which delivered the residual this entry named "
              "one story earlier — and the residual is struck rather than deleted because it is "
              "the record of what `wired` did and did not cover at the time: ~~WHAT IS NOT "
              "DELIVERED, named so this entry does not over-claim the FR: the PACKAGED ASSISTANT "
              "COMMAND ASSETS — the `/audit …` command files and any registration mechanism — are "
              "**Story 12.7's**, the wheel still ships ZERO data assets, and installing this "
              "distribution registers no slash command in any assistant "
              "(`TC-ArgusAgent-DOCS-001-56` holds that gap open with its FORTHCOMING marker, which "
              "this story deliberately did NOT remove).~~ All three of those clauses are now FALSE. "
              "The command assets ship as DATA under `argus/assets/commands/**` (proven on a "
              "freshly built wheel AND sdist by `TC-ArgusAgent-ASSETS-001-12`, so "
              "`BuiltDistribution.data_assets` is non-empty), and the documented step that places "
              "them is a SECOND SUB-COMMAND on this same entry point — `argus install-commands`, "
              "whose logic is `argus/commands/installer.py::install_commands` and whose closed "
              "host registry is `argus/commands/hosts.py::HOST_REGISTRY`. The disposition stays "
              "`wired` and the module/anchor above are UNCHANGED deliberately: `wired` is proven by "
              "`-34` against the import closure from the `[project.scripts]` entry modules, the new "
              "surface adds NO entry point (that is DN-1's whole point), and it is reached from "
              "`argus.cli` — the module this registry already names — so re-pointing the anchor at "
              "the installer would trade a proven coordinate for an equivalent one and lose the "
              "12.6 half. The set that ships now equals the set every surface publishes, in both "
              "directions (`TC-ArgusAgent-ASSETS-001-06`), and `-56`'s delivered branch — which had "
              "never executed and returned after ONE assertion — was corrected to assert that "
              "equality rather than merely the marker's absence. Publishing anything at all is Story "
              "12.9's. ~~Specified for V1.5 and owned by Stories 12.6/12.7 (the local "
              "agent-integration surface; `argus/mcp/**` does not exist on this tree). ⛔ Not "
              "amended by Story 10.5.~~ (§3.4 struck, not deleted — superseded by the delivery "
              "above. ⚠️ That `not-built` entry named NO `seam_modules`, so `not_built_refutations` "
              "could not fire on it: this registry would have gone on asserting FR35 was not built, "
              "behind a fully green suite, exactly as it would have for FR36 before Story 12.2 "
              "added that direction. Nothing mechanical caught this one; it was caught because "
              "Story 12.6's own §0 re-measurement wrote the premise down and checked it.)"),
    _Delivery("FR36", "wired", "argus/audit/deep_pass.py", "def run_deep_pass(",
              "DELIVERED 2026-08-13 by Story 12.2. The opt-in LLM-backed deep pass is reachable "
              "from `argus.cli` through `--deep-audit` → the `deep` token → the gated call site in "
              "`argus/pipeline.py`, which imports this module FUNCTION-LOCALLY so the seam is in "
              "the STATIC closure (proven by `-34` here) while staying absent from `sys.modules` on "
              "a default run (NFR-S6, proven by TC-ArgusAgent-PIPELINE-001-10 with its positive "
              "control `-11`). ⚠️ SCOPE OF `wired`, STATED SO IT CANNOT BE OVER-READ: the pass is "
              "reachable, it dispatches, and it degrades honestly — but the SHIPPED "
              "`OpenLLMAdapter` never populates `LLMRecording.structured_output`, so a `delivered` "
              "deep read is currently reachable only through an INJECTED port (`DF-12-2-D`, "
              "measured by TC-ArgusAgent-AUDIT-001-73 with its positive control `-74`). `wired` "
              "here means the seam is reached and the safety properties hold on it, NOT that the "
              "capability completes end to end through the shipped adapter. ~~Specified for V1.5 "
              "and owned by Story 12.2; the seam modules exist "
              "and are unreachable from `argus.cli`.~~ (§3.4 struck, not deleted — superseded by "
              "the delivery above. That `not-built` disposition made NO reachability claim, so "
              "wiring FR36 would have left this registry asserting 'not built' about something "
              "built, with nothing red; AC7.2 added `not_built_refutations` and it fired on this "
              "very entry before the flip.)"),
    _Delivery("FR37", "not-built", "", "",
              "Specified for V1.5 and owned by Story 12.4 (every terminal outcome names its next "
              "action). ⛔ Not amended by Story 10.5."),
)


# ─────────────────────────────────────────────────────────────────────────────
# Pure parsing helpers. Every one of these takes text or a mapping and returns a value: the
# positive controls (`-36`, `-37`) drive them over SYNTHETIC inputs, so a control can never edit
# the real PRD or the real package (Story 10.5 E.3).
# ─────────────────────────────────────────────────────────────────────────────

_ATOM_SEPARATOR = "·"  # MIDDLE DOT — the PRD's inline scope-list separator

_V1_LINE_SHAPES: tuple[str, ...] = (
    "- **V1 Core:**",
    "- **V1 Differentiator:**",
    "- **Proof:**",
)

_V1_INLINE_SHAPE = re.compile(r"\*\*V1:\*\*(.*?)(?=\*\*V2:\*\*|$)")
_INVARIANTS_HEADING = "### V1 Design Invariants"
_FR_LINE = re.compile(r"^- \*\*FR(\d+):\*\*")


@dataclass(frozen=True)
class _Atom:
    line_no: int
    shape: str
    text: str


def split_atoms(raw: str) -> tuple[str, ...]:
    """Split an inline `·`-separated scope list into atoms WITHOUT breaking inside parentheses.

    The PRD writes ``... (minimal assignment = file-list = the auditor's permission boundary; full
    schema → V3) · ...``. A naive ``str.split`` on the separator is safe today only by luck; a
    single parenthesised aside containing one would silently manufacture two half-atoms, and a
    half-atom matches no registry anchor, so the guard would fire on a claim nobody changed. `-36`
    pins this with a synthetic case rather than trusting the current text.
    """
    atoms: list[str] = []
    buffer: list[str] = []
    depth = 0
    for char in raw:
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        if char == _ATOM_SEPARATOR and depth == 0:
            atoms.append("".join(buffer))
            buffer = []
        else:
            buffer.append(char)
    atoms.append("".join(buffer))
    return tuple(a.strip(" \t.") for a in atoms if a.strip(" \t."))


def v1_claim_atoms(document: str) -> tuple[_Atom, ...]:
    """Derive the V1-commitment population by CLAIM SHAPE over the WHOLE document.

    NOT by section heading, and this is the point of the story. Measured 2026-08-11: the
    ``standards_refs[]`` commitment binds V1 at three coordinates, one of which sits in §Compliance
    & Regulatory in the ``**V1:**`` shape. Every planning document since 2026-08-03 saw only the
    §Product Scope site, because that is the heading everyone thought to sweep. The shape closes
    what the heading does not.
    """
    atoms: list[_Atom] = []
    inside_invariants = False
    for line_no, line in enumerate(document.split("\n"), start=1):
        if line.startswith(_INVARIANTS_HEADING):
            inside_invariants = True
            continue
        if inside_invariants:
            if line.startswith("#"):
                inside_invariants = False
            elif line.startswith("- "):
                for atom in split_atoms(line[2:]):
                    atoms.append(_Atom(line_no, _INVARIANTS_HEADING, atom))
                continue
        matched_block_shape = False
        for shape in _V1_LINE_SHAPES:
            if line.startswith(shape):
                matched_block_shape = True
                for atom in split_atoms(line[len(shape):]):
                    atoms.append(_Atom(line_no, shape, atom))
        if matched_block_shape:
            continue
        inline = _V1_INLINE_SHAPE.search(line)
        if inline is not None:
            for atom in split_atoms(inline.group(1)):
                atoms.append(_Atom(line_no, "**V1:**", atom))
    return tuple(atoms)


def day_one_lines_covered(document: str, atoms: tuple[_Atom, ...]) -> tuple[int, ...]:
    """Return the line numbers carrying *day-one* that produced NO atom.

    ``day-one`` is an AC3.1 claim shape in its own right. Today every occurrence sits inside a
    ``**V1 Core:**`` atom, so it adds nothing to the population — but a future *day-one* commitment
    written outside the enumerated shapes would be invisible, which is exactly how ``prd.md:309``
    stayed invisible for eight days. This reports the escape rather than silently allowing it.
    """
    produced = {atom.line_no for atom in atoms}
    return tuple(
        line_no
        for line_no, line in enumerate(document.split("\n"), start=1)
        if "day-one" in line and line_no not in produced
    )


def functional_requirement_ids(document: str) -> tuple[str, ...]:
    """Enumerate FR ids MECHANICALLY from §Functional Requirements — never hand-typed.

    The FRs are deliberately NOT in numeric order (FR36/FR37 sit inside the Coverage and Verdict
    clusters, FR33–35 among the later ones). A parser handles that; a hand list has already been
    wrong four times in this epic.
    """
    lines = document.split("\n")
    start = None
    for index, line in enumerate(lines):
        if line.startswith("## Functional Requirements"):
            start = index
            break
    if start is None:
        return ()
    ids: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        match = _FR_LINE.match(line)
        if match is not None:
            ids.append(f"FR{match.group(1)}")
    return tuple(ids)


def functional_requirement_text(document: str) -> dict[str, str]:
    """Map each FR id to its own line, so an amendment on that line can be pinned."""
    out: dict[str, str] = {}
    for line in document.split("\n"):
        match = _FR_LINE.match(line)
        if match is not None:
            out[f"FR{match.group(1)}"] = line
    return out


def _module_name(path: Path, package_root: Path) -> str:
    relative = path.relative_to(package_root.parent).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_import_targets(
    module: str, node: ast.Import | ast.ImportFrom, *, is_package: bool, top: str
) -> set[str]:
    targets: set[str] = set()
    if isinstance(node, ast.Import):
        targets.update(alias.name for alias in node.names)
    else:
        if node.level:
            own = module.split(".")
            package = own if is_package else own[:-1]
            climb = node.level - 1
            if climb:
                package = package[:-climb] if climb <= len(package) else []
            prefix = ".".join(package + ([node.module] if node.module else []))
        else:
            prefix = node.module or ""
        if prefix:
            targets.add(prefix)
            targets.update(f"{prefix}.{alias.name}" for alias in node.names)
    return {t for t in targets if t.split(".")[0] == top}


def build_import_graph(package_root: Path) -> dict[str, frozenset[str]]:
    """Build the intra-package import graph STATICALLY, reading source as text (DN-6).

    ``ast`` only — the package is never imported, so lazy imports cannot hide an edge behind a
    runtime branch, an absent optional extra cannot change the answer between CI legs, and no
    ``argus`` line executes, so the coverage figure the ledger cites cannot move.

    An import of ``argus.x.y`` also loads the packages ``argus.x`` and ``argus``, so the ancestor
    edges are recorded too. Omitting them reports every ``__init__.py`` as unreachable and inflates
    the seam count — an over-claim, in a guard whose entire purpose is to stop over-claims.
    """
    modules: dict[str, Path] = {}
    for path in sorted(package_root.rglob("*.py")):
        modules[_module_name(path, package_root)] = path
    top = package_root.name
    graph: dict[str, set[str]] = {name: set() for name in modules}
    for name, path in modules.items():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        is_package = path.name == "__init__.py"
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            for target in _resolve_import_targets(
                name, node, is_package=is_package, top=top
            ):
                resolved = target
                while resolved and resolved not in modules:
                    resolved = resolved.rsplit(".", 1)[0] if "." in resolved else ""
                if not resolved or resolved == name:
                    continue
                graph[name].add(resolved)
                ancestor = resolved
                while "." in ancestor:
                    ancestor = ancestor.rsplit(".", 1)[0]
                    if ancestor in modules and ancestor != name:
                        graph[name].add(ancestor)
    return {name: frozenset(edges) for name, edges in graph.items()}


def reachable_from(graph: dict[str, frozenset[str]], entry: str) -> frozenset[str]:
    """Transitive import closure from a single entry point."""
    if entry not in graph:
        return frozenset()
    seen = {entry}
    stack = [entry]
    while stack:
        current = stack.pop()
        for nxt in graph.get(current, frozenset()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return frozenset(seen)


def reachable_from_any(
    graph: dict[str, frozenset[str]], entries: tuple[str, ...]
) -> frozenset[str]:
    """The UNION of the closures from every entry point (Story 12.6).

    Delivery means *a production call site reaches it*, and from 2026-08-15 this
    distribution ships two entry points rather than one. Taking the union is the only
    reading that keeps the rule's meaning: a module reached from the second entry point is
    reached in production, so a `library-seam` disposition over it would be false — and a
    module reached from neither is a seam however many entry points exist.

    Deliberately the UNION and not the intersection. An intersection would refute a `wired`
    claim for every module the CLI reaches and the adapter does not, which is most of the
    product, and would manufacture exactly the false accusations this file exists to
    prevent.
    """
    seen: set[str] = set()
    for entry in entries:
        seen |= reachable_from(graph, entry)
    return frozenset(seen)


_STRIKE_SPAN = re.compile(r"~~(.+?)~~", re.S)


def struck_spans(text: str) -> tuple[str, ...]:
    """Return the contents of every PAIRED ``~~ … ~~`` strike span in ``text``.

    §3.4 evidence immutability says a superseded commitment is **struck, not deleted**. The obvious
    assertion — *does the atom contain* ``~~`` — is not good enough, and this guard's author found
    that out the honest way: a live-bite check that deleted the OPENING ``~~`` from the amended
    §Compliance site left the closing marker behind, so ``"~~" in text`` stayed true and the guard
    stayed green over a half-broken strike. That is `-40`'s own version of AI-E3-1 (a keystone test
    green over its own keystone bug), caught before it shipped rather than after.

    So the assertion is not *"a strike marker exists"* but *"the commitment itself is inside a
    closed strike span"*: the registry anchor must fall within a matched pair. An unbalanced marker
    yields no span at all and turns the check red.
    """
    return tuple(match.group(1) for match in _STRIKE_SPAN.finditer(text))


def reachability_refutations(
    entries: tuple[tuple[str, str, str], ...], reachable: frozenset[str]
) -> tuple[str, ...]:
    """Refute delivery dispositions against a reachability set — BOTH directions.

    ``entries`` are ``(fr, disposition, module_name)``. A pure function so `-37` can drive it over a
    synthetic graph rather than the real package.

    * ``wired`` over an unreachable module is refuted — the sentence *"maps to a module"* is not
      delivery, and this is the mechanism that retires it.
    * ``library-seam`` over a REACHABLE module is refuted too. When Story 12.1 or 12.3 wires a seam,
      this guard goes red until the disposition is updated. That red is the guard working: a
      disposition that outlives the fact it disposed is the same drift, pointing the other way.

    ``delivered-differently`` still makes no reachability claim and is never refuted here; a walk
    that assigned it one would manufacture the false accusations this product exists to prevent
    (see FR27 in the reverse registry).
    """
    problems: list[str] = []
    for fr, disposition, module_name in entries:
        if disposition == "wired" and module_name not in reachable:
            problems.append(
                f"{fr}: disposed 'wired' but {module_name} is NOT in the import closure from "
                f"{_ENTRY_POINT_LABEL} — a wired claim is proven, never asserted"
            )
        if disposition == "library-seam" and module_name in reachable:
            problems.append(
                f"{fr}: disposed 'library-seam' but {module_name} IS reachable from "
                f"{_ENTRY_POINT_LABEL} — the seam was wired; update the disposition to 'wired'"
            )
    return tuple(problems)


def not_built_refutations(
    entries: tuple[tuple[str, tuple[str, ...]], ...], reachable: frozenset[str]
) -> tuple[str, ...]:
    """Refute a ``not-built`` disposition whose DEDICATED seam has become reachable (AC7.2).

    ``entries`` are ``(fr, seam_module_names)`` for ``not-built`` dispositions only. Pure, so
    `-37b` drives it over a synthetic graph exactly as the two directions above are driven.

    THE HOLE THIS CLOSES. ``not-built`` makes no reachability claim — correctly, since a module's
    mere existence proves nothing about delivery. But that left it unrefutable in the one direction
    that matters: when the FR IS delivered nothing goes red, and the registry keeps asserting *"not
    built"* about something built. Story 12.2 is the worked example — it wires FR36, and without
    this direction the registry would have said FR36 was not built forever, with a green suite.

    Deliberately NARROW: it fires only on modules the entry names as that FR's DEDICATED seam, so a
    shared module going reachable cannot trigger it. An FR delivered inside an already-reachable
    shared module names no seam and is untouched — not a licence to re-litigate any disposition.
    """
    problems: list[str] = []
    for fr, seam_modules in entries:
        live = sorted(name for name in seam_modules if name in reachable)
        if live:
            problems.append(
                f"{fr}: disposed 'not-built' but its dedicated seam {live} IS reachable from "
                f"{_ENTRY_POINT_LABEL} — the FR is being delivered. A 'not-built' disposition that "
                "outlives the delivery it disposed is a committed guard asserting the opposite "
                "of the truth; flip it to 'wired' and name the module and anchor."
            )
    return tuple(problems)


# Phrases by which a disposition's REASON makes a claim about REACHABILITY. Lower-cased
# substrings, matched against the reason text itself, so the claim is read off the committed
# sentence rather than inferred from the label. Story 12.3 measured these against the live
# registry: FR27's reason carried "is unwired" AND "deferred to Story 12.3", both of which its
# own wiring falsified.
_UNWIREDNESS_CLAIM_MARKERS: tuple[str, ...] = (
    "is unwired",
    "mechanism is unwired",
    "not wired",
    "no production call site",
    "no production caller",
    "deferred to story",
)


def delivered_differently_refutations(
    entries: tuple[tuple[str, str, str, str], ...], reachable: frozenset[str]
) -> tuple[str, ...]:
    """Refute a `delivered-differently` disposition whose REASON claims something now false.

    ``entries`` are ``(fr, disposition, module_name, reason)``. Pure, so `-37c` can drive it over
    a synthetic graph exactly as `-37`/`-37b` drive the other three directions.

    THE HOLE THIS CLOSES, measured by Story 12.3 by EXECUTING this module's own code rather than
    reading it. ``delivered-differently`` makes no reachability claim, and
    ``reachability_refutations`` therefore never refutes it — correctly, because a walk that
    assigned it one would manufacture the false accusations this product exists to prevent. But
    that left a gap in the one direction that matters: the LABEL makes no claim while the REASON
    freely does. FR27's reason asserted *"the memoization MECHANISM is unwired … Mechanism
    deferred to Story 12.3"*, and when Story 12.3 wired it, **nothing in this repository was able
    to notice that sentence had become false**. The registry would have gone on asserting it
    forever, behind a fully green suite — a disposition outliving the fact it disposed, arriving
    through the one door `-37`/`-37b` left open.

    Story 12.2's ``not_built_refutations`` is the precedent and this is deliberately just as
    NARROW. It fires only when BOTH hold: the reason makes an explicit unwiredness/deferral claim,
    AND the module that reason is about is reachable. A `delivered-differently` entry that claims
    only *"this holds by another mechanism"* — the disposition's legitimate use — is untouched.
    The remedy when it fires is never to soften the reason: it is to re-derive the disposition,
    which for a seam that has just been wired is ``wired``.
    """
    problems: list[str] = []
    for fr, disposition, module_name, reason in entries:
        if disposition != "delivered-differently" or module_name not in reachable:
            continue
        claims = sorted(
            marker for marker in _UNWIREDNESS_CLAIM_MARKERS if marker in reason.lower()
        )
        if claims:
            problems.append(
                f"{fr}: disposed 'delivered-differently', and its REASON still claims {claims} — "
                f"but {module_name} IS reachable from {_ENTRY_POINT_LABEL}, so that claim is FALSE. "
                "The label makes no reachability claim; the reason did, and it outlived the fact "
                "it disposed. Re-derive the disposition (a seam that has been wired is 'wired') "
                "rather than editing the sentence until it stops matching."
            )
    return tuple(problems)


def closure_errors(
    atoms: tuple[_Atom, ...], anchors: tuple[str, ...]
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Match atoms to registry anchors in BOTH directions.

    Returns ``(unclassified_atoms, dead_anchors, ambiguous_anchors)``:

    * an atom no anchor matches is **unclassified** — a V1 commitment nobody disposed;
    * an anchor no atom matches is **dead** — a disposition that outlived the claim it disposed,
      which is how a sweep log becomes a second, stale source of truth;
    * an anchor matching more than one atom is **ambiguous** — it cannot evidence which claim it
      disposed, so it is a failure rather than a convenience.
    """
    matched: set[int] = set()
    dead: list[str] = []
    ambiguous: list[str] = []
    for anchor in anchors:
        hits = [i for i, atom in enumerate(atoms) if anchor in atom.text]
        if not hits:
            dead.append(anchor)
        elif len(hits) > 1:
            ambiguous.append(anchor)
            matched.update(hits)
        else:
            matched.update(hits)
    unclassified = tuple(
        f"prd.md:{atom.line_no} [{atom.shape}] {atom.text}"
        for i, atom in enumerate(atoms)
        if i not in matched
    )
    return unclassified, tuple(dead), tuple(ambiguous)


def _read(path: Path) -> str:
    assert path.exists(), (
        f"{_GUARD_FILE}: required artifact {path} is missing. This guard resolves the artifact "
        f"tree from __file__; if the tree moved, fix the resolution here rather than deleting the "
        f"assertion — a guard that cannot find its corpus must be RED, not silently green."
    )
    return path.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# -30 / -31 — forward closure: every V1 commitment carries exactly one disposition
# ─────────────────────────────────────────────────────────────────────────────


def test_every_v1_commitment_carries_exactly_one_disposition() -> None:
    """TC-ArgusAgent-DOCS-001-30 — forward closure over the WHOLE PRD, in both directions."""
    atoms = v1_claim_atoms(_read(_PRD))
    anchors = tuple(entry.anchor for entry in _FORWARD_REGISTRY)
    unclassified, dead, ambiguous = closure_errors(atoms, anchors)

    assert not unclassified, (
        "A V1 commitment in the PRD carries NO disposition. Every V1 claim must be delivered, "
        "carried by an FR/NFR, recorded as a constraint, or explicitly reclassified with a date — "
        "'it is in the spec and nobody said anything' is the defect Epic 10 closes.\n"
        "Add a _Commitment to _FORWARD_REGISTRY in "
        f"{_GUARD_FILE} for each of:\n  " + "\n  ".join(unclassified)
    )
    assert not dead, (
        "A disposition in _FORWARD_REGISTRY matches no claim in the PRD, so it has outlived the "
        "claim it disposed. Either the claim was reworded (update the anchor) or it was removed "
        "(remove the entry). A sweep log that drifts from the document is a second source of "
        f"truth, which is what DN-8 forbids.\nDead anchors in {_GUARD_FILE}:\n  "
        + "\n  ".join(dead)
    )
    assert not ambiguous, (
        "A disposition anchor matches MORE THAN ONE claim, so it cannot evidence which one it "
        "disposed. Lengthen the anchor until it is unique.\nAmbiguous anchors:\n  "
        + "\n  ".join(ambiguous)
    )

    escapes = day_one_lines_covered(_read(_PRD), atoms)
    assert not escapes, (
        "A line carrying the 'day-one' V1 claim shape produced no atom, so a V1 commitment is "
        "written outside every enumerated shape and is invisible to this closure — exactly how "
        "prd.md:309 stayed invisible from 2026-08-03 to 2026-08-11. Extend v1_claim_atoms() to "
        f"cover the shape at prd.md line(s): {escapes}"
    )


def test_every_forward_disposition_is_vocabulary_dated_and_reasoned() -> None:
    """TC-ArgusAgent-DOCS-001-31 — a disposition with no reason is not a disposition."""
    for entry in _FORWARD_REGISTRY:
        assert entry.disposition in _FORWARD_VOCABULARY, (
            f"'{entry.disposition}' is not in the CLOSED forward vocabulary "
            f"{sorted(_FORWARD_VOCABULARY)}. A hit that fits none of them is a HALT for the dev, "
            "not a new label invented mid-sweep: an open vocabulary is how 'maps to a module' "
            "became a certification of coverage."
        )
        assert entry.evidence.strip(), (
            f"{entry.anchor!r}: disposition '{entry.disposition}' names no evidence. Name the "
            "FR, NFR, module or story that carries it — BY ANCHOR, never by line number."
        )
        assert len(entry.reason.strip()) >= 40, (
            f"{entry.anchor!r}: the reason is missing or too thin to be a reason. State in one "
            "line WHY this disposition, or the sweep has produced a label rather than a decision."
        )
        assert not re.search(r":\d{2,4}\b", entry.evidence), (
            f"{entry.anchor!r}: evidence cites a LINE NUMBER. Every coordinate in this epic has "
            "drifted at least once (the epic AC itself still cites PRD L168 for a claim now at "
            "L187). Cite by anchor text."
        )


# ─────────────────────────────────────────────────────────────────────────────
# -32 / -33 / -34 / -35 — reverse closure and the mechanical refutation of `wired`
# ─────────────────────────────────────────────────────────────────────────────


def test_every_functional_requirement_carries_a_delivery_disposition() -> None:
    """TC-ArgusAgent-DOCS-001-32 — reverse closure over FR1..FR37, in both directions."""
    prd = _read(_PRD)
    fr_ids = functional_requirement_ids(prd)
    registered = tuple(entry.fr for entry in _REVERSE_REGISTRY)

    duplicates = sorted({fr for fr in registered if registered.count(fr) > 1})
    assert not duplicates, (
        f"{duplicates} carry more than one delivery disposition. Exactly one, or the registry "
        "cannot answer the question it exists to answer."
    )
    missing = [fr for fr in fr_ids if fr not in registered]
    assert not missing, (
        f"{missing} exist in the PRD §Functional Requirements and carry NO delivery disposition. "
        f"Add a _Delivery to _REVERSE_REGISTRY in {_GUARD_FILE}: name the module and an anchor "
        "inside it for 'wired' (which -34 then PROVES against the import closure), or name the "
        "owning story for 'not-built'. Adding FR38 to the PRD is meant to cost this edit."
    )
    stale = [fr for fr in registered if fr not in fr_ids]
    assert not stale, (
        f"{stale} carry a delivery disposition but do not exist in the PRD §Functional "
        "Requirements. Either the FR was renumbered or the section moved — a disposition over a "
        "requirement the contract does not contain is exactly the drift this guard exists to stop."
    )


def test_every_delivery_disposition_is_vocabulary_and_names_where_the_gap_goes() -> None:
    """TC-ArgusAgent-DOCS-001-33 — a gap disposition must name a target, or it is a shrug."""
    for entry in _REVERSE_REGISTRY:
        assert entry.disposition in _REVERSE_VOCABULARY, (
            f"{entry.fr}: '{entry.disposition}' is not in the CLOSED reverse vocabulary "
            f"{sorted(_REVERSE_VOCABULARY)} (DN-4)."
        )
        assert len(entry.reason.strip()) >= 40, (
            f"{entry.fr}: the reason is missing or too thin. Every disposition is dated by this "
            "file's header and reasoned in one line; without the reason it is a label."
        )
        if entry.disposition in _MUST_NAME_A_FORWARD_TARGET:
            assert re.search(r"(Stor(y|ies) \d|target_story|owner)", entry.reason), (
                f"{entry.fr}: disposition '{entry.disposition}' admits a gap but names no owner "
                "and no forward target. AI-E9-8: never target_story NONE without a named human. "
                "An unowned gap is how DF-AUD-APAA-A and -B ended up pointing at an epic that was "
                "already done."
            )
        if entry.disposition == "not-built":
            assert not entry.module, (
                f"{entry.fr}: 'not-built' names a module. If a module exists, the honest "
                "dispositions are 'library-seam' or 'delivered-differently'."
            )
        else:
            assert entry.module and entry.anchor, (
                f"{entry.fr}: disposition '{entry.disposition}' must name a module and an anchor "
                "inside it, so the claim can be checked rather than believed."
            )


def test_a_wired_disposition_is_proven_against_the_import_closure() -> None:
    """TC-ArgusAgent-DOCS-001-34 — `wired` is PROVEN, never asserted. Retires 'maps to a module'."""
    graph = build_import_graph(_PACKAGE_ROOT)
    reachable = reachable_from_any(graph, _ENTRY_POINTS)

    for entry in _REVERSE_REGISTRY:
        if not entry.module:
            continue
        path = _REPO_ROOT / entry.module
        assert path.exists(), (
            f"{entry.fr}: the disposition names {entry.module}, which does not exist. A "
            "disposition over a phantom module is worse than no disposition."
        )
        assert entry.anchor in path.read_text(encoding="utf-8"), (
            f"{entry.fr}: anchor {entry.anchor!r} is not in {entry.module}. The anchor is the "
            "evidence; if the symbol was renamed, re-derive the disposition rather than editing "
            "the anchor to whatever is there now."
        )

    entries = tuple(
        (
            entry.fr,
            entry.disposition,
            _module_name(_REPO_ROOT / entry.module, _PACKAGE_ROOT),
        )
        for entry in _REVERSE_REGISTRY
        if entry.module.startswith("argus/")
    )
    problems = reachability_refutations(entries, reachable)
    assert not problems, (
        "A delivery disposition is REFUTED by the static import graph. `architecture.md`'s "
        "'No FR is unsupported' certifies module PLACEMENT; this asserts REACHABILITY, which is "
        "what delivery means.\n  " + "\n  ".join(problems)
    )

    # Story 12.2 / AC7.2 — the third direction. A `not-built` disposition whose DEDICATED seam
    # has become reachable is refuted, so wiring an FR can no longer leave the registry
    # asserting that it was never built.
    not_built = tuple(
        (entry.fr, entry.seam_modules)
        for entry in _REVERSE_REGISTRY
        if entry.disposition == "not-built"
    )
    stale = not_built_refutations(not_built, reachable)
    assert not stale, (
        "A 'not-built' disposition OUTLIVED THE DELIVERY IT DISPOSED. This is the direction that "
        "did not exist before Story 12.2 and is exactly the rot it was added to catch.\n  "
        + "\n  ".join(stale)
    )

    # Story 12.3 / AC6.3 — the FOURTH direction. A `delivered-differently` disposition whose
    # REASON claims the mechanism is unwired or deferred, over a module that IS reachable. The
    # label makes no reachability claim, so nothing here could see such a reason go false —
    # measured on 12.3's own subject: FR27 said "the memoization MECHANISM is unwired … deferred
    # to Story 12.3", and wiring it turned nothing red anywhere in this repository.
    differently = tuple(
        (
            entry.fr,
            entry.disposition,
            _module_name(_REPO_ROOT / entry.module, _PACKAGE_ROOT),
            entry.reason,
        )
        for entry in _REVERSE_REGISTRY
        if entry.module.startswith("argus/")
    )
    rotted = delivered_differently_refutations(differently, reachable)
    assert not rotted, (
        "A 'delivered-differently' REASON asserts something the import graph now falsifies. The "
        "disposition label was never the problem — the sentence under it was.\n  "
        + "\n  ".join(rotted)
    )


def test_every_library_seam_is_amended_in_the_prd_and_filed_in_the_ledger() -> None:
    """TC-ArgusAgent-DOCS-001-35 — a seam the FR text still reads as delivered is the defect."""
    fr_text = functional_requirement_text(_read(_PRD))
    ledger = _read(_LEDGER)
    for entry in _REVERSE_REGISTRY:
        if entry.disposition != "library-seam":
            continue
        line = fr_text.get(entry.fr, "")
        spans = struck_spans(line)
        # A real FR amendment strikes the whole superseded sentence, not a word. The measured
        # amendments on this tree strike 100+ characters each; 60 is the floor below which the
        # "strike" is decoration rather than a correction.
        assert spans and max(len(span) for span in spans) >= 60, (
            f"{entry.fr} is disposed 'library-seam' — built, test-proven, and reachable from no "
            "production call site — but its PRD text is unamended, so the binding contract still "
            "reads as if an operator can invoke it. Amend it struck-not-deleted (§3.4 evidence "
            "immutability), dated and attributed, following the FR7 (10.2) and FR30 (10.3) "
            "precedent: FRxx is the binding contract, so it is corrected to what the code does."
        )
        assert _DISPOSITION_DATE in line and _DISPOSITION_STORY in line, (
            f"{entry.fr}'s amendment carries no {_DISPOSITION_DATE} / {_DISPOSITION_STORY} "
            "attribution. An undated correction cannot be distinguished from the original claim."
        )
        assert entry.fr in ledger, (
            f"{entry.fr} is a library seam and is not named anywhere in deferred-work.md. Every "
            "seam carries a dated reason, a named owner and a ledger entry — FR24, FR26 and FR29 "
            "went five weeks unfiled precisely because nobody swept the class."
        )


# ─────────────────────────────────────────────────────────────────────────────
# -36 / -37 — positive controls, both directions, over SYNTHETIC inputs only
# ─────────────────────────────────────────────────────────────────────────────


_SYNTHETIC_DOCUMENT = "\n".join(
    (
        "## Some Section",
        "- **V1 Core:** alpha capability · beta capability (with an aside · inline)",
        "- **Standards anchoring.** **V1:** gamma capability **V2:** delta later",
    )
)


def test_forward_closure_fires_on_an_unclassified_claim_and_not_on_a_classified_one() -> None:
    """TC-ArgusAgent-DOCS-001-36 — forward positive control, both directions, synthetic only."""
    atoms = v1_claim_atoms(_SYNTHETIC_DOCUMENT)
    texts = [atom.text for atom in atoms]

    assert texts == [
        "alpha capability",
        "beta capability (with an aside · inline)",
        "gamma capability",
    ], (
        "The atomizer changed shape. A parenthesised separator must NOT split an atom, and the "
        f"inline **V1:** shape must be seen wherever it occurs. Got: {texts}"
    )

    full = ("alpha capability", "beta capability", "gamma capability")
    unclassified, dead, ambiguous = closure_errors(atoms, full)
    assert not unclassified and not dead and not ambiguous, (
        "A fully-classified synthetic document must NOT fire. If it does, the guard cries wolf and "
        f"the third person to hit it deletes it. {unclassified} {dead} {ambiguous}"
    )

    partial = ("alpha capability", "beta capability")
    unclassified, dead, _ = closure_errors(atoms, partial)
    assert len(unclassified) == 1 and "gamma" in unclassified[0], (
        "An UNCLASSIFIED V1 claim must fire. This is the whole guard; if this control does not "
        "fire, nothing below it means anything."
    )
    assert not dead

    outlived = ("alpha capability", "beta capability", "gamma capability", "epsilon capability")
    unclassified, dead, _ = closure_errors(atoms, outlived)
    assert dead == ("epsilon capability",) and not unclassified, (
        "A disposition matching no claim must fire, so a sweep log cannot outlive the document."
    )

    _, _, ambiguous = closure_errors(atoms, ("capability",))
    assert ambiguous == ("capability",), (
        "An anchor matching several atoms must fire: it cannot evidence which claim it disposed."
    )

    # The strike check, pinned as a control because the naive form of it was WRONG here first.
    # A live-bite run that deleted only the OPENING `~~` from an amended site left `"~~" in text`
    # true and the guard green over a half-struck commitment. These four cases are that bug's
    # regression test.
    assert struck_spans("keep ~~gone~~ keep") == ("gone",)
    assert struck_spans("keep ~~gone~~ and ~~also gone~~") == ("gone", "also gone")
    assert struck_spans("keep gone~~ keep") == (), (
        "An UNBALANCED strike marker must yield no span. This is the exact half-broken state that "
        "slipped past the first version of -40."
    )
    assert struck_spans("nothing struck here") == ()


def test_reachability_refutation_fires_in_both_directions_on_a_synthetic_graph() -> None:
    """TC-ArgusAgent-DOCS-001-37 — reverse positive control over a synthetic graph."""
    graph: dict[str, frozenset[str]] = {
        "pkg.cli": frozenset({"pkg.live"}),
        "pkg.live": frozenset(),
        "pkg.seam": frozenset(),
    }
    reachable = reachable_from(graph, "pkg.cli")
    assert reachable == frozenset({"pkg.cli", "pkg.live"}), reachable

    honest = (("FRa", "wired", "pkg.live"), ("FRb", "library-seam", "pkg.seam"))
    assert reachability_refutations(honest, reachable) == (), (
        "A truthful pair of dispositions must NOT fire."
    )

    false_wired = (("FRa", "wired", "pkg.seam"),)
    problems = reachability_refutations(false_wired, reachable)
    assert len(problems) == 1 and "NOT in the import closure" in problems[0], (
        "A 'wired' claim over an unreachable module must be REFUTED. This is the assertion that "
        "retires architecture.md's 'No FR is unsupported' over a module-placement table."
    )

    stale_seam = (("FRb", "library-seam", "pkg.live"),)
    problems = reachability_refutations(stale_seam, reachable)
    assert len(problems) == 1 and "IS reachable" in problems[0], (
        "A 'library-seam' disposition over a module that became reachable must fire, so wiring a "
        "seam in 12.1/12.3 turns this red until the disposition is updated."
    )

    silent = (
        ("FRc", "delivered-differently", "pkg.seam"),
        ("FRd", "not-built", "pkg.absent"),
    )
    assert reachability_refutations(silent, reachable) == (), (
        "Neither 'delivered-differently' nor 'not-built' makes a reachability claim, and a walk "
        "that assigned them one would manufacture a false accusation (FR27 is the worked example)."
    )


def test_a_not_built_disposition_is_refuted_once_its_seam_becomes_reachable() -> None:
    """TC-ArgusAgent-DOCS-001-37b — AC7.2 positive control, over the SAME synthetic graph.

    Story 12.2, third direction, driven exactly as `-37` drives the first two: a refutation nobody
    has watched fire is a refutation nobody knows is reachable.

    THE HOLE IT CLOSES, verified by running the guard's own code on `2bea92f`:
    ``reachability_refutations`` refutes `wired`-over-unreachable and `library-seam`-over-reachable
    and NOTHING else, while `-34` only passed it entries whose `module` began with `argus/` — and
    `-33` forbids a `not-built` entry from naming a module at all. So a `not-built` disposition was
    unrefutable by ANY path, and wiring the FR it disposed produced no red anywhere.

    Both directions are asserted: a guard that only ever rejects cannot be shown reachable, and one
    that only ever accepts cannot be shown to bite.
    """
    graph: dict[str, frozenset[str]] = {
        "pkg.cli": frozenset({"pkg.live"}),
        "pkg.live": frozenset(),
        "pkg.seam": frozenset(),
    }
    reachable = reachable_from(graph, "pkg.cli")

    # HONEST: the FR is genuinely not built — its dedicated seam is unreachable, or it names
    # no dedicated seam at all. Neither may fire.
    honest = (("FRa", ("pkg.seam",)), ("FRb", ()))
    assert not_built_refutations(honest, reachable) == (), (
        "A truthful 'not-built' must NOT fire: the mere existence of a seam module proves "
        "nothing about delivery, which is why this direction did not exist before."
    )

    # REFUTED: the dedicated seam became reachable, so the FR is being delivered.
    delivered = (("FRa", ("pkg.seam", "pkg.live")),)
    problems = not_built_refutations(delivered, reachable)
    assert len(problems) == 1 and "IS reachable" in problems[0], problems
    assert "pkg.live" in problems[0] and "pkg.seam" not in problems[0], (
        "the refutation must name the module that ACTUALLY became reachable, not the whole "
        f"declared seam — an imprecise accusation is the defect class here: {problems[0]}"
    )

    # And it stays silent when nothing is reachable at all (the empty-graph degenerate case).
    assert not_built_refutations(delivered, frozenset()) == ()


def test_a_delivered_differently_reason_is_refuted_once_its_module_becomes_reachable() -> None:
    """TC-ArgusAgent-DOCS-001-37c — AC6.3 positive control, over the SAME synthetic graph.

    Story 12.3, fourth direction, driven exactly as `-37` and `-37b` drive the other three: a
    refutation nobody has watched fire is a refutation nobody knows is reachable.

    THE HOLE IT CLOSES, verified by RUNNING this module's own code on `58c8f6b` rather than by
    reading it. Executed there, ``reachability_refutations`` over
    ``("FR27", "delivered-differently", "argus.cache.memo_store")`` with ``memo_store`` forced
    REACHABLE returned ``()`` — no refutation — while the identical tuple disposed
    ``library-seam`` fired immediately. So `DF-12-1-B`'s stated trigger (*wiring the memo store
    "flips a `library-seam` disposition and turns it red"*) was measurably FALSE: FR27 was never
    disposed `library-seam`. Wiring the store would have turned NOTHING red, and the registry
    would have gone on asserting *"the memoization MECHANISM is unwired … deferred to Story
    12.3"* about a mechanism that had just been built.

    Both directions are asserted, because a guard that only ever rejects cannot be shown
    reachable and one that only ever accepts cannot be shown to bite. The third case is the
    important one: a `delivered-differently` reason that makes NO reachability claim is the
    disposition's legitimate use and must stay silent, or this direction would manufacture the
    false accusations `-37` deliberately refuses to make.
    """
    graph: dict[str, frozenset[str]] = {
        "pkg.cli": frozenset({"pkg.live"}),
        "pkg.live": frozenset(),
        "pkg.seam": frozenset(),
    }
    reachable = reachable_from(graph, "pkg.cli")

    # REFUTED — the exact pre-fix FR27 shape: an unwiredness claim over a module that is now
    # reachable. This is the sentence that could rot, and now cannot.
    rotted = (
        (
            "FRa",
            "delivered-differently",
            "pkg.live",
            "The memoization MECHANISM is unwired, so the property holds by determinism. "
            "Mechanism deferred to Story 12.3.",
        ),
    )
    problems = delivered_differently_refutations(rotted, reachable)
    assert len(problems) == 1, problems
    assert "IS reachable" in problems[0] and "is unwired" in problems[0], problems[0]

    # SILENT — the same claim while the module really is unreachable. Nothing has expired.
    assert delivered_differently_refutations(
        (("FRa", "delivered-differently", "pkg.seam", "The mechanism is unwired."),), reachable
    ) == (), "an unwiredness claim over an UNREACHABLE module is simply true and must not fire"

    # SILENT — the disposition's LEGITIMATE use: delivered by another mechanism, no claim about
    # wiring at all. Refuting this would be the false accusation `-37` exists to avoid.
    assert delivered_differently_refutations(
        (
            (
                "FRb",
                "delivered-differently",
                "pkg.live",
                "Delivered in a different form than promised; the divergence is named and the "
                "property is pinned by the golden tests.",
            ),
        ),
        reachable,
    ) == (), (
        "'delivered-differently' makes no reachability claim BY LABEL, and an entry whose "
        "reason makes none either must never be refuted here"
    )

    # SILENT — other dispositions are not this function's business (they have their own).
    assert delivered_differently_refutations(
        (("FRc", "wired", "pkg.live", "The mechanism is unwired."),), reachable
    ) == ()


# ─────────────────────────────────────────────────────────────────────────────
# -38 — the open set is asserted, not remembered
# ─────────────────────────────────────────────────────────────────────────────


def test_the_open_and_unowned_set_stays_open() -> None:
    """TC-ArgusAgent-DOCS-001-38 — the guard defends against its own author.

    Story 10.5 is the story most likely to close an open item by accident, because *sweep
    everything and classify it* reads like permission to tidy. Two items must survive it, and the
    ≥80% precision gate must survive it too.
    """
    ledger = _read(_LEDGER)
    prd = _read(_PRD)

    # H0 — the Minions handoff. Measured 2026-08-11: its OWNERSHIP was closed on 2026-08-10b by the
    # operator electing pre-authorised option (b). Its EXECUTION was not, and the ledger says so in
    # the same entry. Pinning "H0 is UNOWNED" would pin a fact that stopped being true a day before
    # this story ran; the residual — the filing — is what must stay open, and it is what the
    # forward registry's `specified-not-built` disposition rests on.
    assert "It does not mean\nH1–H4 have been filed" in ledger or (
        "does not mean" in ledger and "H1–H4 have been filed" in ledger
    ), (
        "deferred-work.md no longer records that H0's ownership closure does NOT mean H1–H4 were "
        "filed. The forward registry disposes the Minions consumption-contracts "
        "'specified-not-built' on exactly that residual. If the filing genuinely happened, update "
        "the disposition and this pin together — do not delete the pin."
    )
    assert "A5 remains ⚠️ UNSUPPORTED" in ledger, (
        "The ledger no longer records assumption A5 as UNSUPPORTED. H0's execution gap and A5 "
        "stand or fall together; neither is closed by Story 10.5."
    )

    # DF-7-2-A — an owner was named on 2026-08-10b. A named owner is not an adjudication.
    assert "**The item is NOT closed:**" in ledger, (
        "deferred-work.md no longer records DF-7-2-A as NOT closed. Naming XAgent007 as "
        "adjudicator on 2026-08-10b resolved the OWNER, not the measurement; only the human TP/FP "
        "adjudication (Epic 13) can clear the gate."
    )
    assert "status: OPEN, owned" in ledger, (
        "DF-7-2-A's 'status: OPEN, owned' line is gone. Epic 10 closes the RECORD; it clears no "
        "gate and closes no adjudication."
    )

    # The ≥80% gate itself.
    assert "**Current status (2026-08-10): NOT CLEARED**" in prd, (
        "The PRD no longer records the ≥80% precision gate as NOT CLEARED. Nothing in Epic 10 "
        "clears it — Epic 13 owns it — and the Journey 4 consequence note added by Story 10.5 "
        "must not read as if it does."
    )


# ─────────────────────────────────────────────────────────────────────────────
# -39 — non-vacuity, on BOTH closures
# ─────────────────────────────────────────────────────────────────────────────


def test_neither_closure_can_pass_by_finding_nothing() -> None:
    """TC-ArgusAgent-DOCS-001-39 — a heading rename or a package move must be RED, not green."""
    prd = _read(_PRD)

    assert "## Product Scope" in prd, (
        "§Product Scope cannot be located in prd.md. The forward closure derives its population by "
        "claim SHAPE rather than by this heading, so it would still pass — but losing the section "
        "means the document was restructured, and a restructured document must be re-swept."
    )
    assert "## Functional Requirements" in prd, (
        "§Functional Requirements cannot be located in prd.md, so functional_requirement_ids() "
        "returns nothing and the reverse closure would pass over an empty population."
    )
    assert "a capability not listed here will not exist in V1" in prd, (
        "The binding-contract preamble is gone. It is the sentence that makes the reverse sweep "
        "meaningful in both directions: a capability not listed does not exist, and a capability "
        "listed that no code path reaches does not exist either."
    )

    atoms = v1_claim_atoms(prd)
    assert len(atoms) >= _MIN_CLAIM_ATOMS, (
        f"Only {len(atoms)} V1 claim atoms parsed (floor {_MIN_CLAIM_ATOMS}, measured 20 on "
        "2026-08-11). The claim shapes were renamed or the scope lists were restructured; "
        "re-derive the population rather than lowering the floor."
    )

    fr_ids = functional_requirement_ids(prd)
    assert len(fr_ids) >= _MIN_FR_IDS, (
        f"Only {len(fr_ids)} FR ids parsed (floor {_MIN_FR_IDS}, measured 37). The `- **FRn:**` "
        "shape changed or the section moved."
    )
    assert len(set(fr_ids)) == len(fr_ids), f"Duplicate FR ids in the PRD: {fr_ids}"

    assert len(_FORWARD_REGISTRY) >= _MIN_CLAIM_ATOMS, "The forward registry was emptied."
    assert len(_REVERSE_REGISTRY) >= _MIN_FR_IDS, "The reverse registry was emptied."

    graph = build_import_graph(_PACKAGE_ROOT)
    edges = sum(len(targets) for targets in graph.values())
    reachable = reachable_from_any(graph, _ENTRY_POINTS)
    assert len(graph) >= _MIN_PACKAGE_MODULES, (
        f"Only {len(graph)} modules found under {_PACKAGE_ROOT.name}/ (floor "
        f"{_MIN_PACKAGE_MODULES}, measured 83 on 2026-08-15). The package moved or was renamed, "
        "and every reachability assertion in this file has quietly stopped testing anything."
    )
    assert edges >= _MIN_IMPORT_EDGES, (
        f"Only {edges} import edges resolved (floor {_MIN_IMPORT_EDGES}, measured 401 on "
        "2026-08-15). Either the import style changed or the resolver silently stopped resolving."
    )
    assert len(reachable) >= _MIN_REACHABLE_MODULES, (
        f"Only {len(reachable)} modules reachable from {_ENTRY_POINT_LABEL} (floor "
        f"{_MIN_REACHABLE_MODULES}, measured 68 on 2026-08-15). If an entry point moved, every "
        "'wired' disposition here is being proven against the wrong graph."
    )
    # THE ENTRY-POINT SET IS DERIVED, and its derivation is asserted non-vacuous.
    # ~~It is the ONLY entry point — pyproject.toml ships three console aliases and all three
    # are argus.cli:main.~~ (§3.4 struck, not deleted — that sentence was TRUE when it was
    # written on 2026-08-11 and was made FALSE on 2026-08-15 by Story 12.6's `argus-mcp =
    # argus.mcp.server:main`. It is the exact rot class this file exists to catch, arriving in
    # this file's own prose, and nothing was red when it happened: the walk kept resolving
    # `argus.cli`, so the floors held and the sentence just stopped being true. Replaced by the
    # closure below rather than by a corrected sentence, because a corrected sentence would rot
    # again on the fifth alias.)
    assert _ENTRY_POINTS, (
        "No entry point was derived from pyproject.toml [project.scripts]. A walk from no "
        "entry point reaches nothing, so every 'wired' disposition here would pass vacuously "
        "and every 'library-seam' one would be unrefutable. Fix the derivation; never fall "
        "back to a hand-written entry point."
    )
    missing_entries = [name for name in _ENTRY_POINTS if name not in graph]
    assert not missing_entries, (
        f"{missing_entries} are declared in [project.scripts] but are not modules under "
        f"{_PACKAGE_ROOT.name}/. A console alias pointing at a module that does not exist "
        "installs cleanly and fails on a consumer's first run."
    )
    assert reachable >= reachable_from(graph, _ENTRY_POINTS[0]), (
        "the union closure lost ground against a single entry point's closure, which means "
        "reachable_from_any stopped taking the union"
    )


# ─────────────────────────────────────────────────────────────────────────────
# -40 / -41 — the amendments landed, and the rule is written down where it binds
# ─────────────────────────────────────────────────────────────────────────────


def test_the_standards_decision_is_recorded_at_every_site_it_binds() -> None:
    """TC-ArgusAgent-DOCS-001-40 — one amended site and one unamended site is the defect."""
    prd = _read(_PRD)

    atoms = v1_claim_atoms(prd)
    reclassified = tuple(
        entry for entry in _FORWARD_REGISTRY if entry.disposition == "reclassified-v2"
    )
    assert len(reclassified) >= 2, (
        "Fewer than two `reclassified-v2` dispositions. The standards commitment binds V1 at TWO "
        "independent sites — §Product Scope and §Compliance & Regulatory — and the second was "
        "named in no planning document between 2026-08-03 and 2026-08-11. Amending one leaves the "
        "PRD self-contradicting, which is the state this story exists to end."
    )
    for entry in reclassified:
        hits = [atom for atom in atoms if entry.anchor in atom.text]
        assert len(hits) == 1, f"{entry.anchor!r} matched {len(hits)} atoms, expected 1"
        atom = hits[0]
        assert any(entry.anchor in span for span in struck_spans(atom.text)), (
            f"prd.md:{atom.line_no}: the reclassified commitment is not inside a CLOSED strike "
            "span. §3.4 evidence immutability: a superseded commitment is struck, not deleted, so "
            "a reader can still see what was promised — and the strike must enclose the "
            "COMMITMENT, not merely appear somewhere on the line. An unbalanced `~~` fails here "
            "deliberately; see struck_spans()."
        )
        assert _DISPOSITION_DATE in atom.text and "10.5" in atom.text, (
            f"prd.md:{atom.line_no}: the strike carries no {_DISPOSITION_DATE} / Story 10.5 "
            "attribution."
        )

    assert "a V1 commitment was reclassified into this V2 item" in prd, (
        "The V2 destination does not record the MERGE. The 'standards mapping "
        "(CWE/ASVS/ISO 25010/SLSA)' entry already existed, so an undelivered V1 item absorbed into "
        "it silently would UNDER-count the work and leave no record that anything was ever "
        "promised for V1 — the inverse of Story 10.2's double-count. Record it at the destination."
    )

    assert "no standards reference" in prd and "FR11" in prd, (
        "Journey 4 carries no consequence note. Dana's evidence bundle is weaker compliance "
        "evidence than §Compliance & Regulatory implied, and the note must name FR11 (secret "
        "detection) as the one security-category finding producer in V1, so a future reader knows "
        "exactly which findings the gap applies to."
    )

    frontmatter = prd.split("---", 2)[1] if prd.startswith("---") else ""
    assert _DISPOSITION_DATE in frontmatter and "standards_refs" in frontmatter, (
        "The PRD frontmatter `amendments:` block carries no 2026-08-11 standards entry naming all "
        "three sites. The amendment log is how a reader discovers a decision without reading the "
        "diff."
    )


def test_the_rule_and_this_guard_are_registered_in_the_architecture() -> None:
    """TC-ArgusAgent-DOCS-001-41 — a rule in a test is not a rule; a rule in prose is not enforced.

    The precedent is 10.1's `-23`, 10.3's `-28` and 10.4's `-29`: the enforcing test asserts both
    the rule TEXT and its own REGISTRATION are still present, so neither half can be deleted
    without turning something red.
    """
    architecture = _read(_ARCHITECTURE)

    assert "### Enforcement" in architecture, "§Enforcement cannot be located in architecture.md."
    assert _GUARD_FILE.split("/")[-1] in architecture, (
        f"{_GUARD_FILE} is not registered in architecture.md §Enforcement beside the guards from "
        "Stories 10.1, 10.2, 10.3 and 10.4. An unregistered guard is a private opinion."
    )
    assert (
        "a V1 commitment is delivered only when a production call site reaches it" in architecture
    ), (
        "The rule this story establishes is not written in architecture.md §Enforcement. The rule "
        "is: a V1 commitment is delivered only when a production call site reaches it — mapping to "
        "a module is not delivery, and a commitment with neither a call site nor a dated "
        "reclassification is a defect."
    )
    assert "mapping to a module is not delivery" in architecture, (
        "§Enforcement no longer carries the second half of the rule, which is the half that "
        "retires architecture.md's own 'No FR is unsupported' sentence."
    )
    assert "certifies module PLACEMENT, not reachability" in architecture, (
        "§Requirements Coverage Validation no longer carries the 2026-08-11 caveat. 'All 33 FRs "
        "map to a concrete module. No FR is unsupported' is true and useless over a "
        "module-placement table: four FRs in one row of it (FR23, FR24, FR26, FR29) have no "
        "production call site. A validation section that certifies placement while reading as "
        "certification of coverage is Story 10.1's defect one level up, in the document reviewers "
        "trust most."
    )
