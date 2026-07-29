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

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "Definition",
    "CodeEdge",
    "AstIndexEntry",
    "AstIndex",
    "build_ast_index",
]

_LANGUAGE_BY_SUFFIX: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".pyx": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".rb": "ruby",
    ".php": "php",
}

_PYTHON_SUFFIXES: tuple[str, ...] = (".py", ".pyi", ".pyx")

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

    Records the resolved ``grammar_version`` (the ``tree-sitter-python`` package
    version) so Epic 5 / AR5 can fold it into the determinism cache key — this
    story only RECORDS it. ``partition_id`` is ``"root"`` in V1 (partitioning is
    Story 2.4). Entries are SORTED by ``file_path`` (AR11).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default="1", description="AstIndex schema version (additive-only).")
    partition_id: str = Field(default="root", description="Audit-partition id ('root' in V1).")
    grammar_version: str = Field(
        ..., description="Resolved tree-sitter-python grammar/package version (Epic-5/AR5 cache-key input)."
    )
    entries: tuple[AstIndexEntry, ...] = Field(
        ..., description="Sorted per-file index entries (AR11)."
    )


def _grammar_version() -> str:
    """Resolved ``tree-sitter-python`` package version (AR1 / Epic-5 cache key).

    Recorded, not interpreted, here. Falls back to ``"unknown"`` if metadata is
    unavailable (degraded but honest, AR10) — never raises out of the builder.
    """
    try:
        return importlib.metadata.version("tree-sitter-python")
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


def _get_parser_for_lang(lang: str) -> object | None:
    """Helper to dynamically load tree-sitter language parser for any supported language."""
    try:
        from tree_sitter import Language, Parser
        module_name = f"tree_sitter_{lang}"
        mod = importlib.import_module(module_name)
        lang_func = getattr(mod, "language", None)
        if lang_func is not None:
            return Parser(Language(lang_func()))
    except (ImportError, Exception):
        pass
    return None


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
    """
    root = Path(repo_root)
    grammar_version = _grammar_version()

    # Pre-cache parsers for available language packages
    parsers: dict[str, object | None] = {}

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

        if lang not in parsers:
            parsers[lang] = _get_parser_for_lang(lang)
        parser = parsers[lang]

        if parser is None:
            entries.append(
                AstIndexEntry(
                    file_path=rel_path,
                    ast_eligible=False,
                    parse_failure_reason="non_python" if lang != "python" else "grammar_missing_python",
                )
            )
            continue

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
        entries.append(_index_source_file(rel_path, source, parser))

    sorted_entries = tuple(sorted(entries, key=lambda e: e.file_path))
    return AstIndex(
        partition_id=partition_id,
        grammar_version=grammar_version,
        entries=sorted_entries,
    )
