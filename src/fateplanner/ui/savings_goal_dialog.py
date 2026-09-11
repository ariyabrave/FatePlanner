from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
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

from fateplanner.ui.jalali_date_input import (
    JalaliDateInput,
)


DIGIT_TRANSLATION = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


class SavingsGoalDialog(QDialog):
    def __init__(
        self,
        parent=None,
        goal=None,
    ):
        super().__init__(parent)

        self.goal = goal

        self.setWindowTitle(
            "هدف پس‌انداز جدید"
            if goal is None
            else "ویرایش هدف پس‌انداز"
        )

        self.setMinimumWidth(
            500
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "هدف پس‌انداز"
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

        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "مثلاً سفر، لپ‌تاپ، صندوق اضطراری"
        )

        self.description_input = QTextEdit()

        self.description_input.setPlaceholderText(
            "توضیحات اختیاری..."
        )

        self.description_input.setMaximumHeight(
            90
        )

        self.target_input = QLineEdit()

        self.target_input.setPlaceholderText(
            "مثلاً 50000000"
        )

        self.has_target_date = QCheckBox(
            "تاریخ هدف تعیین شود"
        )

        self.target_date_input = (
            JalaliDateInput(
                default_date=date.today()
            )
        )

        form.addRow(
            "عنوان:",
            self.title_input,
        )

        form.addRow(
            "توضیحات:",
            self.description_input,
        )

        form.addRow(
            "مبلغ هدف (تومان):",
            self.target_input,
        )

        form.addRow(
            "",
            self.has_target_date,
        )

        form.addRow(
            "تاریخ هدف:",
            self.target_date_input,
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

        self.has_target_date.toggled.connect(
            self.update_ui_state
        )

        if goal is not None:
            self.load_goal(
                goal
            )

        self.update_ui_state()

        self.title_input.setFocus()

    def load_goal(
        self,
        goal,
    ):
        self.title_input.setText(
            goal["title"]
        )

        self.description_input.setPlainText(
            goal["description"]
            or ""
        )

        self.target_input.setText(
            str(
                goal["target_amount"]
            )
        )

        if goal["target_date"]:
            self.has_target_date.setChecked(
                True
            )

            self.target_date_input.set_gregorian_date(
                date.fromisoformat(
                    goal["target_date"]
                )
            )

    def update_ui_state(
        self,
    ):
        self.target_date_input.setEnabled(
            self.has_target_date.isChecked()
        )

    def parse_amount(
        self,
    ) -> int:
        text = (
            self.target_input
            .text()
            .strip()
            .translate(
                DIGIT_TRANSLATION
            )
            .replace(",", "")
            .replace("٬", "")
            .replace(" ", "")
        )

        if not text.isdigit():
            raise ValueError(
                "مبلغ هدف باید یک عدد صحیح مثبت باشد."
            )

        amount = int(
            text
        )

        if amount <= 0:
            raise ValueError(
                "مبلغ هدف باید بیشتر از صفر باشد."
            )

        return amount

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
                "لطفاً عنوان هدف را وارد کنید.",
            )

            return

        try:
            self.parse_amount()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "مبلغ نامعتبر",
                str(error),
            )

            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        target_date = None

        if self.has_target_date.isChecked():
            target_date = (
                self.target_date_input
                .to_iso_date()
            )

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
            "target_amount": (
                self.parse_amount()
            ),
            "target_date": (
                target_date
            ),
        }