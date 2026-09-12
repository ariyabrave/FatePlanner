import re
import sys

from pathlib import Path


OUTPUT = (
    Path(__file__)
    .resolve()
    .parent
    / "version_info.txt"
)


def normalize_version(
    value: str,
) -> str:
    version = (
        value.strip()
        .removeprefix("v")
    )

    if not re.fullmatch(
        r"\d+\.\d+\.\d+",
        version,
    ):
        raise ValueError(
            "Version must use X.Y.Z format, "
            "for example 0.1.0."
        )

    return version


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: "
            "python make_version_info.py "
            "0.1.0"
        )

    version = normalize_version(
        sys.argv[1]
    )

    major, minor, patch = (
        int(part)
        for part
        in version.split(".")
    )

    content = f'''VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(
            {major},
            {minor},
            {patch},
            0,
        ),
        prodvers=(
            {major},
            {minor},
            {patch},
            0,
        ),
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    "040904B0",
                    [
                        StringStruct(
                            "CompanyName",
                            "FatePlanner",
                        ),
                        StringStruct(
                            "FileDescription",
                            "FatePlanner Personal Planner",
                        ),
                        StringStruct(
                            "FileVersion",
                            "{version}",
                        ),
                        StringStruct(
                            "InternalName",
                            "FatePlanner",
                        ),
                        StringStruct(
                            "OriginalFilename",
                            "FatePlanner.exe",
                        ),
                        StringStruct(
                            "ProductName",
                            "FatePlanner",
                        ),
                        StringStruct(
                            "ProductVersion",
                            "{version}",
                        ),
                    ],
                ),
            ],
        ),
        VarFileInfo(
            [
                VarStruct(
                    "Translation",
                    [1033, 1200],
                ),
            ],
        ),
    ],
)
'''

    OUTPUT.write_text(
        content,
        encoding="utf-8",
    )

    print(
        f"Created Windows version info "
        f"for FatePlanner {version}"
    )


if __name__ == "__main__":
    main()