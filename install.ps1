# ArgusAgent Installer Script for Windows PowerShell

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

# 3. Detect & Install Adapters
Write-Host "[3/4] Detecting AI Coding Assistants..." -ForegroundColor Yellow
$userHome = [System.Environment]::GetFolderPath('UserProfile')
$adaptersCount = 0

# Claude Code
$claudeDir = Join-Path $userHome ".claude"
if (Test-Path $claudeDir) {
    Write-Host "  -> Detected Claude Code. Installing skills..." -ForegroundColor Green
    $cmdDir = Join-Path $claudeDir "commands"
    New-Item -ItemType Directory -Force -Path $cmdDir | Out-Null
    Copy-Item -Path "adapters\claude-code\*" -Destination $claudeDir -Recurse -Force
    $adaptersCount++
}

# Cursor
$cursorDir = Join-Path $userHome ".cursor"
if (Test-Path $cursorDir) {
    Write-Host "  -> Detected Cursor. Installing rules..." -ForegroundColor Green
    $rulesDir = Join-Path $cursorDir "rules"
    New-Item -ItemType Directory -Force -Path $rulesDir | Out-Null
    Copy-Item -Path "adapters\cursor\*" -Destination $rulesDir -Recurse -Force
    $adaptersCount++
}

# 4. Verify CLI
Write-Host "[4/4] Verifying CLI installation..." -ForegroundColor Yellow
argus --help | Out-Null

Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host " ArgusAgent installation complete! ($adaptersCount adapters installed)" -ForegroundColor Green
Write-Host " Run 'argus --help' or use '/audit' in your AI assistant." -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
