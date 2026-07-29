# APAA — Domain Research (Assurance Disciplines)

**Date:** 2026-06-17
**Purpose:** APAA earns credibility by porting concepts from mature assurance/audit disciplines. This report extracts the canonical principle from each, the authoritative source, and the one-line mapping to APAA — plus where borrowing the vocabulary risks over-claiming.

## Assurance Posture (the verdict's legal/business spine)

| Discipline | Principle | Maps to APAA |
|---|---|---|
| External/financial audit — **negative assurance** | "Nothing has come to our attention to suggest material misstatement" — a bounded, negative-form conclusion (ISAE 3000 / AICPA limited-assurance). | APAA's verdict is negative-assurance: "no disqualifying evidence within the examined scope," never a positive correctness guarantee. |
| **Reasonable vs limited assurance** | Reasonable = "presents fairly, in all material respects" (high bar, sufficient evidence); limited = fewer procedures, smaller samples, negative conclusion (ICAEW; ISAE 3000). | APAA grades its verdict confidence by how much of the repo was actually examined — confidence stated, not assumed. |
| **SOC 2 Type I vs Type II** | Type I = control design at a point in time; Type II = operating effectiveness over a period (AICPA). | APAA distinguishes a single-commit snapshot (Type I analog) from an over-a-release-window verdict (Type II analog). |
| **Materiality & sampling** | Auditors test a sample, judged against a materiality threshold; the conclusion is qualified by sample + materiality (ISAE 3000). | APAA reports its coverage envelope + a materiality bar so a "pass" is qualified by sample size, never implied exhaustive. |
| **Scope statement** | Every opinion is bounded by an explicit scope; out-of-scope ≠ assured. | The verdict ships with a machine-readable scope/coverage statement naming exactly what was **not** examined. |

## Standards to Map Findings To (credibility backbone)

| Standard | Scope | Use in APAA |
|---|---|---|
| **OWASP ASVS** | Verifiable security requirements, each cross-referenced to a CWE, mappable to ISO 27001 / SOC 2 / NIST. | Primary catalog: phrase security findings as "verification requirement N unmet." |
| **CWE** | Canonical weakness-type taxonomy used by tools + ASVS. | Tag each security finding with a CWE id → dedup, comparable, citable. (CWE **required** on security findings in V1.) |
| **NIST SSDF (SP 800-218)** | Secure-development practices/tasks; bidirectional mappings to SAMM and SLSA. | Map process/pipeline findings to SSDF tasks. |
| **SLSA** | Graded build-integrity / artifact-provenance, aligned to SSDF. | Express build-provenance/supply-chain coverage as an SLSA level (uses the hash-chain evidence). |
| **ISO/IEC 25010** | Software product quality model — 8 characteristics (functional suitability, performance, compatibility, usability, reliability, security, maintainability, portability). | Top-level rubric to organize non-security quality findings. |
| **SOC 2 / ISO 27001** | Organizational control frameworks (80–100% control overlap). | Cross-walk control-level findings into an enterprise's existing compliance posture. |

> **V1 standards stance:** optional `standards_refs[]` field on day one (additive, ~zero cost — honors "schemas frozen first"); CWE required on security findings; rich ASVS/ISO/SLSA population deferred to V2.

## Traceability & Coverage (DO-178C lineage)

- **Bidirectional traceability:** every requirement traces down to code AND to verifying tests, and every test back up to a requirement. APAA's coverage primitive is this requirement↔code↔test link; gaps are first-class findings.
- **Structural coverage tiered by criticality (DAL):** statement → decision → MC/DC rigor scales with Design Assurance Level. APAA scales required coverage **depth by component criticality**, not one flat bar.
- **MC/DC:** each condition shown to independently affect the outcome — APAA can demand independent-effect evidence for high-criticality decision logic.
- **Assurance case / safety case:** a structured argument (claims + evidence + reasoning) that a system is acceptably safe — APAA's verdict is structured as an assurance-case argument, not an opaque score.
- **Coverage is the denominator:** a negative-assurance verdict is only as strong as its coverage envelope — always pair verdict with measured coverage.
- **Uncovered ≠ passed:** a requirement with no traceable test is flagged unverified, never silently counted satisfied.

> Traceability (#13) is a **V2** capability — ~70% of real repos have poor docs and can't support a traceability audit (becomes a finding, not a crash).

## Production Readiness (Google SRE PRR)

- PRR is a checklist-driven, criteria-based, risk-proportional, **ongoing** operational-fitness evaluation — APAA models the readiness verdict on PRR structure.
- Dimensions APAA audits as readiness criteria: **observability** (logs/metrics/traces + SLO alerting), **deployment & rollback**, **capacity & scaling**, **reliability mechanisms** (health checks, graceful shutdown, retry/failure-mode handling), **runbooks/docs** (reduce MTTD/MTTR).
- ⚠️ SRE frames PRR as **collaborative, explicitly NOT an audit** — see credibility risks. (PRR / #8 is a **V2** capability.)

## Cost & Project Control (the deferred V3 cost-intelligence layer)

- **COCOMO:** effort = parametric function of size (LOC/FP) × complexity/team factors → parametric size→effort modeling.
- **Function Point Analysis:** size by user-facing functionality (language-independent unit).
- **PERT three-point:** expected = (O + 4M + P)/6 over a beta distribution → ranged, uncertainty-weighted estimates, never single-point.
- **Earned Value Management:** BAC (budget at completion), AC (actual cost), EV (earned value), **CV = EV − AC**, **EAC** (forecast), **CPI = EV/AC**, EAC = BAC/CPI → track delivery vs plan, forecast overrun early.
- All EVM/COCOMO/PERT outputs are **assumption-laden forecasts** — APAA must publish the size/assumption inputs so the number is auditable, not authoritative.

## Substrate Patterns (the event-sourced foundation)

- **Event sourcing:** append-only immutable log of domain events → reconstructable audit trail, never overwritten.
- **CQRS:** separate write (command) from read (projection) → many views from one immutable stream (verdict + reports as projections).
- **Hash chain:** each entry hashes its fields + the previous hash → altering any past record invalidates every later hash (mirrors this repo's ADR #18 ledger).
- **Merkle / content-addressed storage:** address artifacts by their hash; inclusion is provable → content-address evidence.
- **Tamper-evident audit log:** per-entry cryptographic wrapping makes deletion/edit detectable even by a DB-level attacker.
- **Mutation testing ("testing the tests"):** mutation score = killed/total → exposes high line-coverage-with-weak-assertions; basis for v2 vacuous-test detection and the defect-cartridge self-test.

## Credibility Risks (where borrowing a discipline could mislead)

1. **Negative assurance is easily misread as a positive guarantee** — the coverage/scope qualifier must be inseparable from the verdict (don't render as a bare green check).
2. **High coverage + weak suite = false confidence** — without mutation testing, APAA risks attesting "covered" code no assertion verifies.
3. **SRE explicitly says PRR is NOT an audit** — rebranding a collaboration checklist as a pass/fail gate over-claims and can alienate SRE practitioners.
4. **DO-178C / MC-DC carry safety-critical certification weight** — borrowing the vocabulary for non-certified repos risks implying avionics-grade assurance APAA hasn't earned.
5. **SOC 2 / "reasonable assurance" are legally defined CPA terms** — use as **analogies**, not claims, absent an actual attestation engagement.
6. **COCOMO/EVM/PERT are conditional forecasts** — presenting EAC/CPI as authoritative truth invites estimation over-confidence.
7. **Materiality means a clean verdict tolerates immaterial defects by design** — expose the materiality threshold or a "pass" may hide issues a reader would deem material.
