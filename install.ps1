# ArgusAgent Installer Script for Windows PowerShell
#
# Story 12.7 / FR35 — THIS SCRIPT NO LONGER PLACES ANY FILE ITSELF. It installs the
# distribution and then delegates to `argus install-commands`, which is the ONE placement
# mechanism (AR7 / architecture §3.3).
#
# What was here until 2026-08-15, and why it went: this script created a `commands`
# directory under the Claude Code configuration root and then copied `adapters\claude-code\*`
# into the root itself — BESIDE the directory a command is actually read from — so the
# commands it reported installing never appeared. `install.sh` was broken in the identical
# way. A second copy of a placement rule drifts in one of the two; there is now only one, it
# ships in the wheel, and it is covered by the verification area `TC-ArgusAgent-ASSETS-001`.

$ErrorActionPreference = "Stop"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "      ArgusAgent (argus-agent) Installer" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/4] Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Error: Python 3.10+ is required but python command was not found."
    exit 1
}

# 2. Install Package
Write-Host "[2/4] Installing ArgusAgent package locally..." -ForegroundColor Yellow
pip install -e .

# 3. Verify CLI
Write-Host "[3/4] Verifying CLI installation..." -ForegroundColor Yellow
argus --help | Out-Null

# 4. Place the packaged assistant commands — every supported host whose configuration
# directory is detected. `--dest` is not passed, so the destination is your home directory.
# Add `--dry-run` to see the plan first, and `--remove` to take exactly these files away.
Write-Host "[4/4] Placing the packaged assistant commands..." -ForegroundColor Yellow
argus install-commands

Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host " ArgusAgent installation complete!" -ForegroundColor Green
Write-Host " Run 'argus audit .' or use the /argus-audit commands in a supported AI assistant." -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
