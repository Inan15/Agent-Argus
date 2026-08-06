# ArgusAgent (`argus-agent`) 🛡️👁️

> **The Agent-First, Deterministic Repository Audit & Assurance Engine**

`ArgusAgent` combines the high-precision **APAA (AI Project Assurance Audit)** Python verification engine with the vendor-portable **RAM (Repository Audit Method)** framework. Named after *Argus Panoptes* — the mythological 100-eyed all-seeing guardian — `ArgusAgent` provides multi-agent, cross-subsystem vigilance over codebases with zero blind spots.

> **Integrating `argus audit` into a pipeline?** Every consumer-visible change to the exit codes, artifact schemas, defaults, rendered strings and public API — and what deliberately did *not* change — is recorded in **[CHANGELOG.md](CHANGELOG.md)**.

---

## 🌟 Key Features

1. **Deterministic Assurance Kernel (`argus/`)**:
   - **Pure Verdict Gate**: Mathematical, zero-LLM-token release readiness calculation (`RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`).
   - **AST Indexing & Grounding**: `tree-sitter` AST parsing and structural search validating deep audit claims against real code definitions.
   - **Graph-Derived Partitioning**: Auto-partitions large repositories into bounded audit units ($\le 40$ files / $15\text{k}$ LOC) to eliminate context rot.
   - **Content-Addressed Memoization**: Byte-identical execution across hosts via canonical JSON serialization and full closure hashing.
   - **Prosecutor Cut-Edge Pass**: Adversarial second pass ensuring seam-spanning defects across partitions move the verdict to $\color{red}{\text{NOT READY}}$.
   - **Defect Cartridges & Self-Audit Harness**: CI-blocking true-negative clean control cartridges and hidden holdouts.

2. **RAM Workflow Framework (`audit/`, `phases/`, `adapters/`, `templates/`)**:
   - **Vendor & Agent Adapters**: Native slash commands and skills for **Claude Code**, **Cursor**, **Cline**, **RooCode**, **Codex CLI**, **Gemini CLI**, and **Windsurf**.
   - **12 Audit Phases**: Guided markdown workflows from Orientation (`00`) to Verdict (`11`).
   - **12 Developer Report Templates**: Rich, human-readable markdown reporting for Architecture, Security, Performance, Requirements, and Risk.

---

## 🚀 Quickstart & Installation

### Single Command Installation

```bash
# Unix / macOS
./install.sh

# Windows PowerShell
.\install.ps1
```

Or via Python pip:

```bash
pip install -e .
```

---

## 💻 Slash Commands & Usage

When installed, `ArgusAgent` registers slash commands in your AI coding assistant (Claude Code, Cursor, Cline, etc.):

```bash
/audit                  # Run full repository audit pipeline
/audit repo             # Audit repository intake & partitioning
/audit architecture     # Audit architectural integrity & call graphs
/audit security         # Scan secrets, containment, and entropy
/audit subsystem <name> # Audit specific subsystem (e.g. auth, payments)
/audit report           # Generate 12 developer markdown reports
/audit resume           # Resume interrupted audit from on-disk state
```

From terminal CLI:

```bash
argus --budget 500 --materiality critical
```

---

## 📁 Repository Structure

```
ArgusAgent/
├── argus/                 # Standalone Python Assurance Engine Core
│   ├── intake/            # Repository intake & stack detection
│   ├── index/             # tree-sitter AST indexer & partitioner
│   ├── ledger/            # Coverage ledger & depth semantics
│   ├── detectors/         # Vacuous test, secret scan, orphan code, radon
│   ├── verdict/           # Pure verdict gate & Prosecutor pass
│   ├── store/             # Canonical serializer & envelope writer
│   ├── cache/             # Content-addressed memoization
│   ├── audit/             # LLM dispatch port & provider adapters
│   ├── cost/              # Budget governor & resumability
│   ├── governance/        # Escalation manager & decision records
│   └── precision/         # Ground-truth replay harness
├── audit/                 # RAM Skill definitions & Evidence Models
├── phases/                # 12 Audit Phase Markdown Guides (00 to 11)
├── adapters/              # Vendor Adapters (Claude Code, Cursor, Cline, etc.)
├── templates/             # 8 Developer Report Templates
├── tests/                 # Comprehensive Test Suite & Defect Cartridges
├── pyproject.toml         # Package definition
├── install.sh / .ps1      # Auto-installer scripts
└── README.md              # Project documentation
```

---

## 🛡️ License

MIT License. See [LICENSE](LICENSE) for details.
