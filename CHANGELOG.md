# Changelog

All notable consumer-visible changes to **Agent-Argus** (distribution `argus-agent`, package `argus/`)
are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) loosely;
versioning intent is [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Honesty preamble — read this before you read a version number.**
>
> **Superseded, kept on the record (§3.4).** Until 2026-08-29 this preamble read:
>
> > ~~`argus-agent` is **still not published to any package index**, and no PyPI publication was
> > attempted. What changed with `0.1.0` is that a **release workflow now exists**
> > (`.github/workflows/release.yml`): on a `v*.*.*` tag it builds an sdist and a wheel and attaches
> > both to a GitHub Release. The distribution **will be resolvable by the VCS pin below — and by
> > nothing else — once that tag is created and pushed**. ⚠️ **That command does not resolve today.**
> > Tag `v0.1.0` has **not been created or pushed** (`git tag -l` is empty at this commit), so `pip`
> > cannot find the ref. The capability is *prepared*, not *exercised* — nobody has run this install
> > against a real tag. Creating and pushing the tag is an operator step this repository deliberately
> > did not take.~~
>
> 🔴 **CORRECTED 2026-08-29.** Every sentence above was accurate when written and each one is now
> false in a different way, which is why the block is struck whole rather than patched. What is true,
> **measured 2026-08-29**:
>
> * **The repository is PUBLIC** (`gh repo view Inan15/Agent-Argus --json visibility` → `PUBLIC`).
>   The preamble's predecessor said `PRIVATE`, measured 2026-08-15; that measurement was correct on
>   its date and was never re-run.
> * **A release exists.** Tag `v1.0.0` was pushed 2026-08-28 at `5bd9396`
>   (`git ls-remote --tags origin`), with a published GitHub Release carrying built artifacts.
> * **`v0.1.0` was never created.** Every install line in this repository pointed at a tag that does
>   not exist, while the tag that does exist was named nowhere. The caveats stayed *literally* true
>   and became *collectively* false — which is precisely how a guard keyed to the anticipated
>   version number can watch the wrong one.
> * **Still true, and unchanged:** `argus-agent` is on **no package index**, and no PyPI publication
>   has been attempted. The VCS pin below is the whole resolution story.
>
> The corrected dependency string — this one resolves:
>
> ```
> pip install "argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v1.0.0"
> ```
>
> Prefer a standalone binary to a Python install? The Release page attaches Linux, macOS and Windows
> packages; `install.sh` / `install.ps1` at the repository root fetch and place them.
>
> **What is proven and what is not, stated separately.**
>
> ~~The build was proven **locally**: `python -m build` produced `argus_agent-0.1.0.tar.gz` and
> `argus_agent-0.1.0-py3-none-any.whl`, the wheel was installed into a fresh virtualenv with the
> repository absent from `sys.path`, and `argus --help` and `argus audit <fixture-repo>` both ran to
> completion there.~~
>
> 🔴 **CORRECTED 2026-08-15 by Story 12.9 / AC1.** Struck above rather than deleted (§3.4 evidence
> immutability). That claim was true **by hand** on 2026-08-08 and **no committed guard held it** — and
> the distribution has since gained `argus-mcp` (12.6), three packaged command assets (12.7), nine
> grammar dependencies (12.5) and a changed exit-code contract (12.8). A published claim with no test is
> what this repository files as a defect, so it is now held by a guard and the guard is named here:
> **`tests/test_installed_artifact.py` (`TC-ArgusAgent-RELEASE-001-25`..`-28`)** builds the sdist and
> wheel, installs the **wheel into a fresh environment**, refuses unless `argus` resolves from inside
> that environment (`PROBE-INVALID`), and then exercises the artifact: **every** `[project.scripts]`
> alias — derived by closure over the table, so a fifth is covered with no edit — `argus --help` and
> `argus audit --help`, a **fixture audit to a real verdict** whose stdout summary line parses and whose
> exit code matches the AR3 map, and a **real MCP JSON-RPC exchange over stdio through the installed
> `argus-mcp` shim** (absent from the old claim entirely). What it does **not** test is stated with it:
> the dependencies resolve from the machine rather than from an index, because the test contract is
> offline.
>
> The **workflow itself is committed and has
> never executed** — it was added on a feature branch and no tag exists in this repository yet — so
> ~~there is no Actions run id and no release URL to cite~~. Nothing in this file states or implies that a
> release has been published; when one is, this paragraph gets a URL.
>
> 🔴 **NARROWED 2026-08-16 — struck, not deleted (§3.4 evidence immutability).** That clause conflated
> two different workflows, and one half of it has since become false. `.github/workflows/release.yml`
> is still committed-and-never-executed and there is still **no release URL** — `git tag -l` and `gh
> release list` are both empty, re-measured 2026-08-16. But `.github/workflows/audit-ci.yml` — the
> quality gate, a different workflow — **has** now executed on the commit being released, so an Actions
> run id to cite does exist. ~~It is cited directly below, with the sha it covers and the scope of what
> it did not evaluate.~~ A sentence that says "no run id to cite" three lines above a run id is the kind
> of stale absolute this file exists to stop.
>
> 🔴 **RE-NARROWED 2026-08-16 — struck, not deleted (§3.4 evidence immutability).** That run is now
> NAMED directly below, with the sha it covers, inside a `NOT ESTABLISHED` statement — not cited. The
> reason is in the `RE-DERIVED` note further down and it is structural: `HEAD` has moved past the sha
> that run covers, because rendering the observation onto these surfaces was itself a commit. The run
> id and its sha are still on the page; what changed is which of the derivation's two branches the
> observed facts now imply.
>
> **The release status, DERIVED rather than typed** (Story 12.9 / AC2). One function —
> `scripts/release_notes.py::derive_release_status` — computes it from the observed run, the sha that
> run covers, its conclusion and the commit being released; `TC-ArgusAgent-DOCS-001-25` asserts this
> file and `README.md` carry exactly that value, and the same function renders it into the GitHub
> Release note, so the three cannot disagree.

~~CI evidence: NOT ESTABLISHED. No executed gate covers the commit being released — the most
recent `audit-ci.yml` run is run 33235322979, which covers sha
ac1265e6ffabe0a6cb3b7633dc3107bd3556b274 and therefore evidences a different tree; a run id
quoted without the sha it covers is a half-truth, so it is named here as SUPERSEDED rather than
cited. Observed 2026-08-29 through the GitHub API. The human step that would establish one, and
the only one: push `master` to `origin` and let `audit-ci.yml` run to success on the released
commit, then re-derive this sentence from that run. A local `pytest`/`mypy`/`bandit` run is
necessary, not sufficient, and is recorded as LOCAL (architecture.md §H).~~

🔴 **SUPERSEDED 2026-08-16 — struck, not deleted (§3.4 evidence immutability).** The human step that
sentence named was taken: `master` was pushed to `origin`, `audit-ci.yml` executed on the released
commit, and what follows is the SAME function's output over the new observation. The derivation did not
change; its input did.

~~CI evidence: run 31908861401 (cea92689b14f730ff529caeabd74c1f33f84821b, 3/3 legs green) on
`audit-ci.yml` covers the commit being released. Observed 2026-08-16 through the GitHub API.~~

~~SCOPE of that run, because a green run is evidence for what it EXECUTED and this one did not execute
everything it carries. Each leg reported `1539 passed, 4 skipped`. The run recorded the following as
NOT EVALUATED rather than as passing, so the citation above does not reach them: (1)
`tests/test_installed_artifact.py` (`TC-ArgusAgent-RELEASE-001-25`..`-28`) — the fresh-environment
installed-artifact proof: every `[project.scripts]` console script, `argus --help`, a fixture audit run
to a real verdict, and an MCP JSON-RPC exchange over stdio through the installed `argus-mcp` shim. All
four SKIPPED on all three legs, each reporting the named E6 outcome *NOT EVALUATED — uv is not on PATH,
so the wheel could NOT be installed into a fresh environment and nothing about the INSTALLED
distribution was checked*. So the front-door claim of this release is held by LOCAL runs only, and this
citation does not cover it. Provisioning `uv` on the CI runner is a tooling decision that has not been
taken; it is filed OPEN and unscheduled as `DF-12-9-B`, owned by the Engineering Lead. Reading the
citation as covering these would be the same class of overstatement as quoting a run id without the sha
it covers.~~

🔴 **RE-DERIVED 2026-08-16 — struck, not deleted (§3.4 evidence immutability).** The citation above
was true of the tree it names and is stale for this one, and the reason is structural rather than
accidental: recording an observation and rendering it onto these surfaces is ITSELF a commit, so
`HEAD` moves past the sha the cited run covers the instant the render lands. A surface that insisted
the gate always cover `HEAD` could be true for one moment and never again. What follows is therefore
the SAME function over the SAME 2026-08-16 observation, asked about the commit you are reading
rather than about the commit that run covered — and the struck citation stays visible, because *the
gate has executed green on this branch, at the sha named in it* is a materially different fact from
*no gate has ever run*, and a reader is owed both halves. `TC-ArgusAgent-DOCS-001-25` asserts that
the derivation is right for whichever branch the observed facts imply and that these surfaces carry
that value; it does not require the facts to be one particular way, because a guard that can only
pass in a single instant is the mirror image of one that can never fail.

CI evidence: NOT ESTABLISHED. No executed gate covers the commit being released — the most
recent `audit-ci.yml` run is run 33235322979, which covers sha
ac1265e6ffabe0a6cb3b7633dc3107bd3556b274 and therefore evidences a different tree; a run id
quoted without the sha it covers is a half-truth, so it is named here as SUPERSEDED rather than
cited. Observed 2026-08-29 through the GitHub API. The human step that would establish one, and
the only one: push `master` to `origin` and let `audit-ci.yml` run to success on the released
commit, then re-derive this sentence from that run. A local `pytest`/`mypy`/`bandit` run is
necessary, not sufficient, and is recorded as LOCAL (architecture.md §H).
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

_Nothing yet. The next consumer-visible change lands here._

---

## 1.0.0 — 2026-08-29

> **This heading was `## Unreleased` until 2026-08-29, and the relabel is the correction, not a
> reorganisation.** Everything below this line shipped: tag `v1.0.0` points at `5bd9396` and was
> pushed on 2026-08-28, and GitHub Releases carrying built artifacts exist on both
> `Inan15/Agent-Argus` and `XAgents-ai/argus-agent-releases`. Calling shipped work *unreleased* is
> the same defect class this release is correcting elsewhere in this file, so it is fixed in the
> same change that found it rather than left for a later one.

**What v1.0.0 actually is, stated before the feature list.** It is the `0.1.0` tree plus the changes
recorded below, released under the **FR34 Disclosed Tier**: the >=80% finding-precision gate is
**still not cleared**, `argus.__status__` remains `"beta"`, and every user-facing surface still
carries the provisional notice. **A major version number here records a stable consumer contract, not
a cleared precision gate.** Nothing about the disclosure obligation changed with this number, and a
reader who takes `1.0.0` as evidence of validated precision has been misled — which is why this
paragraph is above the changes rather than below them.

**How it was released, including what refused.** The tag was pushed before `pyproject.toml` was
bumped, so `release.yml` **refused it four consecutive times** (runs 33180657062, 33184222319,
33184399896, 33185012952) on `[E5] tag 'v1.0.0' declares version '1.0.0' but pyproject.toml states
'0.1.0'`, and later also on `[E4] a release already exists for tag 'v1.0.0'`. The preflight was
correct both times. The published artifacts therefore did **not** reach the release page through the
gated path; the version disagreement is fixed in this release, and the record of the refusal is kept
here rather than tidied away.

### Changed — a mistyped invocation is refused, and no longer publishes a verdict

**Read this if you consume `argus`'s exit code, or pass `--passes` / `--skip-pass` / `--reports`.**
Two behaviour changes on a published surface, both in the same direction: the tool now refuses an
invocation it cannot honour instead of running a reduced audit and reporting the result as a normal
one.

**1. An unknown `--passes`, `--skip-pass` or `--reports` token is now refused.** It used to be
accepted and silently ignored. Measured on the shipped tool: `argus audit <repo> --passes securty`
disabled **every** detector pass — the pipeline's membership tests simply never matched — and
returned `verdict=RELEASE_READY`, exit `0`, with no message of any kind. One transposed letter
turned the flag that selects the safety passes into a switch that turned them all off, and the run
looked clean because it had looked at nothing. `--reports` had the same shape and a live instance:
this repository's own CI workflow requested the report type `vacuous-tests`, which does not exist,
so three reports were written where four were asked for and nothing said so. The accepted set is
now derived from the one definition of each vocabulary and is named in the refusal message, and
`--help` states it too. **If a pipeline of yours passes a token that was silently ignored, it will
now fail** — which is the point: it was not doing what it said. This follows the precedent Story
10.3 set when it made the `--ignore-pattern` layering fix the condition of that flag's bless and
announced it here in the same way.

**2. A command line the parser rejects now exits `1`, not `2`.** Every argparse usage error —
`--budget 1.5`, an unknown sub-command, a bare `argus` — used to exit `2`, and `action.yml` maps
exit `2` to `verdict=NOT_READY_FOR_RELEASE` with `assessed=true`. A typo therefore published a
**fabricated assessment of a repository for a run that never happened**. It now returns `1`, the
reserved *the audit did not complete and NO verdict was produced* code the wire contract already
publishes and which `action.yml` already renders as `AUDIT_FAILED` / `assessed=false`. **No new
exit code was added** (AR3 stays `0`/`2`/`3`/`1`), `--help` and `-h` still exit `0` unchanged, and
`2` now means — and can only mean — *the audit ran and found at least one verdict-blocking
finding*. A CI step that branched on `2` to mean "blocked" is unaffected; one that treated a
non-zero exit as a verdict without reading `assessed` was already wrong and is now told so.

Alongside these: every operator error names a **fix** as well as a cause, a missing or unusable
language grammar is reported on the **default** run rather than only inside a generated report, an
internal defect in Argus is now distinguishable on stderr from an expected degradation of your
repository (it says which it is, and where to report the former), and the stderr diagnosis no
longer carries an absolute path from the host filesystem.

### Fixed — the default install now grounds every language the tool claims to support

If your project was not Python, the tool you installed was quietly worse than the tool this project
described. The nine non-Python tree-sitter grammars shipped in an **optional extra**, so the documented
install command grounded Python only: a Go or TypeScript repository enumerated and graded normally, no
file in it could reach `audited_deep`, and the result was a lower coverage ratio that reads as a
judgement about the code. NFR-P3 classifies that as a **packaging defect, not a user error** — a
developer should not have to discover an extra to be given a correct answer.

The nine grammars (`tree-sitter-javascript`, `tree-sitter-typescript`, `tree-sitter-go`,
`tree-sitter-rust`, `tree-sitter-java`, `tree-sitter-c`, `tree-sitter-cpp`, `tree-sitter-ruby`,
`tree-sitter-php`) are now ordinary dependencies of the distribution, alongside `tree-sitter-python`.
There is nothing to add to the install command, and no flag to find.

**`pip install "argus-agent[languages]"` still works.** Story 10.2 documented that extra publicly, so
it exists in somebody's script; it is retained as an alias whose requirements are pinned equal to the
default ones, so it can never resolve to a different set. The cost of the change, stated rather than
buried: every install now downloads nine grammar wheels, including a Python-only one.

**A grammar that is missing anyway now says so where it costs you.** An uninstalled, vendored or broken
grammar — or a `tree-sitter` core that does not pass Argus's own self-check — still degrades a file, and
until now a repository where *some* files parsed was told nothing at all about the ones that did not. The
final-verdict report now names each downgraded file, the depth it actually reached and the exact package
that would have grounded it, and the human-register summary states the same facts once per failure class.
The remedy is per class and never blended: an absent package is a `pip install`, a present-but-unrecognised
one is an Argus defect to report rather than reinstall, and a missing or unvalidated `tree-sitter` core
affects every language at once and says so instead of naming one grammar.

No verdict, exit code, threshold or decision-table row changes. On a machine where every grammar was
already installed — including CI, which sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` — the output is
unchanged.

### Added — `argus-mcp`, so a coding agent can run the audit and read the verdict itself

The distribution now ships a **fourth console alias**, `argus-mcp` → `argus.mcp.server:main`, beside the
three that all run `argus.cli:main`. It is an [MCP](https://modelcontextprotocol.io) server speaking
JSON-RPC 2.0 over **stdin/stdout only**, publishing exactly one tool — `audit_repository` — so the loop
that wrote the code can contain something that checks it, without a human relaying the result.

**Same distribution, same version, same release workflow, and no new dependency.** The JSON-RPC layer is
written against the standard library. The official `mcp` Python SDK was measured and refused: it declares
`starlette`, `uvicorn` and `sse-starlette` as *required* dependencies, because it carries its HTTP server
transports in the base package. Installing it would have put a web server into this distribution's
dependency tree and broken the `argus.* ⊬ fastapi/uvicorn/starlette` isolation gate this project has
enforced since Epic 1. The cost of hand-rolling, stated: Argus owns that protocol code and tracks spec
revisions itself.

**What it does not do, so you can plan around it.** It binds no port and opens no listener. It accepts
and stores no key, token or account. It exposes **no capability the command line lacks** — the same
request, the same pipeline, the same permission boundary — and it publishes no tool but the one. A
`notifications/cancelled` is accepted and consumed but **cannot interrupt an audit already running**: the
server is single-threaded by design and reads the next message only after the current audit completes.
That limitation is stated in the tool description itself, not only here.

**The verdict is the CLI's, by construction rather than by care.** The tool's input schema is *derived*
from the CLI's own argument parser, and a call is turned back into an argv and handed to that same
parser, so every CLI default governs this surface too — including the announced `--coverage-scope`
divergence documented under *Known divergence* below, which is precisely what an adapter that built its
own request would have got wrong. Same repository, same commit, same verdict, same exit code, pinned by
test. Both protocol eras are served: the `initialize` handshake for hosts shipping today, and the
stateless `server/discover` revision for newer ones.

`deep_audit` is exposed here exactly as `--deep-audit` is on the command line — off by default, always,
still the only opt-in to egress, and still disclosing what will be transmitted before the first byte
leaves. Every verdict this surface returns carries the instrument-status disclosure below, and so does
the tool description, which an agent reads *before* it can decide to call the tool.

**This was half of FR35.** ~~The packaged assistant command assets — the `/audit …` commands README marks
FORTHCOMING — are not in this release, and the wheel still ships zero data assets.~~ *(Struck
2026-08-15 — superseded by the section immediately below, which delivers the other half. All three
clauses became false in one change: the assets are packaged, the FORTHCOMING marker is gone, and the
wheel ships data assets. §3.4 — the superseded sentence stays legible with its correction.)* Nothing
here is published: no tag, no release, no index upload.

### Added — `argus install-commands`, so the commands this README documents are the commands you get

The other half of FR35, and the half a `pip install` user could actually see nothing of before: the
distribution now **ships the assistant command assets as data** and ships the step that places them.

```bash
argus install-commands --dry-run   # print exactly what would be written; write nothing
argus install-commands             # place them for every supported host that is detected
argus install-commands --remove    # delete exactly what the step wrote, and nothing else
```

**A second sub-command, not a fifth console alias.** `argus/cli.py` called `audit` *"the only V1
sub-command; an additive seam for future ones"*, and this is that seam being used. The transport here
is argv — identical to the CLI's — so a separate entry point would have been a fork of one, whereas
12.6's `argus-mcp` alias was justified by a genuinely different transport (JSON-RPC on stdio). It
therefore adds **no** `[project.scripts]` entry, and 12.6's MCP tool schema — derived from the `audit`
sub-parser alone — is unchanged.

It accepts `--host <name>` (repeatable; default is every registered host whose configuration directory
is detected), `--dest <dir>` (override the configuration root), `--dry-run` and `--remove`, and nothing
more. It obeys the existing contracts unchanged: the exit-code wire contract, a secret-safe stderr line
and exit `1` on a typed failure rather than a traceback, no absolute host path in any message, and no
`.argus/` write, network call or egress. It writes **only** inside the resolved destination root — a
path escaping it via `..`, an absolute asset name or a symlinked configuration directory is refused
with a typed error.

**Three commands ship, and the published set is asserted equal to the shipped one.** `/argus-audit`,
`/argus-audit-security` and `/argus-audit-report`, covering **Claude Code** (`~/.claude/commands/`).
Every surface that publishes a command list is compared against the packaged asset tree in both
directions, and the surface population is resolved by scanning the repository, so a fourth list added
later is red rather than invisible.

**The instrument-status disclosure is rendered into each placed file at install time**, from the one
constant that declares it — never committed into an asset, because a transcribed copy of a pinned
constant goes stale the day the status changes. Re-running the step refreshes it.

**Removed, in the same change, four commands that could not run** (struck, not deleted — §3.4).
~~`/audit repo`~~ and ~~`/audit architecture`~~ named no pass the tool has (`architecture-review` is a
*report*, already produced by `/argus-audit-report`); ~~`/audit subsystem <name>`~~ needed a scoping
capability that does not exist;
and ~~`/audit resume`~~ had a working engine with no command-line entrance at all — a gap filed as
`DF-3-4-A` and open since Story 3.4, and building one is a later story's work, not a documentation
fix's. Three published lists disagreed with each other before this change (`README.md` seven,
`audit/commands.md` ten, `audit/skill.md` six), and the developer-report count was published as **12**
in three places while four are rendered. All of it is corrected here and struck rather than deleted.

**Superseded: the `adapters/` stub tree.** Six two-to-three-line directories that registered nothing,
were packaged nowhere, and named a seventh host (RooCode) that had no directory at all. One of them,
`adapters/codex-cli/prompt_adapter.md`, published `argus --budget 500` — an invocation the real parser
rejects, the same defect class Story 10.3 corrected in the README, surviving in a file no guard was
looking at. `install.sh` and `install.ps1` both created a `commands/` directory and then copied those
stubs *beside* it, so nothing they reported installing ever appeared, and `uninstall.sh` removed none
of it. There is now exactly one command-asset tree, one placement mechanism, and a removal path.

Nothing here is published: no tag, no release, no index upload, no marketplace listing.

### Specified — every terminal outcome names its next action and the ingestion boundary

Argus now states, on every terminal outcome (`RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`, and the `AUDIT_FAILED` non-verdict), why that outcome was reached and the next action that changes it (FR37).

**The Three-Population Ingestion-Boundary Disclosure.** Every verdict explicitly distinguishes three populations by construction: (1) Never ingested: file suffixes outside `AUDITABLE_SUFFIXES` (e.g. `.yml`, `.md`, `.toml`); (2) Ingested but held out; (3) Assessed.

**Specific Unmet Gate Explanation.** `INSUFFICIENT_COVERAGE` output names the specific unmet gate — minimum floor, ratio, or critical subsystem — with measured figures and the required remediation.

**FR16 Decision Table Immutable.** The verdict decision table in `argus/verdict/verdict_gate.py` is untouched.

### Disclosed — Argus now states its own validation status on every verdict surface

Until this release, Argus stated a release-readiness verdict without ever stating that its own
finding precision has never been independently measured. That was true of **every verdict the tool
has ever emitted**, and it is the one gap that gets worse rather than better on publication.

Every surface that carries a verdict now carries this sentence, and it comes from one constant in
`argus/verdict/negative_assurance.py` rather than from four hand-typed copies:

> Argus's audit is deterministic and reproducible by construction. Argus's finding precision has not been independently validated, so treat a finding as a prompt to look rather than as a verdict; its findings rest on the Argus dogfood corpus, a self-audit of this repository. The >=80% precision gate has not been EVALUATED rather than evaluated and missed: its precision condition is UNEVALUABLE because the ratified corpus was read and no finding was promoted to verdict-eligible, so the ratio has an empty denominator rather than a low value. This notice is removed only when the >=80% precision gate is met; nothing else removes it.

**Where it appears.** On `stderr` after the ship-readiness block on every invocation that printed a
`verdict=` line; in all four generated reports (`final-verdict.md`, `coverage-ledger.md`,
`security-review.md`, `architecture-review.md`); and, in a one-line summary form, in this
distribution's PyPI description and the composite action's Marketplace description. **`stdout` is
byte-unchanged** — it is the wire contract a pipeline parses positionally, so the disclosure stays
off it. The residual is stated rather than hidden: a consumer that discards `stderr` sees a verdict
without the disclosure, which is why the four report artifacts carry it too.

**What it is not.** It is **not** the per-run grade. `grade: demo-heuristic-only` describes how a
single run was configured and is removed by engaging the deep pass; this describes how the tool's
findings have been validated, and is removed **only** when the >=80% precision gate clears. Enabling
a deeper audit changes the run's grade — it does not validate the instrument. It is also distinct
from the negative-assurance scope disclaimer, and both apply.

**It cannot quietly become permanent, and it cannot quietly disappear.** The surface set is closed by
a committed test rather than by an author remembering: `tests/test_instrument_disclosure.py` parses
the report writer's own body and fails if a *fifth* report is written without the disclosure, fails
if a consumer-facing listing surface is added without it, and fails the day an MCP entry point
appears without one. When the precision gate does clear, the same guard fails until the sentence is
**replaced** by the cleared statement — never deleted.

**No verdict, threshold, exit code or decision-table string changed.**

### Fixed — an unvalidated parsing toolchain can no longer produce a false green

Argus resolved the `tree-sitter-<lang>` versions it ran on and folded them into its determinism cache
key, and it had **never once checked whether that toolchain actually behaves the way Argus was
validated against**. Every other verdict was defended — the coverage floor against too little
evidence, the decision table against blocking findings, the depth rules against a wrong 🔴. Nothing
defended against a wrong 🟢 caused by the parser itself, which is the direction that matters: a false
red is an annoyance you argue with, a false green from an assurance tool is the product inverted, and
the user has no way to detect it.

**Measured on a repository above the deep-coverage gate**, with an ordinary, in-bound `tree-sitter
0.25.2` installed and a planted vacuous test present in both runs:

```
healthy grammar : NOT_READY_FOR_RELEASE  exit 2  deep 5/6  blocking 1
drifted grammar : RELEASE_READY          exit 0  deep 5/6  blocking 0
```

A CI gate that blocked now passed. The planted defect never moved — Argus simply stopped corroborating
it against the AST, so a verdict-eligible finding silently became an advisory one, and advisory
findings cannot move a verdict by design. **The coverage ratio is identical in both runs**, so no
number Argus printed could have told you.

Argus now **self-checks the toolchain behaviourally**, per language, at the one seam every parse
already passes through: a pinned snippet is parsed and its extraction compared against a frozen
expectation. When it does not match, Argus **withholds the parser rather than computing a verdict on
top of it**, and the run degrades to the existing `INSUFFICIENT_COVERAGE` / exit 3 — the honest "not
enough was assessed to vouch" answer — with a named reason and an operator remedy. No new verdict, no
new exit code, no decision-table change.

**It is deliberately not a version check.** The failure above happens at an *in-bound* version, so a
version assertion would have been green on the exact tree where the defect was live. The declared
supported range is now checked too, as a second and independent signal, and the previously documented
claim that `tree-sitter` 0.26.0 causes this flip has been **re-measured and corrected** — 0.26.0's
breaking changes touch nothing Argus uses. The `<0.26` bound is **retained** as conservative-by-default
and is unchanged; what changed is that it is no longer the only defence.

**Also fixed:** a grammar-failure cause with no registered operator remedy now raises instead of
silently rendering a different cause's remedy — which would have told you to reinstall a package that
was installed and fine.

### Fixed — a production file is no longer mistaken for a test because its name ends in the right letters

Argus identifies test files partly by naming convention. Three of those conventions were written
without a word separator — `test.java`, `spec.rb` and a bare `test.py` — so they matched a **letter
sequence** rather than a word. Any file whose name merely *ended* that way was classified as a test:
`latest.java`, `myspec.rb`, `respec.rb`, `contest.py`, `attest.py`, `greatest.py`, `latest.py` and
`mytest.py` are all ordinary production code, and all eight were called tests.

**Why that mattered, measured rather than described.** A test file is graded shallow by construction
and is excluded from the critical-subsystem set. On a polyglot repository, a production Java file
that Argus assessed **CRITICAL** was therefore removed from that set under the reason `test_file` — a
statement that was simply false — which left the critical set **empty**, so the release gate's "all
critical subsystems examined deeply" clause was satisfied because there was nothing left to satisfy
it with. `RELEASE_READY` was reachable on a repository whose one critical production file had never
been deep-graded and had been reported to the operator as a test.

**What changed.** Every recognised convention now carries the word boundary that ecosystem actually
uses. Java is matched **case-sensitively** against the original-case filename (`*Test.java` — Maven
Surefire's convention is CamelCase, and the capital *is* the separator; spelling it `_test.java`
would have stopped recognising every Java test in existence). Ruby keeps `*_spec.rb`, RSpec's real
convention. `conftest.py` is now matched as a whole filename and still resolved by its content, so a
`conftest.py` holding only fixtures is production and one holding test helpers is not.

**What this means for your repository, stated plainly rather than hedged.** If your repository
contains any of the affected filenames, **your verdict may move** — and it can only move
**conservatively**: files that were being held out of the assessed population return to it, and a
returning file that Argus cannot ground *lowers* the deep-coverage ratio. It can never turn a
blocking verdict into `RELEASE_READY`. This is not a behaviour-preserving change, and on the
repositories it is aimed at it is not meant to be. Two known losses, stated rather than left to be
discovered: a file named literally `spec.rb` outside a `spec/` directory is no longer a test by name,
and one named literally `test.py` is no longer treated as an ambiguous Python test name (`test_*.py`,
`*_test.py` and `conftest.py` all still are).

**Not fixed, and filed:** several real conventions Argus still does not recognise — minitest's
`*_test.rb`, Surefire's `*Tests.java` / `*TestCase.java` / `Test*.java`, PHPUnit's `*Test.php` and
C's `*_test.c`. Those are the opposite error (a test mistaken for production), they would *widen*
what Argus classifies as a test, and they are tracked separately rather than slipped into this fix.

### Security — the composite action no longer pastes your workflow's inputs into its shell script

If you use `action.yml` (the `ArgusAgent Code Audit & Release Gate` composite action), its four
inputs — `repo-path`, `commit-sha`, `report-dir` and `strict` — were expanded **into the text of the
shell script** before `bash` parsed it. That is GitHub's documented script-injection shape: a
`${{ }}` expression is substituted into the script source, so the value is code rather than data.
A workflow that wired any of those inputs to a value an outsider can influence — `${{ github.event.issue.title }}`
is the common one — could have had arbitrary commands run in **its own** job, with that job's token,
`$GITHUB_ENV`, `$GITHUB_OUTPUT` and checked-out source in reach.

Every value the action's shell touches is now bound through a step-level `env:` map and referenced as
a double-quoted shell variable (`"$REPO_PATH"`, `"$COMMIT_SHA"`, `"$REPORT_DIR"`, `"$STRICT"`),
following the discipline `.github/workflows/release.yml` already documented. `github.action_path` on
the install step was bound the same way — it is set by the runner and was never attacker-settable, so
it was not part of the defect; it is included so the file carries zero interpolations inside any
`run:` body rather than one with a footnote. `tests/test_workflow_input_containment.py` now fails on
the next such interpolation written anywhere in this repository's workflows, in both the block-scalar
and the single-line `run:` form.

**Do I need to change anything?** No. No input name, default or description changed; no output name
or value changed; the exit-code map, its `::error::` strings and `assessed` are untouched. A workflow
already using this action needs no edit and will behave identically.

**What is not claimed.** This hardens the action; it does not publish it, and the action is still not
listed on the GitHub Marketplace. The fix was verified by local text-invariance tests on Windows /
CPython 3.11.15 — the property proven is that the script text cannot vary with an input value. **No
CI run has executed this action**, before or after the change, so nothing here rests on a runner
having exercised it, and no statement above should be read as a claim about Argus's finding
precision, which remains not independently validated.

### Fixed — five shipped modules could not be imported from the distribution at all

Installing the distribution and then running `import argus.precision` raised
`ModuleNotFoundError: No module named '_registry'`. Five of the seventy-two shipped modules did it —
`argus/precision/__init__.py`,
`argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`, `argus/dogfood/proof_render.py`
and `argus/dogfood/proof_run.py` — because the precision replay harness inserted `tests/cartridges/`
onto `sys.path` and imported its labelled-cartridge registry **at module import time**, and `tests/`
is not in the distribution (and must not be: it is the golden-key store the precision number is
measured against). The registry is now resolved **lazily**, on first use. Measured on a freshly built
wheel with this repository removed from `sys.path`, one clean subprocess per module: **72 of 72
import**, against 67 of 72 before. `argus audit` was never affected — no consumer-facing module was
ever on that path — and no verdict, exit code, threshold, default or rendered `stdout` string changed.
*Running* the precision replay or the dogfood proof generator still needs the git repository, because
that is where the labelled cartridges live.

**The guard that was supposed to hold this was blind, and that is the more important half.** The old
guard walked the *source tree* with `ast`. It stayed **green across the entire fix** — an
`import _registry` inside a function body is the same AST node as one at module level — and it never
noticed the published figures rotting from "66 of the 71" to a measured 67 of 72 while it watched,
because it pinned a set of paths and the documents publish numbers. It is replaced by
`TC-ArgusAgent-RELEASE-001-20`, which **builds the wheel and the sdist and imports every shipped
module out of the built artifact**, and by `TC-ArgusAgent-DOCS-001-54`, which asserts the published
figures against that measurement in both directions.

**Also corrected in the documents, because a shipped artifact that says untrue things is the same
defect.** The instrument-status disclosure printed on `stderr` by every `argus audit` run said its
findings rest on *"the Minions dogfood corpus"* and then described that corpus, four words later, as
*"a self-audit of this repository"*. The **subject** was wrong and is now *"the Argus dogfood
corpus"*; the claim, the negation, the status vocabulary and the removal condition (Epic 13's human
adjudication, and nothing else) are unchanged. README's *"When installed, `ArgusAgent` registers slash
commands in your AI coding assistant"* is corrected to what the wheel measurably contains — three
console aliases (`argus`, `argus-agent`, `repo-audit`), all three entry points for `argus.cli:main`,
and zero data assets — and the seven ~~`/audit …`~~ commands are **marked forthcoming** against Story
12.7 / FR35 rather than deleted, with a test that fails if the marker outlives the gap or is removed
before it closes. *(Amended 2026-08-15 — the marker's gap is CLOSED by the section*
*"Added — `argus install-commands`" above: the wheel now ships data assets, the seven commands are*
*superseded by three that resolve, and the same test now holds the published set equal to the shipped*
*one. §3.4 — the sentence stays legible because it is the record of why the marker existed.)*

Every figure above is LOCAL, Windows / CPython 3.11.15. **CI evidence: NOT ESTABLISHED** — no CI run
has executed this change. Nothing here is published: no tag, no release, no index upload.

### Specified: `--deep-audit` — the opt-in deep pass, and the false deep claim it replaces

`argus audit` now accepts **`--deep-audit`**, which enables the LLM-backed deep-audit pass (FR36).
**It is off by default, always, and it is the only way to turn it on.** No environment variable and
no packaging extra enables it. Without it, this release is byte-identical to the last one: same
verdict, same exit code, same coverage figures, same report bytes, same `.argus/` bytes, and nothing
leaves your machine.

**This is the only path in Argus that can transmit anything off your machine.** When you pass the
flag, the run states — on stderr, **before the first byte is sent** — how many files' metadata will
be transmitted and to which provider host. What is sent is audit metadata: repo-relative file paths,
a tier hint and a prompt-template version. File contents are not sent.

**Fixed at the same time, and the reason this is one entry rather than two:** the token `deep` was
already accepted in `--passes` and already claimed a deep read that never happened. `--passes` is
not validated against the known pass names, so `argus audit <repo> --passes coverage,deep` printed

> *What `audited_deep` means in this run: a deep read was dispatched for the file and its claim was
> validated against the repository AST.*

on a tree where nothing dispatched and the deep-audit seam had **zero callers**. The sentence was
derived from the presence of a string in a CSV. It is now derived from what the pass actually did,
and there are three states rather than two: not requested; requested and delivered; **requested and
not delivered**, which now says so plainly instead of claiming depth.

**Consumer impact.** If you passed `--passes …,deep` before, you were told a deep read had happened
and it had not. You will now be told the truth, and the files that were counted `audited_deep` on
the strength of that claim are recorded `audited_shallow` instead — they stay in the denominator,
graded at the depth they actually earned. That can lower a deep-coverage ratio and, for that
invocation only, change a verdict from `RELEASE_READY` to `INSUFFICIENT_COVERAGE` (exit `3`). **No
default invocation is affected**, because `deep` is not in the default pass set and never was.

**When the pass cannot run, it degrades and says so — it never fabricates.** An unreachable
provider, an erroring provider, an empty or malformed response, a mid-run model change, an
unconfigured provider, or a budget ceiling reached mid-pass all produce the same honest outcome: a
recorded finding naming each file that was not deeply read, a coverage downgrade for those files,
and a verdict that does not claim depth it did not get. Spend flows through the **existing**
`--budget` ceiling — there is no new budget, no new threshold and no new default.

**No FR16 row, threshold, boundary or exit-code mapping changed.** No network listener is added and
no port is bound.

**⚠️ KNOWN LIMITATION — what `--deep-audit` does NOT yet do, stated here rather than left for you
to discover.** The bundled provider adapter does not currently return the model's answer in the
form the pass consumes: it captures the model id, the token counts and the finish reason, and
discards the completion itself. The practical consequence is that **today, with any provider you
configure, the third state above is the one you will get** — *requested and not delivered*. The
run will dispatch, tell you it dispatched, bill the spend against `--budget`, then report that it
did not get a usable deep read and grade the files at the depth they actually earned. **Nothing
about that is unsafe** — it is the same honest degradation as an unreachable provider, and no deep
claim is ever fabricated — but if you enable this flag expecting deeper coverage, you will not get
it yet, and you should not pay a provider for it. This is tracked as `DF-12-2-D`; closing it needs
a declared claim format the model is actually asked to produce, which is a separate piece of work.
**`--deep-audit` is shipped as the safe, disclosed, opt-in egress path it is, not as a finished
depth feature.**

Every figure above is LOCAL, Windows / CPython 3.11.15. **CI evidence: NOT ESTABLISHED** — no CI run
has executed this change. Nothing here is published: no tag, no release, no index upload.

### Specified — six CLI flags that shipped in `0.1.0` accepted and specified nowhere

`argus audit` has always accepted more than its published invocation contract described. Measured on
2026-08-10 against the full binding corpus — the PRD, the architecture, the epics, this file and the
README — **six accepted flags had zero occurrences in any of them**: `--passes`, `--skip-pass`,
`--reports`, `--strict`, `--ignore-path` and `--ignore-pattern`. An integrator could not discover
them, and could not rely on them, because nothing said what they did.

**These are not new flags.** Every one of them shipped in `0.1.0`; four entered in the repository's
root commit and were inert until 2026-08-09. **No default changed and no verdict moved**, with the
single deliberate exception recorded under *Fixed* below. What this release adds is the
specification, and a test that keeps the specification and the parser equal: the accepted surface is
now derived from `argus/cli.py::build_parser` at test time and compared against a declared contract
registry in **both** directions, so a flag can no longer reach a user unspecified, and a document can
no longer name a flag the tool rejects.

The per-flag statement of record is the *"The LOCKED CLI contract"* block in
[`argus/cli.py`](argus/cli.py), which now carries every accepted argument with its default and its
owning story. The sections below state what a consumer needs.

#### Specified: `--passes` and `--skip-pass`

- **`--passes <csv>`** selects exactly the audit passes named (`coverage`, `vacuous`, `security`,
  `orphan`, `prosecutor`). Omitted, every pass runs. A trailing comma is not a selection, and an
  explicit `--passes` that selects **nothing stays empty** rather than reverting to the default —
  narrowing to zero is an operator statement, not a missing one.
- **`--skip-pass <pass>`** is repeatable and **subtracts only**. It removes passes from whatever
  `--passes` selected; it can never re-add one the operator excluded. Two narrowing flags that could
  widen each other would let a typo silently broaden an audit that was meant to be bounded.
- The narrowing is already disclosed to the operator: the enabled pass set is printed with the
  ship-readiness block, so a partial audit never reads as a full one.

#### Specified: `--reports` and `--report-dir`

- **`--reports <csv>`** selects which report types are rendered. Default:
  `final-verdict,coverage-ledger`.
- ⚠️ **`--reports` is conditionally inert.** Reports are only rendered when **`--report-dir`** is
  set, so `--reports` on its own renders nothing. This is stated rather than left to be discovered:
  blessing a flag while concealing that it does nothing half the time would be the same defect this
  entry exists to close.
- **`--report-dir <path>`** is the output directory for the generated Markdown reports and the
  switch that makes `--reports` do anything. It was thinly documented (one README table row and one
  `action.yml` input) and is now specified alongside the rest.

#### Specified: `--strict`

- **`--strict`** is release-gate mode: it requires a git repository, a clean working tree, and
  `HEAD == --commit`, and refuses otherwise with a typed error. It is the enforcement of the FR1
  determinism pin — without it there is no lever that refuses a drifted tree.
- **Off by default, and that is deliberate.** A first run must work on any directory, including one
  with no git metadata at all; such a run is audited as-is and **recorded** as non-reproducible
  rather than refused. Use `--strict` in CI, where commit-pinned evidence is the contract.

#### Specified: `--ignore-path` and `--ignore-pattern`

Both suppress findings from the secret scan, and both are now bounded, recorded and disclosed. The
reasoning is written up as the **[Suppression threat model](_bmad-output/design-artifacts/ArgusAgent/architecture.md)**
in architecture §G — read it before using either flag in a pipeline.

- **`--ignore-path <glob>`** (repeatable) extends the built-in test/fixture path patterns. Matched
  case-sensitively so the same repository cannot hide a credential on one host and report it on
  another.
- **`--ignore-pattern <substr>`** (repeatable) suppresses a secret finding whose value contains the
  pattern. It matches by **bare substring**, so a short pattern is a wide net; that residual risk is
  stated in the threat model rather than engineered away here.
- **Neither flag can suppress a high-confidence live production key** — an AWS access key, a GitHub
  PAT, a Slack token or a PEM private-key header. Only an explicit inline `# argus:ignore`
  annotation, which lands in a diff where a reviewer sees it, still can.
- **A suppression you caused is now recorded and disclosed.** Every run prints one stderr line
  saying how many security findings your `--ignore-*` rules suppressed — including when the answer
  is none — and each one is recorded as a non-blocking `operator_suppressed_secret:<reason>` finding
  carrying its reason token and its locator and nothing else: never the secret, never source bytes,
  never your pattern, never an absolute path. **The record can never block a release on its own.**

### Fixed — `--ignore-pattern` could defeat the live-key safeguard it was documented to sit under

The secret-suppression engine's own design states that *"high-confidence live production key
signatures override folder glob exemptions unless annotated with an explicit inline line comment."*
It evaluated the CLI-supplied `--ignore-pattern` rules **above** that safeguard instead of below it.

- **Measured before:** `--ignore-pattern "A"` — one character — suppressed every live AWS key,
  GitHub PAT, Slack token and `BEGIN RSA PRIVATE KEY` block in the audited repository, and nothing
  was recorded anywhere: the reason token was discarded on the spot. `--ignore-path 'argus/**'`
  suppressed none of them, so the two flags were never the same risk. **After:** neither flag can
  reach a live key, and any suppression either one causes is recorded and disclosed.
- **This is the one behavioural change in this entry**, and it only ever *reports more*. An
  invocation that passed no `--ignore-pattern` is unaffected. An invocation that used one to hide a
  live production key will now report it — which is the point.
- Inline `# argus:ignore` annotations keep their top precedence, deliberately: they are reviewable
  where they are written.

### Known divergence — `--coverage-scope`'s default differs between the CLI and the library

Stated because it is real, not because it changed. **`--coverage-scope` defaults to `application` at
the CLI**, as announced under *Defaults* below; **`AuditRequest.coverage_scope` defaults to
`repository`** for a consumer constructing the request directly in Python. The same audit therefore
assesses a different population depending on which door you came through. Both are shipped,
announced surfaces, so neither is changed here; the divergence is now pinned in both directions by
test so it cannot drift silently, and aligning them — a behavioural change to two published defaults
— is deliberately left to its own release with a migration note.

### Documented — the `[languages]` extra, which shipped undocumented

Multi-language AST grounding has been in the product since before `0.1.0` and appeared in neither this
file nor the README. A consumer auditing a Go or TypeScript repository had no way to discover that the
capability existed, or that an optional install unlocked it. It is documented now, in
[README §the `[languages]` extra](README.md#auditing-a-non-python-repository-the-languages-extra).

- **`pip install ".[languages]"`** adds nine tree-sitter grammars — JavaScript, TypeScript, Go, Rust,
  Java, C, C++, Ruby, PHP — on top of the Python grammar in the base dependencies. The languages Argus
  reads are the suffixes in `argus/shared/source_languages.py`; that module is the source of truth.
- **Without it, the default install grounds Python only.** A file in another language is still enumerated
  and still graded; it is capped at shallow, reported as `ast_eligible=False` with a named reason token
  (e.g. `grammar_missing_go`). Never a silent drop, and never a deep claim Argus could not verify —
  enumerable is not the same as deeply auditable.
- **No default changed and no verdict moved.** This release documents an existing capability; where the
  grammars live is an open packaging decision, not settled here.

### Fixed — TypeScript and PHP were reported as missing grammars they already had

`ast_index` resolved every grammar through `tree_sitter_<lang>.language()`. Two of the ten packages do
not export it — `tree_sitter_typescript` exports `language_typescript`/`language_tsx`, `tree_sitter_php`
exports `language_php`/`language_php_only` — so both returned `ast_eligible=False` with
`grammar_missing_typescript` / `grammar_missing_php` **while installed**, telling an operator to install
a package they already had. Grammar loading now resolves a per-language entry point, with a suffix-level
override so `.tsx` gets the JSX-aware grammar rather than a syntax error.

- **Measured before:** 8 of 10 languages grounded. **After:** 10 of 10, plus the `.tsx` dialect.
- **No verdict on this repository changed** — it tracks no `.ts/.tsx/.mts/.cts/.php` files, and the
  dogfood verdict is byte-identical either side of the change. A polyglot repository will see *more*
  files reach `audited_deep`, never fewer, and never a file that did not genuinely parse.
- **Known limit, stated rather than left to be found:** C, C++, Ruby and Rust ground but extract no
  definitions yet, so files in those four cannot reach `audited_deep`. Tracked as `DF-10-2-A`.

### Changed — the memoization cache key now names the grammar that actually parsed

Internal (no memoization store is wired into the pipeline yet, so no cached result exists to invalidate).
The recording-producing closure folded **one** grammar version, resolved from `tree-sitter-python`, while
the index parsed ten languages at versions spanning 0.23.1 → 0.25.0 — so upgrading the Go, Rust, Java, C,
C++ or Ruby grammar did not move the key. Provenance is now per-grammar and records only the grammars
that **participated** in the audited build, so the key stays a function of the audit rather than of the
host's installed packages. `CACHE_KEY_SCHEMA_VERSION` is bumped `"2"` → `"3"`; `AstIndex.schema_version`
`"1"` → `"2"`. Both changes are additive — `grammar_version` is retained.

### Changed — the release note and the release status are generated from their sources, and the status now cites its gate

**Nothing a pipeline can trip over.** No default, no exit code, no verdict, no threshold and no
`stdout` byte moves. What changes is what this release says about itself, and how it comes to say it.

**The GitHub Release note is generated, not typed.** It used to be a string literal inside a `run:`
block in `.github/workflows/release.yml`, and that literal hand-transcribed three pinned facts: the
exit-code wire contract, the install command, and a *paraphrase* of the instrument disclosure. When the
previous release changed what exit `2` can mean, the literal did not move — nothing could see it. The
body is now rendered by `scripts/release_notes.py`, which derives the version from `pyproject.toml`, the
exit-code map from `argus/verdict/verdict_gate.py` plus the reserved code in `argus/cli.py`, the
disclosure from `argus/verdict/negative_assurance.py` in its canonical form, and the install command
from the tag. `TC-ArgusAgent-DOCS-001-67`/`-68` render it and assert every claim against the live
constant, in both directions.

**The release status is derived, and it now CITES the gate.** One function computes it from the
observed CI run, the sha that run covers, its conclusion and the commit being released; `README.md`,
this file and the release note all render that one value. ~~The honest answer at this commit is stated
in the preamble at the top of this file: no executed gate covers the commit being released. That is a
first-class recordable state, not a gap.~~

🔴 **RE-DERIVED 2026-08-16 — struck, not deleted (§3.4), and the section heading above was corrected
with it.** When this entry was written the derivation's honest output was `NOT ESTABLISHED`, because no
`audit-ci.yml` run covered the commit being released. `master` has since been pushed and the gate ran
green on the released commit, so the same function — unchanged — now returns a citation. The statement
is in the preamble at the top of this file, and it carries its own SCOPE: the cited run reported `1539
passed, 4 skipped`, and the four skips are the fresh-environment installed-artifact guards, which the
CI runner cannot execute because it has no `uv`. That proof is held by LOCAL runs only and the citation
says so. `NOT ESTABLISHED` remains a first-class recordable state and remains this derivation's answer
the moment the released commit outruns the gate again.

**The install caveats now track the real tag state on every surface that carries them.** The guard that
holds *"this command does not resolve today"* used to read `README.md` alone while the pin also appears
in this file and in `docs/first-run.md`. It is now a closure over every registered release surface, so
the day the tag exists all four pins are reported at once instead of two of them silently becoming
false.

**The repository's visibility has been measured, and it changes what the documented install costs you.**
See *Resolving `argus-agent`* below: it is **private**, so the pinned install cannot resolve without a
read credential — with or without the tag. Both documents previously said the visibility had never been
checked.

---

## 0.1.0 — 2026-08-08

**Version note.** `0.1.0` is shipped **un-bumped**: the version this repository has always declared is
the version being released, so `pyproject.toml`, `argus.__version__` and every in-package reference now
state one value reachable from one source (see [Version](#version-one-value-one-source) below). The
maturity marker stays `__status__ = "experimental"`: the public **Python API** is not stable across
versions. The **CLI wire contract** — exit codes and the stdout summary line — is separately frozen and
is unchanged by this release.

### Resolving `argus-agent`

> 🔴 **CORRECTED 2026-08-29 — read this before the table.** The row below recorded, on 2026-08-08,
> that the pin *did not resolve yet* because tag `v0.1.0` had not been created. **`v0.1.0` was never
> created at all.** The first tag this project ever pushed was `v1.0.0`, on 2026-08-28. So this row
> described a resolution route that never came into being, and the caveat outlived the release it was
> waiting for. The row is amended in place rather than struck, because striking it would leave the
> dead pin as the most prominent text in the 0.1.0 section; the sentence it replaced is quoted here
> in full instead: ~~"⚠️ **does not resolve yet: tag `v0.1.0` has not been created or pushed**
> (`git tag -l` is empty at this commit). Prepared, not exercised."~~ For the route that does work,
> see the 1.0.0 section above.

| | |
|---|---|
| **Dependency string** | `argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v1.0.0` — the pin recorded here in 2026-08-08 named `v0.1.0`, a tag that was never created; see the correction directly above. |
| **Index** | none — `argus-agent` is on no package index |
| **Authentication** | **none required if and only if the repository is public.** ~~⚠️ Visibility was NOT measured when this line was written; open the URL signed out to check. If it is private, the consuming CI needs a read token and must carry it in the URL.~~ 🔴 **CORRECTED 2026-08-15 (Story 12.9 / AC4)** — struck, not deleted (§3.4). It has been measured, and the correction is the paragraph directly below this table. |
| **Status** | **INTERIM.** A git ref is not an immutable index artifact: it depends on the repository staying reachable and the tag staying put. |
| **Exit condition** | When `argus-agent` is claimed on PyPI **and** a PyPI Trusted Publisher (OIDC) is configured for this repository, the publish step is added directly to `.github/workflows/release.yml` — trusted publishing cannot be used from inside a *reusable* workflow — with `permissions: id-token: write` and **no stored token**, and the pin above is replaced by a plain index install of the distribution name. **RE-AFFIRMED 2026-08-15 (Story 12.9 / DN-1):** the index channel still does not ship and no publish was attempted; this condition is restated with a date so *"interim"* keeps a named end rather than becoming permanent by silence. |

Repository visibility, MEASURED 2026-08-29 by `gh repo view Inan15/Agent-Argus --json
visibility,isPrivate` -> `PUBLIC` / `isPrivate: false`. What that buys a consumer, stated
plainly: the pinned install resolves for anybody with no credential, and the GitHub Release and
its attached packages are publicly downloadable. This SUPERSEDES the 2026-08-15 measurement,
which read `PRIVATE` / `isPrivate: true` and said the pinned install cannot resolve for anybody
— tag or no tag — without a read credential carried in the URL
(`git+https://<credential>@github.com/...`) — accurate on its date, never re-run for fourteen
days, and false for an unknown part of them. That is the whole hazard of this sentence: it is a
dated measurement, not a standing claim, and re-running the command above before relying on it
is the only thing that keeps it true.

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
built artifacts: the wheel holds 96 modules plus the packaged command assets and metadata; the sdist adds
`pyproject.toml`, `README.md`, `LICENSE` and `PKG-INFO`. The RAM workflow directories (`audit/`,
`phases/`, `templates/`) and the installer scripts are **repository-only** — see README.md for the full
capability split. *(Amended 2026-08-15 by Story 12.7: the module figure moved with the tree, ~~`adapters/`~~
was superseded by the packaged `argus/assets/commands/` tree, and "and nothing else" no longer implies
zero data assets — `flit_core` ships every file under `argus/`, so the command assets reach the wheel
with no build-backend change and reach the sdist because they are tracked.)*

Measured on the built wheel with this repository removed from `sys.path`, one clean subprocess per module:
**96 of the 96 shipped modules import.** None fail. (The figure read 73 of 73 when `0.1.0` was
written; it is DERIVED from the freshly built artifact by `TC-ArgusAgent-DOCS-001-54` — *the artifact
is the fact* — and moved to 95 on 2026-08-23 when Story 16.7 added
`argus/precision/silent_class.py`: the V2 SILENT predicate and the record that publishes the class
it derives as a question for a named human, promoting nothing and gating nothing. It moved to 94
earlier the same day when Story 16.5 added
`argus/precision/gate_independence.py`: the closed four-member vocabulary that says WHO judged the
adjudication behind the precision figure and whether they were independent of the tool's authors,
derived from the committed record and rendered onto the same sentence as the figure so the two
cannot be quoted apart. A DISCLOSURE, not an eighth §5 condition — protocol §5 stays at seven and
the derived answer today is `NOT_INDEPENDENT`, which is the correct output rather than a failure.
It moved to 93 on 2026-08-22 when the `DF-15-2-D` cohesion split carved
`argus/detectors/vacuous_vocabulary.py` out of `argus/detectors/vacuous_test.py` at 1,196 of 1,200:
names only, no scoring and no behaviour change, with every moved name re-exported so no import path
changed. It moved to 92 on 2026-08-20 when Story 16.3 added
`argus/precision/gate_yield.py`, protocol §5's SEVENTH condition — the YIELD floor under the
precision ratio's denominator — and to 91 the same day when Story 16.2 added
`argus/precision/gate_seal.py`, protocol §5's SEAL condition and the pure partition rule it rests
on, and to 90 the same day when that story split
`argus/precision/gate_decision.py` into `argus/precision/gate_conditions.py` and
`argus/precision/gate_evidence.py` to discharge `DF-16-1-B`'s SPLIT-FIRST trigger before a sixth
§5 condition landed in a module already at 1,197 of 1,200 lines, and moved to 87 on 2026-08-17 when Story 14.1 split
`argus/detectors/provenance_scan.py` out of the vacuous-test detector — the line-oriented
source-text scan behind AST corroboration fact (b), extracted so the detector keeps NFR-M1
headroom for Stories 14.2 and 14.3 — then from 86 on 2026-08-17 when Story 13.3 added
`argus/precision/gate_decision.py` and `argus/precision/gate_disclosure.py`, which compute
protocol §5's four conditions over the committed adjudication record and disclose the concentration
of the population they were computed over, then from 84 on 2026-08-16 when Story 13.2 added
`argus/precision/adjudication.py`, the adjudication record the >=80%-precision gate is measured
from, then to 74 on 2026-08-13 when Story 12.2 added `argus/audit/deep_pass.py`, then
to 75 later the same day when Story 12.3 added `argus/cache/stage_memo.py`, the production call site
that wires the FR27/NFR-D1 memoization store, then to 78 on 2026-08-15 when Story 12.6 added the
three-module `argus/mcp/` stdio adapter behind the `argus-mcp` entry point, then to 83 the same day
when Story 12.7 added `argus/assets/` + `argus/assets/commands/` (the packaged command-asset tree, a
real package so `importlib.resources` resolves it from a built distribution) and `argus/commands/`
(the closed host registry plus the installer behind `argus install-commands`). The
count is restated rather than frozen precisely so it cannot go stale, which is the defect this guard
exists to catch; nothing about the `0.1.0` release itself is amended.) Five modules did fail until
2026-08-12 —
`argus/precision/__init__.py`, `argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`,
`argus/dogfood/proof_render.py` and `argus/dogfood/proof_run.py` — because the precision harness imported
its labelled-cartridge registry from `tests/`, which is not shipped, and the other four reached that
import transitively. The registry is now resolved lazily (`DF-9-2-A`, **CLOSED**); *running* the
precision replay or the dogfood proof generator still needs the git repository, because that is where the
labelled cartridges live. Those are Argus's own self-audit tools; the entire `argus audit` path is
unaffected and was executed from the installed wheel. Every figure in this section is re-derived from a
freshly built wheel and sdist by `TC-ArgusAgent-DOCS-001-54` and `TC-ArgusAgent-RELEASE-001-20`, so it
cannot drift from what actually ships.

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
