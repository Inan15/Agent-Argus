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
from typing import Final, NamedTuple

__all__ = [
    "GrammarFailure",
    "GrammarDiagnosis",
    "CORE_PACKAGE",
    "CORE_RUNTIME_TOKEN",
    "TOKEN_PREFIX_BY_FAILURE",
    "GRAMMAR_PACKAGE_BY_LANGUAGE",
    "registered_failures",
    "reason_token_for",
    "classify_reason",
    "grammar_package_for",
]


class GrammarFailure(str, Enum):
    """The four distinguishable ways a grammar fails to become a parser.

    One member per ARM of ``argus/index/ast_index.py::_get_parser_for_lang``. Adding a
    fifth arm without adding a member here fails
    ``tests/test_grammar_diagnosis.py::…-111`` — the closure that makes this enumeration
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

#: Token prefix per language-scoped failure. ``grammar_missing_`` KEEPS its exact spelling
#: and its exact meaning — the epic requires it and ``TC-ArgusAgent-INDEX-001-73`` pins it.
TOKEN_PREFIX_BY_FAILURE: Final[dict[GrammarFailure, str]] = {
    GrammarFailure.PACKAGE_MISSING: "grammar_missing_",
    GrammarFailure.ENTRY_POINT_MISSING: "grammar_entrypoint_missing_",
    GrammarFailure.LOAD_FAILED: "grammar_load_failed_",
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
    for prefix in prefixes:
        if CORE_RUNTIME_TOKEN.startswith(prefix):
            raise ValueError(
                f"the core-runtime token {CORE_RUNTIME_TOKEN!r} starts with the "
                f"language-scoped prefix {prefix!r}; it would be read as a language failure."
            )


_assert_prefixes_are_unambiguous()


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
    if failure is GrammarFailure.CORE_RUNTIME_MISSING:
        return CORE_RUNTIME_TOKEN
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
    if reason == CORE_RUNTIME_TOKEN:
        return GrammarDiagnosis(GrammarFailure.CORE_RUNTIME_MISSING, None)
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
