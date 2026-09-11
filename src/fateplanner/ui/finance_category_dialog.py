from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class FinanceCategoryDialog(QDialog):
    def __init__(
        self,
        parent=None,
        category=None,
        default_type: str = "expense",
    ):
        super().__init__(parent)

        self.category = category

        self.setWindowTitle(
            "دسته‌بندی جدید"
            if category is None
            else "ویرایش دسته‌بندی"
        )

        self.setMinimumWidth(
            420
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "دسته‌بندی مالی"
        )

        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            title
        )

        form = QFormLayout()

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "مثلاً خوراک، حقوق، حمل‌ونقل"
        )

        self.type_input = QComboBox()

        self.type_input.addItem(
            "هزینه",
            "expense",
        )

        self.type_input.addItem(
            "درآمد",
            "income",
        )

        index = self.type_input.findData(
            default_type
        )

        if index >= 0:
            self.type_input.setCurrentIndex(
                index
            )

        form.addRow(
            "نام:",
            self.name_input,
        )

        form.addRow(
            "نوع:",
            self.type_input,
        )

        layout.addLayout(
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

        layout.addLayout(
            buttons
        )

        if category is not None:
            self.name_input.setText(
                category["name"]
            )

            index = (
                self.type_input.findData(
                    category[
                        "transaction_type"
                    ]
                )
            )

            if index >= 0:
                self.type_input.setCurrentIndex(
                    index
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
                "لطفاً نام دسته‌بندی را وارد کنید.",
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
            "transaction_type": (
                self.type_input
                .currentData()
            ),
        }