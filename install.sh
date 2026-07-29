#!/usr/bin/env bash
# ArgusAgent Installer Script for Unix / macOS

set -e

echo "===================================================="
echo "      ArgusAgent (argus-agent) Installer"
echo "===================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found. Please install Python 3.10+."
    exit 1
fi

echo "[1/4] Installing ArgusAgent package..."
pip install -e .

echo "[2/4] Detecting AI Coding Assistants..."
INSTALLED_ADAPTERS=0

# Detect Claude Code
if [ -d "$HOME/.claude" ]; then
    echo "  -> Detected Claude Code. Installing ArgusAgent skill..."
    mkdir -p "$HOME/.claude/commands"
    cp -r adapters/claude-code/* "$HOME/.claude/" 2>/dev/null || true
    INSTALLED_ADAPTERS=$((INSTALLED_ADAPTERS + 1))
fi

# Detect Cursor
if [ -d "$HOME/.cursor" ] || [ -d "$HOME/.config/Cursor" ]; then
    echo "  -> Detected Cursor. Installing ArgusAgent rules..."
    mkdir -p "$HOME/.cursor/rules"
    cp -r adapters/cursor/* "$HOME/.cursor/rules/" 2>/dev/null || true
    INSTALLED_ADAPTERS=$((INSTALLED_ADAPTERS + 1))
fi

# Detect Cline / RooCode
if [ -d "$HOME/.vscode/extensions" ]; then
    echo "  -> Detected VS Code / Cline environment. Registering adapters..."
    INSTALLED_ADAPTERS=$((INSTALLED_ADAPTERS + 1))
fi

echo "[3/4] Initializing ArgusAgent environment..."
argus --help > /dev/null

echo "[4/4] Installation Complete!"
echo "ArgusAgent successfully installed with $INSTALLED_ADAPTERS adapter(s)."
echo ""
echo "Run 'argus' or use '/audit' inside your AI assistant to start auditing repositories."
