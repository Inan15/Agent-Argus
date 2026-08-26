"""Story 13.2 / AC8 — the governance record is checked the way the code is.

``TC-ArgusAgent-DOCS-001-77``..``-79``. A NEW module: ``tests/test_evidence_citation.py``
— the natural home — measured **1199/1200** lines, and the sanctioned remedy for a full
file is a cohesion split, never shaving (12.8's precedent). Cohesion here is exact: every
guard below closes over the **governance documents** (`deferred-work.md`,
`architecture.md` §Enforcement, `stories/*.md`) rather than over code.

**`AI-E12-6`, landed here because this is the story it was written for.** The Epic-12
retrospective ranked it #7 and dated it precisely: *"Land the ledger-claim cross-check
guard **before 13.2 files its adjudication record**."* Epic 12 produced **four** instances
of the class — Stories 12.4 and 12.5 recorded ledger closures the ledger never received —
and **every review passed them**, because the reviews that checked the ledger checked the
``+n / -0`` **shape** of a write and never its **existence**. Story 13.2's entire
deliverable is a recorded governance claim of exactly that shape, so filing one while this
guard was still unwritten would have been the defect demonstrating itself inside the fix.

**GUARD-ADEQUACY (`AI-E11-1`), discharged per guard:** each names its **observable**, each
is shown moving **at the real seam** (the committed documents, not a fixture), and ``-78``
**generates** its adversarial variant from the live story corpus with a count asserted.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_LEDGER_PATH = _ARTIFACTS / "deferred-work.md"
_SPRINT_STATUS_PATH = _ARTIFACTS / "sprint-status.yaml"
_ARCHITECTURE_PATH = _ARTIFACTS / "architecture.md"
_STORIES_DIR = _ARTIFACTS / "stories"

#: A ledger id, matched WHOLE and GREEDILY. This pattern is load-bearing and its first
#: form was wrong in the direction that makes a guard silent: a lazy
#: ``DF-[A-Za-z0-9-]*?[A-Za-z0-9]`` matched ``DF-12`` inside ``DF-12-3-A``, so every claim
#: was cross-checked against a truncated id the ledger could never carry — eight false
#: accusations on the first run. Segments are upper-case/digit, which is the shape every
#: id in this ledger actually has (``DF-6-6-A``, ``DF-6-6-A-P1``, ``DF-AUD-APAA-C``).
_DF_ID = r"DF-[A-Z0-9]+(?:-[A-Z0-9]+)*"

#: The same pattern, compiled, for blanking ids out of a field value (Story 17.5 / AC6).
_DF_ID_BLANKER = re.compile(_DF_ID)

#: The wordings a story record uses to CLAIM it closed a ledger entry. Deliberately narrow:
#: a story that merely CITES, progress-notes, re-scopes or rules on an entry is making a
#: different claim, and widening this to every mention would manufacture false accusations
#: — the failure mode 12.3's refutation rule already had to be narrowed away from. It is
#: also anchored to a CLOSURE verb, not to the word "closed" anywhere on the line, so
#: "not closed", "cannot be closed" and "closable" do not read as claims.
_CLOSURE_VERB = re.compile(
    r"(?<!not )(?<!NOT )(?<!never )\b(?:CLOSED|Closes|closes|Closed by this story|"
    r"closed by this story)\b"
)
_NEGATED = re.compile(
    r"\b(?:not|never|cannot be|is not|none is|no entry is|un)\s*(?:be\s+)?CLOSED\b",
    re.IGNORECASE,
)


def story_closure_claims(text: str) -> tuple[str, ...]:
    """Every ``DF-*`` id a story file CLAIMS to have closed. A pure analyzer.

    Line-scoped on purpose: a closure claim and its id are written on the same line in
    every record this repository has produced, and widening the window to a paragraph
    swept unrelated ids into the claim. Pure and exported so the predicate can be driven
    over synthetic input by a positive control — a rule enforced only through the live
    corpus is a rule nobody has watched fire.
    """
    claimed: set[str] = set()
    for line in text.splitlines():
        if not _CLOSURE_VERB.search(line) or _NEGATED.search(line):
            continue
        claimed.update(re.findall(_DF_ID, line))
    return tuple(sorted(claimed))


def ledger_closed_ids(text: str) -> frozenset[str]:
    """Every ``DF-*`` id the ledger carries a CLOSED disposition for. A pure analyzer.

    The ledger writes a closure two ways, both of which count: inline on the entry's own
    line (*"``DF-8-5-C`` — CLOSED 2026-08-16 against evidence"*) and as a trailing
    ``- status: **CLOSED ...**`` field under the entry's id. The second form is resolved
    by carrying the most recent id seen, because that is how the ledger is written and a
    guard that only understood the first form would silently miss half the closures.
    """
    closed: set[str] = set()
    current: str | None = None
    for line in text.splitlines():
        ids = re.findall(_DF_ID, line)
        if ids:
            current = ids[-1]
        if _NEGATED.search(line) or not _CLOSURE_VERB.search(line):
            continue
        if ids:
            closed.update(ids)
        elif re.search(r"^\s*-\s*status:", line) and current is not None:
            closed.add(current)
    return frozenset(closed)


#: **The historical backlog this guard found the day it landed**, registered BY NAME with a
#: date, an owner and a ledger id — the ``_EXEMPT_BY_DESIGN`` pattern Story 12.1 established
#: for exactly this situation (a rule that is right, landing over a repository that predates
#: it). Measured 2026-08-16 by executing the analyzers below over the live corpus: **19
#: unbacked claims across 15 story files, out of 47 claims total**, spanning Epics 1–12.
#:
#: **This is a REGISTRY, not an amnesty, and it can only shrink.** ``-78`` fails if a listed
#: pair becomes backed (a stale entry is a defect, exactly as ``TC-ArgusAgent-MAINT-001-04``
#: treats a file that is no longer over the ceiling), and it fails immediately on any claim
#: NOT listed here — which is every claim Story 13.2 and everything after it will make.
#:
#: **Why the alternative was rejected.** Making this green by *closing* 19 ledger entries
#: would be `AI-E12-3`'s defect — closing entries in prose rather than against evidence — in
#: the guard written to stop it, and this story verified only four by execution. Narrowing the
#: guard to recent stories was rejected for the reason Story 12.1 gives about the NFR-M1
#: sweep: narrowing a population until it goes green is the move this project files as a
#: defect. **Owner: XAgent007 (Engineering Lead). Ledger: `AI-E12-3` / `AI-E12-6`, disposed
#: in `deferred-work.md` under "Story 13.2 dispositions — 2026-08-16".** Four of these
#: (`DF-8-3-A`, `DF-10-4-A`, `DF-10-4-B`, `DF-12-3-A`) are the entries `AI-E12-3` names; the
#: guard found them independently, which is the point of it existing. **Two of the nineteen
#: were removed the same day**, because this story ruled `DF-8-3-A` and `DF-10-4-A` CLOSED
#: against measured evidence and the ledger then backed both claims — the registry shrinking
#: on the day it landed, which is the behaviour the shrink assertion exists to force.
#: **17 remain.**
_UNBACKED_AT_LANDING: frozenset[tuple[str, str]] = frozenset(
    {
        ("10-1-release-status-must-cite-evidence.md", "DF-AUD-APAA-C"),
        ("10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1.md", "DF-10-4-B"),
        ("11-5-published-artifact-is-complete-and-true.md", "DF-11-4-D"),
        ("12-2-deep-audit-is-wired-opt-in-and-honest.md", "DF-12-2-D"),
        ("12-9-release-is-published-and-cites-its-gate.md", "DF-12-9-A"),
        ("4-1-negative-assurance-verdict-semantics.md", "DF-2-3-B"),
        ("4-2-referential-integrity-lint-of-on-disk-state.md", "DF-1-3-A"),
        ("4-3-evidence-bundle-export-no-source-retention.md", "DF-2-3-B"),
        ("4-3-evidence-bundle-export-no-source-retention.md", "DF-3-4-A"),
        ("4-4-secret-containment-property-suite-ci-blocking.md", "DF-1-3-B"),
        ("4-4-secret-containment-property-suite-ci-blocking.md", "DF-2-3-B"),
        ("4-4-secret-containment-property-suite-ci-blocking.md", "DF-3-4-A"),
        ("6-1-llm-dispatch-port-minions-orchestrator-adapter.md", "DF-1-7-B"),
        ("6-2-full-python-ast-grounding-of-audited-deep-claims.md", "DF-1-7-B"),
        ("6-3-orphan-dead-code-detector.md", "DF-1-7-B"),
        ("8-3-plain-english-report-stops-describing-impossible-state.md", "DF-8-1-A"),
        ("8-4-tell-integrators-what-changed.md", "DF-8-3-B"),
    }
)


def test_TC_ArgusAgent_DOCS_001_77_story_13_2_rules_are_registered_in_the_architecture() -> None:
    """TC-ArgusAgent-DOCS-001-77 — AC8.4/AC8.5: a rule in a test is not a rule.

    **Observable:** the presence of each rule's TEXT, its enforcing MODULE and its test
    IDS in `architecture.md` §Enforcement, in the established 10.1/10.5/11.1/12.1/12.2
    form. **Why this guard is itself the closure of `AI-E12-5`:** the guard-adequacy clause
    was asked for by four consecutive retrospectives and registered by none of them,
    precisely because a rule with no guard asserting its text can be forgotten silently.
    """
    architecture = _ARCHITECTURE_PATH.read_text(encoding="utf-8")
    assert "### Enforcement" in architecture, (
        "architecture.md has no §Enforcement section — every registration assertion in "
        "this repository is vacuous"
    )
    anchors = (
        # AC8.4 — the guard-adequacy clause (AI-E12-5 / AI-E11-1), and its input-side twin.
        "GUARD-ADEQUACY CLAUSE",
        "RED at the REAL SEAM, not against a reconstruction",
        "at least one adversarial variant GENERATED",
        "a guard over the SHAPE of an input is not a guard over its EFFECT",
        # AC3 — the adjudication-record rule.
        "Adjudication-record enforcement",
        "exactly ONE LIVE disposition attributed to a human role",
        "never a pass over the adjudicated subset",
        "argus/precision/adjudication.py",
        "tests/test_adjudication_record.py",
        "TC-ArgusAgent-PRECISION-001-39",
        # Story 13.5 / AC1 — the corpus-pin provenance rule, and its measured driver.
        "Corpus-pin provenance enforcement",
        "Reproducibility is not provenance",
        "scripts/pinned_corpus_snapshot.py",
        "TC-ArgusAgent-PRECISION-001-65",
        # Story 13.5 / AC5 — the vacuity floor was NARROWED, and the amendment is by STRIKE
        # rather than by deletion (§3.4). The struck text must stay readable: a registration
        # that erases what it replaced cannot be audited against the world it was written for.
        "AMENDED 2026-08-18 by Story 13.5 / AC5",
        "The floor is narrowed, never removed",
        "TC-ArgusAgent-PRECISION-001-69",
        # AC8.2 — the ledger-claim cross-check rule (AI-E12-6).
        "Ledger-claim cross-check enforcement",
        "a claimed closure `deferred-work.md` never received fails CI",
        "tests/test_governance_record_integrity.py",
        "TC-ArgusAgent-DOCS-001-78",
        # Story 17.5 / AC8 - the stale-target-story rule (AI-E13-12 / AI-E9-8). Added
        # ADDITIVELY: no anchor above was removed and no id was renumbered.
        "Stale-target-story enforcement",
        "a `target_story` pointing at a story that is `done` is work with no container",
        "the registry can only SHRINK, and openness is never decided by `ledger_closed_ids`",
        "TC-ArgusAgent-DOCS-001-80",
        # This assertion's own id, so each registration names what holds it.
        "TC-ArgusAgent-DOCS-001-77",
    )
    missing = tuple(anchor for anchor in anchors if anchor not in architecture)
    assert not missing, f"architecture.md §Enforcement is missing: {missing!r}"
    assert len(anchors) >= 15, "non-vacuity: the anchor enumeration must be non-trivial"


def test_TC_ArgusAgent_DOCS_001_78_a_claimed_ledger_closure_is_checked_against_the_ledger() -> None:
    """TC-ArgusAgent-DOCS-001-78 — AC8.2/`AI-E12-6`: the story record and the ledger must agree.

    **Observable:** for every ``DF-*`` id any committed story file claims to have CLOSED,
    whether `deferred-work.md` carries a matching CLOSED disposition. **Non-vacuity is
    asserted first** and it is the whole point: this guard's failure mode is a broken
    extractor returning zero claims and passing forever, over the one surface in this
    repository that had no guard at all.

    **Adversarial variant, GENERATED from the live corpus rather than hand-written:** every
    claimed id is perturbed into an id the ledger does not carry, and the guard's own
    predicate must reject each one — proving the check can fail, on real inputs, in the
    quantity the real corpus produces.
    """
    ledger = _LEDGER_PATH.read_text(encoding="utf-8")
    closed = ledger_closed_ids(ledger)
    assert len(closed) > 0, (
        "non-vacuity: the ledger extractor found ZERO closed entries, so every "
        "cross-check below would pass without observing anything (AI-E11-1)"
    )

    stories = sorted(_STORIES_DIR.glob("*.md"))
    assert len(stories) >= 40, (
        f"non-vacuity: only {len(stories)} story file(s) found under "
        f"{_STORIES_DIR} — the population is derived by glob, and an empty or truncated "
        f"one makes this guard silent"
    )

    claims: list[tuple[str, str]] = []
    for story in stories:
        for claimed in story_closure_claims(story.read_text(encoding="utf-8")):
            claims.append((story.name, claimed))
    assert len(claims) > 0, (
        "non-vacuity: ZERO closure claims were extracted from any story file. Either the "
        "extractor is broken or no story has ever claimed a ledger closure; both are "
        "reasons to go RED, and neither is a reason to pass."
    )

    unbacked = {(story, df) for story, df in claims if df not in closed}
    assert len(unbacked & _UNBACKED_AT_LANDING) > 0, (
        "non-vacuity, the direction that matters most: the registered historical backlog "
        "produced ZERO matches, which means the analyzers stopped extracting anything and "
        "this guard has gone silent rather than green"
    )
    new = sorted(f"{story} claims {df} CLOSED" for story, df in unbacked - _UNBACKED_AT_LANDING)
    assert not new, (
        "a story record claims a ledger closure that `deferred-work.md` never received "
        "(AI-E12-6 — the class Stories 12.4 and 12.5 produced four times and every review "
        "passed):\n  " + "\n  ".join(new) + "\nAppend the closure to the ledger with its "
        "date and evidence, or correct the story record. A closure recorded in prose and "
        "not in the ledger is not a closure."
    )
    # The registry SHRINKS: an entry that has since been backed must be REMOVED, exactly
    # as TC-ArgusAgent-MAINT-001-04 treats a file that is no longer over the ceiling. This
    # is what stops a dated backlog becoming a parking lot.
    stale = sorted(
        f"{story}/{df}" for story, df in _UNBACKED_AT_LANDING - unbacked
    )
    assert not stale, (
        "_UNBACKED_AT_LANDING lists claim(s) that the ledger now backs; remove them from "
        "the registry so it can only shrink: " + ", ".join(stale)
    )

    # The predicate must be able to FAIL. Generated from the live claims, with a count.
    generated = 0
    for _story, df in claims:
        assert f"{df}-NONEXISTENT" not in closed
        generated += 1
    assert generated == len(claims) >= 1, (
        f"non-vacuity: {generated} adversarial variant(s) generated from {len(claims)} "
        f"live claim(s)"
    )
    # Positive control over synthetic input — the rule is watched firing, not only
    # observed passing (12.2's deferred-import precedent).
    assert story_closure_claims("**`DF-9-9-Z` — CLOSED 2026-01-01 against evidence.**") == (
        "DF-9-9-Z",
    )
    assert story_closure_claims("`DF-9-9-Z` is progress-noted and stays OPEN") == ()
    assert "DF-9-9-Z" not in ledger_closed_ids("- `DF-9-9-Z` — OPEN, owned")
    assert "DF-9-9-Z" in ledger_closed_ids("- `DF-9-9-Z` — CLOSED 2026-01-01, evidence")


def test_TC_ArgusAgent_DOCS_001_79_the_ledger_disposes_every_entry_this_story_names() -> None:
    """TC-ArgusAgent-DOCS-001-79 — AC8.1/8.3: no entry is left pointing at a run that has now happened.

    **Observable:** the presence of a dated 2026-08-16 Story 13.2 disposition, in the
    ledger, for each of the eight entries this story is required to dispose — the four
    human-adjudication entries whose target the corpus has now moved under
    (`DF-6-6-A`/`-P1`/`-P2`, `DF-7-2-A`) and `AI-E12-3`'s four falsely-closed entries
    (`DF-8-3-A`, `DF-10-4-A`, `DF-10-4-B`, `DF-12-3-A`), which no story owned.

    This is deliberately a check that the ledger RECEIVED a disposition, not that the
    disposition says any particular thing: ruling an entry OPEN with a named owner and a
    reason is a legitimate outcome, and a guard that demanded closure would create pressure
    to close entries that are not closed — the defect `AI-E12-3` exists to clean up.
    """
    ledger = _LEDGER_PATH.read_text(encoding="utf-8")
    marker = "Story 13.2 dispositions — 2026-08-16"
    assert marker in ledger, (
        f"the ledger carries no {marker!r} section; this story's dispositions were "
        f"recorded in prose somewhere else, which is the AI-E12-6 defect class"
    )
    section = ledger[ledger.index(marker) :]
    required = (
        "DF-6-6-A",
        "DF-6-6-A-P1",
        "DF-6-6-A-P2",
        "DF-7-2-A",
        "DF-8-3-A",
        "DF-10-4-A",
        "DF-10-4-B",
        "DF-12-3-A",
        "AI-E11-8",
    )
    missing = tuple(entry for entry in required if entry not in section)
    assert not missing, (
        f"Story 13.2's ledger section does not dispose: {missing!r}. AI-E9-8 forbids "
        f"leaving an entry without a named owner, and this story's AC8 requires each to "
        f"be closed here or re-recorded with a reason."
    )
    assert len(required) == 9, "non-vacuity: the required enumeration must be non-empty"
    for entry in required:
        window = section[section.index(entry) : section.index(entry) + 4000]
        assert "XAgent007" in window or "owner" in window.lower(), (
            f"{entry}'s disposition names no owner (AI-E9-8)"
        )


#: **Story 17.5 / AC6 — the stale-target-story rule, and its two narrowings.**
#:
#: A `deferred-work.md` entry block's own ``- target_story:`` field is a POINTER at the work's
#: container. When the story it names is `done`, the work has no container and the ledger is
#: recording scheduled work that nobody is doing. Measured at `b8eaeee`: of **169** canonical
#: entry blocks, **70** carry a `- target_story:` line naming at least one story key
#: `sprint-status.yaml` records as `done`.
#:
#: ⛔ **THE POPULATION IS NARROWED BY STATED RULE, NEVER BY CONVENIENCE**, and each narrowing
#: carries a positive control over synthetic input below.
#:
#:  1. **AFFIRMATIVE FORM ONLY.** A field reading ``NONE — no story exists after 9.2`` or
#:     ``NONE — the next story that edits X`` mentions a done story as a **landmark**, not as an
#:     owner. A guard that reddens on those is measuring English, not pointers.
#:  2. **THE DISPOSING-STORY FORM IS NOT A VIOLATION.** An entry naming the story that
#:     DISCHARGED it (`DF-1-7-B` → Story 6.2, 2026-06-29) carries the one true pointer shape in
#:     this file, and re-homing it would falsify a signed record. Excluded BY NAME, below.
#:
#: ⛔ **THIS RULE DOES NOT ASK WHETHER AN ENTRY IS OPEN, AND IT MUST NOT.** The obvious
#: implementation — filter by :func:`ledger_closed_ids` — imports a predicate MEASURED
#: defective for exactly this question: at `b8eaeee` it reports **42** disposed ids, two of
#: which are false positives on entries Story 17.5 handles (`DF-13-5-A` at `:4752`, a future
#: conditional, and at `:5751`, a negation the ``_NEGATED`` lookbehind does not know; and
#: `DF-12-3-A` at `:4292`, a half-disposition). `DF-16-6-D` is the senior record on the class
#: and holds that *"the extractor is correct and essentially unimprovable … the record is what
#: is wrong, every single time"*; `DF-INV-LEDGER-A` proposes the opposite. Story 17.5
#: reconciles neither and repairs neither — it declines to build on the contested predicate and
#: records the third independent measurement in `deferred-work.md` under *"Story 17.5
#: dispositions — 2026-08-26"* §(f). **A stale pointer on a disposed entry is still a stale
#: pointer, so no openness test is needed for the rule to be true.**
_STALE_TARGET_RULE = (
    "no canonical deferred-work.md entry block's own `- target_story:` field may "
    "AFFIRMATIVELY name a story key sprint-status.yaml records as `done`"
)

_ENTRY_ID_LINE = re.compile(r"^ *- id: (DF-[A-Z0-9]+(?:-[A-Z0-9]+)*)")
_TARGET_STORY_LINE = re.compile(r"^ *- target_story:(.*)$")
_DEV_STATUS_ENTRY = re.compile(r"^  ([A-Za-z0-9][A-Za-z0-9\-.]*):\s*([a-z-]+)")
#: ``6.2`` / ``6-2`` / ``12.5`` — the short forms this ledger writes as often as the full key.
_SHORT_STORY_REF = re.compile(r"\b(\d{1,2})[.\-](\d{1,2})\b")
#: Markdown emphasis and quoting a field value may open with, stripped before the form test.
_TARGET_VALUE_LEAD = re.compile(r"^[\s*_`\"']+")
#: The field explicitly declares there is no owner.
_NO_OWNER_FORM = re.compile(r"^(?:NONE|N/?A|TBD|UNASSIGNED|UNSCHEDULED)\b", re.IGNORECASE)
#: The field names an INDEFINITE selector — a description of a future story, not a story.
_STORY_SELECTOR_FORM = re.compile(
    r"^(?:the\s+(?:first|next)\s+story|the\s+story\s+that|whichever\s+story|any\s+story)\b",
    re.IGNORECASE,
)


class TargetPointer(NamedTuple):
    """One canonical entry block's own ``- target_story:`` field. Line is 1-based."""

    entry_id: str
    line: int
    value: str


def done_story_keys(sprint_status: str) -> frozenset[str]:
    """Every STORY key ``development_status`` records as ``done``. A pure analyzer.

    ``epic-*`` keys are excluded deliberately: this rule is about a pointer at a STORY, and an
    epic key names a container that a ledger entry may legitimately outlive. Parsed with a
    line regex rather than a YAML loader because the file's value strings carry unquoted
    colons and multi-kilobyte trailing comments — the loader is the fragile choice here.
    """
    status: dict[str, str] = {}
    inside = False
    for line in sprint_status.splitlines():
        if line.startswith("development_status:"):
            inside = True
            continue
        if not inside:
            continue
        match = _DEV_STATUS_ENTRY.match(line)
        if match:
            status[match.group(1)] = match.group(2)
        elif re.match(r"^[A-Za-z_]", line):
            inside = False
    return frozenset(
        key for key, value in status.items() if value == "done" and not key.startswith("epic-")
    )


def ledger_target_pointers(ledger: str) -> tuple[TargetPointer, ...]:
    """Every canonical ``- id: DF-…`` block's OWN ``- target_story:`` field. A pure analyzer.

    "Own" is load-bearing twice. The field is attributed to the id block it sits inside, and
    only the FIRST such field in a block counts — a later one belongs to an appended correction
    sub-entry, not to the entry. And only the field's own physical line is read: its wrapped
    continuation lines are PROSE ABOUT the pointer, and reading them moves the measured
    population from 70 to 87 by sweeping in entries whose pointer is a landmark and whose
    commentary merely recites history.
    """
    pointers: list[TargetPointer] = []
    current: str | None = None
    seen = False
    for number, line in enumerate(ledger.splitlines(), start=1):
        entry = _ENTRY_ID_LINE.match(line)
        if entry:
            current, seen = entry.group(1), False
            continue
        field = _TARGET_STORY_LINE.match(line)
        if field is None or current is None or seen:
            continue
        seen = True
        pointers.append(TargetPointer(current, number, field.group(1).strip()))
    return tuple(pointers)


def is_affirmative_target(value: str) -> bool:
    """Does this ``- target_story:`` value name a story as the OWNER of remaining work?

    Narrowing 1, as a pure predicate so it can be watched failing. ``False`` for the LANDMARK
    forms — an explicit no-owner declaration, or an indefinite selector describing a future
    story rather than naming one.
    """
    body = _TARGET_VALUE_LEAD.sub("", value)
    return not (_NO_OWNER_FORM.match(body) or _STORY_SELECTOR_FORM.match(body))


def named_done_stories(
    value: str, done: frozenset[str], *, ignore_entry_ids: bool = True
) -> tuple[str, ...]:
    """Which ``done`` story keys this field value names, by full key or by short form.

    ``ignore_entry_ids`` blanks ``DF-…`` ids before resolving, because an id is not a pointer:
    *"NONE — coupled to `DF-14-3-B`"* resolves story ``14-3-…`` through the ID alone, and
    reading that as a pointer measures the ledger's naming scheme rather than its records.
    Exposed as a flag, not hard-coded, precisely so ``-80`` can assert that the AFFIRMATIVE
    population — the only one it acts on — is IDENTICAL either way.
    """
    text = _DF_ID_BLANKER.sub(" ", value) if ignore_entry_ids else value
    named = {key for key in done if key in text}
    for match in _SHORT_STORY_REF.finditer(text):
        prefix = f"{match.group(1)}-{match.group(2)}-"
        named.update(key for key in done if key.startswith(prefix))
    return tuple(sorted(named))


def stale_target_pointers(
    ledger: str, done: frozenset[str], *, ignore_entry_ids: bool = True
) -> tuple[tuple[str, str], ...]:
    """Every ``(entry id, done story key)`` pair that violates :data:`_STALE_TARGET_RULE`.

    Both narrowings applied. Pure and exported so the whole rule can be driven over a synthetic
    ledger fragment — a rule enforced only through the live corpus is a rule nobody has
    watched fire.
    """
    violations: set[tuple[str, str]] = set()
    for pointer in ledger_target_pointers(ledger):
        if not is_affirmative_target(pointer.value):
            continue
        for key in named_done_stories(pointer.value, done, ignore_entry_ids=ignore_entry_ids):
            if (pointer.entry_id, key) not in _DISPOSING_STORY_POINTERS:
                violations.add((pointer.entry_id, key))
    return tuple(sorted(violations))


#: **Narrowing 2, BY NAME** (Story 17.5 / AC2, AC6). An entry whose ``target_story`` names the
#: story that DISCHARGED it is the one correct pointer shape in this ledger. `DF-1-7-B` names
#: `6-2-full-python-ast-grounding-of-audited-deep-claims` because Story 6.2 discharged it on
#: 2026-06-29, and the 6.2 story file, the 6.2 retrospective and `argus/pipeline.py`'s own
#: docstring all record it. ⛔ **Its exclusion is asserted here rather than left to a reviewer's
#: memory**, which is the whole difference between a registry and a habit.
_DISPOSING_STORY_POINTERS: frozenset[tuple[str, str]] = frozenset(
    {
        ("DF-1-7-B", "6-2-full-python-ast-grounding-of-audited-deep-claims"),
        # ── Story 19.6, 2026-08-26. Verified by execution, then admitted here — the ONLY
        # legitimate exit from the registry below (narrowing 2). Both clear `DF-1-7-B`'s
        # three-way bar: the 14.3 story file names them, the Epic-14 retrospective records
        # "**2 closed** (`DF-14-2-A`, `DF-14-2-B`)" and "both verified as genuinely received
        # by the ledger", and the shipped code agrees — `importorskip` in
        # `tests/test_vacuous_detector.py` is now 0, and `provenance_scan.py`'s
        # `_ASSIGNMENT_RE` uses `\A`/`\Z` with its docstring recording "re-anchored `\A`
        # 2026-08-18 (Story 14.3)".
        #
        # ⛔ SIXTEEN other entries were ALSO verified ALREADY-RESOLVED and are deliberately
        # NOT admitted here: their `target_story` does not name the story that discharged
        # them, so the pointer is stale for a different reason and stays registered as
        # evidence. `DF-10-3-A` is the clearest — fixed by Story 12.8 while its pointer
        # names 12.9. Rewriting a pointer to manufacture an exit is the forbidden mechanism.
        ("DF-14-2-A", "14-3-the-assertion-vocabulary-crosses-the-languages-the-installer-ships"),
        ("DF-14-2-B", "14-3-the-assertion-vocabulary-crosses-the-languages-the-installer-ships"),
    }
)

#: **The historical population this guard found the day it landed** — registered BY NAME, with
#: the date **2026-08-26**, the owner **XAgent007 (Engineering Lead)** (`AI-E9-8`), and a
#: per-entry reason. Same pattern as ``_UNBACKED_AT_LANDING`` above and Story 12.1's
#: ``_EXEMPT_BY_DESIGN``: a rule that is right, landing over a repository that predates it.
#:
#: **Reasons, a closed vocabulary of two:**
#:
#: * ``"17-5"`` — Story 17.5 dispositioned this entry: it carries a dated append-only note
#:   under its own bullet block with a corrected pointer and a live owner, and it STAYS OPEN.
#:   The ``target_story`` field itself is deliberately NOT rewritten (§3.4 evidence
#:   immutability), so the stale pointer survives as evidence and the pair stays registered.
#: * ``"unverified"`` — registered, **NOT resolved**. Seventeen of these point at closed Epic
#:   8–14 work and belong to epics Story 17.5 has no standing to reopen. ⛔ **Re-homing an entry
#:   this story never verified would be `AI-E12-3`'s defect — resolving entries in prose rather
#:   than against evidence — committed inside the story written to end it.** Owner:
#:   **XAgent007 (Engineering Lead)**, never ``target_story: NONE`` alone.
#:
#: ⛔ **THIS IS A REGISTRY, NOT AN AMNESTY, AND IT CAN ONLY SHRINK.** ``-80`` fails if a
#: registered pair becomes clean (exactly as ``TC-ArgusAgent-MAINT-001-04`` treats a file no
#: longer over the ceiling), and fails immediately on any affirmative stale pointer NOT listed.
#:
#: **Why the two alternatives were rejected, on the record.** *Mass re-homing* the 26 measured
#: ids is `AI-E12-3`. *Narrowing the population until it goes green* is Story 12.1's named
#: anti-pattern, which ``tests/test_module_size_ceiling.py::_REMEDY`` already forbids in shape.
_POINTS_AT_DONE_AT_LANDING: frozenset[tuple[str, str, str]] = frozenset(
    {
        ("DF-10-2-A", "13-1-decide-what-validation-set-is-then-build-it", "unverified"),
        ("DF-10-3-A", "12-9-release-is-published-and-cites-its-gate", "unverified"),
        ("DF-10-4-A", "12-5-default-install-grounds-languages-it-claims", "unverified"),
        ("DF-10-4-B", "10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1", "unverified"),
        ("DF-10-4-B", "12-4-every-outcome-names-its-next-action", "unverified"),
        ("DF-10-4-C", "12-8-the-tool-explains-itself", "unverified"),
        ("DF-10-4-D", "12-1-pipeline-stops-breaching-its-own-limit", "unverified"),
        ("DF-11-2-A", "12-5-default-install-grounds-languages-it-claims", "unverified"),
        ("DF-11-2-B", "12-5-default-install-grounds-languages-it-claims", "unverified"),
        ("DF-11-4-A", "12-5-default-install-grounds-languages-it-claims", "unverified"),
        ("DF-11-4-B", "12-5-default-install-grounds-languages-it-claims", "unverified"),
        ("DF-11-4-D", "12-4-every-outcome-names-its-next-action", "unverified"),
        ("DF-11-5-A", "12-1-pipeline-stops-breaching-its-own-limit", "unverified"),
        ("DF-11-5-C", "12-7-commands-the-readme-promises-actually-exist", "unverified"),
        ("DF-12-1-A", "12-2-deep-audit-is-wired-opt-in-and-honest", "unverified"),
        ("DF-12-1-A", "12-3-a-re-run-returns-the-recorded-result", "unverified"),
        ("DF-12-1-B", "12-3-a-re-run-returns-the-recorded-result", "unverified"),
        ("DF-12-1-C", "12-5-default-install-grounds-languages-it-claims", "unverified"),
        ("DF-12-2-C", "12-3-a-re-run-returns-the-recorded-result", "unverified"),
        ("DF-12-2-D", "6-2-full-python-ast-grounding-of-audited-deep-claims", "17-5"),
        ("DF-12-3-A", "6-2-full-python-ast-grounding-of-audited-deep-claims", "17-5"),
        ("DF-12-7-B", "13-3-record-the-result-and-let-it-decide", "unverified"),
        ("DF-13-1-A", "13-1-decide-what-validation-set-is-then-build-it", "unverified"),
        ("DF-13-2-A", "13-2-adjudicate-every-finding-by-a-named-human", "unverified"),
        ("DF-14-1-A", "6-2-full-python-ast-grounding-of-audited-deep-claims", "17-5"),
        (
            "DF-14-3-D",
            "15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks",
            "unverified",
        ),
        ("DF-14-3-H", "13-5-re-measure-the-gate-against-the-corrected-instrument", "unverified"),
        ("DF-16-7-A", "6-2-full-python-ast-grounding-of-audited-deep-claims", "17-5"),
        ("DF-16-7-B", "6-2-full-python-ast-grounding-of-audited-deep-claims", "17-5"),
        ("DF-5-1-A", "6-1-llm-dispatch-port-minions-orchestrator-adapter", "unverified"),
        ("DF-6-6-A", "13-2-adjudicate-every-finding-by-a-named-human", "unverified"),
        ("DF-7-2-A", "13-2-adjudicate-every-finding-by-a-named-human", "unverified"),
        ("DF-8-1-A", "8-3-plain-english-report-stops-describing-impossible-state", "unverified"),
        (
            "DF-8-2-A",
            "8-2-critical-subsystem-gates-operator-can-actually-satisfy",
            "unverified",
        ),
        ("DF-8-2-A", "8-3-plain-english-report-stops-describing-impossible-state", "unverified"),
        ("DF-8-2-B", "8-3-plain-english-report-stops-describing-impossible-state", "unverified"),
        ("DF-8-3-A", "12-4-every-outcome-names-its-next-action", "unverified"),
        ("DF-8-3-B", "8-4-tell-integrators-what-changed", "unverified"),
        ("DF-8-4-A", "9-2-ship-distribution-another-repo-can-actually-resolve", "unverified"),
        ("DF-8-5-A", "9-2-ship-distribution-another-repo-can-actually-resolve", "unverified"),
        ("DF-9-2-C", "12-1-pipeline-stops-breaching-its-own-limit", "unverified"),
        ("DF-AUD-APAA-A", "12-3-a-re-run-returns-the-recorded-result", "unverified"),
        ("DF-AUD-APAA-C", "10-1-release-status-must-cite-evidence", "unverified"),
        ("DF-AUD-APAA-D", "10-2-multi-language-grounding-is-v1-in-the-specs", "unverified"),
        ("DF-AUD-APAA-E", "10-3-invocation-contract-says-what-the-cli-accepts", "unverified"),
        ("DF-AUD-APAA-F", "10-4-a-grammar-that-fails-to-load-names-why", "unverified"),
        ("DF-INV-VACUOUS-A", "6-2-full-python-ast-grounding-of-audited-deep-claims", "17-5"),
    }
)

#: The AFFIRMATIVE / LANDMARK partition MEASURED at `b8eaeee` over the 70 blocks whose own
#: ``- target_story:`` line names a `done` story. Asserted, not described: a narrowing whose
#: size nobody watches is a narrowing that can quietly swallow the population.
_LANDMARK_BLOCKS_AT_LANDING = 18
_LANDMARK_BLOCKS_AT_LANDING_IDS_BLANKED = 13
_AFFIRMATIVE_BLOCKS_AT_LANDING = 52


def test_TC_ArgusAgent_DOCS_001_80_no_ledger_entry_points_its_target_story_at_a_done_story() -> None:
    """TC-ArgusAgent-DOCS-001-80 — Story 17.5 / AC6, AC7: nothing points at a closed story.

    **Observable:** for every canonical `deferred-work.md` entry block, whether its own
    ``- target_story:`` field AFFIRMATIVELY names a story key `sprint-status.yaml` records as
    ``done`` — work recorded as scheduled into a container that has already shut.

    **Why the class needed a guard rather than a reviewer.** `DF-16-5-A`'s own body predicted
    one of these in terms — *"Pinning it to a story nobody has written yet is how `DF-14-3-H`'s
    `target_story: 13-5` went stale"* — and `DF-14-3-H` went stale anyway, because nothing was
    watching. In the same epic, Story 17.3 **created** a fresh instance of the twin defect in
    `argus/detectors/assertion_strength.py` one story before the story chartered to remove it.
    ⛔ **Knowing about a defect class does not prevent it** (`DF-16-6-D`).

    **GUARD-ADEQUACY (`AI-E11-1`):** non-vacuity is asserted before anything else and at every
    stage; both narrowings carry positive controls over synthetic input; the whole rule is
    driven RED at the REAL SEAM against a synthetic ledger fragment built in ``tmp_path``
    (never against the committed ledger, which a peer session is writing to); and the
    adversarial variant is GENERATED from the live violation set with its count asserted.
    """
    ledger = _LEDGER_PATH.read_text(encoding="utf-8")
    sprint_status = _SPRINT_STATUS_PATH.read_text(encoding="utf-8")

    # ---- non-vacuity, before any claim ------------------------------------------------
    done = done_story_keys(sprint_status)
    assert len(done) > 0, (
        "non-vacuity: ZERO `done` story keys parsed out of sprint-status.yaml, so every "
        "comparison below would pass without observing anything (AI-E11-1)"
    )
    assert "6-2-full-python-ast-grounding-of-audited-deep-claims" in done, (
        "non-vacuity: the parser lost the one story key this whole rule was written about"
    )
    pointers = ledger_target_pointers(ledger)
    assert len(pointers) > 0, "non-vacuity: the ledger extractor found ZERO target_story fields"
    assert len(pointers) >= 100, (
        f"non-vacuity: only {len(pointers)} target_story field(s) parsed; the ledger carried "
        f"150 at landing and a collapse here makes this guard silent rather than green"
    )

    # ---- narrowing 1, MEASURED both ways, and the affirmative set is the same either way
    resolving = [p for p in pointers if named_done_stories(p.value, done, ignore_entry_ids=False)]
    affirmative = [p for p in resolving if is_affirmative_target(p.value)]
    landmark = [p for p in resolving if not is_affirmative_target(p.value)]
    assert len(landmark) == _LANDMARK_BLOCKS_AT_LANDING, (
        f"the LANDMARK exclusion moved: {len(landmark)} block(s) excluded, "
        f"{_LANDMARK_BLOCKS_AT_LANDING} at landing. A narrowing whose size nobody watches is "
        f"how a population gets quietly swallowed (Story 12.1's anti-pattern)."
    )
    assert len(affirmative) == _AFFIRMATIVE_BLOCKS_AT_LANDING, (
        f"the AFFIRMATIVE population moved: {len(affirmative)} vs "
        f"{_AFFIRMATIVE_BLOCKS_AT_LANDING} at landing"
    )
    blanked = [p for p in pointers if named_done_stories(p.value, done)]
    blanked_landmark = [p for p in blanked if not is_affirmative_target(p.value)]
    assert len(blanked_landmark) == _LANDMARK_BLOCKS_AT_LANDING_IDS_BLANKED, (
        f"the id-blanked LANDMARK count moved: {len(blanked_landmark)} vs "
        f"{_LANDMARK_BLOCKS_AT_LANDING_IDS_BLANKED} at landing"
    )
    assert [p.entry_id for p in blanked if is_affirmative_target(p.value)] == [
        p.entry_id for p in affirmative
    ], (
        "the AFFIRMATIVE population must not depend on whether `DF-…` ids are blanked before "
        "story references are resolved — if it does, this guard is measuring the ledger's "
        "naming scheme rather than its pointers"
    )

    # ---- the rule --------------------------------------------------------------------
    violations = stale_target_pointers(ledger, done)
    assert len(violations) > 0, (
        "non-vacuity: ZERO stale pointers found. Either the analyzers stopped extracting or "
        "the registry below is entirely dead weight; both are reasons to go RED"
    )
    registered = {(entry, key) for entry, key, _ in _POINTS_AT_DONE_AT_LANDING}
    assert len(registered) == len(_POINTS_AT_DONE_AT_LANDING), (
        "_POINTS_AT_DONE_AT_LANDING carries two reasons for one pair"
    )
    assert {reason for _, _, reason in _POINTS_AT_DONE_AT_LANDING} <= {"17-5", "unverified"}, (
        "a registry reason outside the closed vocabulary — a free-text reason is a reason "
        "nobody can audit"
    )
    new = sorted(f"{entry} -> {key}" for entry, key in set(violations) - registered)
    assert not new, (
        f"a deferred-work.md entry points its `target_story` at a story sprint-status.yaml "
        f"records as `done` — {_STALE_TARGET_RULE}:\n  " + "\n  ".join(new) + "\n"
        "Give the entry a live owner and a destination that exists (a named human, or a scope "
        "change to be argued through `bmad-correct-course`), or record its disposition. "
        "⛔ Do NOT register it here to make this green: this registry is dated 2026-08-26 and "
        "can only shrink."
    )
    stale = sorted(f"{entry} -> {key}" for entry, key in registered - set(violations))
    assert not stale, (
        "_POINTS_AT_DONE_AT_LANDING lists pair(s) that are now clean; remove them so the "
        "registry can only shrink (TC-ArgusAgent-MAINT-001-04's treatment): " + ", ".join(stale)
    )

    # ---- narrowing 2, asserted rather than remembered ---------------------------------
    assert len(_DISPOSING_STORY_POINTERS) > 0
    assert ("DF-1-7-B", "6-2-full-python-ast-grounding-of-audited-deep-claims") in (
        _DISPOSING_STORY_POINTERS
    ), (
        "`DF-1-7-B` names Story 6.2 because Story 6.2 DISCHARGED it on 2026-06-29. Re-homing "
        "it would falsify a signed record, and its exclusion is asserted here rather than "
        "trusted to a reviewer's memory (Story 17.5 / AC2)."
    )
    assert not (set(violations) & _DISPOSING_STORY_POINTERS), (
        "the disposing-story narrowing is not being applied"
    )
    assert not (registered & _DISPOSING_STORY_POINTERS), (
        "a disposing-story pointer is registered as a violation; it is not one"
    )

    # ---- positive controls over SYNTHETIC input: each narrowing watched FAILING --------
    assert is_affirmative_target("**12-5-default-install-grounds-languages-it-claims**")
    assert is_affirmative_target("**6.2** (`argus` dataflow / scope-resolved grounding)")
    assert not is_affirmative_target("**NONE — no story exists after 9.2.**")
    assert not is_affirmative_target("NONE — the next story that edits `tests/x.py`")
    assert not is_affirmative_target("the first story that edits the 6.5/6.6 precision surface")
    assert not is_affirmative_target("**whichever story performs the flip — in the SAME change**")
    assert named_done_stories("**6.2** — the full grounding", done) == (
        "6-2-full-python-ast-grounding-of-audited-deep-claims",
    )
    assert named_done_stories("**NONE — coupled to `DF-14-3-B`.**", done) == ()
    assert named_done_stories("**NONE — coupled to `DF-14-3-B`.**", done, ignore_entry_ids=False), (
        "the control is inert: this value must resolve a done key ONLY through the id"
    )

    # ---- RED AT THE REAL SEAM, over a synthetic fragment in tmp_path -------------------
    # The committed ledger is shared with a concurrent peer session and is never mutated to
    # demonstrate a guard (Story 17.3's discipline). The fragment below is the real input
    # shape, parsed by the real analyzers.
    offender = (
        "- **`DF-99-9-Z` — a synthetic entry.**\n"
        "  - id: DF-99-9-Z\n"
        "  - owner: nobody\n"
        "  - target_story: **6-2-full-python-ast-grounding-of-audited-deep-claims**\n"
        "  - category: synthetic\n"
    )
    landmark_twin = offender.replace(
        "  - target_story: **6-2-full-python-ast-grounding-of-audited-deep-claims**\n",
        "  - target_story: **NONE — the next story that edits "
        "`6-2-full-python-ast-grounding-of-audited-deep-claims`**\n",
    )
    assert stale_target_pointers(offender, done) == (
        ("DF-99-9-Z", "6-2-full-python-ast-grounding-of-audited-deep-claims"),
    ), "the rule cannot see a violation it was written to see"
    assert stale_target_pointers(landmark_twin, done) == (), (
        "the LANDMARK narrowing does not hold: a `NONE — the next story that …` field naming "
        "a done story as a reference point is not a pointer at it"
    )


def test_TC_ArgusAgent_DOCS_001_80_the_stale_target_rule_fires_on_a_ledger_read_from_disk(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DOCS-001-80 (part 2) — the same rule, through a real file read.

    Part 1 proves the PREDICATE. This proves the SEAM: a ledger file on disk, read the way the
    guard reads the committed one — ``encoding="utf-8"`` stated explicitly, because the
    artifact tree carries non-ASCII and an inherited host locale is the exact defect class that
    turned a CI run red — parsed, and driven to BOTH outcomes. Written under ``tmp_path`` and
    never against this repository's own ledger, which a peer session is appending to.

    The adversarial variant is GENERATED from the LIVE violation set with a count asserted: each
    real offender's story key is perturbed into one `sprint-status.yaml` does not carry, and the
    rule must stop seeing it. A predicate that cannot be made to change its mind on real inputs
    is not being observed, only trusted.
    """
    done = done_story_keys(_SPRINT_STATUS_PATH.read_text(encoding="utf-8"))
    ledger = _LEDGER_PATH.read_text(encoding="utf-8")
    live = stale_target_pointers(ledger, done)
    assert len(live) > 0, "non-vacuity: no live violations to generate variants from"

    red = tmp_path / "deferred-work.md"
    red.write_text(
        "## Deferred from: a synthetic story\n\n"
        "- **`DF-99-9-Z` — 🔴 a synthetic entry with a non-ASCII body.**\n"
        "  - id: DF-99-9-Z\n"
        "  - target_story: **13-2-adjudicate-every-finding-by-a-named-human** — done since\n"
        "    2026-08-16, so this entry has no container\n"
        "  - severity: 🟡\n",
        encoding="utf-8",
    )
    assert stale_target_pointers(red.read_text(encoding="utf-8"), done) == (
        ("DF-99-9-Z", "13-2-adjudicate-every-finding-by-a-named-human"),
    ), "the rule does not fire on a ledger file read from disk"

    green = tmp_path / "deferred-work-green.md"
    green.write_text(
        "## Deferred from: a synthetic story\n\n"
        "- **`DF-99-9-Z` — 🔴 the same entry, re-homed to a live owner.**\n"
        "  - id: DF-99-9-Z\n"
        "  - target_story: **NONE — XAgent007 (Engineering Lead) to schedule**, superseding "
        "the old pointer at `13-2-adjudicate-every-finding-by-a-named-human`\n"
        "  - severity: 🟡\n",
        encoding="utf-8",
    )
    green_text = green.read_text(encoding="utf-8")
    assert named_done_stories(
        "**NONE — XAgent007 (Engineering Lead) to schedule**, superseding "
        "the old pointer at `13-2-adjudicate-every-finding-by-a-named-human`",
        done,
    ) == ("13-2-adjudicate-every-finding-by-a-named-human",), (
        "the control is inert: the re-homed field must still MENTION the done story, or this "
        "assertion passes for the wrong reason"
    )
    assert stale_target_pointers(green_text, done) == (), (
        "the rule fires on an entry that has been correctly re-homed"
    )

    generated = 0
    for entry_id, key in live:
        mangled = "ZZ-ZZ-" + key.split("-", 2)[-1]
        perturbed = f"  - id: {entry_id}\n  - target_story: **{mangled}**\n"
        assert stale_target_pointers(perturbed, done) == (), (
            f"a story key sprint-status.yaml does not carry was still read as a pointer: "
            f"{mangled}"
        )
        generated += 1
    assert generated == len(live) >= 1, (
        f"non-vacuity: {generated} adversarial variant(s) generated from {len(live)} live "
        f"violation(s)"
    )
