from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class SubtaskDialog(QDialog):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "افزودن زیرکار"
        )

        self.setMinimumWidth(
            400
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "زیرکار جدید"
        )

        title.setStyleSheet(
            """
            font-size: 21px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            title
        )

        form = QFormLayout()

        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "عنوان زیرکار"
        )

        self.description_input = QTextEdit()

        self.description_input.setPlaceholderText(
            "توضیحات اختیاری..."
        )

        self.description_input.setMaximumHeight(
            90
        )

        form.addRow(
            "عنوان:",
            self.title_input,
        )

        form.addRow(
            "توضیحات:",
            self.description_input,
        )

        main_layout.addLayout(
            form
        )

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "ذخیره"
        )

        cancel_button = QPushButton(
            "انصراف"
        )

        save_button.setDefault(
            True
        )

        save_button.clicked.connect(
            self.validate_and_accept
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            save_button
        )

        buttons.addWidget(
            cancel_button
        )

        main_layout.addLayout(
            buttons
        )

        self.title_input.setFocus()

    def validate_and_accept(
        self,
    ):
        if not (
            self.title_input
            .text()
            .strip()
        ):
            QMessageBox.warning(
                self,
                "عنوان خالی",
                "لطفاً عنوان زیرکار را وارد کنید.",
            )

            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        return {
            "title": (
                self.title_input
                .text()
                .strip()
            ),
            "description": (
                self.description_input
                .toPlainText()
                .strip()
            ),
        }