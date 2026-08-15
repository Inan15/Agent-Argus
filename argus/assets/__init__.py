"""Packaged DATA the distribution ships beside its code — never executable authority.

Story 12.7 / FR35 (second half). ``architecture.md`` §A states the rule this package
exists to obey: *"Command assets are data, not code. They instruct a host to invoke the
CLI. They introduce no execution path of their own"*, and it reserved this very path
(``argus/assets/commands/``) for them before anything was written here.

Why this is a real Python package rather than a bare directory
--------------------------------------------------------------
Because the assets must be readable **from a built distribution**, and the only
supported way to do that is :mod:`importlib.resources` over an importable package.
``__file__`` path arithmetic — ``Path(__file__).parent / "commands"`` — happens to work
from a source checkout and breaks the moment the distribution is zip-imported, relocated
or vendored. The packaging itself needs no configuration: ``flit_core`` walks the whole
``argus`` module directory and ships every file in it except ``__pycache__``/``*.pyc``
(``flit_core/common.py::Module.iter_files``), so a ``.md`` committed here reaches the
wheel with no ``pyproject.toml`` change — and reaches the SDIST only once it is
``git add``-ed, because the sdist is built from VCS-tracked files. Both are asserted
(``tests/test_command_assets.py``, ``tests/test_built_distribution.py``).

What may live here
------------------
Inert data. No module under ``argus/assets/**`` may execute anything, open a socket,
read a credential or carry a transcribed copy of a pinned constant — in particular the
FR34 instrument-status disclosure, which is RENDERED into an asset at install time from
``argus/verdict/negative_assurance.py`` and is never committed here (AI-E9-7).
"""

from __future__ import annotations

__all__: list[str] = []
