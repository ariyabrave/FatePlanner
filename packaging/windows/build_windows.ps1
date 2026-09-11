$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (
    Join-Path $PSScriptRoot "..\.."
)

Set-Location $ProjectRoot


Write-Host ""
Write-Host "========================================"
Write-Host " FatePlanner Windows Build"
Write-Host "========================================"
Write-Host ""


$Venv = Join-Path `
    $ProjectRoot `
    ".venv-win"

$Python = Join-Path `
    $Venv `
    "Scripts\python.exe"


if (-not (Test-Path $Python)) {

    Write-Host "Creating Windows virtual environment..."

    py -3.12 -m venv `
        $Venv
}


Write-Host ""
Write-Host "Updating pip..."

& $Python `
    -m pip install `
    --upgrade pip


Write-Host ""
Write-Host "Installing FatePlanner..."

& $Python `
    -m pip install `
    -e ".[dev,build]"


Write-Host ""
Write-Host "Generating Windows icon..."

& $Python `
    "packaging/windows/make_icon.py"


Write-Host ""
Write-Host "Running tests..."

& $Python `
    -m pytest `
    -v


Write-Host ""
Write-Host "Cleaning previous builds..."

if (Test-Path "build") {
    Remove-Item `
        -Recurse `
        -Force `
        "build"
}

if (Test-Path "dist") {
    Remove-Item `
        -Recurse `
        -Force `
        "dist"
}


Write-Host ""
Write-Host "Building FatePlanner..."

& $Python `
    -m PyInstaller `
    --clean `
    --noconfirm `
    "packaging/windows/FatePlanner.spec"


Write-Host ""
Write-Host "========================================"
Write-Host " BUILD COMPLETE"
Write-Host "========================================"
Write-Host ""

Write-Host "Executable:"
Write-Host (
    Join-Path `
        $ProjectRoot `
        "dist\FatePlanner\FatePlanner.exe"
)

Write-Host ""
