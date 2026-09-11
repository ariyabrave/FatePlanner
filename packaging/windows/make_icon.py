from pathlib import Path

from PIL import Image


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

SOURCE = (
    PROJECT_ROOT
    / "src"
    / "fateplanner"
    / "ui"
    / "assets"
    / "app_icon.png"
)

DESTINATION = (
    PROJECT_ROOT
    / "packaging"
    / "windows"
    / "FatePlanner.ico"
)

ICON_SIZES = [
    (16, 16),
    (24, 24),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (256, 256),
]


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Source icon not found: {SOURCE}"
        )

    image = Image.open(
        SOURCE
    ).convert(
        "RGBA"
    )

    if image.width != image.height:
        raise ValueError(
            "FatePlanner icon must be square."
        )

    image.save(
        DESTINATION,
        format="ICO",
        sizes=ICON_SIZES,
    )

    print(
        f"Created Windows icon: {DESTINATION}"
    )


if __name__ == "__main__":
    main()
