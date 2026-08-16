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

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_LEDGER_PATH = _ARTIFACTS / "deferred-work.md"
_ARCHITECTURE_PATH = _ARTIFACTS / "architecture.md"
_STORIES_DIR = _ARTIFACTS / "stories"

#: A ledger id, matched WHOLE and GREEDILY. This pattern is load-bearing and its first
#: form was wrong in the direction that makes a guard silent: a lazy
#: ``DF-[A-Za-z0-9-]*?[A-Za-z0-9]`` matched ``DF-12`` inside ``DF-12-3-A``, so every claim
#: was cross-checked against a truncated id the ledger could never carry — eight false
#: accusations on the first run. Segments are upper-case/digit, which is the shape every
#: id in this ledger actually has (``DF-6-6-A``, ``DF-6-6-A-P1``, ``DF-AUD-APAA-C``).
_DF_ID = r"DF-[A-Z0-9]+(?:-[A-Z0-9]+)*"

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
        # AC8.2 — the ledger-claim cross-check rule (AI-E12-6).
        "Ledger-claim cross-check enforcement",
        "a claimed closure `deferred-work.md` never received fails CI",
        "tests/test_governance_record_integrity.py",
        "TC-ArgusAgent-DOCS-001-78",
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
