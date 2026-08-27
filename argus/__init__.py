"""ArgusAgent — deterministic, headless repository assurance & audit engine.

What ArgusAgent is
------------------
ArgusAgent cold-reads a software repository and emits a **coverage-grounded,
release-readiness verdict** — *"no release-blocking findings within the audited
coverage envelope"* — never a claim that the code is correct. It is an assurance
tool, not an AI code reviewer or a SAST scanner: the verdict is a *pure function*
of a fixed-enum coverage ledger that cannot be minted without ``audited_deep``
evidence (honesty is mechanical, not promised).

Package & distribution
----------------------
This package is ``argus/`` in the standalone **Agent-Argus** repository. It is
declared by ``pyproject.toml`` as the distribution ``argus-agent``, with the
optional extras ``dev`` / ``llm`` / ``languages`` and **four** console scripts
across **two entry points**::

    argus  ·  argus-agent  ·  repo-audit   → argus.cli:main
    argus-mcp                              → argus.mcp.server:main

~~and three console scripts that all resolve to :func:`argus.cli.main`~~ — struck
2026-08-15 (Story 12.6 / FR35), not deleted: it was true until this distribution
gained a second entry point. The three CLI aliases are unchanged; ``argus-mcp``
serves the SAME audit over JSON-RPC on stdin/stdout so an agent can invoke it and
read the verdict without a human relaying it. Both entry points build the same
``AuditRequest`` and consume the same ``AuditVerdict`` — there is no second
decision path, and no capability reachable through one and not the other.

The distribution ALSO ships DATA, since 2026-08-15 (Story 12.7 / FR35): the
assistant command assets under ``argus/assets/commands/``. They are placed by the
second sub-command on the first entry point above::

    argus install-commands [--host …] [--dest …] [--dry-run] [--remove]

~~and no data assets at all: every entry in the wheel is either an ``argus/**``
module or a ``dist-info`` metadata file, so installing this distribution
registers no command in any assistant~~ — struck 2026-08-15 (Story 12.7), not
deleted: it was true until this story. It is a SUB-COMMAND, not a fifth alias, so
the count above is unchanged and stays the ONE statement of it here; the assets
ship because ``flit_core`` walks the whole package directory, with no
build-backend change and no second version or entry-point constant introduced.

It installs and runs **with no Minions package present** — ArgusAgent imports
nothing from a host product and depends on no monorepo layout.

Headless-only: every output is an artifact under ``.argus/``, a verdict, and a
deterministic exit code. There is no UI surface.

Consumer contract
-----------------
Exit codes, artifact ``schema_version`` values, the stdout summary line, the
rendered report strings and the public API surface are stated in **one** place —
the repository-root ``CHANGELOG.md``. That file is the authoritative consumer
contract; nothing here restates it, so there is no second copy to go stale.

``tests/test_release_note.py`` pins the note against the shipped code, but pins
*what the code produces*, not every sentence in the note: the schema constants,
the FR16 decision table, the exit-code map, the coverage floor and threshold, the
public API names, and — per FR16 row, by equality — the ship-readiness headlines,
the ``final-verdict.md`` callouts and the persisted assurance sentences. The note's
surrounding prose is not machine-pinned; read it as documentation, and read the
listed surfaces as contract.

Authoritative sources (all present in this repository)
------------------------------------------------------
- PRD:          _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md
- PRD addendum: _bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md
- Architecture: _bmad-output/design-artifacts/ArgusAgent/architecture.md
- Epics:        _bmad-output/design-artifacts/ArgusAgent/epics.md
- Stories:      _bmad-output/design-artifacts/ArgusAgent/stories/
- Changelog:    CHANGELOG.md

Architecture-driver IDs live in the ``ArgusAgent-AR*`` / ``ArgusAgent-FR*`` /
``ArgusAgent-NFR*`` namespaces defined by the documents above; cite an existing
id, never invent one.
"""

# ArgusAgent's own version constant — the single source for the envelope `argus_version`
# field (story 1.1, ArgusAgent-FR-25). Never hardcode this literal at call sites and
# never derive it from env/clock (it must be byte-stable across hosts, NFR-P1).
__version__ = "0.1.0"

# Explicit, discoverable maturity marker. `beta` states that the public
# Python API is in beta release; the CLI wire contract (exit codes
# + the stdout summary line) IS frozen. See CHANGELOG.md.
__status__ = "beta"

__all__: list[str] = ["__version__", "__status__"]
