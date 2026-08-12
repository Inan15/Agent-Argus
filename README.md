# ArgusAgent (`argus-agent`) 🛡️👁️

> **The Agent-First, Deterministic Repository Audit & Assurance Engine**

`ArgusAgent` combines the high-precision **APAA (AI Project Assurance Audit)** Python verification engine with the vendor-portable **RAM (Repository Audit Method)** framework. Named after *Argus Panoptes* — the mythological 100-eyed all-seeing guardian — `ArgusAgent` provides multi-agent, cross-subsystem vigilance over codebases with zero blind spots.

> **Integrating `argus audit` into a pipeline?** Every consumer-visible change to the exit codes, artifact schemas, defaults, rendered strings and public API — and what deliberately did *not* change — is recorded in **[CHANGELOG.md](CHANGELOG.md)**.

> ⚠️ **Instrument status — read this before you weigh any verdict this tool gives you.**
> Instrument status: Argus's own finding precision has not been independently validated. Its findings rest on the Argus dogfood corpus, a self-audit of this repository with no human true-positive/false-positive adjudication behind it. This notice is removed only when Epic 13's human adjudication clears the >=80% precision gate; nothing else removes it.
>
> This is **distinct from** the scope disclaimer on each audit, and both apply: that one bounds
> *this audit* — what was examined, sampled and not covered — while this one bounds *the tool*.
> An audit can be perfectly scoped and still be produced by an instrument nobody has measured.
> It is also **not** the per-run grade: engaging a deeper audit pass changes how a run was
> configured, and does not validate the instrument.

---

## 🌟 Key Features

1. **Deterministic Assurance Kernel (`argus/`)**:
   - **Pure Verdict Gate**: Mathematical, zero-LLM-token release readiness calculation (`RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`).
   - **AST Indexing & Grounding**: `tree-sitter` AST parsing and structural search validating deep audit claims against real code definitions.
   - **Graph-Derived Partitioning**: Auto-partitions large repositories into bounded audit units ($\le 40$ files / $15\text{k}$ LOC) to eliminate context rot.
   - **Content-Addressed Memoization**: Byte-identical execution across hosts via canonical JSON serialization and full closure hashing.
   - **Prosecutor Cut-Edge Pass**: Adversarial second pass ensuring seam-spanning defects across partitions move the verdict to $\color{red}{\text{NOT READY}}$.
   - **Defect Cartridges & Self-Audit Harness**: CI-blocking true-negative clean control cartridges and hidden holdouts.

2. **RAM Workflow Framework (`audit/`, `phases/`, `adapters/`, `templates/`)** — *repository-only; these directories are not part of the `argus-agent` distribution, see [Quickstart](#-quickstart--installation)*:
   - **Vendor & Agent Adapters**: Native slash commands and skills for **Claude Code**, **Cursor**, **Cline**, **RooCode**, **Codex CLI**, **Gemini CLI**, and **Windsurf**.
   - **12 Audit Phases**: Guided markdown workflows from Orientation (`00`) to Verdict (`11`).
   - **12 Developer Report Templates**: Rich, human-readable markdown reporting for Architecture, Security, Performance, Requirements, and Risk.

---

## 🚀 Quickstart & Installation

### Install as a dependency (no clone required)

`argus-agent` is **not on PyPI or any other package index**, and this repository has
published no release yet. What it does have is a release workflow
(`.github/workflows/release.yml`) — **committed, and never executed** — that builds an
sdist and a wheel for a `v*.*.*` tag and attaches both to a GitHub Release. The dependency
string a consumer will use is therefore a tag-pinned VCS reference:

```bash
# INTERIM — resolve straight from this repository at a tag.
pip install "argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0"
```

> ⚠️ **This command does not resolve today.** Tag `v0.1.0` has **not been created or
> pushed** — `git tag -l` is empty at this commit — so `pip` cannot find the ref and the
> install fails. It begins working once an operator performs the prepared-but-not-executed
> steps recorded in the story record (create and push the tag; the workflow does the rest).
> Nobody has run this command against a real tag: treat it as the documented shape, not as
> an exercised capability.

In a `pyproject.toml` — same caveat, the tag must exist before this resolves:

```toml
dependencies = [
    "argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0",
]
```

> ⚠️ Unresolvable until `v0.1.0` exists, for the same reason as above.

**Authentication.** No credential is required **if and only if**
`github.com/Inan15/Agent-Argus` is a public repository. If it is private, a consumer's CI
needs a token with read access to it and must rewrite the URL to carry that token (for
example `git+https://${TOKEN}@github.com/...`). ⚠️ **This repository's visibility was not
measured when this line was written** — no network call was made from the working tree —
so treat "public" as the thing to CHECK, not as a stated fact. Open the URL above: if it
loads while signed out, no credential is needed.

**This pin is INTERIM.** It resolves a git ref rather than an immutable index artifact,
which means it depends on the repository staying reachable and the tag staying put (the
release workflow refuses a tag move for exactly this reason). It moves to a package index
under one named condition:

> when `argus-agent` is claimed on PyPI **and** a PyPI Trusted Publisher (OIDC) is
> configured for this repository — at which point the publish step is added to
> `.github/workflows/release.yml` directly (trusted publishing cannot be used from inside
> a *reusable* workflow) with `permissions: id-token: write` and **no** stored token, and
> the pin above is replaced by a plain index install of the distribution name.

Publishing to PyPI is deliberately **not** attempted by the current workflow: a released
name+version on an index can never be replaced, which makes it an operator decision taken
with credentials in hand.

### Auditing a non-Python repository: the `[languages]` extra

The default install grounds **Python only**. Nine further tree-sitter grammars ship in an **optional
extra**, and installing it is what lets Argus check claims against the real AST of a JavaScript,
TypeScript, Go, Rust, Java, C, C++, Ruby or PHP file:

```bash
pip install "argus-agent[languages] @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0"
# or, from a clone:
pip install -e ".[languages]"
```

> ⚠️ Same interim caveat as above — the tag does not exist yet, so the first command does not resolve
> today. The clone form works now.

**What it changes, and what it does not.** The languages Argus reads are the suffixes in
[`argus/shared/source_languages.py`](argus/shared/source_languages.py) — that module is the single
source of truth, not this paragraph, and `tests/test_multilanguage_audit.py` fails if a language in it
has no grounding fixture. The extra changes what happens *after* a file is read:

| | Grammar installed | Grammar absent |
|---|---|---|
| The file is enumerated and graded | ✅ | ✅ |
| It can reach `audited_deep` | ✅ | ❌ — capped at shallow |
| What the report says | the deep grade it earned | `ast_eligible=False` with a named reason token, e.g. `grammar_missing_go` |

**Enumerable is not the same as deeply auditable, and a missing grammar is never a silent drop.** A file
whose grammar is absent is still counted, still graded, and still reported — it simply cannot reach
`audited_deep`, so it lowers the coverage ratio instead of quietly disappearing from it. That is the
point of enumerating it: an audit that cannot examine a file has to say so. Argus will not emit a deep
claim it could not verify.

**Measured limits, so you can plan around them rather than discover them.** All ten languages ground
(`ast_eligible=True`), including `.tsx` via the JSX-aware grammar. But structure extraction is narrower
than grounding: **C, C++, Ruby and Rust currently yield no function/class definitions**, because the
definition vocabulary was written against Python's node names. A file in those four parses cleanly and is
graded, but has no definition for the depth gate to stand on. Pinned language-by-language by
`TC-ArgusAgent-INTAKE-003-09` and tracked as `DF-10-2-A` in
`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`.

### What the distribution contains, and what needs the git repository

MEASURED from the built wheel (`argus_agent-0.1.0-py3-none-any.whl`, 78 entries) and sdist
(`argus_agent-0.1.0.tar.gz`, 77 files), not inferred: `[tool.flit.module] name = "argus"`
packages **the `argus` Python package and nothing else**. The sdist additionally carries
`pyproject.toml`, `README.md`, `LICENSE` and `PKG-INFO`. Both figures are re-derived from a
freshly built pair of artifacts by `TC-ArgusAgent-DOCS-001-54`, which fails if this
paragraph and the artifact ever disagree — in either direction.

| Capability | From the installed distribution | Needs the git repository |
|---|---|---|
| `argus` / `argus-agent` / `repo-audit` console scripts | ✅ | |
| `argus audit <repo>` — the full deterministic audit, verdict and exit-code contract | ✅ | |
| Report generation (`--report-dir`) | ✅ | |
| The RAM workflow framework — `audit/`, `phases/`, `adapters/`, `templates/` | ❌ **not packaged** — these are sibling top-level directories, not part of the `argus` module | ✅ |
| `install.sh` / `install.ps1` (which copy the adapters into your assistant) | ❌ not packaged | ✅ |
| The test suite and the defect cartridges under `tests/` | ❌ not packaged | ✅ |
| Argus's own dogfood proof generator (`argus.dogfood.*`, `argus.precision.*`) | ✅ imports; **generating a proof still needs the repository** — see the note below | ✅ for the proof run |

> **Measured limitation, stated rather than discovered later — and now measured away.** On a
> freshly built wheel, with this repository removed from `sys.path` and one clean subprocess
> per module, **73 of the 73 shipped modules import**. None fail.
>
> Until 2026-08-12 five did — `argus/precision/__init__.py`,
> `argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`,
> `argus/dogfood/proof_render.py` and `argus/dogfood/proof_run.py` — all with
> `ModuleNotFoundError: No module named '_registry'`, because
> `argus/precision/replay_harness.py` imported the labelled-cartridge registry from
> `tests/cartridges/` at module import time and the distribution does not (and should not)
> contain it. That registry is now resolved **lazily**, so importing the module from the
> wheel succeeds; *running* the precision replay or the dogfood proof generator still needs
> the git repository, because that is where the labelled cartridges live. Those are Argus's
> *self-audit and precision-measurement* tools, not consumer features. `DF-9-2-A` in
> `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` is **CLOSED**.
>
> **What holds this claim.** `TC-ArgusAgent-RELEASE-001-20`
> (`tests/test_built_distribution.py`) **builds the wheel and the sdist and imports every
> shipped module out of the built artifact**, so the count above cannot drift from what
> actually ships. It replaces a claim that used to be made here for
> `TC-ArgusAgent-RELEASE-001-11`, which was **false**: `-11` walks the *source tree* with
> `ast`, cannot tell a module-level import from a lazy one, and stayed green across the
> entire fix while the published figures rotted from "66 of 71" to a measured 67 of 72
> underneath it. A guard that inspects the source tree cannot hold a claim about the
> distribution.

### Clone-based installation (for the RAM framework and development)

```bash
# Unix / macOS
./install.sh

# Windows PowerShell
.\install.ps1
```

Or, for an editable development install:

```bash
pip install -e .
```

---

## 💻 Slash Commands & Usage

**What `pip install argus-agent` actually installs — measured on the built wheel, not assumed.**
Three console aliases, and nothing else: `argus`, `argus-agent` and `repo-audit`, all three
entry points for `argus.cli:main`. The wheel carries **zero data assets** (77 entries = 72
`argus/**` modules + 5 `dist-info` files), so the distribution contains no command file, no
skill manifest and no registration mechanism of any kind. **Installing it registers no slash
command in any assistant.**

> 🚧 **FORTHCOMING — documented ahead of delivery, owned by Story 12.7 / FR35.** The seven
> commands below are the shape the vendor adapters are being built to, not a capability the
> published distribution has today. They are kept here rather than deleted because the shape
> is the contract 12.7 delivers against — and `TC-ArgusAgent-DOCS-001-56` fails the build if
> this marker is ever removed while the wheel still ships no mechanism, **or** left in place
> once it does.

```bash
/audit                  # Run full repository audit pipeline
/audit repo             # Audit repository intake & partitioning
/audit architecture     # Audit architectural integrity & call graphs
/audit security         # Scan secrets, containment, and entropy
/audit subsystem <name> # Audit specific subsystem (e.g. auth, payments)
/audit report           # Generate 12 developer markdown reports
/audit resume           # Resume interrupted audit from on-disk state
```

From terminal CLI — the `audit` sub-command is required, and every flag below is the real spelling:

```bash
# The whole contract in one line: audit this repo at HEAD, no ceiling, default passes.
argus audit .

# Release-gate mode, as a CI step would run it.
argus audit . --commit HEAD --strict --budget 500 --materiality-bar critical

# Write the Markdown reports (--reports renders nothing unless --report-dir is set).
argus audit . --report-dir ./argus-reports --reports final-verdict,coverage-ledger
```

> *Corrected 2026-08-10 (Story 10.3 / `DF-AUD-APAA-E`).* This block previously read
> ~~`argus --budget 500 --materiality critical`~~, which exits with an argparse usage error: the
> `audit` sub-command was missing and `--materiality` is not a flag this parser has ever accepted
> (it is `--materiality-bar`). Every `argus …` command line committed in this README, in
> `action.yml` and in the workflows is now parsed by the real parser in CI
> (`TC-ArgusAgent-DOCS-001-28`), so a documented invocation that would fail for a reader fails the
> build first.

---

## 📁 Repository Structure

```
ArgusAgent/
├── argus/                 # Standalone Python Assurance Engine Core
│   ├── intake/            # Repository intake & stack detection
│   ├── index/             # tree-sitter AST indexer & partitioner
│   ├── ledger/            # Coverage ledger & depth semantics
│   ├── detectors/         # Vacuous test, secret scan, orphan code, radon
│   ├── verdict/           # Pure verdict gate & Prosecutor pass
│   ├── store/             # Canonical serializer & envelope writer
│   ├── cache/             # Content-addressed memoization
│   ├── audit/             # LLM dispatch port & provider adapters
│   ├── cost/              # Budget governor & resumability
│   ├── governance/        # Escalation manager & decision records
│   └── precision/         # Ground-truth replay harness
├── audit/                 # RAM Skill definitions & Evidence Models
├── phases/                # 12 Audit Phase Markdown Guides (00 to 11)
├── adapters/              # Vendor Adapters (Claude Code, Cursor, Cline, etc.)
├── templates/             # 8 Developer Report Templates
├── tests/                 # Comprehensive Test Suite & Defect Cartridges
├── pyproject.toml         # Package definition
├── install.sh / .ps1      # Auto-installer scripts
└── README.md              # Project documentation
```

---

## 🛡️ License

MIT License. See [LICENSE](LICENSE) for details.
