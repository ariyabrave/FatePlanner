from datetime import date

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


class SavingsEntryDialog(QDialog):
    def __init__(
        self,
        goal,
        parent=None,
        default_type: str = "deposit",
    ):
        super().__init__(parent)

        self.goal = goal

        self.setWindowTitle(
            "ثبت تغییر پس‌انداز"
        )

        self.setMinimumWidth(
            460
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            goal["title"]
        )

        title.setStyleSheet(
            """
            font-size: 21px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            title
        )

        form = QFormLayout()

        self.type_input = QComboBox()

        self.type_input.addItem(
            "واریز به هدف",
            "deposit",
        )

        self.type_input.addItem(
            "برداشت از هدف",
            "withdrawal",
        )

        index = self.type_input.findData(
            default_type
        )

        if index >= 0:
            self.type_input.setCurrentIndex(
                index
            )

        self.amount_input = QLineEdit()

        self.amount_input.setPlaceholderText(
            "مثلاً 1000000"
        )

        self.date_input = JalaliDateInput(
            default_date=date.today()
        )

        self.note_input = QTextEdit()

        self.note_input.setPlaceholderText(
            "یادداشت اختیاری..."
        )

        self.note_input.setMaximumHeight(
            80
        )

        form.addRow(
            "نوع:",
            self.type_input,
        )

        form.addRow(
            "مبلغ (تومان):",
            self.amount_input,
        )

        form.addRow(
            "تاریخ:",
            self.date_input,
        )

        form.addRow(
            "یادداشت:",
            self.note_input,
        )

        layout.addLayout(
            form
        )

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "ثبت"
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

    def parse_amount(
        self,
    ) -> int:
        text = (
            self.amount_input
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
                "مبلغ باید یک عدد صحیح مثبت باشد."
            )

        amount = int(
            text
        )

        if amount <= 0:
            raise ValueError(
                "مبلغ باید بیشتر از صفر باشد."
            )

        return amount

    def validate_and_accept(
        self,
    ):
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
        return {
            "goal_id": (
                self.goal["id"]
            ),
            "entry_type": (
                self.type_input
                .currentData()
            ),
            "amount": (
                self.parse_amount()
            ),
            "entry_date": (
                self.date_input
                .to_iso_date()
            ),
            "note": (
                self.note_input
                .toPlainText()
                .strip()
            ),
        }