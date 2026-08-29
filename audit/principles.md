# Agent-Argus Audit Principles

1. **Evidence-Driven, Never Hallucinated**: Every defect claimed must cite exact AST spans or verified zero-token tool outputs.
2. **False-Accusation Moat**: Heuristic findings are advisory-by-contract. No red verdict ($\color{red}{\text{NOT READY}}$) without AST grounding and Prosecutor verification.
3. **Deterministic & Canonical**: Content-addressed cache keys, single serializer, exact fractions (no floats).
4. **Honest Degradation**: Budget exhaustion auto-downgrades coverage depth to `SKIPPED` and emits floor warnings (`INSUFFICIENT_COVERAGE`), never fabricating a fake release readiness.
5. **Producer-Side Redaction**: Secret values are masked at emission time; raw secret bytes never hit on-disk logs or evidence envelopes.
