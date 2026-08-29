# Agent-Argus — Quickstart

**Version 1.0.0 · Windows, macOS and Linux · no Python installation required**

Agent-Argus audits a code repository and gives you a deterministic, zero-LLM-token
**ship-readiness verdict**: whether there are blocking problems, and whether enough of the code
was actually examined to say so.

This is a **single self-contained executable**. You do not need Python, pip, git, or a GitHub
account.

---

## ⚠️ Read this before you weigh any verdict

**Agent-Argus's finding precision has not been independently validated.** The tool prints a
notice saying so on every run, generated from a constant in the code rather than copied by hand
— so it is deliberately not transcribed here, where a copy could drift out of step with what
your binary actually says. Read what your own run prints.

What it means, plainly: the audit is deterministic and reproducible by construction, but nobody
outside the team has checked how often a finding is *right*. **Treat a finding as a prompt to
look, not as a verdict.**

The ≥80% precision gate that would remove the notice has **not been evaluated** — which is not
the same as evaluated and missed. When the corrected detector was run over the ratified corpus,
no finding was promoted to verdict-eligible, so the precision ratio has an empty denominator
rather than a low value. Both halves of that matter: the tool is not hiding a bad score, and it
is not claiming a good one either.

That is precisely why we want you using it. **If Agent-Argus flags something you believe is fine,
that is a report we want** — see `FEEDBACK.md`.

Licensed under the **MIT Licence**. See `LICENSE.txt`.

---

## 1. Run it

1. Download `argus.exe`.
2. Open PowerShell or Command Prompt in the folder containing it.
3. Audit a project:

```powershell
.\argus.exe audit C:\path\to\my-project
```

Or from inside your project folder:

```powershell
C:\path\to\argus.exe audit .
```

Check it starts at all:

```powershell
.\argus.exe --help
```

> **Windows SmartScreen.** The executable is unsigned, so Windows may warn on first run. Choose
> *More info → Run anyway*, or verify the checksum in `SHA256SUMS.txt` first:
> `Get-FileHash .\argus.exe -Algorithm SHA256`

Argus reads your files locally. It never uploads your source, and on the default path it makes
**no network calls at all**.

---

## 2. What a run looks like

```
Ship-readiness: READY - no blocking problems found, and enough of the code was
examined deeply to say so.
  - Verdict-blocking findings: 0
  - Deeply examined: 1 of 1 assessed files
  - Next: repository satisfies all release gates

verdict=RELEASE_READY deep_ratio=1/2 blocking_findings=0 scope=application
```

---

## 3. Reading the result

| Verdict | Exit code | Meaning |
|---|---|---|
| `RELEASE_READY` | `0` | No blocking findings, and enough code was examined deeply to say so. |
| `NOT_READY_FOR_RELEASE` | `2` | At least one blocking finding. Argus names the file and line. |
| `INSUFFICIENT_COVERAGE` | `3` | Too little code could be examined for the verdict to mean anything. **Not a pass and not a fail** — Argus refusing to guess. |

> 🔴 **Corrected 2026-08-29.** This table previously gave `NOT_READY_FOR_RELEASE` as exit
> ~~`1`~~. It is **`2`**, as `argus/reports/plain_english.py` has always defined it. If you wired
> a CI step on `exit 1`, it never caught a blocking finding — `1` is the *crash* exit code, a
> different event entirely. Struck rather than deleted, because anyone who scripted against the
> old number needs to see that it moved.

The third verdict is the deliberate design choice: a tool that cannot examine your code should
say so rather than award a pass.

**"Deeply examined"** means the file parsed cleanly, contains at least one real function or
class, and every deterministic detector ran over it. It is a structural grade, not a claim that
anything understood your intent.

---

## 4. Useful flags

```powershell
.\argus.exe audit . --report-dir .\argus-reports    # write markdown reports
.\argus.exe audit . --coverage-scope repository     # include test files in scope
.\argus.exe audit . --help                          # everything else
```

> **On `--coverage-scope repository`.** By default Argus holds test files out of scope. This flag
> brings them in and enables the vacuous-test detector. Expect false positives there; it is the
> detector whose accuracy is least established. On the default scope it does not run at all.

---

## 5. Languages

Ten languages ground out of the box: **Python, JavaScript, TypeScript, Go, Rust, Java, C, C++,
Ruby, PHP**.

A known limit, stated rather than left for you to discover: **C, C++ and Ruby parse cleanly and
are graded, but currently yield no function or class definitions**, because the definition
vocabulary in `argus/index/ast_index.py` does not carry those grammars' node names. Those files
still count toward coverage; they just cannot reach the deep grade.

> 🔧 **Corrected 2026-08-29.** This list previously also named ~~Rust~~. Measured on this
> version — one single-definition file per language, through `build_ast_index` — Rust returns
> **1** definition (`fn_item` and `struct_item` are both in the vocabulary), while C, C++ and
> Ruby each return **0** with `parse_failed=False`. The limit is narrower than it was written.

---

## 6. Also in this package

- `FEEDBACK.md` — how to report a wrong finding. **The most useful thing you can do with this.**
- Issues and feedback: https://github.com/Inan15/Agent-Argus/issues
- `LICENSE.txt` — the MIT Licence. This is open-source software.
- `THIRD-PARTY-NOTICES.txt` — bundled open-source components and their licences.
- `SHA256SUMS.txt` — checksum for the executable.

---

## Verified for this build

> 🔧 **Re-scoped 2026-08-29.** This section used to say *"Measured on 2026-08-17 against this
> exact executable."* That was true of the `0.1.0-beta` Windows binary it shipped in, and it was
> carried into the 1.0.0 package unchanged — so it described a different executable from the one
> it travelled with.

These checks run against **this** binary, on the runner that produced it, and they fail the build
rather than being asserted afterwards:

- the executable exists at the expected path and `--help` resolves;
- a full `audit` run reaches a `verdict=` line;
- the instrument-status notice is present in that run's output.

All three are enforced in `.github/workflows/build-binaries.yml`; a binary failing any of them is
never packaged. What is **not** established for this build: an end-to-end audit of a third-party
project on a machine with no Python on PATH. That was measured for the beta and has not been
re-measured here.

**Platform:** builds are published for Windows x64, macOS arm64 and Linux x64. On macOS and Linux
the executable is named `argus` (no `.exe`); make it executable with `chmod +x argus` and run it
as `./argus audit .`.
