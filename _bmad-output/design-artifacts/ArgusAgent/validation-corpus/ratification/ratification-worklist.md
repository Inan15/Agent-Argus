# Ratification worklist — the SEALED bench partition (protocol §6 R2)

> ⛔ **THIS DOCUMENT RATIFIES NOTHING AND RECOMMENDS NOTHING.** It is the evidence
> package for the operator act filed as Story 19.2. Produced by
> `scripts/build_ratification_record.py` from
> `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/ratification/ratification-record.json`.

**Rows:** 6 · **`eligible_member_count()`:** 5 before, 5 after · **sealed ∩ ratified:** `[]`

## ⛔ Read this before the table

OBSERVATION, NOT A RECOMMENDATION. Story 19.1 was chartered to put a heuristic finding count in front of the operator BEFORE the R2 ratification of story 19.2. Measurement shows that count cannot exist before that ratification: the instrument that produces it refuses unratified members by construction (see finding_count_unmeasured_reason). The R2 judgement is therefore available on twelve of the thirteen columns and not on the thirteenth, and whether that is sufficient to rule on is the operator's decision and is NOT taken here. This record neither argues for ratification nor against it.

**Why the finding-count column is empty:**

UNMEASURABLE-BEFORE-RATIFICATION. The one producer of this column, scripts/audit_validation_corpus.py, folds over manifest.eligible_members(), which selects only members carrying eligible_for_n = True. All six sealed members carry eligible_for_n = False with ineligible_reason 'candidate - awaiting operator ratification (protocol section 6 R2)', so the runner selects none of them and exits 'REFUSED - no eligible members selected' (exit 2). Obtaining this number would require flipping eligible_for_n (which IS the R2 operator act this record exists to inform), writing a second walker (barred by AR7/DN-3 and by story 19.1 AC4.1), or widening the runner to audit unratified repositories (which would remove the refusal that makes corpus-shopping unexpressible). All three are refused. The column is therefore reported UNMEASURED with this reason rather than estimated, and the member is NOT dropped from the population.

## The members

| member | pin | licence | files @ pin | `.py` @ pin | findings @ pin |
|---|---|---|---:|---:|---|
| `aws-aws-sam-cli` | `5b6ebdba5866` | Apache-2.0 — 'Apache License' (LICENSE, tracked at the pin) | 3919 | 1703 | UNMEASURED |
| `celery-celery` | `2c42237d3757` | BSD-3-Clause — 'Copyright (c) 2017-2026 Asif Saif Uddin, core team & contributors. All rights reserved.' (LICENSE, tracked at the pin) | 823 | 419 | UNMEASURED |
| `certbot-certbot` | `abf9d1b2e143` | Apache-2.0 — 'Certbot ACME Client' (LICENSE.txt, tracked at the pin) | 1252 | 366 | UNMEASURED |
| `conda-conda` | `ad60271d8409` | BSD-3-Clause — 'BSD 3-Clause License' (LICENSE, tracked at the pin) | 2164 | 447 | UNMEASURED |
| `getsentry-sentry-python` | `064542dd2cbd` | MIT — 'MIT License' (LICENSE, tracked at the pin) | 638 | 499 | UNMEASURED |
| `googleapis-google-auth-library-python` | `2ea24b034367` | Apache-2.0 — 'Apache License' (LICENSE, tracked at the pin) | 374 | 192 | UNMEASURED |

## What each member says about itself

⛔ Read verbatim from the manifest's `adjudication_caveat`. Not re-derived, not summarised.

### `aws-aws-sam-cli`

- **Repository:** https://github.com/aws/aws-sam-cli
- **Pin:** `5b6ebdba5866be7a9430d2127630e96329a87649`
- **Provenance:** independent · **Language:** python
- **`eligible_for_n`:** `False` — candidate - awaiting operator ratification (protocol section 6 R2)
- **Caveat:** THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE its tests drive the AWS SDK across a service boundary that is substituted throughout — a rationale that references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the git object database with the detector NOT imported: 497 test files, 296 binding a mock primitive, 217 asserting on a mock-derived value, 215 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 218), rate 215/497 exact, 3294 days of history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's act at R2.

### `celery-celery`

- **Repository:** https://github.com/celery/celery
- **Pin:** `2c42237d375718a84f01f3a7b4eb12a85e061e37`
- **Provenance:** independent · **Language:** python
- **`eligible_for_n`:** `False` — candidate - awaiting operator ratification (protocol section 6 R2)
- **Caveat:** THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE its tests drive broker and transport boundaries that cannot be exercised for real in a unit suite — a rationale that references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the git object database with the detector NOT imported: 147 test files, 81 binding a mock primitive, 71 asserting on a mock-derived value, 71 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 73), rate 71/147 exact, 6325 days of history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's act at R2.

### `certbot-certbot`

- **Repository:** https://github.com/certbot/certbot
- **Pin:** `abf9d1b2e143c51fe1a2209a3b8be33e6a24267f`
- **Provenance:** independent · **Language:** python
- **`eligible_for_n`:** `False` — candidate - awaiting operator ratification (protocol section 6 R2)
- **Caveat:** THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE its tests drive an ACME client against a CA and against system configuration, neither reachable in a unit suite — a rationale that references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the git object database with the detector NOT imported: 97 test files, 73 binding a mock primitive, 54 asserting on a mock-derived value, 53 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 53), rate 53/97 exact, 5206 days of history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's act at R2.

### `conda-conda`

- **Repository:** https://github.com/conda/conda
- **Pin:** `ad60271d84099ea3bac642038560ecf0e2ad0a41`
- **Provenance:** independent · **Language:** python
- **`eligible_for_n`:** `False` — candidate - awaiting operator ratification (protocol section 6 R2)
- **Caveat:** THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE its tests drive a package solver against network and filesystem boundaries that are conventionally faked — a rationale that references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the git object database with the detector NOT imported: 170 test files, 55 binding a mock primitive, 29 asserting on a mock-derived value, 22 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 23), rate 11/85 exact, 5055 days of history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's act at R2.

### `getsentry-sentry-python`

- **Repository:** https://github.com/getsentry/sentry-python
- **Pin:** `064542dd2cbdbe0b11f1cda7f47d7d2920b0c38b`
- **Provenance:** independent · **Language:** python
- **`eligible_for_n`:** `False` — candidate - awaiting operator ratification (protocol section 6 R2)
- **Caveat:** THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE it is an SDK whose tests must substitute the HTTP transport that ships events — a rationale that references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the git object database with the detector NOT imported: 155 test files, 69 binding a mock primitive, 25 asserting on a mock-derived value, 25 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 28), rate 5/31 exact, 2977 days of history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's act at R2.

### `googleapis-google-auth-library-python`

- **Repository:** https://github.com/googleapis/google-auth-library-python
- **Pin:** `2ea24b03436765fa3cf279ce148482ff6332136b`
- **Provenance:** independent · **Language:** python
- **`eligible_for_n`:** `False` — candidate - awaiting operator ratification (protocol section 6 R2)
- **Caveat:** THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE its tests must substitute the token endpoint and the HTTP request callable — a rationale that references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the git object database with the detector NOT imported: 84 test files, 52 binding a mock primitive, 45 asserting on a mock-derived value, 45 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 46), rate 15/28 exact, 3440 days of history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's act at R2.

## Scope

This record ratifies nothing, fetches nothing, adjudicates nothing and spends no round. DF-13-5-A stays OPEN and UNSPENT. The protocol §2 External adjudicator stays UNFILLED (AI-E17-8), which is what blocks story 19.4 and is not addressed here. The gate stays BLOCKED and protocol_cleared stays False. No finding is judged TP or FP: a population size is not a yield forecast.
