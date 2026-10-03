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

Argus's other detectors — hardcoded secrets, tool-runner findings and most orphan
code — are **advisory**: they inform a reader and do not on their own move a
verdict to blocking. The exception is one narrow `orphan_code` case: a top-level
function or class whose name occurs nowhere else in the repository, in a module
the tests import, blocks (a token scan, not an AST fact). The demo's code is kept
to a single function that its test calls precisely so that case cannot fire: a
second, unused function would make the "fixed" run exit 2 as well. A wrong 🔴 is
the failure that gets a tool removed from a pipeline, so blocking is kept narrow.
The demo shows the main class that earns it.
