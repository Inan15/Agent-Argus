"""Story 11.5 / AC6 — the bare-word "Minions" subject claims, and the corpus the FR34
disclosure names.

Verification area ``ArgusAgent-DOCS`` (``TC-ArgusAgent-DOCS-001-57``, ``-58``). **Test ids are
byte-identical to the ones this module was split out of** — ``architecture.md``,
``deferred-work.md`` and five test modules cite them, and renumbering an id silently
invalidates every one of those citations.

**Why this module exists — the cohesion boundary, stated so the next reader does not have to
guess.** ``tests/test_built_distribution.py`` measures a freshly BUILT wheel and sdist: does
every shipped module import from the artifact, does the sdist ship no test tree, do the
published module figures match the built thing. That is a claim about a *distribution*, and
every guard there pays the cost of building one.

``-57`` and ``-58`` are a different subject on a different substrate: they read the SOURCE
tree and the FR34 disclosure CONSTANTS and ask whether the sentences Argus prints about
itself have the right SUBJECT. They never build anything. They lived next door because
Story 11.5 wrote both in one pass, not because they belong together — and the cost of that
adjacency came due in Story 13.5, which had to correct
``INSTRUMENT_DISCLOSURE_VALIDATED``'s corpus name against a module sitting at exactly
**1200 of NFR-M1's 1200 lines, with zero headroom**.

Split by COHESION and not by arithmetic (the Story 13.4 precedent): the boundary is the
section banner Story 11.5 itself drew, no function is split across it, no test id moved, and
the import edge runs one way only — this module imports nothing from
``tests/test_built_distribution.py``, and that module imports nothing from here. There is no
``_EXEMPT_BY_DESIGN`` entry: ``MAINT-001-04`` audits that registry and it may only shrink.

**What ``-58`` asserts after Story 13.5, and what it deliberately does not.** The two
disclosure constants name DIFFERENT corpora, and that asymmetry is the correction, not an
oversight:

* ``INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED`` — the live text — names the **Argus
  dogfood corpus**, because the self-audit of this repository is what it rests on. Story 11.5
  corrected its subject from "Minions" and nothing since has touched it.
* ``INSTRUMENT_DISCLOSURE_VALIDATED`` — reachable ONLY in the ``VALIDATED`` branch, which no
  production call site can reach today — named the same dogfood corpus, and that was
  **latently false**: the Epic 13 adjudication ran over the ratified five-repository
  validation corpus, which is exactly the population Story 13.1 EXCLUDED the dogfood
  self-audit from. The sentence has never been read in anger because nobody can reach it;
  the Epic-13 interim retrospective §11.3(a) recorded it, and Story 13.5 / AC6 corrected it.
  Correcting an unreachable string must not flip the gate, so ``-58`` asserts in the same
  place that ``INSTRUMENT_STATUS`` is still ``NOT_INDEPENDENTLY_VALIDATED``.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

# ─────────────────────────────────────────────────────────────────────────────
# AC6 — the bare-word "Minions" subject claims, classified one by one
# ─────────────────────────────────────────────────────────────────────────────

_BARE_MINIONS = re.compile(r"(?<![A-Za-z_])Minions(?![A-Za-z_])")

# AC6.1 — all 21 measured occurrences, classified with a reason. NINETEEN are
# TRUE-HISTORICAL and stay: each records where a design, a constant or a containment rule
# came FROM, and deleting that provenance would make the module less true, not more. TWO
# were FALSE-SUBJECT claims about what Argus does TODAY and were rewritten (below).
# No blanket find-and-replace: this table is why.
_TRUE_HISTORICAL_SITES: dict[str, tuple[tuple[str, str], ...]] = {
    "argus/__init__.py": (
        (
            "with no Minions package present",
            "KEEP — a NEGATIVE claim about the dependency graph, and it is true.",
        ),
    ),
    "argus/audit/deep_audit.py": (
        (
            "wired into the Minions product run path",
            "KEEP — states where the module is NOT wired; historical boundary.",
        ),
        (
            "nothing in Minions orchestration",
            "KEEP — the other half of the same negative boundary claim.",
        ),
    ),
    "argus/audit/minions_llm_adapter.py": (
        (
            "Backward-compatible Minions LLM Adapter wrapper",
            "KEEP — names the upstream interface this shim is compatible WITH.",
        ),
    ),
    "argus/cost/__init__.py": (
        (
            "reusing the Minions",
            "KEEP — AR7 reuse provenance for the account_spend fold.",
        ),
    ),
    "argus/cost/budget_governor.py": (
        (
            "UPSTREAM Minions cost-guardrails module ACROSS a product boundary",
            "KEEP — the reuse target this module wraps; unit 2, zero lines spent.",
        ),
        (
            "Story 3.1 required wrapping the UPSTREAM Minions cost-guardrails module",
            "KEEP — dated historical requirement, true as written.",
        ),
        (
            "Minions stayed the ONE hard-ceiling authority",
            "KEEP — past tense, describes the Story-3.1 arrangement.",
        ),
    ),
    "argus/dogfood/proof_render.py": (
        (
            "The independent Story-7.2 run over the Minions",
            "KEEP — the run really was over Minions; that is what makes it independent.",
        ),
    ),
    "argus/dogfood/proof_run.py": (
        (
            "Story 7.2 originally ran it over the Minions platform",
            "KEEP — explicitly past tense and explicitly superseded. Also byte-fenced "
            "by AC1.5 and in unit 2, so a rewrite would spend budget to make it worse.",
        ),
    ),
    "argus/evidence/__init__.py": (
        (
            "SEPARATE from the Minions",
            "KEEP — a separation claim; the subject is the separation, not the corpus.",
        ),
    ),
    "argus/evidence/bundle.py": (
        (
            "Separateness from the Minions governance bundle",
            "KEEP — names the artifact this one is deliberately NOT; unit 2, free.",
        ),
        (
            "a DIFFERENT artifact from Minions'",
            "KEEP — same separation claim, restated for the reader of the class.",
        ),
    ),
    "argus/index/partitioner.py": (
        (
            "the 18-2 Minions ``is_relative_to``-not-``startswith`` precedent",
            "KEEP — a citation of where the rule came from; unit 2, free.",
        ),
    ),
    "argus/store/__init__.py": (
        (
            "the Minions ``WorkspaceContainmentError`` containment logic",
            "KEEP — names the imported authority, which is the AR7 point.",
        ),
    ),
    "argus/store/paths.py": (
        (
            "REUSE Minions' canonical containment authority by import",
            "KEEP — AR7 reuse provenance for a SECURITY control.",
        ),
        (
            "The architecture mandates reuse of Minions'",
            "KEEP — restates the architectural mandate this module obeys.",
        ),
        (
            "mirror of the Minions helper",
            "KEEP — tells a maintainer which upstream helper to diff against.",
        ),
    ),
    "argus/store/writer.py": (
        (
            "the Minions ``WorkspaceContainmentError``",
            "KEEP — same imported containment authority.",
        ),
    ),
    # The two occurrences that survive in this file are NOT the disclosure any more. They
    # are the correction record itself: it cites the two modules whose true-historical
    # claims make the old subject false. Deleting them would delete the evidence.
    "argus/verdict/negative_assurance.py": (
        (
            "`argus/dogfood/proof_run.py` records that the Minions",
            "KEEP — cites the superseded Story-7.2 run that the old subject leaned on.",
        ),
        (
            'Minions package present". A false SUBJECT',
            "KEEP — cites argus/__init__.py's negative dependency claim.",
        ),
    ),
}

# The TWO false-subject claims, and what replaced them. Both are printed on a user's
# terminal by `argus audit .` today via the FR34 instrument disclosure, which makes them
# the highest-visibility sentences Argus has. "the Minions dogfood corpus" was false and
# the sentence contradicted itself four words later ("a self-audit of THIS repository");
# argus/dogfood/proof_run.py records that the Minions run was Story 7.2's and superseded,
# and argus/__init__.py states Argus runs "with no Minions package present". The SUBJECT is
# corrected; the claim, the status vocabulary and the removal condition are untouched.
#
# ⚠️ SECOND CORRECTION, 2026-08-18 (Story 13.5 / AC6). The second row's "now" text was
# `"Argus dogfood corpus. The corpus and the adjudication"` and that was STILL wrong — 11.5
# fixed the subject and left the CORPUS wrong. The >=80% gate was measured over the ratified
# five-repository validation corpus, not over the dogfood self-audit Story 13.1 excluded
# from N. The "was" side is UNCHANGED and stays asserted: the Minions subject must never
# come back, and this table is what proves it did not while the sentence was corrected twice.
_REWRITTEN_FALSE_SUBJECT_SITES: dict[str, tuple[tuple[str, str], ...]] = {
    "argus/verdict/negative_assurance.py": (
        (
            "rest on the Minions dogfood corpus, a self-audit of this ",
            "rest on the Argus dogfood corpus, a self-audit of this ",
        ),
        (
            "Minions dogfood corpus. The corpus and the adjudication",
            "ratified five-repository validation corpus. The corpus and the adjudication",
        ),
    ),
}


def _tracked_argus_modules() -> tuple[str, ...]:
    done = subprocess.run(
        ["git", "ls-files", "--", "argus"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, f"`git ls-files -- argus` failed: {done.stderr}"
    return tuple(p for p in done.stdout.split() if p.endswith(".py"))


def test_TC_ArgusAgent_DOCS_001_57_every_minions_claim_in_the_package_is_classified() -> None:
    """TC-ArgusAgent-DOCS-001-57 — AC6.1/AC6.3: a closure over the tree, not a list.

    The epic's premise said 22 occurrences across 14 modules and the ledger said 25; the
    measured truth was 21 across 14. This project has hand-counted wrong six times, so the
    contract is the regex over ``git ls-files -- argus``, never the table. A NEW bare-word
    occurrence fails until somebody reads it and classifies it, which is the only step that
    can tell a historical provenance note from a false claim about what Argus is.
    """
    measured: dict[str, int] = {}
    for rel in _tracked_argus_modules():
        hits = len(_BARE_MINIONS.findall((_REPO_ROOT / rel).read_text(encoding="utf-8")))
        if hits:
            measured[rel] = hits

    unclassified = sorted(set(measured) - set(_TRUE_HISTORICAL_SITES))
    assert not unclassified, (
        f"module(s) carry an unclassified bare-word 'Minions' subject claim: {unclassified}. "
        "Read each occurrence and record it as true-historical or false-subject in "
        "_TRUE_HISTORICAL_SITES — a blanket replace is banned precisely because the two "
        "classes read identically to a regex."
    )
    vanished = sorted(set(_TRUE_HISTORICAL_SITES) - set(measured))
    assert not vanished, (
        f"classified provenance disappeared from {vanished}. If it was removed on purpose, "
        "remove it from the table too, so the table never describes a tree that is gone."
    )
    for rel, entries in _TRUE_HISTORICAL_SITES.items():
        assert measured[rel] == len(entries), (
            f"{rel} carries {measured[rel]} bare-word occurrence(s) but "
            f"{len(entries)} are classified"
        )
        text = (_REPO_ROOT / rel).read_text(encoding="utf-8")
        for snippet, reason in entries:
            assert snippet in text, f"{rel}: classified snippet is not in the file: {snippet!r}"
            assert reason.startswith("KEEP — "), f"{rel}: {snippet!r} has no recorded reason"

    for rel, corrections in _REWRITTEN_FALSE_SUBJECT_SITES.items():
        text = (_REPO_ROOT / rel).read_text(encoding="utf-8")
        for was, now in corrections:
            assert was not in text, f"{rel}: the FALSE SUBJECT came back: {was!r}"
            assert now in text, f"{rel}: the corrected text is missing: {now!r}"


def test_TC_ArgusAgent_DOCS_001_58_the_instrument_disclosure_names_the_corpus_it_rests_on() -> None:
    """TC-ArgusAgent-DOCS-001-58 — AC6.2: a SUBJECT was corrected; no claim was changed.

    The disclosure is Story 11.1's FR34 surface and is single-sourced — README.md,
    CHANGELOG.md, pyproject.toml and action.yml are compared against these constants by
    tests/test_instrument_disclosure.py. This asserts the part that guard cannot: that the
    corpus is named correctly, and that correcting the name did not quietly weaken the
    status vocabulary, the negation, or what removes the notice.

    AMENDED 2026-08-18 (Story 13.5 / AC6). The two members name DIFFERENT corpora and the
    guard now asserts the ASYMMETRY rather than a shared literal. Until today it looped over
    both constants asserting ``"Argus dogfood corpus" in text``, which is exactly why the
    ``VALIDATED`` member's corpus name was wrong and green at the same time: the live text
    genuinely rests on the dogfood self-audit, the unreachable one describes an Epic 13
    adjudication that ran over the five-repository validation corpus, and one literal
    asserted over both could only be right about one of them.
    """
    from argus.verdict.negative_assurance import (
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_SHORT_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_VALIDATED,
        INSTRUMENT_STATUS,
        InstrumentStatus,
        render_instrument_disclosure,
    )

    for text in (
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_VALIDATED,
    ):
        assert not _BARE_MINIONS.findall(text), f"false subject restored: {text}"

    # (a) The LIVE text rests on the dogfood self-audit, and says so.
    assert "Argus dogfood corpus" in INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED

    # (b) The VALIDATED text names the corpus the adjudication ACTUALLY ran over. Both
    # directions: the corrected name is present AND the false one is gone, because an
    # assertion that only checks the new string stays green if somebody adds the old one back
    # beside it.
    assert (
        "ratified five-repository validation corpus" in INSTRUMENT_DISCLOSURE_VALIDATED
    ), (
        "the VALIDATED disclosure must name the corpus the >=80% adjudication ran over — "
        "the ratified five-repository validation set (tests/corpus/_manifest.py)"
    )
    assert "dogfood" not in INSTRUMENT_DISCLOSURE_VALIDATED.lower(), (
        "the VALIDATED disclosure names the DOGFOOD corpus again. Story 13.1 excluded the "
        "dogfood self-audit from N precisely so a tool could not validate itself on itself; "
        "a cleared-gate sentence citing it would publish that exclusion as its opposite."
    )

    # (c) NON-VACUITY, and the reason this assertion sits here rather than anywhere else:
    # correcting an unreachable string must not be able to flip the gate. The declared
    # status is unchanged and every RENDERED surface is byte-identical to the live text —
    # so the corrected sentence provably reaches no user today.
    assert INSTRUMENT_STATUS is InstrumentStatus.NOT_INDEPENDENTLY_VALIDATED, (
        "correcting the VALIDATED branch's corpus name must not move the declared status. "
        "The gate is BLOCKED with the precision condition UNEVALUABLE (Story 13.5); an "
        "UNEVALUABLE outcome does not clear anything."
    )
    assert (
        render_instrument_disclosure(INSTRUMENT_STATUS)
        == INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED
    ), "the rendered notice moved — AC6 changes only the branch nothing renders"
    assert (
        render_instrument_disclosure(InstrumentStatus.VALIDATED)
        == INSTRUMENT_DISCLOSURE_VALIDATED
    ), "the VALIDATED branch must render the constant this guard just checked, not a copy"

    # AMENDED 2026-08-17: by SUBSTANCE, not internal literals. Dropped "no human
    # true-positive/false-positive adjudication" (FALSE since the named human adjudicated
    # all 31 findings that day) and "Epic 13" (internal, ships to end users). FR34's three
    # requirements -- validation state, corpus, removal condition -- all still asserted.
    current = INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED
    assert "has not been independently validated" in current
    assert "a self-audit of this repository" in current
    assert "precision gate" in current, "the removal condition must be named (FR34.4)"
    assert "removed only when" in current
    assert "nothing else removes it" in current
    assert INSTRUMENT_DISCLOSURE_SHORT_NOT_INDEPENDENTLY_VALIDATED in current
    assert [status.value for status in InstrumentStatus] == [
        "not-independently-validated",
        "validated",
    ], "the two-member InstrumentStatus vocabulary is Epic 13's, not this story's"
