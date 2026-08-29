#!/usr/bin/env bash
# Agent-Argus Installer Script for Unix / macOS
#
# Story 12.7 / FR35 — THIS SCRIPT NO LONGER PLACES ANY FILE ITSELF. It installs the
# distribution and then delegates to `argus install-commands`, which is the ONE placement
# mechanism (AR7 / architecture §3.3).
#
# What was here until 2026-08-15, and why it went: this script created
# "$HOME/.claude/commands" and then copied `adapters/claude-code/*` into "$HOME/.claude/" —
# BESIDE the directory a command is actually read from — so the commands it reported
# installing never appeared. `install.ps1` was broken in the identical way, and the Cline
# branch incremented its counter and copied nothing at all. A second copy of a placement
# rule drifts in one of the two; there is now only one, it ships in the wheel, and it is
# covered by the verification area `TC-ArgusAgent-ASSETS-001`.

set -e

echo "===================================================="
echo "      Agent-Argus (argus-agent) Installer"
echo "===================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found. Please install Python 3.10+."
    exit 1
fi

echo "[1/4] Installing Agent-Argus package..."
pip install -e .

echo "[2/4] Verifying the CLI..."
argus --help > /dev/null

echo "[3/4] Placing the packaged assistant commands..."
# Every supported host whose configuration directory is detected. `--dest` is not passed,
# so the destination is your home directory. Add `--dry-run` to see the plan first, and
# `--remove` (or ./uninstall.sh) to take exactly these files away again.
argus install-commands

echo "[4/4] Installation Complete!"
echo ""
echo "Run 'argus audit .' from a terminal, or use the /argus-audit commands inside a supported AI assistant."
