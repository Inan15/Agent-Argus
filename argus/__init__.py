"""ArgusAgent — AI Project Assurance Audit (headless audit sub-tool).

STATUS: **EXPERIMENTAL** (story 22-15, M9 decision). ArgusAgent is NOT wired into the
Minions product run path — no orchestration, route, or workflow-runner stage
invokes it. It exists as a self-contained, story-driven sub-package that is
exercised only by its own tests and (optionally) its standalone CLI. The
wire-or-graduate decision is tracked as DF-22-15-A; do NOT treat any ArgusAgent seam
as a live product dependency until that operator ruling lands.

RESERVED PACKAGE SHELL — no business logic yet (placement-only, per the
governed "planning path first" setup decision 2026-06-18). Implementation is
story-driven and will land via the ArgusAgent architecture + epics decomposition;
do NOT add audit logic here until the corresponding story exists.

What ArgusAgent is
------------
ArgusAgent cold-reads a software repository (V1: built by Minions agents or
spec-driven development) and emits a **coverage-grounded, release-readiness
verdict** — *"no release-blocking findings within the audited coverage
envelope"* — never a claim that the code is correct. It is an assurance tool,
not an AI code reviewer or a SAST scanner: the verdict is a *pure function* of
a fixed-enum coverage ledger that cannot be minted without `audited_deep`
evidence (honesty is mechanical, not promised).

Dual-use, headless
------------------
- **Internal:** callable by Minions orchestration to audit Minions-built
  software.
- **External:** runnable as a standalone CLI (`argus audit ./repo`) by users
  outside Minions, distributed via the optional extra ``minions[argus]``
  (see ``pyproject.toml`` ``[project.optional-dependencies]``).
- **Headless-only** (CLAUDE.md §3.7): all output is artifacts under ``.argus/``,
  a verdict, and a deterministic exit code. No UI/UX surface.

Placement & reuse
-----------------
Lives at ``minions_core/argus/`` as a self-contained sub-package (a sub-package,
not a flat singleton, so the §4a flat-file allow-list is unaffected). It reuses
proven Minions infrastructure via direct import rather than re-implementation:
the ADR #18 hash-chained ledger patterns, permission tiers, budget guardrails,
and workspace-containment (CLAUDE.md §3.8 / §4a #19).

Authoritative sources (read before implementing)
-----------------------------------------------
- PRD:        _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md  (33 FRs, 21 NFRs)
- Placement:  _bmad-output/planning-artifacts/decisions/2026-06-18-argus-placement-under-minions-core.md
- Readiness:  _bmad-output/design-artifacts/ArgusAgent/implementation-readiness-report-2026-06-18.md
- Architecture / epics / stories: TO BE CREATED (the gating prerequisites —
  this shell exists so they can target a real package path).

Architecture-driver IDs are assigned at architecture time (ArgusAgent-* namespace);
they do not exist yet and must not be invented in code before the architecture
document defines them.
"""

# ArgusAgent's own version constant — the single source for the envelope `argus_version`
# field (story 1.1, ArgusAgent-FR-25). Never hardcode this literal at call sites and
# never derive it from env/clock (it must be byte-stable across hosts, NFR-P1).
__version__ = "0.1.0"

# Explicit, discoverable experimental-status marker (story 22-15, M9). ArgusAgent is
# NOT wired into the Minions product run path; see the module docstring and
# DF-22-15-A for the wire-or-graduate decision.
__status__ = "experimental"

__all__: list[str] = ["__version__", "__status__"]
