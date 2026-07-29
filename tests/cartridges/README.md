# APAA defect cartridges

A **cartridge** is a minimal, self-contained fixture repository carrying a known,
planted condition with a documented **golden outcome**. The Epic-1 capstone
(story 1.7) ships cartridge #1 (the vacuous-test signature demo) plus a clean
true-negative control. Story 6.5 extends this directory ADDITIVELY into the
parametrized multi-cartridge self-audit harness (+ hidden holdout); the layout
here is designed so 6.5 can drop in more cartridges with no refactor.

## Layout (so 6.5 can extend additively)

Each cartridge is a directory under `tests/apaa/cartridges/<id>/` whose files are
stored as `*.py.txt` **templates** (NOT `.py`, so the main pytest run never
collects/imports them). The test harness
(`tests/apaa/cartridges/_cartridge.py::stage_cartridge`) copies the templates
into a fresh temp directory, strips the `.txt` suffix, `git init`s, commits once,
and returns `(repo_path, commit_sha)`. Staging into a fresh git repo per run is
the **cartridge-pinning approach** (LOCKED): the loader (`load_repo_at_commit`)
requires a clean working tree at a resolved pin, and a fresh single-commit repo
satisfies that deterministically — the audited byte content is fixed by the
committed templates, so the same cartridge audited twice yields byte-identical
`.apaa/` output (AC5 / NFR-P1).

## Cartridge #1 — `vacuous_basic` (the signature demo)

- `src/calculator.py` — a clean SUT module (`compute_total` / `apply_discount`).
- `tests/test_calculator.py` — the **planted vacuous test**: it calls the real
  SUT (`compute_total([1,2,3])`) but asserts a **Mock's** configured return value,
  never the SUT output. It is flagged by BOTH the heuristic AND the Tier-A
  vacuous-path AST subset → `rule_id="vacuous_test_ast"`,
  `depth_supported=AUDITED_SHALLOW` → **verdict-eligible**.

**Coverage grading (clears the 20% floor — LOCKED).** The pipeline grades a
cleanly-parsed Python NON-test file `audited_deep` (the 1.2 claim-emitted deep
path). Here: `src/calculator.py` → `audited_deep` (deep numerator);
`tests/test_calculator.py` → `audited_shallow`. deep-% = 1/2 = 50% ≥ 20% floor.

**Golden outcome (pinned by `test_pipeline_signature_demo.py`):**
verdict `NOT_READY_FOR_RELEASE` (BLOCKED 🔴), exit code **2**, ≥1
`vacuous_test_ast` finding present and sorted first. This is the
`GitHub green · Sonar green · APAA 🔴 tests appear vacuous` signature demo.

## Clean control — `clean_control` (the false-accusation floor)

- `src/adder.py`, `src/multiplier.py` — two clean SUT modules (both `audited_deep`).
- `tests/test_math.py` — a genuine, well-asserting test (no mocks; asserts real
  SUT output) → `audited_shallow`, NOT flagged (the moat).

deep-% = 2/3 ≈ 66.7% ≥ 60%, zero blocking findings → **`RELEASE_READY`** (exit 0).
Proves APAA does not emit a false 🔴 on honest tests.
