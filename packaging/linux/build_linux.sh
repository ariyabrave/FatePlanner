#!/usr/bin/env bash

set -euo pipefail


PROJECT_ROOT="$(
    cd "$(
        dirname "${BASH_SOURCE[0]}"
    )/../.."
    pwd
)"

cd "$PROJECT_ROOT"


echo
echo "========================================"
echo " FatePlanner Linux Build"
echo "========================================"
echo


PYTHON="${PYTHON:-python3}"


echo "Installing build dependencies..."

"$PYTHON" -m pip install \
    -e ".[dev,build]"


echo
echo "Running tests..."

QT_QPA_PLATFORM=offscreen \
"$PYTHON" -m pytest -v


echo
echo "Cleaning previous build..."

rm -rf \
    build \
    dist


echo
echo "Building FatePlanner..."

"$PYTHON" -m PyInstaller \
    --clean \
    --noconfirm \
    packaging/linux/FatePlanner.spec


echo
echo "Creating portable archive..."

cd dist

tar \
    -czf \
    FatePlanner-Linux-x86_64.tar.gz \
    FatePlanner


echo
echo "========================================"
echo " BUILD COMPLETE"
echo "========================================"
echo

echo "Archive:"
echo "$PROJECT_ROOT/dist/FatePlanner-Linux-x86_64.tar.gz"
echo