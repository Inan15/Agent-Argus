# docs/

Project-knowledge root for ArgusAgent. Resolved from `modules.bmm.project_knowledge`
in `_bmad/config.toml`.

BMad skills read from and write to this directory:

- `bmad-document-project` (`[DP]`) — brownfield codebase documentation
- `bmad-generate-project-context` (`[GPC]`) — `project-context.md` AI rules file
- `bmad-agent-tech-writer` (`[WD]`, `[EC]`) — authored docs and concept explanations
- `bmad-domain-research` / `bmad-technical-research` — research reports

~~Currently empty apart from this file.~~ (§3.4 struck, not deleted — corrected 2026-08-15
by Story 12.8. The sentence became false the moment `first-run.md` landed here.)

**This directory now has two tenants, and the co-tenancy is stated rather than left to be
discovered** (Story 12.8 / DN-1):

- **`first-run.md` — CONSUMER-FACING.** The first-run page: install, first audit, reading the
  ledger, what each verdict means. It is linked from the root `README.md`, registered as a
  published surface in `tests/test_release_surface_honesty.py`, and every `argus …` command
  line on it is parsed by the real CLI parser in `tests/invocation_sources.py`'s corpus. It is
  **not** packaged in the wheel (`flit_core` packages `argus/**` only), so the README link is
  its whole delivery mechanism. Three homes were weighed — a root `FIRST-RUN.md` competes with
  `README.md` for the first thing a reader sees, and a packaged asset under `argus/assets/`
  would blur the "command assets with no execution authority" boundary Story 12.7 spent a whole
  story drawing — and `epics.md:2421` names this one. **Please do not "tidy" it into
  `_bmad-output/`: it is a product surface, not a planning artifact, and moving it breaks a
  link a consumer follows.**
- **everything else — BMad tooling**, as described above.

The v1.0.0 planning and implementation record lives separately, under
`_bmad-output/design-artifacts/ArgusAgent/`.
