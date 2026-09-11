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


class StudySubjectDialog(QDialog):
    def __init__(
        self,
        parent=None,
        subject=None,
    ):
        super().__init__(parent)

        self.subject = subject

        self.setWindowTitle(
            "موضوع جدید"
            if subject is None
            else "ویرایش موضوع"
        )

        self.setMinimumWidth(
            430
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "موضوع مطالعه جدید"
            if subject is None
            else "ویرایش موضوع مطالعه"
        )

        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            title
        )

        form = QFormLayout()

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "مثلاً ریاضی، زبان انگلیسی، امنیت شبکه"
        )

        self.description_input = QTextEdit()

        self.description_input.setPlaceholderText(
            "توضیحات اختیاری..."
        )

        self.description_input.setMaximumHeight(
            100
        )

        form.addRow(
            "نام موضوع:",
            self.name_input,
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

        if subject is not None:
            self.name_input.setText(
                subject["name"]
            )

            self.description_input.setPlainText(
                subject["description"] or ""
            )

        self.name_input.setFocus()

    def validate_and_accept(
        self,
    ):
        if not (
            self.name_input
            .text()
            .strip()
        ):
            QMessageBox.warning(
                self,
                "نام خالی",
                "لطفاً نام موضوع مطالعه را وارد کنید.",
            )

            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        return {
            "name": (
                self.name_input
                .text()
                .strip()
            ),
            "description": (
                self.description_input
                .toPlainText()
                .strip()
            ),
        }