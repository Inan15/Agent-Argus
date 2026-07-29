#!/usr/bin/env bash
# ArgusAgent Uninstaller Script

set -e

echo "Uninstalling ArgusAgent (argus-agent)..."
pip uninstall -y argus-agent 2>/dev/null || true
echo "ArgusAgent uninstalled successfully."
