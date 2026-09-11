from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
)


PROJECT_ROOT = (
    Path(SPECPATH)
    .resolve()
    .parents[1]
)

ENTRY_POINT = (
    PROJECT_ROOT
    / "src"
    / "fateplanner"
    / "main.py"
)

ICON_PATH = (
    PROJECT_ROOT
    / "packaging"
    / "windows"
    / "FatePlanner.ico"
)

VERSION_FILE = (
    PROJECT_ROOT
    / "packaging"
    / "windows"
    / "version_info.txt"
)


datas = collect_data_files(
    "fateplanner"
)


a = Analysis(
    [str(ENTRY_POINT)],
    pathex=[
        str(
            PROJECT_ROOT
            / "src"
        ),
    ],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(
    a.pure
)


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FatePlanner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(
        ICON_PATH
    ),
    version=str(
        VERSION_FILE
    ),
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="FatePlanner",
)
