#!/usr/bin/env bash
# ArgusAgent Uninstaller Script
#
# Story 12.7 / FR35 — this now removes the placed command assets BEFORE removing the tool
# that knows how to find them. Until 2026-08-15 it ran `pip uninstall` only, so every file
# `install.sh` / `install.ps1` had copied stayed in the user's home directory forever: an
# install path with no matching removal path. `argus install-commands --remove` deletes
# exactly the files this project wrote — recognised by the marker each asset carries — and
# leaves a file of the same name that the user wrote themselves entirely alone.

set -e

echo "Removing the placed ArgusAgent assistant commands..."
# Ordered deliberately: `--remove` needs the installed CLI, so it runs FIRST. A failure here
# must not stop the package removal, so it is tolerated and reported.
argus install-commands --remove || echo "  (no placed commands were removed; continuing)"

echo "Uninstalling ArgusAgent (argus-agent)..."
pip uninstall -y argus-agent 2>/dev/null || true
echo "ArgusAgent uninstalled successfully."
