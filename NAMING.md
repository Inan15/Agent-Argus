# Naming

**The project is called Agent-Argus.** Everything else on this page exists because that one
sentence is not sufficient: a project has several names that live in different systems, and this
file records which is which so they stop drifting.

Decided 2026-08-29 by XAgent007.

## The canonical set

| Kind | Value | Where it appears | May it change? |
|---|---|---|---|
| **Project / product name** | `Agent-Argus` | README title, docs prose, release notes, GitHub description, marketing | This is the name. |
| **GitHub repository** | `Inan15/Agent-Argus` | clone URLs, issue links, install pins | Renaming breaks every published install pin. |
| **Distribution name** | `argus-agent` | `pip install "argus-agent @ …"`, `pyproject.toml [project].name` | **Frozen.** Published at v1.0.0 and pinned in released install commands. |
| **Import package** | `argus` | `import argus`, `argus/**` | **Frozen.** Public API surface. |
| **CLI command** | `argus` | `argus audit .` | **Frozen.** Wire contract (FR18 / AR3). |
| **MCP entry point** | `argus-mcp` | `[project.scripts]` | **Frozen.** Published console script. |
| **Distribution repository** | `XAgents-ai/argus-agent-releases` | mirror of this repository | See below. |

## The identifier namespace is `ArgusAgent`, and it does not move

Roughly **5,600** occurrences of the token `ArgusAgent` exist in this repository as *identifiers*,
not as prose:

- test case ids — `TC-ArgusAgent-DOCS-001-71`, `TC-ArgusAgent-PRECISION-001-94`, ~1,600 of them;
- architecture driver ids — `ArgusAgent-FR-17`, `ArgusAgent-NFR-D3`, ~4,000 references;
- the planning artifact path — `_bmad-output/design-artifacts/ArgusAgent/`, across ~140 files.

**These are frozen.** They are contract names cited by tests, stories, retrospectives and signed
records; renaming them would rewrite history that other documents cite by id, for no reader benefit.
A test id is not a brand.

So: **`Agent-Argus` in prose, `ArgusAgent` in identifiers, `argus-agent` on a package index, `argus`
at a shell prompt.** Four spellings, each with one job, none of them interchangeable.

## Why not rename the distribution to match the project

It was considered and rejected. `argus-agent` is published in the v1.0.0 release, appears in the
install command in the README, the CHANGELOG, `docs/first-run.md` and both release pages, and is the
name a consumer's lockfile would carry. Renaming it would break every one of those to make two names
match — a cost paid entirely by users so that a document could be tidier.

## The two repositories

`Inan15/Agent-Argus` and `XAgents-ai/argus-agent-releases` carry identical git history and both
publish releases. Measured 2026-08-29: same branches, same commits.

- **`Inan15/Agent-Argus` is the source of truth.** Issues, pull requests and discussion go here.
- **`XAgents-ai/argus-agent-releases` is a distribution mirror.** It exists so releases can be
  published under an organisation account. It carries the same artifacts.

If those two ever diverge, the source of truth wins.

## Copyright holder

Files carrying a copyright line — `LICENSE`, `packaging/LICENSE.txt` — name the **Agent-Argus
maintainers**. Update them together or not at all.

## If you are adding a new surface

Ask which kind of name it needs, then take it from the table above rather than typing something that
looks right. A new user-facing string takes `Agent-Argus`. A new test takes an `ArgusAgent-` id. A
new console script takes the `argus` family.
