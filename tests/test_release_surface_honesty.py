"""Story 9.2 / AC12 + D12 — the release surfaces are an enumerated space, and they are honest.

Verification area ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-16``..``-18``, CONTINUING the
index locked by Story 8.4; ``-01``..``-13`` were taken, ``-14``/``-15`` are Story 9.2's
version-surface enumeration in ``tests/test_release_note.py``).

Two things are pinned here, in one file because they fail for the same reason — a guard
that names the files that existed when it was written.

**1. The release note's section list (D12, closing ledger item ``DF-8-4-B``).**
``DF-8-4-B``'s ``target_story`` is *"the first story after 8.5 that edits
``tests/test_release_note.py`` (or Epic-9 ``9-2``, whichever fires first)"*. BOTH clauses
fire here, because AC6 had to update ``TC-ArgusAgent-DOCS-001-01``'s ``## Unreleased``
pin. Its suggested close was a section-presence assertion over each ``###`` heading PLUS a
bytes-example equality check. **The heading half is closed by ``-16``. The bytes-example
half is left OPEN and recorded as such in ``deferred-work.md``**: the note already carries
byte-equality assertions over the surfaces that matter — the FR16 decision table, the
ship-readiness headlines, the ``final-verdict.md`` callouts and the persisted assurance
sentences are each compared byte-for-byte by ``-03``..``-06`` — so a second generic bytes
check would add duplication rather than coverage. Naming which half closed is the
disposition; closing one half silently would not be.

**2. No release surface presents the self-audit as assurance (AC12, SD-2).**
The repo separation silently changed the CLASS of Argus's flagship evidence. Story 8.5
measured it: the preserved independent Minions run found 2906 findings over 135 files and
returned ``NOT_READY_FOR_RELEASE`` (exit 2); the re-derived Argus SELF-audit finds ~101
over 69 files and returns ``RELEASE_READY`` (exit 0). A self-audit is materially weaker
evidence than an independent-repository run and is NEVER independent corroboration, and
the >=80%-precision externalization gate is defined over the Minions population, which can
never be re-derived in this repository.

A release is where a project describes itself to strangers, so it is the moment that
distinction is most likely to be lost. ``-17`` asserts no registered surface over-claims;
``-18`` asserts the registry is CLOSED — a new consumer-facing surface added to the
release without being registered fails, which is the ``_REPORT_POINTERS``
fail-on-unregistered shape Story 8.3 established for exactly this (AI-E8-6). All five
Epic-8 stories shipped a guard narrower than its own AC by omitting this half.
"""

from __future__ import annotations

import re
from pathlib import Path

from argus.reports.plain_english import TERMINAL_OUTCOMES
from argus.verdict.verdict_gate import Verdict, exit_code_for_verdict

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CHANGELOG = _REPO_ROOT / "CHANGELOG.md"
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"

# Every `###` section the note carries, in order, as of 0.1.0. The registry is the
# enumerated space: removing a section fails, and ADDING one without registering it fails
# too — so a future edit can neither quietly drop the exit-code contract nor bolt on an
# unreviewed claim section.
_NOTE_SECTIONS: tuple[str, ...] = (
    # `## Unreleased` — added 2026-08-15 by Story 12.8 (AC3 + AC8). A PURE INSERTION: no existing
    # section moved relative to any other, and nothing was demoted.
    # Placed FIRST, and the placement is the DECISION this registry's comment above demands rather
    # than a default. The registry's stated principle is *what a consumer of THIS release hits
    # first*, and the three entries below it — 12.5's grammars, 12.6's fourth alias, 12.7's data
    # files and second sub-command — each won their places on the ground that they change what a
    # consumer HAS before Argus has run at all. This one is promoted above all three on a stronger
    # reading of the same principle, and the promotion was not taken lightly.
    # It is the ONLY entry in the whole note that can BREAK AN EXISTING PIPELINE ON AN UNCHANGED
    # REPOSITORY, in two directions at once: a `--passes` / `--skip-pass` / `--reports` token that
    # was silently ignored now fails the run, and an invocation the parser rejects now exits `1`
    # where it exited `2`. A consumer meets an install-time change when they choose to upgrade;
    # they meet this one in a red pipeline they did not touch. It is also the only entry that
    # REMOVES A FALSE STATEMENT THE TOOL WAS MAKING ABOUT THEIR CODE — a typo used to publish
    # `NOT_READY_FOR_RELEASE assessed=true` for a run that never happened, and `--passes <typo>`
    # used to publish `RELEASE_READY` for a run that examined nothing — so a reader who weighs any
    # other claim in this note needs this one first to know whether a past verdict meant anything.
    # It sits ABOVE 11.1's instrument disclosure for the reason 12.5's, 12.6's and 12.7's do, and
    # without competing with it: 11.1 bounds how far to trust a verdict the tool DID produce, while
    # this section is about verdicts it should never have produced at all.
    "### Changed — a mistyped invocation is refused, and no longer publishes a verdict",
    # `## Unreleased` — added 2026-08-15 by Story 12.5 (NFR-P3). A PURE INSERTION: no existing
    # section moved relative to any other, and nothing was demoted.
    # Placed FIRST, and the placement is the DECISION this registry's comment above demands
    # rather than a default. Promotion above 11.1's instrument disclosure — which has held first
    # place since it was registered, on the ground that it bounds how a consumer should weigh
    # every other claim in this note — was NOT taken lightly, and it survives the registry's own
    # stated principle, *what a consumer of THIS release hits first*, applied literally: this is
    # the only entry in the note that changes what `pip install` puts on their disk, and it is
    # therefore the only one they encounter before Argus has run at all. It is also the only
    # entry that silently changed the ANSWER for a whole class of user — a non-Python repository
    # was graded by a tool that could not read it — and 11.1's disclosure is what tells them how
    # much to trust the answer, which is a question that arises after there is one. Everything
    # below it can move a verdict, an exit code or a claim; this one moves what the product IS.
    "### Fixed — the default install now grounds every language the tool claims to support",
    # `## Unreleased` — added 2026-08-15 by Story 12.6 (FR35). A PURE INSERTION: no existing
    # section moved relative to any other, and nothing was demoted.
    # Placed SECOND, and the placement is the DECISION this registry's comment above demands
    # rather than a default. It is NOT placed first: 12.5's entry stays there on its own
    # recorded ground — it is the only entry that changes what `pip install` puts on a
    # consumer's disk before Argus has run at all — and this entry is the second such, which
    # is exactly why it sits directly beneath it rather than anywhere else. Applying the
    # registry's stated principle literally, *what a consumer of THIS release hits first*:
    # this adds a FOURTH CONSOLE ALIAS to the distribution, so like 12.5's it is encountered
    # at install time rather than at verdict time, and it is the only other entry in the note
    # that changes the answer to "what did I just install".
    # It is placed ABOVE 11.1's instrument disclosure, and that promotion was not taken
    # lightly, because 11.1 has held first place on the ground that it bounds how a consumer
    # should weigh every other claim in this note. Two things reconcile it. First, this entry
    # does not compete with that role: the new surface CARRIES 11.1's disclosure — in every
    # tool result and in the tool description an agent reads before calling — so a reader who
    # meets this section has already been handed the caveat rather than had it deferred.
    # Second, the reader most affected is a NEW KIND of reader: an autonomous agent's
    # operator, who needs to know a second entry point now exists in their supply chain
    # before they need to know how far the instrument has been validated. Everything below
    # can move a verdict, an exit code or a claim; these first two move what the product IS.
    "### Added — `argus-mcp`, so a coding agent can run the audit and read the verdict itself",
    # `## Unreleased` — added 2026-08-15 by Story 12.7 (FR35, second half). A PURE INSERTION: no
    # existing section moved relative to any other, and nothing was demoted.
    # Placed THIRD, and the placement is the DECISION this registry's comment above demands rather
    # than a default. Applying the registry's stated principle literally, *what a consumer of THIS
    # release hits first*: this is the THIRD and last entry in the note that changes the answer to
    # "what did I just install" — 12.5's changed what the install GROUNDS, 12.6's added a fourth
    # console alias, and this one adds DATA FILES to the wheel plus a second sub-command. It sits
    # directly beneath 12.6's for a second, stronger reason: it delivers the half of FR35 that
    # 12.6's own section explicitly names as NOT delivered, so a reader meets the two halves in
    # delivery order rather than having to reconcile them.
    # PROMOTION ABOVE 12.5's AND 12.6's WAS CONSIDERED AND DECLINED, on the honest reading rather
    # than the flattering one. The argument for promotion is real: this is the only entry in the
    # whole note that writes a file into the consumer's OWN configuration directory, outside any
    # repository, which is the most invasive thing anything in this release does. It is declined
    # because that write happens only on an EXPLICIT OPERATOR ACT — running `argus
    # install-commands` — whereas 12.5's grammar promotion and 12.6's fourth alias both land
    # unconditionally at `pip install` time and change what a consumer has before they have typed
    # anything. That is the same test the registry applied to 12.2's egress entry, which was
    # declined promotion for being unreachable without an explicit new flag; applying it one way to
    # a transmit path and another way to a write path would make the principle decorative.
    # It stays ABOVE 11.1's instrument disclosure for the reason 12.5's and 12.6's do, and without
    # competing with it: the assets this step places CARRY that disclosure, rendered at write time,
    # so a reader who reaches this section has already been handed the caveat rather than had it
    # deferred.
    "### Added — `argus install-commands`, so the commands this README documents are the commands you get",
    # `## Unreleased` — added 2026-08-13 by Story 12.4 (FR37 / DF-11-4-D / AI-E11-6).
    "### Specified — every terminal outcome names its next action and the ingestion boundary",
    # `## Unreleased` — added 2026-08-11 by Story 11.1 (FR34). Registered FIRST because it is
    # the claim a consumer of THIS release must read before weighing any other: the tool now
    # states its own validation status on every verdict surface. Order is pinned by `-16`, so
    # a later story cannot demote it by adding a section above it without deciding to.
    "### Disclosed — Argus now states its own validation status on every verdict surface",
    # `## Unreleased` — added 2026-08-12 by Story 11.4. Registered SECOND, and the placement is
    # the DECISION this registry's comment above demands rather than a default. 11.1's
    # instrument disclosure stays first for the reason it was placed there — it bounds how a
    # consumer should weigh every other claim in this note, including this one — so it was NOT
    # demoted. This section is placed above 11.2's and 11.3's on the registry's own stated
    # principle, *what breaks a pipeline soonest*: it is the only entry that can change an EXIT
    # CODE on an unchanged repository, from `0` to `3`, for a consumer who changed nothing but
    # their environment. 11.2's classification fix moves a verdict conservatively and 11.3's
    # binds only the marketplace channel; this one binds every channel and every language,
    # because the toolchain it validates is the substrate under all of them. It is also the
    # entry a reader most needs BEFORE the others: if their toolchain does not validate, the
    # coverage numbers every other section discusses are withheld rather than wrong. No
    # existing section moved relative to any other — this is a pure insertion.
    "### Fixed — an unvalidated parsing toolchain can no longer produce a false green",
    # `## Unreleased` — added 2026-08-11 by Story 11.2 (DF-8-2-B). Registered THIRD, and that
    # placement is a DECISION this registry's own comment above demands rather than a default:
    # 11.1's instrument disclosure bounds how a consumer should weigh every other claim in this
    # note, including this one, so demoting it beneath a behavioural fix would be the wrong
    # signal for an assurance tool. This section is nonetheless a consumer-visible BEHAVIOUR
    # change — it can move a polyglot repository's verdict, conservatively — which is why it
    # precedes the 10.2/10.3 sections and states its direction rather than hedging it.
    "### Fixed — a production file is no longer mistaken for a test because its name ends in the right letters",
    # `## Unreleased` — added 2026-08-12 by Story 11.3 (DF-9-2-D). Registered FOURTH (was third
    # until Story 11.4 inserted above it on 2026-08-12; its own reasoning below is unchanged and
    # still holds — it was not reordered relative to any other section). The placement is the
    # DECISION this registry's comment above demands rather than a default.
    # Urgency alone would promote it: it is the only *security* entry in the note. It is placed
    # below 11.1's and 11.2's anyway because the stated principle is *what a consumer of THIS
    # release hits first*, and the dominant install path for this release is the index/VCS channel:
    # a CLI or library consumer is entirely UNAFFECTED by the composite-action fix, whereas 11.1's
    # instrument disclosure bounds how they should weigh every claim in this note and 11.2's
    # classification change can move ANY consumer's verdict. The action fix binds only the
    # marketplace channel, which `epics.md` Story 11.3 AC3 hard-gates on this story and ships later
    # (Story 12.9). Reordering an already-reviewed entry would also add avoidable churn to a
    # security change, so no existing section moved.
    "### Security — the composite action no longer pastes your workflow's inputs into its shell script",
    # `## Unreleased` — added 2026-08-12 by Story 11.5 (DF-9-2-A / DF-9-2-B). Registered FIFTH,
    # and the placement is the DECISION this registry's comment above demands rather than a
    # default. THIS IS THE FIFTH CONSECUTIVE STORY TO EDIT THIS REGISTRY (11.1, 11.2, 11.3,
    # 11.4, now 11.5), filed as `DF-11-4-D` and stated here rather than left to be counted:
    # the Epic-11 checkpoint review should look at this file's history and decide whether the
    # registry's cost is buying what it was meant to buy. It is a pure INSERTION — no existing
    # section moved relative to any other, and nothing was demoted.
    # Placed below the four above it on the registry's own stated principle, *what breaks a
    # pipeline soonest*, applied honestly against this entry rather than flatteringly:
    # 11.1 bounds how a consumer weighs every other claim here (including this one); 11.4 can
    # change an EXIT CODE on an unchanged repository; 11.2 can move any consumer's verdict;
    # 11.3 is a security fix on an executable surface. This entry changes NO verdict, NO exit
    # code, NO threshold, NO default and no `stdout` byte — it can only turn an import that
    # failed into one that succeeds, and correct sentences that were untrue. Promotion above
    # 11.3 was considered on the ground that this one binds the dominant index/VCS channel
    # while 11.3 binds only the marketplace channel, and DECLINED: a security fix on an
    # executable surface outranks a packaging fix on a non-consumer module surface.
    "### Fixed — five shipped modules could not be imported from the distribution at all",
    # `## Unreleased` — added 2026-08-13 by Story 12.2 (FR36). A PURE INSERTION: no existing
    # section moved relative to any other, and nothing was demoted.
    # ⚠️ `DF-11-4-D` / `AI-E11-6` are LIVE about this registry and are targeted at Story 12.4.
    # Adding a section is NOT the same as re-opening the impact-rank question, so this entry
    # does exactly what the ledger asks of a story that must touch the file anyway: it is added
    # in registry order with its placement reasoned, and the RANKING of every existing section
    # is left entirely alone. The registry's cost/benefit question stays open for 12.4.
    # Placed SIXTH — below every Epic-11 section — on the registry's own stated principle,
    # *what breaks a pipeline soonest*, applied against this entry honestly rather than
    # flatteringly. It is tempting to promote it: it introduces the ONLY code path in the
    # product that can transmit anything off the machine, and for an assurance tool that is the
    # kind of claim a reader wants early. DECLINED, because the principle is about what a
    # consumer HITS, and this path is unreachable without an explicit new flag: it changes no
    # default, no exit code, no verdict and no byte on any invocation that existed before this
    # release. Each of the five above it can move a consumer who changed nothing — 11.1 bounds
    # how every other claim here should be weighed, 11.4 can change an exit code on an unchanged
    # repository, 11.2 can move any polyglot verdict, 11.3 is a security fix on an executable
    # surface, and 11.5 turns a failing import into a working one.
    # It is placed ABOVE the 10.3 group deliberately: both specify the invocation surface, and a
    # consumer reading the CLI-contract sections should meet the egress opt-in before the six
    # already-shipped flags, because it is the only one of the seven that sends anything.
    "### Specified: `--deep-audit` — the opt-in deep pass, and the false deep claim it replaces",
    # `## Unreleased` — added 2026-08-10 by Story 10.2 (DF-AUD-APAA-D). Registered deliberately,
    # which is what this enumeration is for: each one is a consumer-visible claim someone signed
    # off. "Documented" records the `[languages]` extra, which shipped with zero README/CHANGELOG
    # coverage; "Fixed" records TypeScript/PHP being reported as missing grammars they already had;
    # "Changed" records the per-grammar cache-key provenance (internal — no store is wired, so no
    # cached result exists to invalidate).
    # `## Unreleased` — added 2026-08-10 by Story 10.3 (DF-AUD-APAA-E). "Specified" records the six
    # CLI flags that shipped in 0.1.0 accepted and specified in no binding document; "Fixed" records
    # the one behavioural change under that bless — `--ignore-pattern` was evaluated ABOVE the
    # Live-Key Safeguard its own module docstring promised, so `--ignore-pattern "A"` suppressed
    # every live credential in the audited repository with nothing recorded; "Known divergence"
    # states, rather than changes, the `--coverage-scope` CLI/library default split (DN-8). These
    # precede 10.2's sections because they are what a consumer of THIS release hits first.
    "### Specified — six CLI flags that shipped in `0.1.0` accepted and specified nowhere",
    "### Fixed — `--ignore-pattern` could defeat the live-key safeguard it was documented to sit under",
    "### Known divergence — `--coverage-scope`'s default differs between the CLI and the library",
    "### Documented — the `[languages]` extra, which shipped undocumented",
    "### Fixed — TypeScript and PHP were reported as missing grammars they already had",
    "### Changed — the memoization cache key now names the grammar that actually parsed",
    # `## Unreleased` — added 2026-08-15 by Story 12.9 (AC2 + AC3). A PURE INSERTION: no
    # existing section moved relative to any other, and nothing was demoted.
    # Placed LAST among the Unreleased sections, and the placement is the DECISION this
    # registry's comment above demands rather than a default. PROMOTION WAS CONSIDERED AND
    # DECLINED, on the honest reading rather than the flattering one.
    # The argument for promoting it is real and tempting: it is the entry that states whether
    # ANY claim in this note is backed by an executed gate, and a reader who weighs the other
    # sections arguably needs that frame first — the same ground 11.1's instrument disclosure
    # holds first place on.
    # It is declined because the registry's stated principle is *what a consumer of THIS
    # release HITS*, and 12.2's egress entry was declined promotion under exactly that test:
    # it *"changes no default, no exit code, no verdict and no byte on any invocation that
    # existed before this release"*. That sentence is true of this entry word for word. Every
    # section above it can move something a consumer observes — 12.8 can change an exit code
    # on an unchanged repository, 12.5/12.6/12.7 change what `pip install` puts on their disk,
    # 11.x can move a verdict or a coverage number — while this one changes what the release
    # SAYS ABOUT ITSELF and nothing a pipeline can trip over. Applying the principle one way
    # to a transmit path and another way to a governance statement would make it decorative.
    # The frame this entry provides is not deferred by the placement either: the honesty
    # preamble at the head of this file carries the same derived status sentence, so a reader
    # meets it before any section at all.
    "### Changed — the release note and the release status are generated from their sources, and the status is NOT ESTABLISHED",
    "### Resolving `argus-agent`",
    "### Version: one value, one source",
    "### Behaviour: the composite action distinguishes a crash from an assessment",
    "### Packaging: what the distribution contains",
    "### No assurance claim is made by this release",
    "### The FR16/FR4 verdict-contract amendment",
    "### Behaviour: exit codes",
    "### Artifacts: schema versions",
    "### Defaults: `--coverage-scope`",
    "### Output: changed strings",
    "### Unchanged on purpose",
    "### API (library consumers)",
    "### Do I need to change anything?",
)

# The consumer-facing surfaces this release publishes or regenerates.
_RELEASE_SURFACES: tuple[str, ...] = (
    "README.md",
    "CHANGELOG.md",
    "action.yml",
    # Registered 2026-08-11 by Story 11.1 (FR34). `[project].description` is the ONE-LINE
    # PyPI summary a stranger reads beside the package name — before the README, before
    # anything. It now carries the instrument-status disclosure, so it has to be inside the
    # over-claim guard: a surface this release publishes on and `-17` does not scan is a
    # surface where an over-claim can land unseen.
    "pyproject.toml",
    ".github/workflows/release.yml",
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md",
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md",
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md",
    # Registered 2026-08-15 by Story 12.7 (FR35, second half). These are the packaged command
    # assets: they SHIP IN THE WHEEL and are then written into a consumer's own assistant
    # configuration directory, which makes them the most directly consumer-facing text this
    # project publishes — an agent reads them before it decides to run anything. A surface this
    # release publishes on and `-17` does not scan is a surface where an over-claim can land
    # unseen, and this is the one class of surface where an over-claim would be read by a
    # machine that then acts on it.
    # Registered INDIVIDUALLY and matched by a pattern below, which is `-18`'s design and not a
    # redundancy: the pattern is what makes a FOURTH asset red rather than invisible, and the
    # named entry is what makes adding one a deliberate, reviewed act. A registry entry no
    # pattern resolves proves nothing, and a pattern with no registry lets anything through.
    "argus/assets/commands/argus-audit.md",
    "argus/assets/commands/argus-audit-report.md",
    "argus/assets/commands/argus-audit-security.md",
    # Registered 2026-08-15 by Story 12.8 (AC1). `docs/first-run.md` is the FIRST document a
    # reader with no prior exposure meets — install, first audit, reading the ledger, what each
    # verdict means — and it makes claims about verdicts, exit codes and command lines. A page
    # that states what `RELEASE_READY` means is a verdict surface in the sense `-17` cares
    # about, so it is scanned for over-claims like every other.
    # `docs/README.md` is registered ALONGSIDE it, deliberately. It is a BMad tooling stub
    # rather than a consumer document, but Story 12.8 / DN-1 put a consumer page in that
    # directory and recorded the co-tenancy THERE so a later reader does not "tidy" the page
    # away; a directory-wide pattern is the only shape that makes a SECOND page red rather than
    # invisible, and a pattern that resolves a file no registry entry covers is `-18`'s whole
    # failure mode. Registering both is what makes the pattern below honest.
    "docs/first-run.md",
    "docs/README.md",
    # Registered 2026-08-15 by Story 12.9 (AC3). This module RENDERS the GitHub Release note
    # body and the published release-status sentence, so the sentences a stranger reads on the
    # Release page and in `README.md`/`CHANGELOG.md` are committed HERE. It is the most
    # consumer-facing non-document file in the tree: an over-claim landing in it is published
    # on every surface at once, which no other member of this registry can do.
    # Registered INDIVIDUALLY and matched by an exact pattern below, which is `-18`'s design:
    # a directory-wide `scripts/*.py` glob was CONSIDERED AND DECLINED because `scripts/`
    # holds release machinery and maintenance tooling that publishes nothing (the preflight,
    # the dogfood regenerator), and a pattern that drags them in would force four unrelated
    # registry entries whose only content would be "this is not a publication surface" — the
    # exemption-by-attrition shape `_PRESERVED_RECORD` exists to avoid. The RENDERED body is
    # separately held to this same over-claim rule by
    # `tests/test_release_note_body.py::TC-ArgusAgent-DOCS-001-67`, which is the half a file
    # scan cannot reach.
    "scripts/release_notes.py",
)

# Globs that resolve to every file that COULD be such a surface. Anything they find which
# is not registered above fails -18.
_RELEASE_SURFACE_PATTERNS: tuple[str, ...] = (
    "README.md",
    "CHANGELOG.md",
    "action.yml",
    "pyproject.toml",
    ".github/workflows/release.yml",
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-*.md",
    # Added 2026-08-15 by Story 12.7, WITH the registry entries above. Without this pattern
    # `-18`'s closure never resolves the asset tree at all and would pass vacuously about the one
    # surface class this story adds — which is exactly the shape of the `_CONSOLE_SCRIPTS` and
    # `_ENTRY_POINT` defects Story 12.6 found twice: a recognizer that quietly stops recognizing.
    "argus/assets/commands/*.md",
    # Added 2026-08-15 by Story 12.8, WITH the two registry entries above — both, for 12.7's
    # recorded reason: *a registry entry no pattern resolves proves nothing, and a pattern with
    # no registry lets anything through*. The glob is directory-wide rather than
    # `docs/first-run.md`, so a SECOND consumer-facing page dropped into `docs/` is RED until
    # somebody decides it is honest, which is exactly what `-18` exists for.
    "docs/*.md",
    # Added 2026-08-15 by Story 12.9, WITH the registry entry above — both, for 12.7's
    # recorded reason: *a registry entry no pattern resolves proves nothing, and a pattern
    # with no registry lets anything through*. Exact rather than directory-wide, for the
    # reason recorded beside the registry entry.
    "scripts/release_notes.py",
)

# The preserved, frozen Story-7.2 independent run matches the dogfood glob but is NOT a
# surface this release publishes — it is the record being SUPERSEDED, it is the only
# surviving copy of the independent Minions evidence, and Story 9.2 / AC15 fences it.
# Exempted by name so the exemption is a decision rather than an oversight.
_PRESERVED_RECORD = (
    "_bmad-output/design-artifacts/ArgusAgent/"
    "minions-dogfood-proof-story-7-2-superseded.md"
)

# Phrases that would present the self-audit as assurance, claim external validation, or
# claim a cleared precision gate.
_OVER_CLAIMS: tuple[str, ...] = (
    "externally validated",
    "independently validated",
    "independent validation",
    "independent corroboration",
    "externalization-grade",
    "gate is cleared",
    "gate cleared",
    "precision gate cleared",
    "protocol_cleared=true",
    "validated deep audit",
    "third-party validated",
    "independently verified",
)

# A blunt substring scan cannot tell an over-claim from its own denial, and these surfaces
# are FULL of denials — that is the point of them. `minions-dogfood-proof.md` says "The
# gate is cleared ONLY by the human TP/FP adjudication"; CHANGELOG.md says "No statement
# ... should be read as a claim that Argus has been externally validated". Both are the
# honest form and both contain a banned phrase.
#
# So the scan is SENTENCE-scoped and a sentence carrying any of these markers is a denial
# or a condition, not an assertion. This generalises the `-30` precedent in
# tests/test_dogfood_proof.py, which splits the gate-status string on an "EARLY" marker to
# isolate the affirmative region. `-17b` below is the positive control: it proves the
# filter still catches a genuine affirmative over-claim, so the exemption cannot silently
# swallow the thing it exists to find.
#
# POSITION MATTERS, and the first version of this filter ignored it. A bare `"no "` or
# `"not "` ANYWHERE in the sentence exempted it, so "Argus has been externally validated
# with no exceptions" — an affirmative over-claim with a negation trailing behind it —
# passed. English negation binds LEFTWARD to the claim it denies, so a negation is only a
# denial of this claim if it appears BEFORE the banned phrase. Two classes, therefore:
#
#   _DENIAL_MARKERS    — negations. Must appear BEFORE the banned phrase in the sentence.
#   _QUALIFIER_MARKERS — restrictions that legitimately follow the phrase and narrow it,
#                        e.g. "The gate is cleared ONLY by the human TP/FP adjudication",
#                        which is the honest form and says the gate is NOT cleared today.
#
# Both classes are still sentence-scoped, and `-17b` now carries the trailing-negation
# sentence as a second positive control so this exact escape cannot reopen.
_DENIAL_MARKERS: tuple[str, ...] = (
    " not ",
    "not ",
    " no ",
    "no ",
    "never",
    "cannot",
    "must not",
    "should not",
    "n't",
)

_QUALIFIER_MARKERS: tuple[str, ...] = (
    "only by",
    "only cleared",
    "would be",
    "stays provisional",
    "remains provisional",
    "is provisional",
)


def _split_sentences(text: str) -> list[str]:
    """Sentence-ish units over MARKDOWN, which hard-wraps mid-sentence.

    Paragraphs are separated by blank lines; inside a paragraph the line breaks are
    cosmetic, so they are collapsed BEFORE splitting. Splitting on raw line breaks was the
    first thing tried and it failed on a real case: ``CHANGELOG.md``'s "No statement ...
    should be read as a claim that Argus has been / externally validated." wraps so that
    the banned phrase lands on a line of its own, stripped of the "No" that denies it.

    Sentences are then split on ``. `` only. Where this errs it errs toward LARGER units,
    which makes the denial filter easier to satisfy and the guard weaker — which is
    exactly why ``-17b`` exists as a positive control.
    """
    import re

    units: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        flat = " ".join(paragraph.split())
        if not flat:
            continue
        for part in flat.split(". "):
            stripped = part.strip()
            if stripped:
                units.append(stripped)
    return units


def _is_denied(sentence: str, claim_at: int) -> bool:
    """Is the banned phrase at *claim_at* denied or narrowed by the rest of *sentence*?

    A negation counts only when it PRECEDES the phrase — that is where English puts the
    negation of a claim, and accepting one that trails behind is how "externally validated
    with no exceptions" escaped. A qualifier may appear anywhere, because it restricts the
    phrase rather than negating it, and restriction reads naturally after the claim.
    """
    if any(marker in sentence for marker in _QUALIFIER_MARKERS):
        return True
    return any(
        0 <= sentence.find(marker) < claim_at for marker in _DENIAL_MARKERS
    )


def _affirmative_over_claims(text: str) -> list[tuple[str, str]]:
    """Every (phrase, sentence) pair where a banned phrase is asserted, not denied."""
    hits: list[tuple[str, str]] = []
    for sentence in _split_sentences(text.lower()):
        for claim in _OVER_CLAIMS:
            claim_at = sentence.find(claim)
            if claim_at >= 0 and not _is_denied(sentence, claim_at):
                hits.append((claim, sentence))
    return hits


def test_TC_ArgusAgent_DOCS_001_16_note_sections_are_an_enumerated_space() -> None:
    """TC-ArgusAgent-DOCS-001-16 — Story 9.2/D12 (closes DF-8-4-B, heading half).

    The note IS the consumer contract — ``argus/__init__.py`` defers to it explicitly so
    there is no second copy to cross-check against. A section silently deleted from it
    deletes part of that contract with nothing going red, which is what DF-8-4-B was filed
    about. Order is pinned too: the note is ordered by what breaks a pipeline soonest, and
    a reordering changes what a skimming reader hits first.
    """
    note = _CHANGELOG.read_text(encoding="utf-8")
    present = [line.rstrip() for line in note.splitlines() if line.startswith("### ")]

    missing = [section for section in _NOTE_SECTIONS if section not in present]
    assert not missing, f"the release note lost registered section(s): {missing}"

    unregistered = [section for section in present if section not in _NOTE_SECTIONS]
    assert not unregistered, (
        "the release note grew section(s) not registered in _NOTE_SECTIONS: "
        f"{unregistered}. Register them deliberately — an unenumerated section is a "
        "consumer claim nobody reviewed."
    )
    assert present == list(_NOTE_SECTIONS), (
        "the note's sections are all registered but their ORDER changed.\n"
        f"  registry: {list(_NOTE_SECTIONS)}\n  measured: {present}"
    )


def test_TC_ArgusAgent_DOCS_001_17_no_release_surface_over_claims() -> None:
    """TC-ArgusAgent-DOCS-001-17 — Story 9.2/AC12 (SD-2): every registered surface is honest.

    Each registered surface must exist, and none may contain a phrase asserting external
    validation or a cleared precision gate.
    """
    for rel in _RELEASE_SURFACES:
        path = _REPO_ROOT / rel
        assert path.is_file(), f"registered release surface is missing: {rel}"
        hits = _affirmative_over_claims(path.read_text(encoding="utf-8"))
        assert not hits, (
            f"{rel} ASSERTS an over-claim (phrase, sentence): {hits}. The dogfood run is "
            "a SELF-audit; it is never independent corroboration, and the >=80%-precision "
            "gate stays PROVISIONAL (SD-2)."
        )


def test_TC_ArgusAgent_DOCS_001_17b_the_over_claim_detector_actually_bites() -> None:
    """TC-ArgusAgent-DOCS-001-17b — Story 9.2/AC12: the denial filter is not a loophole.

    A guard whose exemption swallows the thing it looks for passes on any text. This is
    the positive control: an affirmative over-claim is caught, and each of the real
    denials the surfaces actually contain is correctly NOT caught.
    """
    caught = _affirmative_over_claims(
        "Argus has been externally validated by a third party and the precision "
        "gate is cleared."
    )
    assert caught, "the detector missed a plain affirmative over-claim"
    assert {claim for claim, _ in caught} >= {"externally validated"}

    # SECOND positive control — the trailing-negation escape, found by code review.
    # The first version of the filter exempted any sentence containing a bare "no " or
    # "not " ANYWHERE, so this sentence — an affirmative over-claim with a negation
    # trailing harmlessly behind it — walked straight through. A negation only denies a
    # claim it precedes.
    for trailing_negation in (
        "Argus has been externally validated with no exceptions.",
        "The precision gate is cleared and there is no caveat.",
        "Argus is independently verified; we are not exaggerating.",
    ):
        assert _affirmative_over_claims(trailing_negation), (
            "the denial filter exempted an affirmative over-claim because a negation "
            f"appeared AFTER the banned phrase: {trailing_negation!r}"
        )

    # The real denials on the shipped surfaces, verbatim, must NOT be flagged.
    for honest in (
        "No statement in this release should be read as a claim that Argus has been "
        "externally validated.",
        "The gate is cleared ONLY by the human TP/FP adjudication over the REAL dogfood "
        "findings above.",
        "it is NEVER independent corroboration of the tool's detection ability.",
        "The >=80%-precision externalization gate stays PROVISIONAL and is not cleared.",
    ):
        assert not _affirmative_over_claims(honest), (
            f"the detector flagged an honest denial as an over-claim: {honest!r}"
        )


def test_TC_ArgusAgent_DOCS_001_18_release_surface_set_is_closed() -> None:
    """TC-ArgusAgent-DOCS-001-18 — Story 9.2/AC12: a NEW surface cannot escape the guard.

    The failure shape this prevents is always the same: a guard names the files that
    existed when it was written, and the next file added is outside it. Resolving the
    patterns against the tree and failing on anything unregistered means a fourth dogfood
    artifact, or a second release workflow, goes RED until someone decides it is honest.
    """
    found: set[str] = set()
    for pattern in _RELEASE_SURFACE_PATTERNS:
        for path in _REPO_ROOT.glob(pattern):
            if path.is_file():
                found.add(path.relative_to(_REPO_ROOT).as_posix())
    assert found, "the release-surface patterns resolved to nothing — the globs are broken"
    assert _PRESERVED_RECORD in found or not (_REPO_ROOT / _PRESERVED_RECORD).exists(), (
        "the preserved Story-7.2 record should have been matched by the dogfood glob; if "
        "it no longer exists, RS-3 'supersede, don't erase' has been violated"
    )
    found.discard(_PRESERVED_RECORD)
    unregistered = sorted(found - set(_RELEASE_SURFACES))
    assert not unregistered, (
        f"consumer-facing release surface(s) exist but are not registered: {unregistered}. "
        "Register them in _RELEASE_SURFACES so the over-claim guard covers them."
    )
    # Non-vacuity: the registry is not a superset of nothing.
    assert set(_RELEASE_SURFACES) - {_PRESERVED_RECORD} <= found | {
        rel for rel in _RELEASE_SURFACES if (_REPO_ROOT / rel).is_file()
    }


def test_TC_ArgusAgent_DOCS_001_19_provisional_gate_language_survives_regeneration() -> None:
    """TC-ArgusAgent-DOCS-001-19 — Story 9.2/AC12: the honesty language is present, not merely un-negated.

    ``-17`` proves no over-claim was ADDED. That is only half of AC12: a surface could
    satisfy it by saying nothing at all, and silence about a self-audit reads as a normal
    audit. The regenerated proof artifact must still SAY the things that make it
    falsifiable — the honest grade, the self-audit clause, and the provisional gate.
    """
    proof = _ARTIFACT_DIR / "minions-dogfood-proof.md"
    assert proof.is_file()
    text = proof.read_text(encoding="utf-8")
    for required in (
        "grade: demo-heuristic-only",
        "SELF-audit",
        "MATERIALLY WEAKER",
        "STAYS PROVISIONAL",
        "NEVER independent corroboration",
    ):
        assert required in text, (
            f"the regenerated proof artifact lost its honesty language: {required!r}"
        )
    # And the two plan artifacts carry the same subject-honesty clause.
    for name in (
        "minions-dogfood-partition-plan.md",
        "minions-dogfood-budget-plan.md",
    ):
        plan_text = (_ARTIFACT_DIR / name).read_text(encoding="utf-8")
        assert "SELF-scoped plan" in plan_text, f"{name} lost its subject-honesty clause"


# ─────────────────────────────────────────────────────────────────────────────────────
# Story 12.8 / AC1 — the first-run page: REACHABLE, and every checkable claim DERIVED
#
# `epics.md:2421-2425` asked for a first-run page. What it assumed — that `docs/` already held
# an integrator-shaped README — was measured FALSE on `2f84a0b`: `docs/README.md` is a 642-byte
# BMad tooling stub ending *"Currently empty apart from this file"*, the integrator-shaped
# README is the ROOT one, and `README.md` contained ZERO occurrences of `docs/`, so nothing
# linked there at all. Reachability is therefore part of the delivery, not a nicety — and the
# page does NOT ship in the wheel (`flit_core` packages `argus/**` only), so the README link is
# its whole delivery mechanism.
#
# Every FACTUAL claim on it is derived by the guards below rather than transcribed (AI-E9-7):
# a fourth `Verdict` member, a changed exit code or a moved command line turns them RED rather
# than leaving the page quietly stale.
# ─────────────────────────────────────────────────────────────────────────────────────

_FIRST_RUN = _REPO_ROOT / "docs" / "first-run.md"
_README = _REPO_ROOT / "README.md"


def test_TC_ArgusAgent_DOCS_001_62_the_first_run_page_is_reachable_and_says_what_it_is() -> None:
    """TC-ArgusAgent-DOCS-001-62 — Story 12.8 / AC1: an unlinked page is not a first-run surface.

    Three facts, and the first is the one the epic's premise got wrong. (a) The page exists.
    (b) `README.md` LINKS it, and the link target resolves to a file that is really there — a
    link is only a delivery mechanism if it lands. (c) The page states plainly that it is
    repository documentation, because it is NOT in the wheel and a reader who `pip install`ed
    the distribution will not find it on their disk.
    """
    assert _FIRST_RUN.is_file(), "docs/first-run.md is missing — AC1's whole delivery"
    page = _FIRST_RUN.read_text(encoding="utf-8")
    readme = _README.read_text(encoding="utf-8")

    links = re.findall(r"\]\((docs/[^)]+\.md)\)", readme)
    assert "docs/first-run.md" in links, (
        "README.md does not link docs/first-run.md. Measured on 2f84a0b, README contained ZERO "
        f"occurrences of 'docs/' — an unreachable page is not a first-run surface. Found: {links}"
    )
    for target in links:
        assert (_REPO_ROOT / target).is_file(), (
            f"README.md links {target!r}, which resolves to nothing. A link that does not land "
            "is worse than no link: it sends the reader somewhere that does not exist, which is "
            "the exact failure FR37 is written against."
        )

    assert "not packaged in the wheel" in page or "not* packaged in the wheel" in page, (
        "the page does not say it is repository documentation. A reader who installed the "
        "distribution and cannot find this file has been told nothing about why."
    )


def test_TC_ArgusAgent_DOCS_001_63_the_verdict_vocabulary_on_the_page_is_derived() -> None:
    """TC-ArgusAgent-DOCS-001-63 — Story 12.8 / AC1: a fourth verdict turns this RED, not stale.

    The page's verdict table is a transcription risk of exactly the class AI-E9-7 names: a
    prose copy of a pinned constant. So the constant is the authority — `Verdict`
    (`argus/verdict/verdict_gate.py`) — and the page is checked against it in BOTH directions:
    every member must appear, and the page may name no token that is not a member. Adding a
    fourth `Verdict` member makes this fail rather than leaving a published page quietly
    incomplete.
    """
    page = _FIRST_RUN.read_text(encoding="utf-8")
    members = {member.value for member in Verdict}
    assert len(members) >= 3, "the Verdict enum collapsed; this comparison would be vacuous"

    missing = sorted(token for token in members if token not in page)
    assert not missing, (
        f"docs/first-run.md does not name verdict member(s) {missing}. The page tells a "
        "first-time reader what each verdict means; one it does not mention is one they meet "
        "for the first time in a red CI log."
    )
    # Direction two: no INVENTED token. A verdict token is SCREAMING_SNAKE_CASE — the
    # underscore is what makes the pattern a verdict-shape rather than "any shouted word", and
    # it is the corrected form: a first draft matched `[A-Z][A-Z_]{5,}` and flagged `README`,
    # which is a guard failing on the wrong observable. `AUDIT_FAILED` is admitted because it
    # is `plain_english.TERMINAL_OUTCOMES`' fourth member — a real, published non-verdict
    # outcome token — and it is read from that tuple rather than typed here.
    allowed = members | set(TERMINAL_OUTCOMES)
    shaped = set(re.findall(r"\b[A-Z]+(?:_[A-Z]+)+\b", page))
    invented = sorted(word for word in shaped if word not in allowed)
    assert not invented, (
        f"docs/first-run.md names verdict-shaped token(s) the gate cannot produce: {invented}. "
        "A published page naming an outcome the tool cannot emit teaches a reader to expect "
        "something they will never see."
    )
    # Positive control: the corrected pattern still catches a real invented token.
    assert re.findall(r"\b[A-Z]+(?:_[A-Z]+)+\b", "the verdict was PROBABLY_FINE") == [
        "PROBABLY_FINE"
    ], "the verdict-shape pattern stopped matching a verdict-shaped token"
    assert not re.findall(r"\b[A-Z]+(?:_[A-Z]+)+\b", "see README for details")


def test_TC_ArgusAgent_DOCS_001_64_the_exit_codes_on_the_page_are_the_AR3_mapping() -> None:
    """TC-ArgusAgent-DOCS-001-64 — Story 12.8 / AC1: the exit-code table is DERIVED.

    An exit code is the one fact a CI consumer acts on without reading anything else, and a
    published page stating the wrong one is the worst kind of stale. The authority is
    `exit_code_for_verdict` plus AR3's reserved `1`, and the page's table row for each verdict
    must carry the code that function actually returns — read from the row, not from anywhere
    on the page, so a correct code sitting beside the wrong verdict is still RED.
    """
    page = _FIRST_RUN.read_text(encoding="utf-8")
    rows = [line for line in page.splitlines() if line.startswith("| ")]
    assert rows, "the page has no table at all"

    checked = 0
    for member in Verdict:
        code = exit_code_for_verdict(member)
        matching = [row for row in rows if member.value in row]
        assert len(matching) == 1, (
            f"expected exactly one table row naming {member.value}, found {len(matching)}"
        )
        assert f"`{code}`" in matching[0], (
            f"docs/first-run.md states the wrong exit code for {member.value}: the AR3 map "
            f"returns {code} and the row reads {matching[0]!r}"
        )
        checked += 1
    assert checked == len(Verdict) >= 3

    # AR3's reserved crash code, which is NOT a verdict and must be stated as such.
    reserved_row = [row for row in rows if "`1`" in row and "no verdict" in row]
    assert reserved_row, (
        "the page does not state that exit 1 is the reserved 'no verdict produced' code. It is "
        "the code a usage error and every typed failure now return (Story 12.8 / AC8), and a "
        "consumer who reads it as a verdict has been handed a fabricated assessment."
    )
    assert set(re.findall(r"^\| .*?\| `(\d)` \|", page, re.M)) == {
        str(exit_code_for_verdict(m)) for m in Verdict
    } | {"1"}, "the page's exit-code column is not exactly the AR3 wire contract"


def test_TC_ArgusAgent_DOCS_001_65_no_diagnosis_sends_the_user_to_the_page() -> None:
    """TC-ArgusAgent-DOCS-001-65 — Story 12.8 / AC1: the page must not become where the answer lives.

    FR37 is explicit — *"the next action is present in the tool's own output. A user with no
    colleague and no internal wiki must not be sent elsewhere to interpret a verdict."* A
    first-run page is an orientation surface; the moment a diagnosis says *"see
    docs/first-run.md"* it has become the wiki FR37 forbids, and it is one that does not ship
    in the wheel, so the reader may not even have it.

    Asserted over the SOURCE of every module that renders a user-facing message, so it holds
    for messages this story did not write as well as the ones it did.
    """
    package_root = _REPO_ROOT / "argus"
    surfaces = [
        package_root / "cli.py",
        package_root / "reports" / "plain_english.py",
        package_root / "reports" / "generator.py",
        package_root / "intake" / "source_state.py",
        package_root / "intake" / "repo_loader.py",
        package_root / "pipeline.py",
        package_root / "mcp" / "server.py",
    ]
    assert all(path.is_file() for path in surfaces), "a diagnosis surface moved; fix this list"

    # The observable is the PATH, not the bare phrase. A first draft searched for `first-run`
    # and flagged `argus/pipeline.py`, which uses *"a first-run / no-prior-state signal"* about
    # the resume seam — a guard firing on unrelated prose is a guard that gets deleted by the
    # third person to hit it. What FR37 forbids is a message CITING the page, and a citation
    # carries the path.
    pointer = "docs/first-run.md"
    offenders = [
        str(path.relative_to(_REPO_ROOT)).replace("\\", "/")
        for path in surfaces
        if pointer in path.read_text(encoding="utf-8")
    ]
    assert not offenders, (
        f"{offenders} point the user at {pointer}. FR37 requires the next action to be IN the "
        "tool's own output; a page that is not in the wheel cannot be where the answer lives. "
        "State the answer, do not cite the page."
    )
    # Positive control — the narrowed observable still catches the thing it exists to catch,
    # and is not satisfied by the fact that nobody happens to have written it.
    synthetic = 'print(f"{PROG}: coverage below the floor — see docs/first-run.md")'
    assert pointer in synthetic, "the detector no longer recognises a real citation"


def test_TC_ArgusAgent_DOCS_001_66_the_docs_readme_no_longer_claims_the_folder_is_empty() -> None:
    """TC-ArgusAgent-DOCS-001-66 — Story 12.8 / AC1: a false sentence is STRUCK, not deleted.

    `docs/README.md` ended *"Currently empty apart from this file."* That became false the
    moment `first-run.md` landed beside it. §3.4 evidence immutability says supersede and
    strike, never erase — so the sentence must still be legible, wearing `~~`, with the
    correction beside it, and the deliberate co-tenancy DN-1 records must be named so a later
    reader does not "tidy" a consumer-facing page out of a tooling directory.
    """
    text = (_REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    assert "Currently empty apart from this file" in text, (
        "the superseded sentence was DELETED rather than struck (§3.4 evidence immutability)"
    )
    assert "~~Currently empty apart from this file.~~" in text, (
        "the sentence is still asserted rather than struck — it is false and reads as current"
    )
    assert "first-run.md" in text, "the correction does not name what is actually in the folder"
    assert "CONSUMER-FACING" in text, (
        "the co-tenancy DN-1 records is not stated, so the next reader has no reason not to "
        "move a product surface into the planning tree"
    )
