#!/usr/bin/env pwsh
# Build and install d_back module in virtual environment

Write-Host "=== Building and Installing d_back Module ===" -ForegroundColor Green

$venvName = "dissentinenv"
# used for testing python module in develop discord bot
$venvActivatePath = Join-Path -Path $env:USERPROFILE -ChildPath "$venvName\Scripts\Activate.ps1"
# used for testing python module directly
$localVenvPath = ".\.venv\Scripts\Activate.ps1"

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& $localVenvPath

# Check if virtual environment is active
if (-not (Test-Path env:VIRTUAL_ENV)) {
    Write-Host "Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Uninstall existing version if present
Write-Host "Uninstalling existing d_back module (if present)..." -ForegroundColor Yellow
pip uninstall d_back -y

# Clean up build artifacts
Write-Host "Cleaning up build artifacts..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "d_back.egg-info") { Remove-Item -Recurse -Force "d_back.egg-info" }

# Build the package
Write-Host "Building the package..." -ForegroundColor Yellow
python -m build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Install the built package
Write-Host "Installing the built package..." -ForegroundColor Yellow
$wheelFile = Get-ChildItem -Path "dist" -Filter "*.whl" | Select-Object -First 1
if ($wheelFile) {
    pip install "$($wheelFile.FullName)" --force-reinstall
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully built and installed d_back module!" -ForegroundColor Green
        Write-Host "You can now import it with: from d_back.server import WebSocketServer" -ForegroundColor Cyan
    } else {
        Write-Host "Installation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "No wheel file found in dist directory!" -ForegroundColor Red
    exit 1
}
