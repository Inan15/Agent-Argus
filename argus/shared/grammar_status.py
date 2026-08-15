"""Single source of truth for "why did a tree-sitter grammar fail to become a parser".

Drivers: ArgusAgent-AR8 (PURE contract — frozen data + pure functions; no I/O, no
``importlib``, no ``importlib.metadata``, no ``tree_sitter`` import), AR10 (a failure is
recorded as a named degraded outcome, and the name must be the cause it actually had),
AR4 (deterministic — a frozen mapping, no iteration-order reliance), ArgusAgent-NFR-P2
(the language conditional stays in ``index/`` + this pure contract; ``ledger/`` and
``verdict/`` gain no language field).

Why this module exists (Story 10.4 / ``DF-AUD-APAA-F``)
-------------------------------------------------------
``_get_parser_for_lang`` used to wrap the whole load in ``except (ImportError, Exception):
pass``. That tuple *looks* like it discriminates, but ``ImportError`` is a subclass of
``Exception``, so it is ``except Exception`` written to look like two arms — and the
redundancy was the tell. **Four** distinguishable failures collapsed into the one token
``grammar_missing_<lang>``, and in **three** of the four the remedy that token implies is
wrong:

===  ============================================  =====================================
#    What the operator actually has                Remedy the old token implied
===  ============================================  =====================================
1    the grammar package is not installed          ``pip install tree-sitter-<lang>`` ✅
2    the package IS installed; Argus does not      "install what you already have" ❌
     know its entry point (nothing raises —        — it is an **Argus** defect
     ``getattr`` simply returns ``None``)
3    the package is installed and BROKEN for       "install what you already have" ❌
     this runtime (ABI mismatch, corrupt build)    — reinstall / rebuild instead
4    the ``tree_sitter`` CORE is not importable    "install one language package" ❌
     — EVERY language is down, not this one       — ``pip install tree-sitter`` instead
===  ============================================  =====================================

Cause 2 is the one the ledger's own stated repair (splitting the ``except``) does **not**
catch, because nothing raises; Story 10.2 measured it, fixed its two instances with
``_ENTRY_POINT_BY_LANGUAGE``, and handed the *class* forward by name.

Why the classification lives HERE and not at either call site
--------------------------------------------------------------
The report used to recover the language by string arithmetic::

    prefix = "grammar_missing_"
    if reason.startswith(prefix):
        missing[reason[len(prefix):]] += 1

A second prefix guess is exactly how this fix breaks itself. ``grammar_entrypoint_missing_go``
does not start with ``grammar_missing_``, so it would be silently skipped (the callout goes
**silent**); a naive widening to ``startswith("grammar_")`` would slice it into the "language"
``entrypoint_missing_go`` and hand the operator ``pip install tree-sitter-entrypoint_missing_go``
(the callout **misdirects**). Both sides therefore import ``classify_reason`` from here.
One definition, imported everywhere, is the rule ``argus/shared/source_languages.py`` exists
to enforce — this project has already paid twice for the same mapping living in several places.

What this module deliberately does NOT do
------------------------------------------
* **It does not carry exception detail.** Classification is by ARM POSITION — *which call
  raised* — never by exception type and never by exception message. The same broken grammar
  surfaces as ``ValueError`` ("invalid language ID"), ``TypeError`` ("an integer is required")
  or ``OSError`` depending on how it is broken, and the ABI message is a C format string
  (``Incompatible Language version %u. Must be between %u and %u``) a tree-sitter release may
  change. Persisting ``str(exc)`` would also put a host filesystem path into the index
  (NFR-S1). The exception detail an operator might want is Story 12.8's surface.
* **It does not carry operator PROSE.** The report layer owns report wording (and Story 12.8
  owns the CLI's). This module answers *which class, which language, which package* — the
  facts a message is built from — so the two surfaces cannot drift apart on the facts while
  each keeps its own voice.
"""

from __future__ import annotations

from enum import Enum
from typing import Final, Iterable, NamedTuple

__all__ = [
    "GrammarFailure",
    "GrammarDiagnosis",
    "GrammarCanary",
    "CanaryObservation",
    "CORE_PACKAGE",
    "CORE_RUNTIME_TOKEN",
    "RUNTIME_UNVALIDATED_TOKEN",
    "CORE_VERSION_FLOOR",
    "CORE_VERSION_CEILING_EXCLUSIVE",
    "SUPPORTED_CORE_RANGE",
    "INSPECT_CORE_VERSION_COMMAND",
    "TOKEN_PREFIX_BY_FAILURE",
    "TOKEN_BY_UNSUFFIXED_FAILURE",
    "GRAMMAR_PACKAGE_BY_LANGUAGE",
    "CANARY_BY_ENTRY_POINT",
    "registered_failures",
    "reason_token_for",
    "classify_reason",
    "grammar_package_for",
    "parse_version_tuple",
    "core_version_is_supported",
    "canary_for",
    "canary_matches",
    "downgrade_reasons",
]


class GrammarFailure(str, Enum):
    """The five distinguishable ways a grammar fails to become a *trustworthy* parser.

    One member per ARM of ``argus/index/ast_index.py::_get_parser_for_lang``. Adding a
    sixth arm without adding a member here fails
    ``tests/test_grammar_diagnosis.py::…-115`` — the closure that makes this enumeration
    a contract rather than a comment.
    """

    #: Cause 1 — ``importlib.import_module("tree_sitter_<lang>")`` raised ``ImportError``.
    PACKAGE_MISSING = "package_missing"
    #: Cause 2 — the module imported, but it exports no entry point Argus knows. NOTHING
    #: RAISES here; ``getattr(mod, entry_point, None)`` simply returns ``None``.
    ENTRY_POINT_MISSING = "entry_point_missing"
    #: Cause 3 — the entry point exists, and constructing ``Parser(Language(...))`` failed.
    LOAD_FAILED = "load_failed"
    #: Cause 4 — the ``tree_sitter`` CORE runtime is not importable. Not language-specific.
    CORE_RUNTIME_MISSING = "core_runtime_missing"
    #: Cause 5 (Story 11.4) — a parser WAS constructed, and it did not pass Argus's
    #: behavioural self-check: the pinned canary for this seam did not extract what Argus
    #: was validated against (or the resolved core version is outside the declared range).
    #: NOTHING RAISES here either — that is the whole point. Causes 1–4 are a toolchain
    #: that is visibly absent; this one is a toolchain that is visibly PRESENT and quietly
    #: wrong, which is the only one that can produce a false 🟢.
    RUNTIME_UNVALIDATED = "runtime_unvalidated"


class GrammarDiagnosis(NamedTuple):
    """What a recorded ``parse_failure_reason`` token means.

    ``language`` is ``None`` for :attr:`GrammarFailure.CORE_RUNTIME_MISSING`, which is a
    statement about the runtime rather than about one language.
    """

    failure: GrammarFailure
    language: str | None


#: The tree-sitter CORE distribution — the one every language depends on.
CORE_PACKAGE: Final[str] = "tree-sitter"

#: Cause 4's token. It carries NO ``<lang>`` suffix on purpose: the core being unimportable
#: is not a fact about one language, and suffixing it would invite the reader to install a
#: single grammar package when every language is down.
CORE_RUNTIME_TOKEN: Final[str] = "tree_sitter_runtime_missing"

#: Cause 5's token (Story 11.4). It carries NO ``<lang>`` suffix for the SAME reason cause
#: 4's does not: an unvalidated toolchain is a fact about the RUNTIME. Suffixing it would
#: invite a per-language remedy, and there is none — reinstalling one grammar cannot make an
#: unsupported core, or a drifted extraction vocabulary, behave the way Argus was validated
#: against. The remedy names the supported range instead (``_render_grammar_remedy``).
RUNTIME_UNVALIDATED_TOKEN: Final[str] = "tree_sitter_runtime_unvalidated"

#: Token prefix per language-scoped failure. ``grammar_missing_`` KEEPS its exact spelling
#: and its exact meaning — the epic requires it and ``TC-ArgusAgent-INDEX-001-73`` pins it.
TOKEN_PREFIX_BY_FAILURE: Final[dict[GrammarFailure, str]] = {
    GrammarFailure.PACKAGE_MISSING: "grammar_missing_",
    GrammarFailure.ENTRY_POINT_MISSING: "grammar_entrypoint_missing_",
    GrammarFailure.LOAD_FAILED: "grammar_load_failed_",
}

#: The failures whose token names the RUNTIME rather than one language. Kept as a table
#: rather than as a chain of ``if failure is …``: with two such causes a third would
#: otherwise be a third special case in three functions, which is how ``grammar_missing_``
#: came to be parsed in two places in the first place.
TOKEN_BY_UNSUFFIXED_FAILURE: Final[dict[GrammarFailure, str]] = {
    GrammarFailure.CORE_RUNTIME_MISSING: CORE_RUNTIME_TOKEN,
    GrammarFailure.RUNTIME_UNVALIDATED: RUNTIME_UNVALIDATED_TOKEN,
}

_FAILURE_BY_UNSUFFIXED_TOKEN: Final[dict[str, GrammarFailure]] = {
    token: failure for failure, token in TOKEN_BY_UNSUFFIXED_FAILURE.items()
}

#: Language token → the PyPI distribution that ships its grammar. Moved here from
#: ``argus/reports/generator.py`` (Story 10.4 / AC6.6) so the producer's classification and
#: the consumer's remedy are read off ONE table. The set of keys is pinned equal to
#: ``LANGUAGE_BY_SUFFIX``'s value set by ``TC-ArgusAgent-REPORT-002-25``, so an eleventh
#: language cannot be added to one and not the other.
GRAMMAR_PACKAGE_BY_LANGUAGE: Final[dict[str, str]] = {
    "c": "tree-sitter-c",
    "cpp": "tree-sitter-cpp",
    "go": "tree-sitter-go",
    "java": "tree-sitter-java",
    "javascript": "tree-sitter-javascript",
    "php": "tree-sitter-php",
    "python": "tree-sitter-python",
    "ruby": "tree-sitter-ruby",
    "rust": "tree-sitter-rust",
    "typescript": "tree-sitter-typescript",
}

# Longest prefix first, so classification is unambiguous even if a future token prefix is
# ever an extension of another. `_assert_prefixes_are_unambiguous` below makes that
# impossible in the first place; the ordering is the belt to its braces.
_PREFIXES_LONGEST_FIRST: Final[tuple[tuple[str, GrammarFailure], ...]] = tuple(
    sorted(
        ((prefix, failure) for failure, prefix in TOKEN_PREFIX_BY_FAILURE.items()),
        key=lambda pair: (-len(pair[0]), pair[0]),
    )
)


def _assert_prefixes_are_unambiguous() -> None:
    """No token prefix may be a prefix of another (import-time invariant).

    If it were, one recorded token would classify as two causes depending on match order —
    the ``startswith`` trap this module exists to remove, reintroduced one layer down.

    Story 11.4 extends it in two directions the fifth cause makes reachable: the unsuffixed
    tokens are now a SET, so they are checked against each other as well as against the
    language prefixes, and every registered failure must own exactly one token spelling —
    a sixth member added with neither would otherwise reach ``reason_token_for`` at audit
    time rather than at import time.
    """
    prefixes = [prefix for prefix, _ in _PREFIXES_LONGEST_FIRST]
    for outer in prefixes:
        for inner in prefixes:
            if outer != inner and outer.startswith(inner):
                raise ValueError(
                    f"grammar reason-token prefix {inner!r} is a prefix of {outer!r}; a "
                    "recorded token would classify as two different causes. Choose a "
                    "token spelling that no other prefix can swallow."
                )
    for token in TOKEN_BY_UNSUFFIXED_FAILURE.values():
        for prefix in prefixes:
            if token.startswith(prefix):
                raise ValueError(
                    f"the runtime-scoped token {token!r} starts with the language-scoped "
                    f"prefix {prefix!r}; it would be read as a language failure."
                )
        for other in TOKEN_BY_UNSUFFIXED_FAILURE.values():
            if token != other and token.startswith(other):
                raise ValueError(
                    f"the runtime-scoped token {other!r} is a prefix of {token!r}; the two "
                    "causes could not be told apart from a recorded token alone."
                )
    unnamed = sorted(
        failure.value
        for failure in GrammarFailure
        if failure not in TOKEN_PREFIX_BY_FAILURE and failure not in TOKEN_BY_UNSUFFIXED_FAILURE
    )
    if unnamed:
        raise ValueError(
            f"GrammarFailure member(s) {unnamed} have no registered token spelling. Register "
            "each in TOKEN_PREFIX_BY_FAILURE (language-scoped) or TOKEN_BY_UNSUFFIXED_FAILURE "
            "(runtime-scoped); a member with neither is a cause that cannot be recorded."
        )


_assert_prefixes_are_unambiguous()

# ─────────────────────────────────────────────────────────────────────────────
# Story 11.4 — the toolchain the verdict rests on, as pure data
# ─────────────────────────────────────────────────────────────────────────────
#
# ⚠️ THE VERSION BOUND BELOW IS EVIDENCE, NOT THE CHECK. Story 11.4 measured the false 🟢
# it exists to stop and it happens at an IN-BOUND version: with `tree-sitter 0.25.2`
# installed, a drifted call/reference node vocabulary flipped a staged repository from
# NOT_READY_FOR_RELEASE / exit 2 to RELEASE_READY / exit 0 while `deep_ratio` stayed 5/6 in
# BOTH runs. A version comparison is green on the exact tree where that defect is live, so
# the mechanism is the behavioural canary below; the bound is a second, independent signal.

#: Inclusive floor and EXCLUSIVE ceiling of the supported `tree-sitter` core, as integer
#: tuples rather than a specifier string: `packaging` is present in this venv only
#: transitively (via `bandit`/`build`) and is declared in neither `dependencies` nor
#: `[dev]`, so importing it would add an undeclared dependency to a PURE contract module.
#: Normalised to three components by `parse_version_tuple` so that `0.25` and `0.25.0`
#: compare equal — tuple ordering would otherwise put `(0, 25)` BELOW `(0, 25, 0)`.
CORE_VERSION_FLOOR: Final[tuple[int, int, int]] = (0, 25, 0)
CORE_VERSION_CEILING_EXCLUSIVE: Final[tuple[int, int, int]] = (0, 26, 0)

#: The same range in the spelling `pyproject.toml` uses. ONE source of truth: a test parses
#: the specifier out of `pyproject.toml` and asserts equality with this constant in both
#: directions, because this project has paid at least four times for a duplicated
#: enumerable fact (see `argus/shared/source_languages.py`'s docstring for the tally).
SUPPORTED_CORE_RANGE: Final[str] = ">=0.25.0,<0.26"

#: What an operator runs to see what they actually have. The observed version is NOT
#: persisted and NOT rendered (NFR-S1 / Story 10.4 DN-5); a richer diagnostic is 12.8's.
INSPECT_CORE_VERSION_COMMAND: Final[str] = "pip show tree-sitter"

_VERSION_COMPONENTS: Final[int] = 3


def parse_version_tuple(version: str | None) -> tuple[int, int, int] | None:
    """Parse a released version string into a comparable 3-tuple, or ``None`` (PURE, total).

    Deliberately lenient about what follows the numbers (``0.26.0rc1`` → ``(0, 26, 0)``) and
    deliberately strict about returning ``None`` when there is no leading integer at all: a
    version Argus cannot read is a version Argus has not checked, and the caller must treat
    that as unsupported rather than as "probably fine". Never raises — a metadata string is
    host input (AR10).
    """
    if not version:
        return None
    parts: list[int] = []
    for chunk in version.split("."):
        digits = ""
        for char in chunk:
            if not char.isdigit():
                break
            digits += char
        if not digits:
            break
        parts.append(int(digits))
        if len(parts) == _VERSION_COMPONENTS:
            break
    if not parts:
        return None
    while len(parts) < _VERSION_COMPONENTS:
        parts.append(0)
    return (parts[0], parts[1], parts[2])


def core_version_is_supported(version: tuple[int, int, int] | None) -> bool:
    """Is *version* inside the declared supported range (PURE)?

    ``None`` — unresolvable or unreadable metadata — is **not** supported. Fail closed: the
    whole point of the story is that an assurance tool must not vouch on top of a toolchain
    it has not checked, and "I could not tell" is not "I checked".
    """
    if version is None:
        return False
    return CORE_VERSION_FLOOR <= version < CORE_VERSION_CEILING_EXCLUSIVE


def registered_failures() -> frozenset[GrammarFailure]:
    """Every failure class this contract knows (PURE).

    The registry side of the both-direction closure in ``tests/test_grammar_diagnosis.py``:
    a class registered here that no test drives fails, and an observed token that does not
    classify to a member here fails.
    """
    return frozenset(GrammarFailure)


def reason_token_for(failure: GrammarFailure, language: str | None = None) -> str:
    """The ``parse_failure_reason`` token recording *failure* for *language* (PURE).

    Raises ``ValueError`` rather than guessing when a language-scoped failure arrives with
    no language: a token like ``grammar_missing_None`` would be a named reason in form only,
    which is the exact defect this story closes.
    """
    unsuffixed = TOKEN_BY_UNSUFFIXED_FAILURE.get(failure)
    if unsuffixed is not None:
        return unsuffixed
    prefix = TOKEN_PREFIX_BY_FAILURE.get(failure)
    if prefix is None:  # pragma: no cover — unreachable while the registry is complete
        raise ValueError(
            f"{failure!r} has no registered token prefix. Every GrammarFailure member must "
            "appear in TOKEN_PREFIX_BY_FAILURE or be the core-runtime failure."
        )
    if not language:
        raise ValueError(
            f"{failure.value} is language-scoped and needs a language token; got {language!r}."
        )
    return f"{prefix}{language}"


def classify_reason(reason: str | None) -> GrammarDiagnosis | None:
    """Classify a recorded ``parse_failure_reason``, or ``None`` if it is not a grammar-load failure (PURE).

    ``None`` is the honest answer for ``syntax_error``, ``parser_error``, ``read_error``,
    ``non_python`` and ``None`` itself: those are not grammar-load failures and must not be
    given a grammar remedy.

    ⛔ Callers use THIS. A second ``startswith``/slice at a call site is the defect
    (see the module docstring).
    """
    if not reason:
        return None
    runtime_scoped = _FAILURE_BY_UNSUFFIXED_TOKEN.get(reason)
    if runtime_scoped is not None:
        return GrammarDiagnosis(runtime_scoped, None)
    for prefix, failure in _PREFIXES_LONGEST_FIRST:
        if reason.startswith(prefix):
            language = reason[len(prefix):]
            if not language:
                return None  # a bare prefix names no language — not a valid record
            return GrammarDiagnosis(failure, language)
    return None


def grammar_package_for(language: str) -> str:
    """The distribution that ships *language*'s grammar (PURE).

    Falls back to the ``tree-sitter-<lang>`` convention every published grammar follows, so
    an eleventh language degrades to a plausible name rather than to nothing. The fallback
    is a courtesy, not the contract — ``TC-ArgusAgent-REPORT-002-25`` requires the table to
    stay complete.
    """
    return GRAMMAR_PACKAGE_BY_LANGUAGE.get(language, f"tree-sitter-{language}")


# ─────────────────────────────────────────────────────────────────────────────
# The behavioural canary corpus — Story 11.4's actual mechanism
# ─────────────────────────────────────────────────────────────────────────────


class GrammarCanary(NamedTuple):
    """The pinned behavioural expectation for one ``(language, entry point)`` load seam.

    ``vocabulary`` is the load-bearing field, and it is not the same thing as
    ``definitions``/``edges``: it is the set of tree-sitter NODE TYPES in the parsed canary
    that ``ast_index``'s own extraction tables (``_DEF_KIND_BY_NODE`` ∪ ``_CALL_NODE_TYPES``)
    actually match. That is precisely the surface a drifted grammar moves — and precisely
    the surface Story 11.4's demonstrated false 🟢 travelled on — so pinning it makes the
    check fire on a vocabulary drift even where the extracted output is legitimately empty.

    That distinction is what keeps FOUR languages honest. ``DF-10-2-A`` is open and measured:
    C, C++, Ruby and Rust load, parse cleanly and extract ZERO definitions on this tree for
    structural reasons (their definition nodes are ``function_item`` / ``method`` / a
    ``declarator`` field, none of which ``_DEF_KIND_BY_NODE`` or ``_node_name`` cover). A
    canary asserting "≥1 definition" uniformly would fire on four HEALTHY grammars and take
    every polyglot audit to ``INSUFFICIENT_COVERAGE`` — a false-green fix that ships a mass
    false red. Their expectations therefore pin today's honest truth, including the empty
    tuples; ``DF-10-2-A`` owns changing them, not this story.
    """

    #: A tiny, syntactically complete snippet in the language. Frozen data, no I/O.
    source: str
    #: Sorted node types the extraction tables match in the parsed canary. NEVER empty —
    #: an empty expectation is a canary that cannot fail (§C.3), and a test pins that.
    vocabulary: tuple[str, ...]
    #: The ``(kind, name)`` pairs ``_extract`` yields, in its own sorted order.
    definitions: tuple[tuple[str, str], ...]
    #: The callee names ``_extract`` yields, in its own sorted order.
    edges: tuple[str, ...]


class CanaryObservation(NamedTuple):
    """What a REAL toolchain actually did with a canary, measured by the impure probe.

    Deliberately the same three fields as :class:`GrammarCanary` plus ``parse_error``, so the
    comparison is a total equality rather than a set of hand-written conditions that could
    drift apart from the corpus.
    """

    parse_error: bool
    vocabulary: tuple[str, ...]
    definitions: tuple[tuple[str, str], ...]
    edges: tuple[str, ...]


#: ``(language, entry point) → canary``. Keyed by the SAME pair
#: ``ast_index._get_parser_for_lang`` caches on, so the two TypeScript dialects
#: (``language_typescript`` / ``language_tsx``) are validated separately — a `.tsx` file
#: routed through a drifted TSX grammar is exactly the blind spot Story 10.2 paid for.
#:
#: 🚩 EVERY VALUE BELOW WAS MEASURED ON THIS HOST BY EXECUTION, never assumed — see the
#: Story 11.4 Dev Agent Record for the eleven-row transcript. Do not hand-edit an
#: expectation to make a canary pass: a mismatch means the toolchain moved, which is the
#: signal this table exists to raise.
CANARY_BY_ENTRY_POINT: Final[dict[tuple[str, str], GrammarCanary]] = {
    ("c", "language"): GrammarCanary(
        source="int argus_probe(void) { return 1; }\n\nint argus_canary(void) { return argus_probe(); }\n",
        vocabulary=("call_expression", "function_definition"),
        definitions=(),  # DF-10-2-A: C names its function through a `declarator` field.
        edges=("argus_probe",),
    ),
    ("cpp", "language"): GrammarCanary(
        source="int argus_probe() { return 1; }\n\nint argus_canary() { return argus_probe(); }\n",
        vocabulary=("call_expression", "function_definition"),
        definitions=(),  # DF-10-2-A, as for C.
        edges=("argus_probe",),
    ),
    ("go", "language"): GrammarCanary(
        source=(
            "package main\n\nfunc argus_probe() int { return 1 }\n\n"
            "func argus_canary() int { return argus_probe() }\n"
        ),
        vocabulary=("call_expression", "function_declaration"),
        definitions=(("function", "argus_probe"), ("function", "argus_canary")),
        edges=("argus_probe",),
    ),
    ("java", "language"): GrammarCanary(
        source=(
            "class ArgusCanary {\n  int argus_probe() { return 1; }\n"
            "  int argus_canary() { return argus_probe(); }\n}\n"
        ),
        vocabulary=("class_declaration", "method_declaration", "method_invocation"),
        definitions=(
            ("class", "ArgusCanary"),
            ("function", "argus_probe"),
            ("function", "argus_canary"),
        ),
        edges=("argus_probe",),
    ),
    ("javascript", "language"): GrammarCanary(
        source="function argus_canary(value) {\n  return argus_probe(value);\n}\n",
        vocabulary=("call_expression", "function_declaration"),
        definitions=(("function", "argus_canary"),),
        edges=("argus_probe",),
    ),
    ("php", "language_php"): GrammarCanary(
        source=(
            "<?php\nfunction argus_probe() { return 1; }\n"
            "function argus_canary() { return argus_probe(); }\n"
        ),
        vocabulary=("function_call_expression", "function_definition"),
        definitions=(("function", "argus_probe"), ("function", "argus_canary")),
        edges=(),  # PHP names a call target through a `name` node `_callee_name` skips.
    ),
    ("python", "language"): GrammarCanary(
        source="def argus_canary(value):\n    return argus_probe(value)\n",
        vocabulary=("call", "function_definition"),
        definitions=(("function", "argus_canary"),),
        edges=("argus_probe",),
    ),
    ("ruby", "language"): GrammarCanary(
        source="def argus_probe\n  1\nend\n\ndef argus_canary\n  argus_probe()\nend\n",
        vocabulary=("call",),
        definitions=(),  # DF-10-2-A: Ruby's definition node is `method`.
        edges=(),  # …and its call node names the target through a `method` field.
    ),
    ("rust", "language"): GrammarCanary(
        source="fn argus_probe() -> i32 { 1 }\n\nfn argus_canary() -> i32 { argus_probe() }\n",
        vocabulary=("call_expression",),
        definitions=(),  # DF-10-2-A: Rust's definition node is `function_item`, not `fn_item`.
        edges=("argus_probe",),
    ),
    ("typescript", "language_typescript"): GrammarCanary(
        source="function argus_canary(value: number): number {\n  return argus_probe(value);\n}\n",
        vocabulary=("call_expression", "function_declaration"),
        definitions=(("function", "argus_canary"),),
        edges=("argus_probe",),
    ),
    ("typescript", "language_tsx"): GrammarCanary(
        source="function argus_canary(value) {\n  return argus_probe(value);\n}\n",
        vocabulary=("call_expression", "function_declaration"),
        definitions=(("function", "argus_canary"),),
        edges=("argus_probe",),
    ),
}


def canary_for(language: str, entry_point: str) -> GrammarCanary | None:
    """The pinned canary for one load seam, or ``None`` if none is pinned (PURE).

    ⛔ ``None`` means UNVALIDATED, and the caller must fail closed on it. An eleventh
    language whose canary was never measured must not be silently exempted from the check
    the whole story exists to add — that is the "guard that goes green by finding nothing"
    failure (§C.3). ``TC-ArgusAgent-INDEX-001-123`` pins the corpus against
    ``LANGUAGE_BY_SUFFIX``, so adding a language turns a test red at edit time rather than
    turning an audit grey at run time.
    """
    return CANARY_BY_ENTRY_POINT.get((language, entry_point))


def canary_matches(canary: GrammarCanary, observation: CanaryObservation) -> bool:
    """Did this toolchain do what Argus was validated against (PURE)?

    Total equality on all four fields, not a "close enough" heuristic. Argus's grounding is
    exact — a definition it does not see is a claim it cannot corroborate — so a toolchain
    that extracts *nearly* the right thing is one that will silently downgrade a
    verdict-eligible finding to advisory, which is the exact false-🟢 path Story 11.4
    demonstrated.
    """
    return (
        not observation.parse_error
        and observation.vocabulary == canary.vocabulary
        and observation.definitions == canary.definitions
        and observation.edges == canary.edges
    )


def downgrade_reasons(entries: Iterable[object]) -> tuple[str, ...]:
    """The recorded tokens of the entries a GRAMMAR-LOAD failure downgraded (PURE).

    Story 12.8 / AC7. *entries* is any iterable of objects carrying a
    ``parse_failure_reason`` attribute (the 1.4 ``AstIndexEntry`` shape, duck-typed so this
    pure module keeps no dependency on the impure index layer). Membership is decided by
    :func:`classify_reason` and by nothing else: ``syntax_error``, ``read_error``,
    ``non_python`` and ``None`` are NOT grammar-load failures and are excluded, because
    handing them a grammar remedy would be the same class of wrong answer a prefix guess
    gives (see this module's docstring).

    Order is preserved from *entries*, which the AST index already sorts (AR11), so the
    result is deterministic without a second sort.

    It exists so the population *"which files did a grammar failure downgrade?"* has ONE
    definition that the pipeline can hand to the CLI. ``reports/generator.py``'s two folds
    walk the entries themselves rather than calling this, because they need each entry's
    LANGUAGE and PACKAGE as well as its token — but they classify through the same
    :func:`classify_reason`, which is the part that must never be forked.
    """
    return tuple(
        reason
        for reason in (getattr(entry, "parse_failure_reason", None) for entry in entries)
        if reason is not None and classify_reason(reason) is not None
    )
