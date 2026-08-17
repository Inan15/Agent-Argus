# ArgusAgent — Beta Quickstart

**Version 0.1.0-beta · Windows, macOS and Linux · no Python installation required**

ArgusAgent audits a code repository and gives you a deterministic, zero-LLM-token
**ship-readiness verdict**: whether there are blocking problems, and whether enough of the code
was actually examined to say so.

This is a **single self-contained executable**. You do not need Python, pip, git, or a GitHub
account.

---

## ⚠️ Read this before you weigh any verdict

> Instrument status: Argus's own finding precision has not been independently validated. Its findings rest on the Argus dogfood corpus, a self-audit of this repository with no human true-positive/false-positive adjudication behind it. This notice is removed only when Epic 13's human adjudication clears the >=80% precision gate; nothing else removes it.

Argus prints that on every run. Plainly: **this is a beta and we have not yet proven how often
Argus is right.** The first human adjudication of its blocking findings, on 2026-08-17, did not
clear our own accuracy gate, so the notice stays on.

That is precisely why we want you using it. **If Argus flags something you believe is fine, that
is a report we want** — see `FEEDBACK.md`.

This software is proprietary and licensed for evaluation only. See `LICENSE.txt`.

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

Argus reads your files locally. It never uploads your source, and on the default path it never
calls a language model.

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
| `NOT_READY_FOR_RELEASE` | `1` | At least one blocking finding. Argus names the file and line. |
| `INSUFFICIENT_COVERAGE` | `3` | Too little code could be examined for the verdict to mean anything. **Not a pass and not a fail** — Argus refusing to guess. |

The third is the deliberate design choice: a tool that cannot examine your code should say so
rather than award a pass.

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
> brings them in and enables the vacuous-test detector — the one whose precision measured poorly.
> Expect false positives there. On the default scope it does not run at all.

---

## 5. Languages

Ten languages ground out of the box: **Python, JavaScript, TypeScript, Go, Rust, Java, C, C++,
Ruby, PHP**.

A known limit, stated rather than left for you to discover: **C, C++, Ruby and Rust parse and are
graded, but currently yield no function/class definitions**, because the definition vocabulary
was written against Python's node names. Those files still count toward coverage; they just
cannot reach the deep grade.

---

## 6. Also in this package

- `FEEDBACK.md` — how to report a wrong finding. **The most useful thing you can do with this.**
- Issues and feedback: https://github.com/XAgents-ai/argus-agent-releases/issues
- `LICENSE.txt` — the Beta Evaluation Licence. Evaluation only; no redistribution.
- `THIRD-PARTY-NOTICES.txt` — bundled open-source components and their licences.
- `SHA256SUMS.txt` — checksum for the executable.

---

## Verified for this build

Measured on 2026-08-17 against this exact executable, on Windows x64 with no Python
installation on PATH:

- `argus.exe --help` resolves and prints the invocation contract
- a full audit of a sample Python project runs to a verdict and exit code 0
- the instrument-status notice prints on every run
- the executable contains no plain-text Python source

**Platform:** builds are published for Windows x64, macOS and Linux x64. On macOS and Linux the
executable is named `argus` (no `.exe`); make it executable with `chmod +x argus` and run it as
`./argus audit .`.
