"""IMPURE tree-sitter Python AST / code-graph index (Decision B substrate).

Drivers: ArgusAgent-FR-7 (Python AST grounding — structural code-graph substrate;
deep grounding of audited claims is Epic 6, this story builds the index it folds
over), AR1 (the sanctioned ``tree-sitter`` + ``tree-sitter-python`` 0.25 toolchain;
the resolved grammar version is RECORDED here for the Epic-5 / AR5 determinism
cache key — this story only records it, the cache key is Epic 5), AR8 (impure
shell — the parser runs here; the index DATA models are frozen pure contracts),
AR10 (a file tree-sitter cannot parse is captured as a per-file DEGRADED outcome
``parse_failed=true`` + a reason token — the run continues, NEVER an uncaught
crash, NEVER a fabricated successful parse, NEVER a bare ``except: pass``),
AR11 (entries / definitions / edges are SORTED, never arrival order),
ArgusAgent-NFR-P2 (stack-agnostic by construction — non-Python / unparseable files
route to the ``claim_emitted`` proxy via the ``ast_eligible`` seam; the language
conditional lives ONLY in this ``index`` layer, NOT in ``ledger``/``verdict``).

Why tree-sitter, not embeddings (Decision B / cross-cutting #1)
---------------------------------------------------------------
ArgusAgent does STRUCTURAL search — it grounds a deep claim against the real AST, not a
fuzzy vector match. The 0.25-era API loads the grammar via the per-language
package: ``Language(tree_sitter_python.language())`` → ``Parser`` (distinct from
the older ``Language.build_library(...)`` pattern).

The AST-eligibility seam (NFR-P2 — the keystone of this story)
--------------------------------------------------------------
Deep AST analysis is Python-only in V1. Every index entry carries an
``ast_eligible: bool`` flag — ``True`` only for a Python file that parsed cleanly.
A non-Python file, or a Python file the parser could not parse, is
``ast_eligible=False``: the downstream depth audit knows it can only ground a
``claim_emitted`` proxy there. Python is implementation #1 of the seam; V2
multi-language is purely additive. The language conditional is confined to this
module — ``ledger/coverage_ledger.py`` / ``ledger/recording.py`` are NOT given a
language field beyond the ``ast_span`` Story 1.2 already reserves.

Index granularity (locked V1 decision)
--------------------------------------
Per Python file the index extracts:
- DEFINITIONS — every ``function_definition`` / ``class_definition`` with its
  name, kind, and 1-based inclusive line span (``Definition.ast_span`` renders a
  ``Locator.ast_span``-compatible token, e.g. ``"function:foo@4-5"``).
- A CALL/REFERENCE EDGE SET — the called-name of every ``call`` node (the
  ``identifier`` or trailing ``attribute`` name), enough for the Story 1.5
  vacuous-path reachability check and the Epic-6 orphan/dead-code detector. This
  is the structural substrate ONLY — NOT a full call-graph resolver (that is
  Epic-6 depth); name binding / scope resolution is deliberately not done here.

The absolute repo root is held only transiently by the impure builder; index
entries carry repo-root-relative POSIX paths only (NFR-S1 — no absolute host
path persisted).
"""

from __future__ import annotations

import importlib.metadata
from pathlib import Path
from typing import NamedTuple

from pydantic import BaseModel, ConfigDict, Field

# The per-grammar provenance SHAPE is defined by the pure cache-key contract that consumes it
# (``argus/cache/key.py``), and imported here rather than redeclared. One definition, imported
# everywhere, is the same rule ``argus/shared/source_languages.py`` exists to enforce: this project
# has already paid once for the same mapping living in four places. The dependency direction is
# impure-shell → pure-contract, which is the sanctioned one (AR8); ``cache/key.py`` imports nothing
# from ``index/`` and stays free of I/O and ``importlib.metadata``.
from argus.cache.key import GrammarProvenance

# The reason-token vocabulary is a PURE contract, defined once and imported by both the
# producer (here) and the consumer (``argus/reports/generator.py``). Story 10.4 / DN-3: the
# alternative — the report importing this impure module for a constant, or each side doing
# its own ``startswith`` on the token — is how ``grammar_entrypoint_missing_go`` becomes
# either silence or ``pip install tree-sitter-entrypoint_missing_go``.
from argus.shared.grammar_status import GrammarFailure, reason_token_for
from argus.shared.source_languages import LANGUAGE_BY_SUFFIX, PYTHON_SUFFIXES

__all__ = [
    "Definition",
    "CodeEdge",
    "AstIndexEntry",
    "AstIndex",
    "GrammarProvenance",
    "build_ast_index",
]

# Imported, not redeclared — this map and intake's enumerable set MUST agree, and
# they previously did not (see argus.shared.source_languages for what that cost).
_LANGUAGE_BY_SUFFIX: dict[str, str] = LANGUAGE_BY_SUFFIX

_PYTHON_SUFFIXES: tuple[str, ...] = tuple(sorted(PYTHON_SUFFIXES))

# tree-sitter node types we treat as definitions across languages.
_DEF_KIND_BY_NODE: dict[str, str] = {
    "function_definition": "function",
    "function_declaration": "function",
    "fn_item": "function",
    "method_definition": "function",
    "method_declaration": "function",
    "class_definition": "class",
    "class_declaration": "class",
    "struct_item": "class",
    "type_declaration": "class",
}

_CALL_NODE_TYPES: frozenset[str] = frozenset(
    {"call", "call_expression", "function_call_expression", "method_invocation"}
)

# The tree-sitter entry point every grammar package is ASSUMED to export.
_DEFAULT_ENTRY_POINT = "language"

# Per-language entry-point overrides (Story 10.2 / AC3.1). DATA, not a chain of ``if``s: adding a
# language stays a one-line edit in one place, the ``source_languages.py`` precedent.
#
# Two of the ten grammar packages do not export a bare ``language()``, because they ship several
# dialects from one package:
#
#   tree_sitter_typescript 0.23.2 → language_typescript, language_tsx
#   tree_sitter_php        0.24.1 → language_php, language_php_only
#
# ``getattr(mod, "language", None)`` therefore returned ``None`` for both. Nothing raised — the code
# fell straight through to the ``parser is None`` branch — so TypeScript and PHP were reported
# ``ast_eligible=False`` with ``grammar_missing_<lang>``, a token that tells an operator to install a
# package they already have. Measured 2026-08-10: eligible 8 / 10 with both grammars installed and
# both declared in the ``[languages]`` extra.
_ENTRY_POINT_BY_LANGUAGE: dict[str, str] = {
    "typescript": "language_typescript",
    "php": "language_php",
}

# SUFFIX-level overrides, for the case one grammar package ships several dialects and the dialect is
# a property of the suffix rather than of the language token. ``.ts`` and ``.tsx`` are both
# ``typescript`` in ``LANGUAGE_BY_SUFFIX``, but JSX syntax is a hard parse error under the plain
# TypeScript grammar, so a ``.tsx`` file routed to ``language_typescript()`` would degrade to
# ``syntax_error`` — eligible-looking language support that silently grades every React component
# shallow. Resolution is therefore keyed by (language, entry point), not by language alone.
_ENTRY_POINT_BY_SUFFIX: dict[str, str] = {
    ".tsx": "language_tsx",
}


class Definition(BaseModel):
    """A function/class definition with its 1-based inclusive line span (frozen).

    ``ast_span`` renders a stable token droppable into ``Locator.ast_span`` (the
    Story 1.2 reservation) so a downstream finding can cite an AST span, not just
    a line range. Construction-pure; line numbers are ``int`` (no float, AR4).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Definition name (function/class identifier).")
    kind: str = Field(..., description="'function' | 'class'.")
    start_line: int = Field(..., ge=1, description="1-based inclusive start line.")
    end_line: int = Field(..., ge=1, description="1-based inclusive end line (>= start_line).")

    @property
    def ast_span(self) -> str:
        """A ``Locator.ast_span``-compatible token: ``<kind>:<name>@<start>-<end>``."""
        return f"{self.kind}:{self.name}@{self.start_line}-{self.end_line}"


class CodeEdge(BaseModel):
    """A call/reference edge: a callee name referenced at a 1-based line (frozen).

    The structural substrate for the Story 1.5 vacuous-path reachability check
    and the Epic-6 orphan/dead-code detector — NOT a resolved call graph (no name
    binding / scope resolution in V1).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    callee: str = Field(..., description="Referenced callee name (identifier or trailing attribute).")
    line: int = Field(..., ge=1, description="1-based line of the call/reference site.")


class AstIndexEntry(BaseModel):
    """Per-file AST-index entry (frozen pure contract).

    The ``ast_eligible`` flag is the stack-agnostic ``claim → validated?`` seam
    (NFR-P2): ``True`` for any cleanly-parsed source file (Python or multi-language).
    A non-supported or unparseable file is ``ast_eligible=False`` (routed to the ``claim_emitted``
    proxy) and, when a parse failed, ``parse_failed=True`` + a
    ``parse_failure_reason`` token (the degraded DATA a Story 1.5 / 2.6 finding
    later folds — AR10).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Repo-root-relative POSIX path (NFR-S1; never absolute).")
    ast_eligible: bool = Field(
        ..., description="Deep-AST eligible (clean-parsed source). False routes to claim_emitted proxy (NFR-P2)."
    )
    parse_failed: bool = Field(
        default=False, description="A source file the parser could not parse cleanly (AR10 degraded)."
    )
    parse_failure_reason: str | None = Field(
        default=None, description="Reason token for a degraded parse ('non_source' | 'syntax_error' | ...)."
    )
    definitions: tuple[Definition, ...] = Field(
        default=(), description="Sorted function/class definitions (AR11)."
    )
    edges: tuple[CodeEdge, ...] = Field(
        default=(), description="Sorted call/reference edge set (AR11)."
    )


class AstIndex(BaseModel):
    """The whole-repo AST index (frozen pure contract).

    Records **per-grammar provenance** in ``grammar_versions`` — for each language whose grammar
    actually parsed a file in THIS build, that grammar package's own resolved version — so Epic 5 /
    AR5 can fold a faithful fingerprint into the determinism cache key. ``partition_id`` is
    ``"root"`` in V1 (partitioning is Story 2.4). Entries are SORTED by ``file_path`` (AR11).

    ``grammar_version`` (singular) is RETAINED under the additive-only schema-evolution policy (PRD
    §"Migration guide", story 10.2 DN-5) and is what it has always actually been: the resolved
    ``tree-sitter-python`` package version. It was never the index's provenance, and reading it as
    though it were is what left the R3 cache key blind to nine of ten grammars (DF-AUD-APAA-D).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default="2", description="AstIndex schema version (additive-only).")
    partition_id: str = Field(default="root", description="Audit-partition id ('root' in V1).")
    grammar_version: str = Field(
        ...,
        description=(
            "Resolved tree-sitter-python package version ONLY — not the index's provenance. "
            "Retained for compatibility (additive-only); see grammar_versions for provenance."
        ),
    )
    grammar_versions: tuple[GrammarProvenance, ...] = Field(
        default=(),
        description=(
            "Per-grammar provenance: the resolved package version of every grammar that actually "
            "parsed a file in this build, SORTED by language (AR11). A grammar installed on the "
            "host but not used by this audit is absent — the key is a function of the audit, not "
            "of the host (Epic-5/AR5 cache-key input)."
        ),
    )
    entries: tuple[AstIndexEntry, ...] = Field(
        ..., description="Sorted per-file index entries (AR11)."
    )


def _grammar_version() -> str:
    """Resolved ``tree-sitter-python`` package version (AR1 / Epic-5 cache key).

    Recorded, not interpreted, here. Falls back to ``"unknown"`` if metadata is
    unavailable (degraded but honest, AR10) — never raises out of the builder.
    """
    return _package_version("python")


def _package_version(lang: str) -> str:
    """Resolved ``tree-sitter-<lang>`` package version, or ``"unknown"`` (AR10, never raises).

    The IMPURE probe. It lives here, in the impure shell, and the resolved strings are PASSED IN to
    the pure ``cache/key.py`` — reading package metadata inside that module would breach its stated
    AR8 purity contract.
    """
    try:
        return importlib.metadata.version(f"tree-sitter-{lang}")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _is_python(rel_path: str) -> bool:
    return Path(rel_path).suffix in _PYTHON_SUFFIXES


def _detect_language(rel_path: str) -> str | None:
    return _LANGUAGE_BY_SUFFIX.get(Path(rel_path).suffix.lower())


def _node_name(node: object) -> str | None:
    name_node = node.child_by_field_name("name")  # type: ignore[attr-defined]
    if name_node is None:
        return None
    return name_node.text.decode("utf-8", errors="replace")


def _callee_name(call_node: object) -> str | None:
    fn = call_node.child_by_field_name("function")  # type: ignore[attr-defined]
    if fn is None:
        fn = call_node.child_by_field_name("name")  # type: ignore[attr-defined]
    if fn is None:
        return None
    if fn.type in ("identifier", "field_identifier", "property_identifier"):
        return fn.text.decode("utf-8", errors="replace")
    if fn.type == "attribute" or fn.type == "member_expression":
        attr = fn.child_by_field_name("attribute") or fn.child_by_field_name("property")
        if attr is not None:
            return attr.text.decode("utf-8", errors="replace")
    return None


def _extract(root_node: object) -> tuple[tuple[Definition, ...], tuple[CodeEdge, ...]]:
    definitions: list[Definition] = []
    edges: list[CodeEdge] = []
    stack: list[object] = [root_node]
    while stack:
        node = stack.pop()
        node_type = node.type  # type: ignore[attr-defined]
        kind = _DEF_KIND_BY_NODE.get(node_type)
        if kind is not None:
            name = _node_name(node)
            if name is not None:
                start_row = node.start_point[0]  # type: ignore[attr-defined]
                end_row = node.end_point[0]  # type: ignore[attr-defined]
                definitions.append(
                    Definition(
                        name=name,
                        kind=kind,
                        start_line=start_row + 1,
                        end_line=end_row + 1,
                    )
                )
        elif node_type in _CALL_NODE_TYPES:
            callee = _callee_name(node)
            if callee is not None:
                line = node.start_point[0] + 1  # type: ignore[attr-defined]
                edges.append(CodeEdge(callee=callee, line=line))
        stack.extend(node.children)  # type: ignore[attr-defined]

    sorted_defs = tuple(
        sorted(definitions, key=lambda d: (d.start_line, d.end_line, d.kind, d.name))
    )
    sorted_edges = tuple(sorted(edges, key=lambda e: (e.line, e.callee)))
    return sorted_defs, sorted_edges


def _entry_point_for(lang: str, suffix: str) -> str:
    """The tree-sitter entry-point name to resolve for *lang* / *suffix* (PURE lookup).

    Suffix beats language (``.tsx`` is a TypeScript dialect); ``language`` is the default, so eight
    of the ten grammars need no entry at all.
    """
    return _ENTRY_POINT_BY_SUFFIX.get(suffix) or _ENTRY_POINT_BY_LANGUAGE.get(
        lang, _DEFAULT_ENTRY_POINT
    )


class _ParserLoad(NamedTuple):
    """The outcome of one grammar load: a parser, or the CAUSE there is none.

    Both fields are never set together and never both empty. Carrying the cause back to the
    caller — rather than returning a bare ``None`` — is what lets the emitted reason token be
    *the arm's*, instead of one constant standing in for four different situations.
    """

    parser: object | None
    failure: GrammarFailure | None


def _get_parser_for_lang(lang: str, entry_point: str = _DEFAULT_ENTRY_POINT) -> _ParserLoad:
    """Load the tree-sitter parser for *lang*, or name WHY there is none (Story 10.4).

    *entry_point* names the module attribute to resolve (Story 10.2 / AC3.1) — see
    ``_ENTRY_POINT_BY_LANGUAGE`` for why ``language`` is not universal. It defaults to ``language``
    so every existing caller and every single-dialect grammar is unaffected.

    Why this is four arms and not one ``try``
    ------------------------------------------
    This function used to be one ``try`` ending in ``except (ImportError, Exception): pass``.
    **The redundancy in that tuple was the tell**: ``ImportError`` is a subclass of
    ``Exception``, so it is ``except Exception`` written to look like it discriminates. It did
    not. Four measurably different situations — the package absent, the package present with
    an entry point Argus does not know, the package present and broken for this runtime, and
    the ``tree_sitter`` CORE itself unimportable — all left through the same exit and were all
    recorded ``grammar_missing_<lang>``. Three of those four told an operator to install a
    package they already had, or to install one language while every language was down.
    Do not re-merge these arms: the shape is forbidden by AR10 / ``architecture.md`` §Error
    Degradation and pinned by ``tests/test_grammar_diagnosis.py`` (``…-115``), which walks this
    function's own AST and rejects a bare, silent or redundant handler.

    Classification is by **arm position** — *which call raised* — never by exception type and
    never by exception message (DN-4). Measured on this host, the same broken grammar surfaces
    as ``ValueError('invalid language ID')``, ``TypeError('an integer is required')`` or an
    ``OSError`` from the loader, and the ABI-mismatch text is a C format string
    (``Incompatible Language version %u. Must be between %u and %u``) a tree-sitter release may
    change. Nothing here reads a message, and nothing persists one (NFR-S1: a message like
    ``/home/…/libfoo.so: cannot open shared object file`` is a host path).

    ``BaseException`` is deliberately NOT caught anywhere below. AR10 degrades *errors*, never
    *signals*: ctrl-c during a grammar load must interrupt the audit, not be recorded as a
    broken grammar.
    """
    # ── ARM 4 — the tree_sitter CORE runtime ──────────────────────────────────────────
    # Resolved through ``importlib`` rather than a ``from tree_sitter import …`` statement so
    # that all four causes sit on ONE seam a test can drive (Story 10.4 / DEV-1). A broken
    # core is not a fact about ``lang``: every language is down, so this token carries no
    # language suffix and its remedy names the core package.
    try:
        core = importlib.import_module("tree_sitter")
        language_cls = core.Language
        parser_cls = core.Parser
    except (ImportError, AttributeError):
        # Not a redundant pair: neither is a subclass of the other. ImportError = the core is
        # absent; AttributeError = it imported but does not expose the 0.25-era API.
        return _ParserLoad(None, GrammarFailure.CORE_RUNTIME_MISSING)

    # ── ARM 1 — the per-language grammar package ──────────────────────────────────────
    # The ONE cause whose old token was right, so its spelling is unchanged: the remedy really
    # is ``pip install tree-sitter-<lang>``.
    try:
        mod = importlib.import_module(f"tree_sitter_{lang}")
    except ImportError:
        return _ParserLoad(None, GrammarFailure.PACKAGE_MISSING)

    # ── ARM 2 — the package is installed; Argus does not know its entry point ─────────
    # NOTHING RAISES HERE. This is why splitting the ``except`` alone would not have closed
    # the defect, and why Story 10.2 — which fixed the two instances it had (TypeScript, PHP)
    # with ``_ENTRY_POINT_BY_LANGUAGE`` — handed the CLASS forward to Story 10.4 by name.
    # The operator can do nothing about this one; it is an Argus defect and says so.
    lang_func = getattr(mod, entry_point, None)
    if lang_func is None:
        return _ParserLoad(None, GrammarFailure.ENTRY_POINT_MISSING)

    # ── ARM 3 — the grammar is installed and broken for THIS runtime ──────────────────
    try:
        return _ParserLoad(parser_cls(language_cls(lang_func())), None)
    except Exception:  # noqa: BLE001 — degraded outcome `grammar_load_failed_<lang>`, not an uncaught raise (AR10)
        # Broad ON PURPOSE, and it carries a recorded outcome rather than a `pass`: the type
        # genuinely varies (ValueError / TypeError / OSError, and whatever the next
        # tree-sitter release invents), while the MEANING does not — "the parser could not be
        # constructed from an installed grammar". Same house form as `_index_source_file`
        # below, `secret_scan.py` and `tool_runner.py`.
        return _ParserLoad(None, GrammarFailure.LOAD_FAILED)


def _index_source_file(rel_path: str, source: bytes, parser: object) -> AstIndexEntry:
    try:
        tree = parser.parse(source)  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001 — degraded outcome, not an uncaught raise (AR10)
        return AstIndexEntry(
            file_path=rel_path,
            ast_eligible=False,
            parse_failed=True,
            parse_failure_reason="parser_error",
        )
    root_node = tree.root_node
    if root_node.has_error:
        return AstIndexEntry(
            file_path=rel_path,
            ast_eligible=False,
            parse_failed=True,
            parse_failure_reason="syntax_error",
        )
    definitions, edges = _extract(root_node)
    return AstIndexEntry(
        file_path=rel_path,
        ast_eligible=True,
        definitions=definitions,
        edges=edges,
    )


def build_ast_index(
    repo_root: str | Path,
    source_files: tuple[str, ...],
    *,
    partition_id: str = "root",
) -> AstIndex:
    """Build multi-language tree-sitter code-graph index over *source_files*.

    Supports Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby, PHP.
    Dynamically loads tree-sitter grammars when available; falls back to ast_eligible=False
    when a language grammar is un-installed or unparseable.

    Records per-grammar provenance for exactly the grammars that PARSED here (story 10.2 / DN-6):
    a grammar installed on the host but never used by this audit is deliberately absent, so the
    derived R3 cache key stays a function of the audit rather than of the machine it ran on.
    """
    root = Path(repo_root)
    grammar_version = _grammar_version()

    # Parser cache keyed by (language, entry point): ONE package can ship several dialects, and
    # `.ts` vs `.tsx` is a suffix-level distinction a language-keyed cache cannot express.
    # It caches the LOAD OUTCOME, not just the parser, so a failure is diagnosed once and every
    # file of that language reports the same cause without re-probing the import machinery.
    parsers: dict[tuple[str, str], _ParserLoad] = {}
    # Resolved version per language, populated only when that grammar actually parses something.
    parsed_versions: dict[str, str] = {}

    entries: list[AstIndexEntry] = []
    for rel_path in source_files:
        lang = _detect_language(rel_path)
        if lang is None:
            entries.append(
                AstIndexEntry(
                    file_path=rel_path,
                    ast_eligible=False,
                    parse_failure_reason="non_python",
                )
            )
            continue

        entry_point = _entry_point_for(lang, Path(rel_path).suffix.lower())
        cache_key = (lang, entry_point)
        if cache_key not in parsers:
            parsers[cache_key] = _get_parser_for_lang(lang, entry_point)
        load = parsers[cache_key]

        if load.failure is not None:
            # Name the ACTUAL cause — the ARM's, not a constant. This first reported
            # ``non_python`` for every non-Python language ("unsupported" when the truth was
            # "supported, grammar not installed"), then reported ``grammar_missing_<lang>``
            # for all FOUR ways a grammar can fail to load — which tells three operators out
            # of four to run a command that cannot help them. ``parse_failed`` stays False:
            # the flag means *a parse was attempted and failed*, and no parse is attempted
            # when there is no parser (the convention ``non_python`` already follows). The
            # report turns this token into a per-cause remedy via the same shared classifier.
            entries.append(
                AstIndexEntry(
                    file_path=rel_path,
                    ast_eligible=False,
                    parse_failure_reason=reason_token_for(load.failure, lang),
                )
            )
            continue
        parser = load.parser

        abs_path = root / rel_path
        try:
            source = abs_path.read_bytes()
        except OSError:
            entries.append(
                AstIndexEntry(
                    file_path=rel_path,
                    ast_eligible=False,
                    parse_failed=True,
                    parse_failure_reason="read_error",
                )
            )
            continue
        # The grammar is about to determine this file's index entry, so it PARTICIPATED and its
        # version belongs in the provenance record — including when the parse degrades, because a
        # `syntax_error` outcome is just as much a function of the grammar version as a clean one.
        if lang not in parsed_versions:
            parsed_versions[lang] = _package_version(lang)
        entries.append(_index_source_file(rel_path, source, parser))

    sorted_entries = tuple(sorted(entries, key=lambda e: e.file_path))
    grammar_versions = tuple(
        GrammarProvenance(language=lang, version=parsed_versions[lang])
        for lang in sorted(parsed_versions)
    )
    return AstIndex(
        partition_id=partition_id,
        grammar_version=grammar_version,
        grammar_versions=grammar_versions,
        entries=sorted_entries,
    )
