"""The project name is spelled one way on the surfaces a stranger reads (NAMING.md).

Verification area ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-81``..``-83``, continuing the
index; ``-80`` was the previous highest).

``NAMING.md`` was written 2026-08-29 and settled four spellings, each with one job:
``Agent-Argus`` in prose, ``ArgusAgent`` in identifiers, ``argus-agent`` on a package
index, ``argus`` at a shell prompt. It settled them and nothing enforced them, so on the
day it was written the repository disagreed with it in 41 places across 19 files --
including ``action.yml``, which said ``Agent-Argus`` on line 1 and ``ArgusAgent`` on line
81. A rule with no guard is a claim, and this repository does not accept claims that
nothing measures.

WHAT IS ALLOWED, and why the token is not simply banned. Roughly 5,600 occurrences of
``ArgusAgent`` are *identifiers* -- driver ids, test-case ids, the artifact directory,
``DOGFOOD_ArgusAgent_VERSION``. Those are contract names cited by stories and signed
records; ``NAMING.md`` freezes them deliberately. A doc may also QUOTE the token inside
backticks, which is how ``NAMING.md`` states its own rule. What is forbidden is the bare
word standing in prose where the product is being named.

WHY ``CHANGELOG.md`` IS SCOPED TO ITS PREAMBLE. Its dated entries were written when the
project was called ``ArgusAgent``, and architecture.md 3.4 forbids rewriting a record to
match a later state. Only the standing header -- the text before the first ``##`` heading,
which describes the project in the present tense -- is guarded.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]

# Frozen identifier forms, per NAMING.md. Stripped before the prose check.
_FROZEN = re.compile(
    r"ArgusAgent-[A-Z]"  # driver ids in both shapes: ArgusAgent-FR-17, ArgusAgent-AR8, -NFR-D3
    r"|TC-ArgusAgent-[A-Z]+"  # test-case ids
    r"|design-artifacts[/\\]+ArgusAgent"  # planning-artifact path
    r"|DOGFOOD_ArgusAgent"  # derived constant
    r"|ArgusAgent/"  # the artifact directory in a tree diagram
    r"|`ArgusAgent-?`"  # a doc quoting the token, or its id prefix, to explain the rule
)

# The enumerated surfaces. CLOSED: a new consumer-facing file is added here or -82 fails.
_SURFACES: tuple[str, ...] = (
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "NAMING.md",
    "action.yml",
    "install.sh",
    "install.ps1",
    "uninstall.sh",
    "docs/README.md",
    "docs/first-run.md",
    ".github/workflows/audit-ci.yml",
    ".github/workflows/argus-student-audit.yml",
    ".github/workflows/build-binaries.yml",
    ".github/workflows/release.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    # Shipped INSIDE every binary zip by build-binaries.yml's "Assemble the package" step.
    "packaging/QUICKSTART.md",
    "packaging/FEEDBACK.md",
    "packaging/generate_third_party_notices.py",
    # The packaged assistant-skill docs.
    "audit/skill.md",
    "audit/commands.md",
    "audit/principles.md",
    "audit/workflow.md",
    "audit/evidence-model.md",
    "audit/repository-memory.md",
    "audit/precision-validation-protocol.md",
)

# Surfaces that still violate, each with the reason it has not been swept yet -- DEBT,
# recorded rather than hidden. -83 makes the list self-cleaning: fix a file and its
# exemption must be deleted in the same change, or the suite goes red.
#
# It is EMPTY, which is the point of it existing. It held ten entries when this guard was
# written and they were paid off in the same change; the mechanism stays so the next
# unswept surface has somewhere honest to sit instead of being quietly left out.
_NOT_YET_SWEPT: dict[str, str] = {}


def _guarded_text(rel: str) -> str:
    """The part of a surface the rule applies to."""
    text = (_REPO_ROOT / rel).read_text(encoding="utf-8")
    if rel == "CHANGELOG.md":
        head, sep, _ = text.partition("\n## ")
        return head if sep else text
    return text


def _offences(text: str) -> list[str]:
    return [
        line.strip() for line in text.splitlines() if "ArgusAgent" in _FROZEN.sub("", line)
    ]


@pytest.mark.parametrize("rel", _SURFACES)
def test_surface_spells_the_project_name_one_way(rel: str) -> None:
    """TC-ArgusAgent-DOCS-001-81 -- prose on a read-by-strangers surface says Agent-Argus.

    Not a style preference. ``audit-ci.yml``'s display name is the check GitHub shows on
    every commit and pull request, and ``action.yml``'s step names print in the Actions log
    of every repository that consumes the action. Two spellings there teach a reader that
    they are looking at two different things.
    """
    path = _REPO_ROOT / rel
    assert path.is_file(), f"{rel} is registered as a surface but does not exist"
    offences = _offences(_guarded_text(rel))
    assert not offences, (
        f"{rel} spells the project name `ArgusAgent` in prose; NAMING.md says "
        f"`Agent-Argus` there and reserves `ArgusAgent` for identifiers:\n  "
        + "\n  ".join(offences)
    )


def test_the_surface_registry_is_closed() -> None:
    """TC-ArgusAgent-DOCS-001-82 -- a new consumer-facing file must be registered here.

    Same fail-on-unregistered shape Story 8.3 established: a guard that silently ignores a
    file it has never heard of protects the files that existed when it was written, and
    nothing else.
    """
    candidates = {
        p.relative_to(_REPO_ROOT).as_posix()
        for p in [
            *(_REPO_ROOT / ".github" / "workflows").glob("*.yml"),
            *(_REPO_ROOT / "packaging").glob("*"),
            *(_REPO_ROOT / "audit").glob("*.md"),
            *_REPO_ROOT.glob("*.md"),
            *_REPO_ROOT.glob("install*"),
            *_REPO_ROOT.glob("uninstall*"),
        ]
        if p.is_file()
    }
    known = set(_SURFACES) | set(_NOT_YET_SWEPT)
    # LICENSE-style files carry no product prose of their own.
    ignorable = {"LICENSE.md"}
    unregistered = sorted(candidates - known - ignorable)
    assert not unregistered, (
        "consumer-facing files exist that this naming guard has never heard of; add each "
        f"to _SURFACES (or to _NOT_YET_SWEPT with a reason): {unregistered}"
    )


@pytest.mark.parametrize("rel", sorted(_NOT_YET_SWEPT))
def test_the_exemption_list_cleans_itself(rel: str) -> None:
    """TC-ArgusAgent-DOCS-001-83 -- an exemption outlives its violation by zero commits.

    An exemption list that keeps entries for files nobody violates any more is how a guard
    quietly stops guarding. If this fails, the file was fixed: delete its entry and move it
    into ``_SURFACES``.
    """
    path = _REPO_ROOT / rel
    assert path.is_file(), f"{rel} is exempted but does not exist; delete the exemption"
    assert _offences(_guarded_text(rel)), (
        f"{rel} no longer spells the project name `ArgusAgent` in prose. Remove it from "
        "_NOT_YET_SWEPT and add it to _SURFACES."
    )
