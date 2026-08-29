# Reporting a wrong finding

**This is the most valuable thing you can do with Agent-Argus.**

Agent-Argus's own accuracy has not been independently validated, and the ≥80% precision gate that
would lift that notice is **unevaluable rather than unmet** — run over the ratified corpus, the
corrected detector promoted no finding to verdict-eligible, so the precision ratio has an empty
denominator instead of a low value. That is why the instrument-status notice is on every run, and
why your disagreement is data rather than noise.

> 🔴 **Corrected 2026-08-29.** This page used to say: *"On 2026-08-17 we ran the first human
> adjudication of its blocking findings across five real repositories, and ~~none of the 31
> findings held up as a true positive~~."* Two things were wrong with that. It implied a measured
> precision of 0/31 when the corrected detector yields **no verdict-eligible findings at all** —
> a different and much weaker statement. And it presented the 31 judgements as an independent
> result when every one of them was authored by the tool's own author, which derives as
> `NOT_INDEPENDENT`. Struck, not deleted: the record that the claim was made is what makes the
> correction checkable.

A tool that fails your build on good code is worse than no tool. Tell us when it does.

---

## What to send

For each finding you think is wrong, the four things that make it actionable:

| Field | Example |
|---|---|
| **Rule id** | `vacuous_test_ast` |
| **Locator** | `tests/test_client.py:32` — file and line, exactly as Argus printed it |
| **Your call** | `FALSE POSITIVE` — Argus is wrong / `TRUE POSITIVE` — Argus is right / `BORDERLINE` — genuinely unclear |
| **Why, in one or two sentences** | "The assertions on lines 35-36 verify the outgoing payload, so the test is not vacuous." |

If you can, paste the flagged function. If the code is private, describe its shape instead —
how many assertions, whether mocks are involved, what it checks. **Never send us anything you
are not free to share.** Argus itself never transmits your source anywhere.

`BORDERLINE` is a real answer, not a cop-out. If you cannot decide, say so — a forced call is
worse than an honest "unclear."

---

## Also worth reporting

- **A crash or traceback** — include the full output and your Python version (`python -V`).
- **A wrong verdict** — Argus said `RELEASE_READY` on something you know is broken, or the
  reverse.
- **`INSUFFICIENT_COVERAGE` you cannot explain** — Argus refusing to grade code it should have
  been able to read.
- **Anything in the docs that is wrong or missing.** Two errors in this package were found that
  way and are struck above and in `QUICKSTART.md`; there are certainly others.

---

## What happens to your report

False positives you report become candidates for the validation corpus — the labelled set the
precision gate is measured over. The current corpus is narrow, and adjudication of it is not
independent: every live judgement was authored by the tool's own author. **Findings from code we
have never seen are worth far more than anything we can generate ourselves**, and adjudication by
someone outside the team is worth strictly more than adjudication by us.

If a report changes the measured precision, that shows up in the instrument-status notice, which
is derived rather than hand-written.

---

## Where to send it

**Open an issue:** https://github.com/Inan15/Agent-Argus/issues

Use the four fields above — rule id, locator, your call, and one or two sentences of why.
A title like `FP: vacuous_test_ast at tests/test_client.py:32` is ideal.

If the finding involves code you cannot share publicly, describe its shape instead: how many
assertions, whether mocks are involved, what it checks. That is still a useful report.
