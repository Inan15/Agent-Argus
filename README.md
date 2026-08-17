# ArgusAgent (`argus-agent`) 🛡️👁️

> **The Agent-First, Deterministic Repository Audit & Assurance Engine**

`ArgusAgent` combines the high-precision **APAA (AI Project Assurance Audit)** Python verification engine with the vendor-portable **RAM (Repository Audit Method)** framework. Named after *Argus Panoptes* — the mythological 100-eyed all-seeing guardian — `ArgusAgent` provides multi-agent, cross-subsystem vigilance over codebases with zero blind spots.

> **Never run `argus` before?** Start at **[docs/first-run.md](docs/first-run.md)** — install, your first audit, how to read the ledger, and what each verdict and exit code means. Four sections, nothing else. *(Added 2026-08-15, Story 12.8: until then this README was the only integrator-shaped document in the repository and it linked to `docs/` nowhere at all — measured, zero occurrences — so a first-time reader met the full integration surface or nothing. The page is repository documentation and is **not** packaged in the wheel, which is why this link is its whole delivery mechanism.)*

> **Integrating `argus audit` into a pipeline?** Every consumer-visible change to the exit codes, artifact schemas, defaults, rendered strings and public API — and what deliberately did *not* change — is recorded in **[CHANGELOG.md](CHANGELOG.md)**.

> ⚠️ **Instrument status — read this before you weigh any verdict this tool gives you.**
> Beta: Argus's finding precision has not been independently validated. Its findings rest on the Argus dogfood corpus, a self-audit of this repository. Treat findings as a prompt to look, not a verdict. This notice is removed only when the >=80% precision gate is met; nothing else removes it.
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

2. **Packaged assistant commands (`argus/assets/commands/`)** — *shipped in the wheel, placed by `argus install-commands`, see [Slash Commands](#-slash-commands--usage)*:
   - **Verified host: Claude Code.** One host, not a list of aspirations. Each host is a single entry in the closed registry at [`argus/commands/hosts.py`](argus/commands/hosts.py), and an entry exists only once its exact configuration directory and its exact resulting command spelling have been verified. Additional hosts are each one reviewed registry entry away.

3. **RAM Workflow Framework (`audit/`, `phases/`, `templates/`)** — *repository-only; these directories are not part of the `argus-agent` distribution, see [Quickstart](#-quickstart--installation)*:
   - **12 Audit Phases**: Guided markdown workflows from Orientation (`00`) to Verdict (`11`).
   - **8 Developer Report Templates**, of which **4 are rendered** by `argus audit --report-dir`: `final-verdict`, `coverage-ledger`, `security-review` and `architecture-review`.

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
`github.com/Inan15/Agent-Argus` is a public repository.

> **Superseded, kept on the record.** This previously read:
> ~~⚠️ **This repository's visibility was not measured when this line was written** — no network
> call was made from the working tree — so treat "public" as the thing to CHECK, not as a stated
> fact.~~ It has since been measured, and it is the worse case. Struck rather than deleted, because
> the record that the gap existed is what makes the correction auditable.

This is the single source of that fact; `TC-ArgusAgent-DOCS-001-71` asserts it appears
verbatim here, in `CHANGELOG.md` and in `docs/first-run.md`, so the three cannot drift apart:

Repository visibility, MEASURED 2026-08-15 by `gh repo view Inan15/Agent-Argus --json
visibility,isPrivate` -> `PRIVATE` / `isPrivate: true`. What that costs a consumer, stated
plainly: while it stays private the pinned install cannot resolve for anybody — tag or no
tag — without a read credential carried in the URL
(`git+https://<credential>@github.com/...`), and a GitHub Release on a private repository is
not publicly resolvable either. Making the repository public is an outward-facing operator
act that has not been taken. This is a dated measurement, not a standing claim: re-run the
command above before relying on it.

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
with credentials in hand. **Re-affirmed 2026-08-15 (Story 12.9 / DN-1):** still not
attempted, and the exit condition above still has a named end rather than becoming permanent
by silence.

### Release status: what evidence backs this, stated rather than implied

A release status here cites an executed gate — a GitHub Actions run **together with the sha
that run covers** — or it records `NOT ESTABLISHED`, which is a first-class recordable state
and not a gap (`architecture.md` §H, Story 10.1). The sentence below is **derived**, not
typed: `scripts/release_notes.py::derive_release_status` computes it from the observed run,
its sha, its conclusion and the commit being released, and
`TC-ArgusAgent-DOCS-001-25` asserts that this file and `CHANGELOG.md` carry exactly that
value. The same function renders it into the GitHub Release note, so the three cannot
disagree.

CI evidence: NOT ESTABLISHED. No executed gate covers the commit being released — the most
recent `audit-ci.yml` run is run 31908861401, which covers sha
cea92689b14f730ff529caeabd74c1f33f84821b and therefore evidences a different tree; a run id
quoted without the sha it covers is a half-truth, so it is named here as SUPERSEDED rather than
cited. Observed 2026-08-16 through the GitHub API. The human step that would establish one, and
the only one: push `master` to `origin` and let `audit-ci.yml` run to success on the released
commit, then re-derive this sentence from that run. A local `pytest`/`mypy`/`bandit` run is
necessary, not sufficient, and is recorded as LOCAL (architecture.md §H).

### Auditing a non-Python repository: nothing extra to install

**The default install grounds every language Argus claims to support** — Python, JavaScript,
TypeScript, Go, Rust, Java, C, C++, Ruby and PHP. All ten tree-sitter grammars are ordinary
dependencies of the distribution, so the plain install command is the whole story:

```bash
pip install "argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0"
# or, from a clone:
pip install -e .
```

> ⚠️ Same interim caveat as above — the tag does not exist yet, so the first command does not resolve
> today. The clone form works now.

> **Superseded, kept on the record.** This section previously read:
> ~~The default install grounds **Python only**. Nine further tree-sitter grammars ship in an
> **optional extra**, and installing it is what lets Argus check claims against the real AST of a
> JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby or PHP file.~~ The nine grammars moved into the base dependencies on 2026-08-15, because
> NFR-P3 classifies coverage lost to a grammar missing from the default install as a **packaging
> defect, not a user error**. The `[languages]` extra is retained so
> `pip install "argus-agent[languages]"` keeps working; it now resolves to requirements the default
> install already carries, and a test pins the two lists equal.

**Which languages, and where that list actually lives.** The languages Argus reads are the suffixes in
[`argus/shared/source_languages.py`](argus/shared/source_languages.py) — that module is the single
source of truth, not this paragraph, and `tests/test_multilanguage_audit.py` fails if a language in it
has no grounding fixture. `TC-ArgusAgent-DOCS-001-61` asserts the default dependency list grounds
exactly that set, so a language added to the tool but not to the install turns red at edit time.

**A grammar can still be missing at run time, and Argus tells you so where it costs you.** An
uninstalled, vendored, or broken grammar — or a `tree-sitter` core that fails Argus's own self-check —
still degrades a file, so the run states the reason at the point the file is downgraded rather than
leaving a coverage number to be misread as a judgement about the code:

| | Grammar usable | Grammar unusable |
|---|---|---|
| The file is enumerated and graded | ✅ | ✅ |
| It can reach `audited_deep` | ✅ | ❌ — capped at `audited_shallow` |
| What the report says | the deep grade it earned | the file, the depth it reached, **the exact package** (e.g. `tree-sitter-go`) and the `pip install` command that restores deep grounding |

The remedy is per failure class, never blended: a package that is *absent* is a `pip install`, a package
that is *present but unrecognised* is an Argus defect you should report rather than reinstall, and a
`tree-sitter` core that is missing or unvalidated affects every language at once and says so.

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

MEASURED from the built wheel (`argus_agent-0.1.0-py3-none-any.whl`, 94 entries) and sdist
(`argus_agent-0.1.0.tar.gz`, 93 files), not inferred: `[tool.flit.module] name = "argus"`
packages **the `argus` Python package and nothing else** — which, since Story 12.7, includes
the command assets under `argus/assets/commands/`: `flit_core` walks the whole `argus/`
directory and ships every file in it, so a `.md` there reaches the wheel with **no**
`pyproject.toml` change, and reaches the sdist because it is tracked in version control.
The sdist additionally carries
`pyproject.toml`, `README.md`, `LICENSE` and `PKG-INFO`. Both figures are re-derived from a
freshly built pair of artifacts by `TC-ArgusAgent-DOCS-001-54`, which fails if this
paragraph and the artifact ever disagree — in either direction. **This paragraph is the one
place this README states those two numbers**; everything else below refers to it rather
than restating them, because two remembered statements of one measurement is how they came
to contradict each other (see the struck sentence under [Slash Commands](#-slash-commands--usage)).

| Capability | From the installed distribution | Needs the git repository |
|---|---|---|
| `argus` / `argus-agent` / `repo-audit` console scripts (all three run `argus.cli:main`) | ✅ | |
| `argus-mcp` console script (`argus.mcp.server:main`) — the same audit over MCP on stdin/stdout | ✅ | |
| `argus audit <repo>` — the full deterministic audit, verdict and exit-code contract | ✅ | |
| Report generation (`--report-dir`) | ✅ | |
| `argus install-commands` — places the packaged assistant commands into your assistant's configuration directory (and `--remove` takes them away) | ✅ | |
| The packaged command assets themselves (`argus/assets/commands/*.md`) | ✅ they ship in the wheel **and** the sdist as data | |
| The RAM workflow framework — `audit/`, `phases/`, `templates/` | ❌ **not packaged** — these are sibling top-level directories, not part of the `argus` module | ✅ |
| `install.sh` / `install.ps1` — convenience wrappers that `pip install -e .` and then **delegate** to `argus install-commands`; they copy nothing themselves | ❌ not packaged | ✅ |
| The test suite and the defect cartridges under `tests/` | ❌ not packaged | ✅ |
| Argus's own dogfood proof generator (`argus.dogfood.*`, `argus.precision.*`) | ✅ imports; **generating a proof still needs the repository** — see the note below | ✅ for the proof run |

> **Measured limitation, stated rather than discovered later — and now measured away.** On a
> freshly built wheel, with this repository removed from `sys.path` and one clean subprocess
> per module, **86 of the 86 shipped modules import**. None fail. (86, not 84, since
> 2026-08-17: Story 13.3 added `argus/precision/gate_decision.py` and
> `argus/precision/gate_disclosure.py` — the gate-decision instrument and the renderer that
> states its outcome; neither resolves a repository path at module level, so both import
> from the wheel like the rest; 84, not 83, since
> 2026-08-16: Story 13.2 added `argus/precision/adjudication.py`, the adjudication record
> the >=80%-precision gate is measured from — it resolves no repository path at module
> level, so it imports from the wheel like the rest; 83, not 78, since
> 2026-08-15: Story 12.7 added `argus/assets/` and `argus/assets/commands/` — the packaged
> command-asset tree, which is a real package so `importlib.resources` can resolve it from a
> built distribution — plus `argus/commands/` with its closed host registry and the
> installer behind `argus install-commands`; 78, not 75, since
> 2026-08-15: Story 12.6 added `argus/mcp/` — `__init__.py`, `protocol.py` and `server.py`, the
> MCP stdio adapter behind the `argus-mcp` entry point; 75, not 74, since 2026-08-13, when
> Story 12.3 added `argus/cache/stage_memo.py`, the production call site that wires the
> FR27/NFR-D1 memoization store; 74, not 73, since Story 12.2 added
> `argus/audit/deep_pass.py`, the opt-in deep pass. The figure is DERIVED from the freshly built
> artifact by `TC-ArgusAgent-DOCS-001-54` — *the artifact is the fact* — so it moves with the
> tree rather than being remembered.)
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

Both scripts do the same two things and nothing else: an editable install, then a delegation
to `argus install-commands`. **You do not need either of them to get the commands** — that
step ships in the distribution, so a `pip install` user runs it directly:

```bash
# Preview the plan, then place the commands.
argus install-commands --dry-run
argus install-commands
```

> There is exactly one placement mechanism, it ships in the wheel, and `--remove` takes
> back exactly what it wrote.

Or, for an editable development install with no command placement at all:

```bash
pip install -e .
```

---

## 💻 Slash Commands & Usage

**What `pip install argus-agent` actually installs — measured on the built wheel, not assumed.**
Four console aliases across two entry points: `argus`, `argus-agent` and `repo-audit`, all
three entry points for `argus.cli:main`; and `argus-mcp`, which is `argus.mcp.server:main`.
**And, since Story 12.7, the command assets themselves**: the wheel carries the
`argus/assets/commands/*.md` files as data, the `argus install-commands` sub-command places
them into a supported assistant's configuration directory, and `--remove` takes back exactly
what it wrote. The wheel's entry count is stated once, in
[What the distribution contains](#what-the-distribution-contains-and-what-needs-the-git-repository)
above.


**Using it from a coding agent (`argus-mcp`).** The `argus-mcp` alias starts an
[MCP](https://modelcontextprotocol.io) server that speaks JSON-RPC 2.0 over **stdin/stdout
only** — it binds no port, opens no listener, and accepts no key, token or account. It
publishes exactly one tool, `audit_repository`, whose arguments are the `argus audit` flags and
whose result is the same verdict, exit code and coverage figures the command line returns for
the same arguments. Configure it as a stdio server in your assistant:

```json
{"mcpServers": {"argus": {"command": "argus-mcp", "args": []}}}
```

It takes no arguments; its entire input is the message stream, and it exits when stdin closes:

```bash
argus-mcp
```

**The assistant commands that ship, and the step that places them.** Install the
distribution, then run the sub-command:

```bash
# Print exactly what would be written, and write nothing.
argus install-commands --dry-run

# Place them for every supported host whose configuration directory is detected.
argus install-commands

# Delete exactly what the step wrote, and nothing else.
argus install-commands --remove
```

It accepts `--host <name>` (repeatable), `--dest <dir>` (override the configuration root),
`--dry-run` and `--remove`, and nothing more. **Hosts covered: Claude Code**, whose commands
directory is `~/.claude/commands/`; each supported host is one entry in the closed registry
at [`argus/commands/hosts.py`](argus/commands/hosts.py). The three commands it places are:

```bash
/argus-audit             # Run the full deterministic audit and report the verdict
/argus-audit-security    # Run the security pass alone (secret scan + containment)
/argus-audit-report      # Run the audit and render the four developer markdown reports
```

Each of those is a packaged asset carrying a description and the literal `argus audit …`
line it instructs your assistant to run — no shell beyond that invocation, no network call,
no credential and no interpolation construct. The FR34 instrument-status disclosure is
**rendered into each file at install time** from the one constant that declares it, so the
copy on your disk is never a stale transcription; re-run the step to refresh it. The
spellings above are DERIVED from the shipped asset names and the host registry by
`TC-ArgusAgent-ASSETS-001-06`, never hand-typed here, and that guard fails in both
directions — a command documented with no shipped asset, or an asset absent from this list.


From terminal CLI — the `audit` sub-command is required, and every flag below is the real spelling:

```bash
# The whole contract in one line: audit this repo at HEAD, no ceiling, default passes.
argus audit .

# Release-gate mode, as a CI step would run it.
argus audit . --commit HEAD --strict --budget 500 --materiality-bar critical

# Write the Markdown reports (--reports renders nothing unless --report-dir is set).
argus audit . --report-dir ./argus-reports --reports final-verdict,coverage-ledger
```

> Every `argus …` command line committed in this README, in `action.yml` and in the
> workflows is parsed by the real parser in CI (`TC-ArgusAgent-DOCS-001-28`), so a
> documented invocation that would fail for a reader fails the build first.

---

## 📁 Repository Structure

```
ArgusAgent/
├── argus/                 # Standalone Python Assurance Engine Core
│   ├── assets/commands/   # The ONE command-asset tree — packaged DATA, shipped in the wheel
│   ├── commands/          # `argus install-commands`: the closed host registry + the installer
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
├── templates/             # 8 Developer Report Templates (4 of which are rendered)
├── tests/                 # Comprehensive Test Suite & Defect Cartridges
├── pyproject.toml         # Package definition
├── install.sh / .ps1      # Convenience wrappers; they delegate to `argus install-commands`
└── README.md              # Project documentation
```

> `argus/assets/commands/` is the single command-asset tree. Every `argus …` line inside it
> is parsed by the real parser in CI (`TC-ArgusAgent-DOCS-001-28`), and
> `TC-ArgusAgent-ASSETS-001-07` fails if a second tree ever appears in the repository.

---

## 🛡️ License

MIT License. See [LICENSE](LICENSE) for details.
