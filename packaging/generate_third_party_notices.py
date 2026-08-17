"""Emit THIRD-PARTY-NOTICES.txt for a release package, from installed metadata.

Written to stdout so the build workflow can redirect it into the package. DERIVED, never
hand-maintained: a hand-written notices file goes stale the first time a dependency moves,
and this repository has a named defect class for published figures that are typed rather
than measured.

Build tooling that is not shipped inside the executable is excluded by name below, so the
file lists what the binary actually bundles rather than whatever happened to be in the
build environment.
"""

from __future__ import annotations

import importlib.metadata as md

#: Present in the build environment, NOT bundled into the executable. Excluded by name with
#: a reason rather than by a silent filter.
_BUILD_ONLY = {
    "pyinstaller": "build tool",
    "pyinstaller-hooks-contrib": "build tool",
    "altgraph": "PyInstaller dependency",
    "pefile": "PyInstaller dependency (Windows)",
    "pywin32-ctypes": "PyInstaller dependency (Windows)",
    "macholib": "PyInstaller dependency (macOS)",
    "setuptools": "build tool",
    "wheel": "build tool",
    "packaging": "build tool",
    "pip": "build tool",
}

_HEADER = """ArgusAgent — THIRD-PARTY NOTICES
============================================================

This product bundles the third-party components listed below. Each remains licensed
under its own terms, which are unaffected by the ArgusAgent Beta Evaluation Licence.
"""

_FOOTER = """------------------------------------------------------------
Each component above is used under its own licence, which is unchanged by the
ArgusAgent Beta Evaluation Licence. Licence names are taken from each package's
published metadata.

If you need the full licence text for any component, or believe an attribution here
is incomplete or wrong, please open an issue and we will correct it:
https://github.com/XAgents-ai/argus-agent-releases/issues
"""


def _licence_of(dist: md.Distribution) -> str:
    """The licence name, preferring the classifier over a pasted licence body."""
    declared = dist.metadata.get("License") or ""
    if declared and len(declared) <= 60:
        return declared
    classifiers = [
        c for c in (dist.metadata.get_all("Classifier") or []) if c.startswith("License ::")
    ]
    if classifiers:
        return classifiers[0].split("::")[-1].strip()
    return declared[:60] if declared else "see project metadata"


def main() -> int:
    rows: list[tuple[str, str, str, str]] = []
    for dist in md.distributions():
        name = dist.metadata["Name"]
        if not name or name.lower() in _BUILD_ONLY:
            continue
        rows.append((name, dist.version, _licence_of(dist), dist.metadata.get("Home-page") or ""))
    rows.sort(key=lambda row: row[0].lower())

    print(_HEADER)
    for name, version, licence, home in rows:
        print(f"{name} {version}")
        print(f"    Licence: {licence}")
        if home:
            print(f"    Home:    {home}")
        print()
    print(_FOOTER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
