# Examples

## `demo.py` — Agent-Argus in 90 seconds

```bash
python examples/demo.py
```

The whole point of the tool in one arc: a repository whose test suite is **green
under pytest**, which Argus then **blocks** (`NOT_READY_FOR_RELEASE`, exit 2)
because the test asserts a value it invented rather than the value the code
returned — and which goes **green again** (`RELEASE_READY`, exit 0) once the test
is fixed to assert the real result.

The planted defect is the one worth showing: the test *does* call the code under
test, so a naive "is the SUT reached?" check passes. It then builds a `Mock`,
configures a return value, and asserts that. It is green on every CI in the
world, and it proves nothing.

**Hermetic.** Everything is built from bytes inside `demo.py` — no network, no
downloaded fixture, no corpus member read, nothing cached. It writes to a
temporary directory and cleans up after itself.

**Nothing is pre-recorded.** Every figure it prints comes from a run performed
while you watch. No expected output is baked into the file, deliberately: a demo
with hardcoded output is a screenshot, and screenshots rot silently while
everyone keeps quoting them. The script exits non-zero if the behaviour it
narrates does not actually happen, so it doubles as a small end-to-end check of
the claim the README makes on its front page.

Requires `git` on `PATH` and the `argus` package importable — `pip install -e .`
from a clone, or the published pin from the README.

### What it deliberately does not show

Argus's other detectors — orphan code, hardcoded secrets, tool-runner findings —
are **advisory by contract**: they inform a reader and cannot on their own move a
verdict to blocking. That is a design decision rather than an omission, and it is
the reason this demo is trustworthy: a wrong 🔴 is the failure that gets a tool
removed from a pipeline, so only an AST-corroborated finding is allowed to block
a release. The demo shows the one class that earns it.
