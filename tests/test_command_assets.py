"""Story 12.7 / FR35 (second half) — the commands the README promises actually exist.

Verification area **ArgusAgent-ASSETS** (``TC-ArgusAgent-ASSETS-001-01``..``-13``), OPENED by this
story. The decision to open an area rather than extend one is recorded here because **Story 12.5
rejected an invented area** (``PACKAGING-001``) and this must not read as ignoring that ruling.
12.5's objection was specific: the new area *and a new file* were a **second home for a fact that
already had one** — ``test_grammar_runtime_validation.py`` already parsed ``pyproject.toml`` for the
same drift class. Here there is no existing home. No test file in this suite covers *a step that
writes files into a host's configuration directory*, and folding it into ``DOCS-001`` would mix a
filesystem-writing installer into the area bound to published-document honesty. Opening an area is
ordinary here when the subject is new (12.6 opened ``MCP-001`` on the same reasoning); edits to
existing files continue their own indices.

**What is under test, in one sentence:** the distribution ships command assets as data, one
documented step places them, every shipped command resolves through the REAL parser, and the set that
ships equals the set every surface publishes — in both directions.

**AI-E11-1 compliance, per guard.** Each test below states its OBSERVABLE, and the four that carry
the story names its adversarial variant explicitly:

* set equality (``-06``) — shown red by a command published with no shipped asset **and** by a
  shipped asset absent from a published list. Both directions, or it is half a guard;
* invocation resolution (``-02``) — shown red by an asset carrying ``argus --budget 500``, which is
  not a hypothetical: it is the REAL line measured at ``adapters/codex-cli/prompt_adapter.md:3``
  before this story removed that stub tree;
* no transcribed disclosure (``-03``/``-04``) — shown red by pasting the constant's text into a
  committed asset **and** by an installer that writes an asset without it;
* containment (``-05``) — shown red by an asset name that escapes the destination root, and by a
  symlinked configuration directory pointing outside it.

**Every write in this file goes to a ``tmp_path`` through ``--dest``. No test here reads or writes a
real ``$HOME``**, which is what the ``--dest`` seam exists for. No network, no subprocess, no sleep,
no ``.argus/`` write. Every file is opened ``encoding="utf-8"`` explicitly: an inherited host locale
is the defect class that turned a whole CI leg red once already.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

from argus import cli
from argus.assets.commands import ASSET_MARKER, ASSET_SUFFIX, DISCLOSURE_PLACEHOLDER
from argus.commands import hosts as host_registry
from argus.commands.installer import (
    ASSET_PACKAGE,
    CommandAsset,
    CommandInstallError,
    ContainmentError,
    install_commands,
    load_command_assets,
    plan_writes,
    render_asset,
    render_outcome,
)
from argus.verdict.negative_assurance import (
    INSTRUMENT_STATUS,
    render_instrument_disclosure,
)
from tests.test_invocation_contract import parse_failure

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ASSET_DIR = _REPO_ROOT / "argus" / "assets" / "commands"

# ─────────────────────────────────────────────────────────────────────────────
# Derivation — everything below is DERIVED from the tree, never transcribed
# ─────────────────────────────────────────────────────────────────────────────

# A published command token, in every spelling this repository has ever used for one. The leading
# `/` is required and a word character or `/` before it excludes a URL path and a file path, both of
# which are ordinary in these documents (`https://…/audit`, `docs/audit`). The trailing class admits
# the namespaced spellings the hosts actually produce (`/argus-audit-security`) as well as the bare
# legacy one (`/audit`), so a surviving legacy token is RED rather than invisible.
PUBLISHED_COMMAND_RE = re.compile(r"(?<![\w/-])/(?:argus-)?audit[a-z0-9-]*")

# §3.4 supersession: text inside `~~…~~` is a RECORD of what a document used to say, not a claim it
# makes. Multi-line, because every strike in this repository wraps across lines. Replaced by spaces
# of equal length rather than removed, so reported offsets stay true to the file.
_STRUCK_RE = re.compile(r"~~.*?~~", re.S)

# Directories whose markdown is NOT a consumer-facing publication of the command set, each with the
# reason it is excluded. The corpus is EXCLUSION-based on purpose: a new document anywhere else is
# INCLUDED by default, which is the only arrangement under which "a fourth list added later is RED,
# not invisible" is true. Every prefix must exist (asserted by `-11`), so a stale exclusion — the
# quietest way to widen a hole — turns red instead of silently admitting a whole tree.
_NON_PUBLISHING_PREFIXES: dict[str, str] = {
    "_bmad-output/": "planning artifacts and story files — the project's META-DISCUSSION of the "
    "command set, never a command a consumer is told to run. This is `-28`'s own corpus rule: a "
    "guard that fires on the story that specifies the change cries wolf and gets deleted.",
    "_bmad/": "the installed BMAD method module — third-party workflow content, not this "
    "project's publication.",
    ".claude/": "this repository's OWN assistant configuration. It is a consumer of the "
    "convention, not a publisher of Argus's command set.",
    ".github/": "issue/PR templates and workflow documentation — CI plumbing, not a command list.",
    "tests/": "test fixtures and cartridges. A fixture that names a command is an input to a "
    "guard, not a claim to a reader.",
    "argus/assets/commands/": "THE SHIPPED SET ITSELF. Comparing it to itself would be a "
    "tautology; it is the left-hand side of every comparison below.",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tracked_markdown() -> tuple[str, ...]:
    """Every tracked ``*.md`` path, POSIX-style (IMPURE read over ``git ls-files``).

    ``git ls-files`` rather than ``rglob`` deliberately: the question is what this repository
    PUBLISHES, and an untracked scratch file is not published. It also means a new document is in
    the corpus the moment it is staged, which is the property AC4's *"resolved by scan, not
    declared"* asks for.
    """
    done = subprocess.run(
        ["git", "ls-files", "--", "*.md"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, f"`git ls-files -- '*.md'` failed: {done.stderr}"
    return tuple(sorted(line for line in done.stdout.splitlines() if line.strip()))


def publishing_corpus() -> tuple[str, ...]:
    """Tracked markdown that COULD publish a command list (PURE over :func:`tracked_markdown`)."""
    return tuple(
        rel
        for rel in tracked_markdown()
        if not any(rel.startswith(prefix) for prefix in _NON_PUBLISHING_PREFIXES)
    )


def published_commands(text: str) -> frozenset[str]:
    """Every command token *text* AFFIRMATIVELY publishes (PURE).

    Struck spans are removed first: §3.4 requires a superseded list to stay legible, and a guard
    that could not tell a retraction from a claim would make the honest form of a correction
    impossible to write. That is the same device ``-17``'s denial filter uses on over-claims.
    """
    return frozenset(PUBLISHED_COMMAND_RE.findall(_STRUCK_RE.sub(" ", text)))


def publishing_surfaces() -> dict[str, frozenset[str]]:
    """``{path: published command set}`` for every surface that publishes at least one (IMPURE read)."""
    found: dict[str, frozenset[str]] = {}
    for rel in publishing_corpus():
        path = _REPO_ROOT / rel
        if not path.is_file():
            continue
        commands = published_commands(_read(path))
        if commands:
            found[rel] = commands
    return found


def shipped_asset_paths() -> tuple[Path, ...]:
    """The committed command assets, BY GLOB (IMPURE read). Never a hand-list."""
    return tuple(sorted(_ASSET_DIR.glob(f"*{ASSET_SUFFIX}")))


def shipped_command_spellings() -> frozenset[str]:
    """The command set that SHIPS, derived from the asset names x the host registry (IMPURE read).

    DN-4: the documented spelling is the one the user actually gets. It is computed here from the
    two facts that determine it — the shipped asset's own file name and the host's convention — so
    the README states a derivation rather than a hand-typed claim, and the published ``/audit repo``
    *space-separated argument* form (which nothing ever produced) cannot survive by being retyped.
    """
    return frozenset(
        host.command_spelling(path.name[: -len(ASSET_SUFFIX)])
        for host in host_registry.HOST_REGISTRY
        for path in shipped_asset_paths()
    )


def fenced_command_lines(text: str) -> tuple[str, ...]:
    """Every line inside a fenced shell block (PURE).

    Reuses the fence rule rather than restating it: ``executable_line_numbers`` in
    ``tests/test_invocation_contract.py`` is the single definition of "which lines are shell
    source?" in this repository (Story 11.3 / DN-2 made it public for exactly this reason), and
    ``-28`` already applies it to these files. This helper only needs the LINES, for the
    no-extra-authority assertion in ``-02``.
    """
    from tests.test_invocation_contract import executable_line_numbers

    inside = executable_line_numbers(text, ".md")
    lines = text.splitlines()
    return tuple(lines[n - 1].strip() for n in sorted(inside) if lines[n - 1].strip())


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — the assets are PACKAGED, resolvable, and carry no execution authority
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_ASSETS_001_01_the_assets_exist_and_resolve_through_importlib() -> None:
    """TC-ArgusAgent-ASSETS-001-01 — AC1: real packages, resolved as RESOURCES, non-vacuously.

    OBSERVABLE: the number of assets :func:`load_command_assets` resolves through
    ``importlib.resources``, and whether that number equals what is committed on the tree.

    ``importlib.resources`` over ``__file__`` arithmetic is the requirement, not a preference:
    ``Path(__file__).parent / "commands"`` works from a source checkout and fails the moment the
    distribution is zip-imported, relocated or vendored — the same class of *works here, not there*
    defect Story 11.5 measured on the wheel. The ``> 0`` floor is mandatory: every equality below
    would pass over an empty set.
    """
    resolved = load_command_assets()
    assert resolved, (
        "importlib.resources resolved NO command asset from "
        f"{ASSET_PACKAGE!r}. Every assertion in this file is vacuous until that is repaired — the "
        "package may have lost its __init__.py, or the assets may have moved."
    )
    committed = shipped_asset_paths()
    assert committed, f"no committed asset under {_ASSET_DIR.relative_to(_REPO_ROOT).as_posix()}"
    assert {asset.name for asset in resolved} == {path.name for path in committed}, (
        "the assets importlib.resources resolves and the assets committed on the tree disagree: "
        f"resolved={sorted(a.name for a in resolved)} committed={sorted(p.name for p in committed)}"
    )

    # Both directories are REAL packages, which is what makes the resource lookup legal at all.
    for package_dir in (_ASSET_DIR, _ASSET_DIR.parent):
        assert (package_dir / "__init__.py").is_file(), (
            f"{package_dir.relative_to(_REPO_ROOT).as_posix()} has no __init__.py, so it is a bare "
            "directory rather than an importable package and importlib.resources cannot address it"
        )

    # The installer never reaches for the filesystem to find its own data. Asserted with `ast`
    # rather than by substring, because the module DOCUMENTS the banned idiom in order to explain
    # why it is banned — a substring check would forbid writing down the reason.
    import ast

    tree = ast.parse(_read(_REPO_ROOT / "argus" / "commands" / "installer.py"))
    dunder_file = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "__file__"]
    assert not dunder_file, (
        "the installer resolves its assets by __file__ path arithmetic (used at line(s) "
        f"{[n.lineno for n in dunder_file]}), which breaks inside a zip-imported or relocated "
        "distribution (AC1)"
    )


def test_TC_ArgusAgent_ASSETS_001_02_every_shipped_command_resolves_and_grants_nothing_more() -> None:
    """TC-ArgusAgent-ASSETS-001-02 — AC1/AC3/DN-6: data, not authority — asserted, not asserted-about.

    OBSERVABLE: for every executable line in every shipped asset, (a) the REAL
    ``build_parser().parse_args`` verdict on it, and (b) whether it contains an interpolation
    construct.

    ADVERSARIAL VARIANT, generated from the corpus rather than imagined: ``argus --budget 500``, the
    line ``adapters/codex-cli/prompt_adapter.md:3`` actually published before this story removed
    that tree. The real parser rejects it — the ``audit`` sub-command is missing — which is the same
    defect class Story 10.3 corrected in the README, surviving in a file no guard was looking at.
    """
    assets = load_command_assets()
    checked = 0
    for asset in assets:
        for line in fenced_command_lines(asset.text):
            checked += 1
            assert line.split(" ", 1)[0] == "argus", (
                f"{asset.name}: executable line {line!r} is not an `argus …` invocation. A command "
                "asset instructs a host to run THIS tool and nothing else; it introduces no "
                "execution path of its own (architecture §A constraint 2.3)."
            )
            failure = parse_failure(line)
            assert failure is None, (
                f"{asset.name}: the shipped invocation {line!r} is REJECTED by the real parser "
                f"({failure}). A consumer's assistant would run it and get a usage error."
            )
            assert "--deep-audit" not in line, (
                f"{asset.name}: a shipped asset enables the deep pass. `--deep-audit` is THE ONLY "
                "OPT-IN TO EGRESS (Story 12.2), and a file placed in a user's configuration "
                "directory can never constitute that operator act."
            )
    assert checked, (
        "NO executable line was extracted from any shipped asset — either the assets stopped "
        "carrying their invocation or the fence rule stopped matching. This guard is vacuous."
    )

    # No interpolation construct anywhere in an asset. Story 11.3 shipped a whole story about this
    # class on `action.yml`; here it is a gate rather than a review note.
    for asset in assets:
        for construct in ("${", "$(", "`$", "%(", "{{"):
            assert construct not in asset.text, (
                f"{asset.name} contains the interpolation construct {construct!r}. A command asset "
                "is inert data: a construct that can splice consumer-controlled text onto a "
                "command line is the DF-9-2-D injection class at a new seam."
            )

    # POSITIVE CONTROL — the real invalid line, proving the parser check bites.
    assert parse_failure("argus --budget 500") is not None, (
        "the parser ACCEPTED `argus --budget 500`, the exact line adapters/codex-cli published. "
        "This check cannot detect the defect it was written for."
    )


def test_TC_ArgusAgent_ASSETS_001_03_no_committed_asset_transcribes_the_disclosure() -> None:
    """TC-ArgusAgent-ASSETS-001-03 — AC6.1 / AI-E9-7: the constant is never committed here.

    OBSERVABLE: whether the disclosure text appears in any committed file under ``argus/assets/**``.

    A committed transcription of a pinned constant is the drift class ``-49`` was CORRECTED to
    forbid one story ago — that guard used to demand the opposite, and satisfying it would have
    required pasting the constant into ``argus/mcp/**``. It goes stale the day Story 13.3 flips the
    status, and a stale disclosure on a surface an agent reads before it acts is worse than none.
    The placeholder is asserted PRESENT in the same breath, so this cannot be satisfied by deleting
    the mechanism.

    ADVERSARIAL VARIANT: the constant's text pasted into an asset body — checked directly against
    the detector below, since a committed test may never rewrite the source tree to prove a point.
    """
    for form in (False, True):
        text = render_instrument_disclosure(INSTRUMENT_STATUS, short=form)
        for path in sorted((_REPO_ROOT / "argus" / "assets").rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            body = _read(path)
            assert " ".join(text.split()) not in " ".join(body.split()), (
                f"{path.relative_to(_REPO_ROOT).as_posix()} carries a TRANSCRIBED copy of the FR34 "
                "instrument-status disclosure. It must be RENDERED at install time from the one "
                "constant in argus/verdict/negative_assurance.py (AI-E9-7 / DN-7)."
            )

    for asset in load_command_assets():
        assert DISCLOSURE_PLACEHOLDER in asset.text, (
            f"{asset.name} has no {DISCLOSURE_PLACEHOLDER!r} placeholder, so the installer has "
            "nowhere to render the disclosure — and this guard would be satisfied by an asset that "
            "simply has no disclosure mechanism at all."
        )
        assert ASSET_MARKER in asset.text, f"{asset.name} carries no {ASSET_MARKER!r} marker"

    # ADVERSARIAL VARIANT — a transcribed asset is refused by the same predicate, in memory.
    poisoned = render_instrument_disclosure(INSTRUMENT_STATUS, short=True)
    assert poisoned in f"prefix {poisoned} suffix", (
        "the substring detector this guard relies on does not detect the constant it looks for"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC2 / AC6 / AC8 — the install step, driven for real against a tmp_path
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_ASSETS_001_04_the_installer_writes_the_disclosure_into_every_asset(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-ASSETS-001-04 — AC6.2: the OTHER direction, proven on written bytes.

    OBSERVABLE: the bytes of every file the REAL installer writes into a fixture destination.

    ``-03`` proves no committed asset carries the text. On its own that is satisfied by an installer
    that never renders it — half a guard. This drives the real step into a ``tmp_path`` and reads
    what landed on disk, so the two directions together are the whole claim: never committed, always
    written.

    ADVERSARIAL VARIANT: :func:`render_asset` over an asset with no placeholder must REFUSE rather
    than write a disclosure-free file, which is the only way the "always written" half can be
    defeated without touching this test.
    """
    (tmp_path / ".claude").mkdir()
    outcome = install_commands(dest=str(tmp_path))
    assert outcome.written, "the installer reported writing nothing into a detected host"

    expected = render_instrument_disclosure(INSTRUMENT_STATUS, short=True)
    for relative in outcome.written:
        body = _read(tmp_path / relative)
        assert expected in body, (
            f"{relative} was written WITHOUT the FR34 instrument-status disclosure. A command asset "
            "is what an agent reads before it decides to run the tool — 12.6 put the same "
            "disclosure in the tools/list description for exactly that reason."
        )
        assert DISCLOSURE_PLACEHOLDER not in body, (
            f"{relative} still carries the unrendered placeholder"
        )
        assert ASSET_MARKER in body, f"{relative} lost the marker that makes --remove possible"

    # ADVERSARIAL VARIANT — an asset with no placeholder is REFUSED, not silently written bare.
    with pytest.raises(CommandInstallError):
        render_asset(CommandAsset(name="x.md", text=f"{ASSET_MARKER}\nno placeholder"), expected)


def test_TC_ArgusAgent_ASSETS_001_05_a_write_can_never_escape_the_destination_root(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-ASSETS-001-05 — AC8: containment, in both halves, each shown red.

    OBSERVABLE: whether a planned write whose name or whose directory escapes the destination root
    is REFUSED with a typed error.

    This is the only place Argus writes outside the audited repository at all, so NFR-S4/NFR-S5
    containment discipline applies to it directly. Two halves, because one cannot cover the other:
    a pure check catches ``..`` and an absolute name; only a real-path check catches a symlink.

    ADVERSARIAL VARIANTS, generated from the shape of the join rather than imagined: an asset named
    ``../escape.md``, one named with an absolute path, and a ``commands/`` directory that is a
    symlink pointing outside the root.
    """
    host = host_registry.HOST_REGISTRY[0]
    disclosure = render_instrument_disclosure(INSTRUMENT_STATUS, short=True)
    body = f"{ASSET_MARKER}\n{DISCLOSURE_PLACEHOLDER}\n"

    for evil in ("../escape.md", "sub/escape.md", os.path.abspath("/escape.md")):
        with pytest.raises(ContainmentError):
            plan_writes((CommandAsset(name=evil, text=body),), (host,), disclosure)

    # The honest name is accepted by the same call, so the refusal is not a blanket one.
    assert plan_writes((CommandAsset(name="ok.md", text=body),), (host,), disclosure)

    # Half two — a symlinked configuration directory. Skipped, with a NAMED reason, where the host
    # forbids symlink creation (unprivileged Windows), never passed silently.
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "root"
    root.joinpath(*host.config_root_parts).mkdir(parents=True)
    link = root.joinpath(*host.config_root_parts, *host.commands_parts)
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:  # pragma: no cover - host without symlink rights
        pytest.skip(f"E2: this host cannot create a directory symlink, so the symlink-escape half "
                    f"of containment was NOT checked here: {exc}")
    with pytest.raises(ContainmentError):
        install_commands(dest=str(root))
    assert not list(outside.iterdir()), (
        "the installer wrote THROUGH a symlinked configuration directory and its files landed "
        "outside the destination root entirely"
    )


def test_TC_ArgusAgent_ASSETS_001_08_the_step_is_deterministic_dry_run_writes_nothing_and_remove_is_exact(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-ASSETS-001-08 — AC2/AC8: NFR-P1, and ``--remove`` removes exactly its own.

    OBSERVABLE: the bytes written by two independent runs; the file count after ``--dry-run``; and
    which files survive ``--remove``.

    ``--remove`` closes the measured asymmetry: ``uninstall.sh`` ran ``pip uninstall`` only, so every
    file the two installers copied stayed in the user's home directory forever. "Exactly its own" is
    the load-bearing half — a removal keyed on the file NAME would delete a user's own command of
    the same name, so it is keyed on the marker each written asset carries.
    """
    first, second = tmp_path / "a", tmp_path / "b"
    for root in (first, second):
        (root / ".claude").mkdir(parents=True)

    dry = install_commands(dest=str(first), dry_run=True)
    assert dry.written, "--dry-run reported no plan at all"
    assert not list((first / ".claude").rglob("*.md")), (
        "--dry-run WROTE files. It resolves and containment-checks the whole plan and writes "
        "nothing; a dry run that writes is not a dry run."
    )
    assert render_outcome(dry)[0].startswith("argus: install-commands dry-run")

    one = install_commands(dest=str(first))
    two = install_commands(dest=str(second))
    assert one.written == two.written == dry.written, (
        "the planned set, the dry-run set and the written set disagree across two identical runs"
    )
    for relative in one.written:
        assert (first / relative).read_bytes() == (second / relative).read_bytes(), (
            f"{relative} differs between two runs with identical inputs (NFR-P1)"
        )

    # A user's own file under one of our names survives --remove, and is not overwritten either.
    theirs = first / one.written[0]
    theirs.write_text("my own command, no marker\n", encoding="utf-8")
    again = install_commands(dest=str(first))
    assert one.written[0] in again.unchanged and one.written[0] not in again.written
    assert _read(theirs) == "my own command, no marker\n", "the step overwrote a file it did not write"

    removed = install_commands(dest=str(first), remove=True)
    assert set(removed.removed) == set(one.written) - {one.written[0]}, (
        f"--remove removed {sorted(removed.removed)}; it must remove exactly the files this step "
        "wrote and leave a same-named file the user wrote alone"
    )
    assert theirs.is_file(), "--remove deleted a file this step never wrote"
    assert render_outcome(removed)[0].startswith("argus: install-commands remove")


def test_TC_ArgusAgent_ASSETS_001_09_the_host_registry_is_closed_verified_and_message_safe(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-ASSETS-001-09 — AC2/DN-2: an entry exists only if it was VERIFIED.

    OBSERVABLE: every registry entry's recorded verification, the refusal on an unregistered
    ``--host``, and whether any rendered message carries an absolute host path.

    DN-2 refused to hand this story a host list to trust, and the measurement is why: ``README.md``
    named seven hosts, ``adapters/`` held six stub directories, and one of the seven had no
    directory at all. The structural rule is enforced here — an entry with no recorded convention
    fails, so a host cannot be added on a guess.
    """
    assert host_registry.HOST_REGISTRY, "the host registry is empty — every plan would be vacuous"
    for host in host_registry.HOST_REGISTRY:
        assert host.convention and len(host.convention) > 60, (
            f"{host.host_id} carries no recorded verification of its configuration convention. "
            "DN-2: an unverified host does not ship."
        )
        assert host.config_root_parts and host.commands_parts, (
            f"{host.host_id} names no configuration/commands path"
        )
        for part in (*host.config_root_parts, *host.commands_parts):
            assert part not in ("", ".", "..") and "/" not in part and "\\" not in part, (
                f"{host.host_id} stores a JOINED or escaping path segment {part!r}; the registry "
                "holds segments precisely so a `..` cannot be smuggled in as data"
            )

    with pytest.raises(host_registry.UnknownHostError):
        host_registry.resolve_hosts(("no-such-host",))
    assert host_registry.resolve_hosts(None) == host_registry.HOST_REGISTRY

    # NFR-S1 — no absolute host path in anything a user is shown.
    (tmp_path / ".claude").mkdir()
    outcome = install_commands(dest=str(tmp_path))
    for line in render_outcome(outcome):
        assert str(tmp_path) not in line, (
            f"a rendered message carries the absolute destination path: {line!r}"
        )
        assert not os.path.isabs(line.split(": ")[-1].strip()), (
            f"a rendered message ends in an absolute path: {line!r}"
        )


def test_TC_ArgusAgent_ASSETS_001_10_every_failure_is_a_named_typed_outcome_never_a_crash(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-ASSETS-001-10 — AC8 / NFR-R1: no crash, and the exit code is the CLI's.

    OBSERVABLE: the process exit code and the stream a failure lands on, for each named failure.

    Driven through ``cli.main`` rather than the installer, because the claim is about the WIRE
    CONTRACT: a typed failure is one secret-safe stderr line and exit ``1``, never a traceback
    (AR3/AR10). Reuses today's message wording — authoring new diagnosis prose is fenced to a later
    story.
    """
    # An undetected host: nothing is placed, and that is a failure rather than a silent success.
    empty = tmp_path / "empty"
    empty.mkdir()
    assert cli.main(["install-commands", "--dest", str(empty)]) == 1

    # An unregistered --host name.
    assert cli.main(["install-commands", "--dest", str(empty), "--host", "no-such-host"]) == 1

    # The happy path returns 0 and is not confused with either of the above.
    (tmp_path / ".claude").mkdir()
    assert cli.main(["install-commands", "--dest", str(tmp_path)]) == 0
    assert cli.main(["install-commands", "--dest", str(tmp_path), "--remove"]) == 0


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — the documented set EQUALS the shipped set, on every surface, both ways
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_ASSETS_001_06_every_published_command_list_equals_the_shipped_set() -> None:
    """TC-ArgusAgent-ASSETS-001-06 — AC4: set equality, both directions, over a SCANNED population.

    OBSERVABLE: the symmetric difference between the derived shipped set and each surface's
    published set.

    Measured before this story: THREE surfaces published a command list and all three disagreed —
    ``README.md`` seven, ``audit/commands.md`` ten, ``audit/skill.md`` six — and not one of the sets
    was delivered by anything. "One fact, one place" is the remedy this repository has now applied
    three times. The surface population is resolved by SCANNING tracked markdown rather than
    declared, so a fourth list added later is red rather than invisible.

    ADVERSARIAL VARIANTS, both directions, exercised against the pure comparator so the real tree is
    never mutated: a document publishing a command with no shipped asset, and a shipped asset absent
    from a document.
    """
    shipped = shipped_command_spellings()
    assert shipped, "the shipped command set derived to nothing — every comparison below is vacuous"

    surfaces = publishing_surfaces()
    assert len(surfaces) >= 2, (
        f"only {sorted(surfaces)} publish a command list. Before this story there were three; if a "
        "surface was deliberately retired, say so — a shrinking population is how this guard stops "
        "guarding without anybody noticing."
    )
    for rel, published in sorted(surfaces.items()):
        assert published == shipped, (
            f"{rel} and the shipped asset tree disagree.\n"
            f"  published but NOT shipped: {sorted(published - shipped)}\n"
            f"  shipped but NOT published: {sorted(shipped - published)}\n"
            "A documented command that is not delivered is removed in the same change, and a "
            "shipped command that nobody documents is one a reader can never find."
        )

    # ADVERSARIAL VARIANT, direction one — a phantom command in a document.
    assert published_commands("Run `/audit resume` to continue.") - shipped, (
        "the comparator did not flag a published command with no shipped asset"
    )
    # ADVERSARIAL VARIANT, direction two — a document missing a shipped command.
    assert shipped - published_commands("Only `/argus-audit` is documented here."), (
        "the comparator did not flag a shipped command missing from a document"
    )
    # And it does NOT fire on a §3.4 strike, which is what makes an honest retraction writable.
    assert published_commands("~~`/audit resume`~~ was removed.") == frozenset()


def test_TC_ArgusAgent_ASSETS_001_07_exactly_one_command_asset_tree_exists() -> None:
    """TC-ArgusAgent-ASSETS-001-07 — AC4/DN-5: one source of truth, asserted over the whole tree.

    OBSERVABLE: the set of directories in the repository containing marker-bearing files.

    This is what forced ``adapters/**`` to be RESOLVED rather than left as a second, drifting copy
    of the command set. It closes over ``git ls-files``, so a second tree added anywhere — under a
    new top-level directory, inside ``argus/``, beside the first — is red on the commit that adds
    it, not on the day somebody remembers this file.
    """
    done = subprocess.run(
        ["git", "ls-files"], cwd=str(_REPO_ROOT), capture_output=True, text=True
    )
    assert done.returncode == 0, f"`git ls-files` failed: {done.stderr}"
    tracked = [line for line in done.stdout.splitlines() if line.strip()]
    assert tracked, "git ls-files returned nothing — this guard would pass over an empty tree"

    trees: dict[str, list[str]] = {}
    for rel in tracked:
        path = _REPO_ROOT / rel
        if not path.is_file() or path.suffix.lower() not in (".md", ".mdc", ".json", ".txt"):
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):  # pragma: no cover - binary or unreadable
            continue
        if ASSET_MARKER in body:
            trees.setdefault(str(Path(rel).parent).replace("\\", "/"), []).append(rel)

    assert set(trees) == {"argus/assets/commands"}, (
        f"marker-bearing command definitions exist in {sorted(trees)}. EXACTLY ONE command-asset "
        "tree may exist (AC4/DN-5): a second one is a second source of truth about what ships, "
        "which is precisely what the six `adapters/**` stubs were."
    )
    assert len(trees["argus/assets/commands"]) == len(shipped_asset_paths())


def test_TC_ArgusAgent_ASSETS_001_13_exactly_one_placement_mechanism_exists(tmp_path: Path) -> None:
    """TC-ArgusAgent-ASSETS-001-13 — AC2/AR7: one mechanism, and it stays inside its fence.

    OBSERVABLE: every committed file outside ``argus/commands/**`` that copies something into an
    assistant configuration directory; and what a real run leaves on disk beyond the placed files.

    ``-07`` closes the DATA side (one asset tree). This closes the MECHANISM side, which is the
    half that was actually broken: ``install.sh`` and ``install.ps1`` each carried their OWN copy
    rule, both got it wrong in the identical way — creating ``commands/`` and then copying the files
    beside it — and ``uninstall.sh`` had no removal rule at all. That is AR7 / architecture §3.3
    exactly: a rule implemented twice drifts in one of the two, except here it drifted in both. The
    three scripts must DELEGATE, so this asserts each one invokes ``install-commands`` and none of
    them copies anything.

    The second half is the containment-of-scope claim AC2 makes alongside it: the step performs no
    ``.argus/`` write, opens no socket and reaches no network. Asserted structurally over the module
    sources AND behaviourally over what a real run leaves behind, because a source scan alone would
    miss a transitive one and a behavioural check alone would miss an unexercised branch.
    """
    scripts = {
        rel: _read(_REPO_ROOT / rel)
        for rel in ("install.sh", "install.ps1", "uninstall.sh")
        if (_REPO_ROOT / rel).is_file()
    }
    assert len(scripts) == 3, f"an installer script disappeared: {sorted(scripts)}"
    for rel, body in scripts.items():
        assert "install-commands" in body, (
            f"{rel} does not delegate to `argus install-commands`. It is the ONE placement "
            "mechanism; a script that places files itself is the second mechanism AR7 forbids."
        )
        # A copy rule is a placement rule. `~~struck~~` prose describing the OLD behaviour is fine;
        # a live command is not, so the check is on non-comment lines only.
        live = [
            line
            for line in body.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        for banned in ("cp -r", "cp ", "Copy-Item", "xcopy", "robocopy"):
            offenders = [line for line in live if banned in line]
            assert not offenders, (
                f"{rel} still copies files itself ({banned!r}): {offenders}. Delegate to "
                "`argus install-commands`; two placement mechanisms is how both of these came to "
                "create a `commands/` directory and then copy beside it."
            )

    # No egress, no `.argus/` write — structurally, over the mechanism's own modules.
    for module in sorted((_REPO_ROOT / "argus" / "commands").glob("*.py")):
        source = _read(module)
        for banned in ("httpx", "requests", "urllib", "socket", "http.client", ".argus"):
            assert banned not in source, (
                f"{module.name} mentions {banned!r}. The install step performs no network call and "
                "no `.argus/` write; it is the one path that writes outside the audited repository "
                "and its scope is the destination root and nothing else."
            )

    # …and behaviourally: a real run leaves the placed files and NOTHING else.
    (tmp_path / ".claude").mkdir()
    outcome = install_commands(dest=str(tmp_path))
    written = {(tmp_path / rel).resolve() for rel in outcome.written}
    stray = sorted(
        p.relative_to(tmp_path).as_posix()
        for p in tmp_path.rglob("*")
        if p.is_file() and p.resolve() not in written
    )
    assert not stray, f"the step wrote files it did not report: {stray}"
    assert not (tmp_path / ".argus").exists(), "the install step created a `.argus/` store"


def test_TC_ArgusAgent_ASSETS_001_11_the_scan_population_is_honest_and_non_vacuous() -> None:
    """TC-ArgusAgent-ASSETS-001-11 — AC4/E.3: the corpus really is a corpus, and every hole is named.

    OBSERVABLE: the size of the scanned corpus, and whether each declared exclusion still resolves.

    ``-06`` passes by finding nothing if the scan silently stops reaching documents. A stale
    exclusion is the quietest way for that to happen — a prefix that no longer exists still
    suppresses nothing visible, but it makes the exclusion registry read as reviewed when it is not.
    Both are asserted here, and the README/CHANGELOG membership is asserted by name because those
    are the two surfaces the whole story is about.
    """
    corpus = publishing_corpus()
    assert len(corpus) >= 5, f"the markdown scan reached only {list(corpus)}"
    assert "README.md" in corpus and "CHANGELOG.md" in corpus, (
        f"the consumer-facing surfaces fell out of the scanned corpus: {list(corpus)}"
    )
    for prefix, reason in _NON_PUBLISHING_PREFIXES.items():
        assert reason, f"exclusion {prefix!r} carries no reason"
        assert (_REPO_ROOT / prefix.rstrip("/")).exists(), (
            f"the exclusion {prefix!r} names a path that no longer exists. Remove it deliberately: "
            "a stale exclusion makes this registry look reviewed when it is not."
        )
    assert any(rel.startswith("audit/") for rel in corpus), (
        "the RAM-framework command lists are no longer in the scanned corpus"
    )


def test_TC_ArgusAgent_ASSETS_001_12_the_assets_ship_in_both_the_wheel_and_the_sdist() -> None:
    """TC-ArgusAgent-ASSETS-001-12 — AC1: packaged as DATA, in BOTH artifacts.

    OBSERVABLE: the asset entries present in a freshly built wheel and sdist.

    Both, because the two are built from different populations and the asymmetry is silent:
    ``flit_core`` walks the whole ``argus/`` directory for the WHEEL (so a ``.md`` ships with no
    ``pyproject.toml`` change at all), while the SDIST is built from VCS-tracked files — so an asset
    that was never ``git add``-ed reaches one and not the other, and a consumer installing from the
    sdist gets a distribution whose installer has nothing to place. Reuses the built-distribution
    fixture rather than building a second time (AR7).
    """
    from tests.test_built_distribution import _distribution

    dist = _distribution()
    names = {path.name for path in shipped_asset_paths()}
    assert names, "no asset on the tree — this guard has nothing to look for"

    wheel = {
        e
        for e in dist.wheel_entries
        if e.startswith("argus/assets/commands/") and e.endswith(ASSET_SUFFIX)
    }
    assert {Path(e).name for e in wheel} == names, (
        f"the WHEEL does not carry the shipped asset set: {sorted(wheel)} vs {sorted(names)}. Do "
        "not 'fix' this with a build-backend change — flit ships every file under argus/."
    )
    sdist = {
        m
        for m in dist.sdist_members
        if "/argus/assets/commands/" in m.replace("\\", "/") and m.endswith(ASSET_SUFFIX)
    }
    assert {Path(m).name for m in sdist} == names, (
        f"the SDIST does not carry the shipped asset set: {sorted(sdist)} vs {sorted(names)}. The "
        "sdist is built from VCS-TRACKED files, so an asset that was never `git add`-ed ships in "
        "the wheel and not here — a silent asymmetry, which is why both are asserted."
    )
    assert dist.data_assets, (
        "BuiltDistribution.data_assets is empty. That property is the closure "
        "TC-ArgusAgent-DOCS-001-56 keys its delivered branch on."
    )
