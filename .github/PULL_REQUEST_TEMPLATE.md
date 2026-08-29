## What this changes

## Why

Link the issue if there is one.

## What you measured

Not what you changed — what you *ran*, and what it said. Paste output where it helps.

## Checklist

- [ ] `pytest tests/` green
- [ ] `mypy argus` clean
- [ ] `bandit -r argus --severity-level medium` exits 0
- [ ] No test assertion was weakened to make this land (see CONTRIBUTING.md → House rules)
- [ ] Corrections to existing claims are struck and dated, not deleted (§3.4)
- [ ] Any derived value is derived, not hand-typed
- [ ] Mechanical regenerations are in their own commit
