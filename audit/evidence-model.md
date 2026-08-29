# Agent-Argus Evidence Model & Confidence Engine Specification

## Evidence Model

Every finding emitted by Agent-Argus carries a verifiable evidence descriptor:
- `finding_id`: Content-derived sha256 hash of location and rule id.
- `rule_id`: E.g., `vacuous_test_ast`, `hardcoded_secret`, `orphan_code`.
- `locators`: List of AST spans (file, start line, end line, symbol name).
- `advisory`: Boolean flag indicating whether finding is advisory-only or verdict-eligible.
- `depth_supported`: Minimum coverage depth required to validate this finding.

## Confidence Engine

- **High Confidence**: Grounded in concrete tree-sitter AST nodes + zero-token tool output + Prosecutor sign-off.
- **Medium Confidence**: Heuristic indicator with zero-token tool corroboration.
- **Advisory**: Preliminary pattern match; recorded in evidence ledger, excluded from verdict gate until AST-corroborated.
