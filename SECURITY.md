# Security Policy

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

Report privately through GitHub:

1. Go to the [Security tab](https://github.com/Inan15/Agent-Argus/security) of this repository.
2. Choose **Report a vulnerability** to open a private security advisory.

This keeps the report visible only to you and the maintainers until a fix exists.

> **Maintainer note.** Private vulnerability reporting must be switched on for this repository
> (Settings → Code security and analysis → Private vulnerability reporting). If the button above is
> not present, that setting has not been enabled yet, and this document is describing an intention
> rather than a working channel — please open an issue saying only *"security contact needed"*, with
> no detail, and a maintainer will arrange a private channel.

### What to expect

This is a small project maintained part-time. Concretely, rather than a promise nobody can keep:

- an acknowledgement when a maintainer next reads the queue — realistically within a week;
- an assessment of whether it is in scope (below) and, if so, what the fix looks like;
- credit in the advisory and the changelog, unless you prefer otherwise.

If a report goes unanswered for two weeks, please escalate by opening a public issue that says only
that a private report is awaiting response — no technical detail.

## Supported versions

Only the latest release receives fixes. There is no long-term support branch.

| Version | Supported |
|---|---|
| 1.0.x | ✅ |
| < 1.0 | ❌ |

## What is in scope

Agent-Argus reads source code and writes artifacts, so the security surface is mostly about what it
reads, what it emits, and what it reaches. In scope:

- **Leakage into output.** Argus is designed never to write source bytes, secret values or absolute
  host paths into its artifacts, its stdout contract or its error messages (NFR-S1/S2). A path that
  does is a vulnerability, including in an error or degradation path.
- **Unexpected egress.** The default audit path performs **no network I/O at all** (NFR-S6); the
  LLM-backed deep pass is opt-in behind `--deep-audit` and discloses itself before the first byte
  leaves. Any egress on the default path is a vulnerability.
- **Workspace containment.** Argus should read the repository it was pointed at and write only under
  `.argus/` and any explicitly requested report directory. Escaping that is in scope.
- **Untrusted-input handling.** Argus parses arbitrary third-party source. Crashes are bugs;
  anything reaching code execution, path traversal or resource exhaustion from repository content is
  a vulnerability.
- **The packaged GitHub Action and the release workflows.** Shell-injection through workflow inputs,
  or a supply-chain weakness in how artifacts are built and attached, is in scope.
- **The MCP server.** `argus-mcp` speaks JSON-RPC over stdio; protocol handling issues are in scope.

## What is not in scope

- **A finding Argus missed, or a finding you disagree with.** That is a detector accuracy issue, not
  a vulnerability — please open a normal issue, and see [CONTRIBUTING.md](CONTRIBUTING.md) job 1.
  These are genuinely wanted; they are just not security reports.
- **Vulnerabilities in a repository you audited.** Argus reports on other people's code; a finding
  about that code belongs to that code's maintainers.
- **Weaknesses in third-party dependencies** without a demonstrated path through Argus. Report those
  upstream; tell us if Argus's usage makes them reachable.
- **The precision of Argus's own findings.** This is disclosed rather than hidden: Argus's finding
  precision has not been independently validated, and every user-facing surface says so. That is a
  known, published limitation, not a vulnerability.

## A note on what Argus does not claim

Argus issues **negative assurance**: the absence of *detected* blocking findings within an
*assessed* scope. It is not an attestation of correctness, and a `RELEASE_READY` verdict is never a
statement that code is secure. Treating an Argus verdict as a security guarantee would be a
misreading of the tool, and the tool says so in its own output.
