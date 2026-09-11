import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.backup_service import (
    create_automatic_backup,
)
from fateplanner.ui.semantic_ui import (
    install_semantic_ui,
)
from fateplanner.ui.main_window import (
    MainWindow,
)

from fateplanner.ui.theme import (
    apply_appearance,
)


def main():
    initialize_database()

    try:
        create_automatic_backup()

    except Exception as error:
        print(
            "Warning: automatic backup failed:",
            error,
            file=sys.stderr,
        )

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "FatePlanner"
    )

    app.setOrganizationName(
        "FatePlanner"
    )

    app.setDesktopFileName(
        "fateplanner"
    )

    app.setLayoutDirection(
        Qt.LayoutDirection.RightToLeft
    )

    apply_appearance(
        app
    )

    semantic_ui = install_semantic_ui(
        app
    )

    window = MainWindow()

    # Open FatePlanner maximized by default.
    window.showMaximized()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()