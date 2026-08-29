# Sprint Change Proposal — Epic 20: Post-V1 Capabilities

**Date:** 2026-08-28  
**Author:** Developer Agent / Amelia  
**Project:** ArgusAgent  
**Approved By:** User (Incremental Approval 2026-08-28)  

---

## 1. Issue Summary

Following the successful delivery and retrospective sign-off of Epics 1 through 19, ArgusAgent reached complete V1 status as a headless assurance audit tool. 

To expand ArgusAgent into post-V1 capabilities, the project is initiating **Epic 20: Post-V1 Capabilities — Remediation, IDE Diagnostics & Multi-Language Expansion**. This change addresses user requirements for real-time IDE feedback, automated remediation diff generation, and extended AST parsing for TypeScript/JavaScript, Go, and Java.

---

## 2. Impact Analysis

- **Epic Impact**: Appends **Epic 20** (4 new stories, 1 retrospective). Does NOT alter or invalidate completed Epics 1–19.
- **Story Impact**: 4 new stories created: `20.1`, `20.2`, `20.3`, `20.4`.
- **Artifact Impacts**:
  - `E-PRD/addendum.md`: Appends FR38 (Remediation Proposals), FR39 (LSP/IDE Surface), FR40 (Multi-Language AST Expansion).
  - `architecture.md`: Appends component specs for `argus.remediation`, `argus.adapters.lsp`, and `argus.parsers.extended`.
  - `epics.md`: Appends Epic 20 definition and story breakdown.
  - `sprint-status.yaml`: Appends `epic-20` and constituent stories with status `backlog`.
- **Technical Impact**: Purely additive. Preserves all core verification pipeline invariants, precision thresholds, and test suites.

---

## 3. Recommended Approach

- **Selected Approach**: **Direct Adjustment (Additive Epic 20)**
- **Scope Classification**: **Moderate** (Backlog expansion and artifact synchronization)
- **Rationale**: Expanding scope via a dedicated post-v1 epic maintains 100% backward compatibility with V1 contracts while introducing new developer-facing value cleanly.

---

## 4. Detailed Change Proposals (Approved)

### PRD Extensions (`E-PRD/addendum.md`)
- **FR38**: Automated Defect Remediation Proposals
- **FR39**: IDE & LSP Diagnostic Surface
- **FR40**: Multi-Language AST Expansion (TypeScript/JS, Go, Java)

### Architecture Spine Updates (`architecture.md`)
- **`argus.remediation`**: Remediation Engine for code transformation diffs.
- **`argus.adapters.lsp`**: Diagnostic Adapter for JSON-RPC 2.0 LSP diagnostics.
- **`argus.parsers.extended`**: Tree-sitter parsers for TypeScript, Go, and Java.

### Epic 20 Breakdown (`epics.md`)
- **Story 20.1**: Multi-Language AST Parsers (`argus.parsers.extended`)
- **Story 20.2**: Defect Remediation Engine (`argus.remediation`)
- **Story 20.3**: LSP Diagnostic Adapter (`argus.adapters.lsp`)
- **Story 20.4**: Post-V1 Integration & Verification Suite

### Tracker Updates (`sprint-status.yaml`)
- `epic-20`: `backlog`
- `20-1-multi-language-ast-parsers`: `backlog`
- `20-2-defect-remediation-engine`: `backlog`
- `20-3-lsp-diagnostic-adapter`: `backlog`
- `20-4-post-v1-integration-verification`: `backlog`
- `epic-20-retrospective`: `optional`

---

## 5. Implementation Handoff

- **Scope**: Moderate
- **Handoff Recipient**: Product Owner / Developer Agent
- **Next Workflow Steps**:
  1. Append Epic 20 definitions to `epics.md` and `E-PRD/addendum.md`.
  2. Register `epic-20` in `sprint-status.yaml`.
  3. Execute `/bmad-create-story` for Story 20.1 to begin development.
