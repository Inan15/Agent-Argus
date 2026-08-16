# Blocking-finding adjudication worklist — Story 13.2

> DERIVED by `scripts/audit_validation_corpus.py`. Do not hand-edit: re-run the
> script. Every row is a **blocking** (verdict-eligible) finding — the population the
> ≥80% precision gate is measured over. Advisory findings are in
> `adjudication-set.json` and are deliberately absent here: an advisory finding does
> not move a verdict and is not a false accusation, so it is not in the denominator.

**Nothing below is adjudicated.** TP/FP is the named human's call (protocol §2/§4).

## ai-body-runtime — 0 blocking

Pin `4480ffdeb4c56e232d230ebb67572117b72dd754` · python · 15 source files · verdict `RELEASE_READY` (exit 0) · deep 2/3

_No blocking finding. Nothing to adjudicate for this member._

## agent-markovich — 0 blocking

Pin `a561668636d8dac922b72d548ad92fdcc814a2ac` · python · 65 source files · verdict `INSUFFICIENT_COVERAGE` (exit 3) · deep 24/65

_No blocking finding. Nothing to adjudicate for this member._

## minions — 24 blocking

Pin `ec63b7293b7036bf910a0d1b5e61aba7dc551526` · python · 591 source files · verdict `NOT_READY_FOR_RELEASE` (exit 2) · deep 74/197

| # | rule_id | locator | TP/FP | adjudicator | rationale |
|---|---|---|---|---|---|
| 1 | `vacuous_test_ast` | `tests/clients/test_minion_client_cli_agent.py:32` | | | |
| 2 | `vacuous_test_ast` | `tests/interop/test_capability_catalog_boot_durability.py:162` | | | |
| 3 | `vacuous_test_ast` | `tests/observability/test_telemetry_engine.py:136` | | | |
| 4 | `vacuous_test_ast` | `tests/observability/test_telemetry_engine.py:80` | | | |
| 5 | `vacuous_test_ast` | `tests/providers/test_anthropic_provider.py:362` | | | |
| 6 | `vacuous_test_ast` | `tests/providers/test_ollama_provider.py:415` | | | |
| 7 | `vacuous_test_ast` | `tests/providers/test_openai_provider.py:280` | | | |
| 8 | `vacuous_test_ast` | `tests/providers/test_openai_provider.py:629` | | | |
| 9 | `vacuous_test_ast` | `tests/providers/test_truncated_response_classification.py:434` | | | |
| 10 | `vacuous_test_ast` | `tests/providers/test_truncated_response_classification.py:709` | | | |
| 11 | `vacuous_test_ast` | `tests/providers/test_truncated_response_classification.py:734` | | | |
| 12 | `vacuous_test_ast` | `tests/providers/test_truncated_response_classification.py:898` | | | |
| 13 | `vacuous_test_ast` | `tests/providers/test_truncated_response_classification.py:942` | | | |
| 14 | `vacuous_test_ast` | `tests/providers/test_truncated_response_classification.py:984` | | | |
| 15 | `vacuous_test_ast` | `tests/runtime/test_run_index_patrol.py:333` | | | |
| 16 | `vacuous_test_ast` | `tests/security/test_story_write_routes_least_privilege.py:209` | | | |
| 17 | `vacuous_test_ast` | `tests/security/test_story_write_routes_least_privilege.py:221` | | | |
| 18 | `vacuous_test_ast` | `tests/services/test_api_server.py:1008` | | | |
| 19 | `vacuous_test_ast` | `tests/services/test_api_server.py:861` | | | |
| 20 | `vacuous_test_ast` | `tests/services/test_api_server.py:956` | | | |
| 21 | `vacuous_test_ast` | `tests/services/test_help_recommender.py:467` | | | |
| 22 | `vacuous_test_ast` | `tests/services/test_help_recommender.py:545` | | | |
| 23 | `vacuous_test_ast` | `tests/services/test_help_recommender.py:607` | | | |
| 24 | `vacuous_test_ast` | `tests/services/test_help_recommender.py:798` | | | |

## xagents-webapp — 0 blocking

Pin `33a86525a4981c2725133c3f297ce003c1ef8a2b` · typescript · 862 source files · verdict `INSUFFICIENT_COVERAGE` (exit 3) · deep 513/862

_No blocking finding. Nothing to adjudicate for this member._

## agent-smith — 7 blocking

Pin `9ab774d7bf5d61da552c61094b2d478f72dfbb6d` · typescript · 435 source files · verdict `NOT_READY_FOR_RELEASE` (exit 2) · deep 72/145

| # | rule_id | locator | TP/FP | adjudicator | rationale |
|---|---|---|---|---|---|
| 1 | `vacuous_test_ast` | `agentsmith-core/tests/test_gateway_failover.py:10` | | | |
| 2 | `vacuous_test_ast` | `agentsmith-core/tests/test_gateway_failover.py:105` | | | |
| 3 | `vacuous_test_ast` | `agentsmith-core/tests/test_gateway_failover.py:124` | | | |
| 4 | `vacuous_test_ast` | `agentsmith-core/tests/test_gateway_failover.py:46` | | | |
| 5 | `vacuous_test_ast` | `agentsmith-core/tests/test_ir_copilot.py:128` | | | |
| 6 | `vacuous_test_ast` | `agentsmith-core/tests/test_ir_copilot.py:147` | | | |
| 7 | `vacuous_test_ast` | `agentsmith-core/tests/test_trace_emitter.py:129` | | | |

---

**Total blocking findings to adjudicate: 31.** Precision = TP / (TP + FP) over this population, as an exact `Fraction` (AR4). The gate additionally requires 0 blocking false positives on a clean repository, N ≥ 5, and the adjudication run recorded cleared — all four, or the gate stays PROVISIONAL (protocol §5).
