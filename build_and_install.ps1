#!/usr/bin/env pwsh
# Build and install d_back module in specified virtual environment
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("local", "dissentin")]
    [string]$Environment = "local"
)

Write-Host "=== Building and Installing d_back Module ===" -ForegroundColor Green

# Define environment paths
$venvName = "dissentinenv"
$localVenvPath = ".\.venv\Scripts\Activate.ps1"
$dissentinVenvPath = Join-Path -Path $env:USERPROFILE -ChildPath "$venvName\Scripts\Activate.ps1"

# Select the appropriate environment
if ($Environment -eq "local") {
    $venvPath = $localVenvPath
    $envDisplayName = "LOCAL .venv"
    Write-Host "Target environment: LOCAL .venv" -ForegroundColor Cyan
} elseif ($Environment -eq "dissentin") {
    $venvPath = $dissentinVenvPath
    $envDisplayName = "DISSENTIN ($venvName)"
    Write-Host "Target environment: DISSENTIN ($venvName)" -ForegroundColor Cyan
    
    # Check if the dissentin environment exists
    if (-not (Test-Path $venvPath)) {
        Write-Host "Dissentin environment not found at: $venvPath" -ForegroundColor Red
        Write-Host "Please create the environment first or check the path." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "Invalid environment specified. Use 'local' or 'dissentin'." -ForegroundColor Red
    exit 1
}

# Activate the selected virtual environment
Write-Host "Activating $envDisplayName environment..." -ForegroundColor Yellow
& $venvPath

# Check if virtual environment is active
if (-not (Test-Path env:VIRTUAL_ENV)) {
    Write-Host "Failed to activate $envDisplayName virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "Active virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Cyan

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
Write-Host "Installing the built package to $envDisplayName..." -ForegroundColor Yellow
$wheelFile = Get-ChildItem -Path "dist" -Filter "*.whl" | Select-Object -First 1
if ($wheelFile) {
    pip install "$($wheelFile.FullName)" --force-reinstall
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully built and installed d_back module in $envDisplayName!" -ForegroundColor Green
        Write-Host "You can now import it with: from d_back.server import WebSocketServer" -ForegroundColor Cyan
    } else {
        Write-Host "Installation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "No wheel file found in dist directory!" -ForegroundColor Red
    exit 1
}
