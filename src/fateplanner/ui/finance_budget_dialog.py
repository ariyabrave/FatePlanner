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

from fateplanner.services.finance_service import (
    get_finance_categories,
)
from fateplanner.utils.date_utils import (
    format_jalali_month_title,
)


DIGIT_TRANSLATION = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


class FinanceBudgetDialog(QDialog):
    def __init__(
        self,
        *,
        jalali_year: int,
        jalali_month: int,
        parent=None,
        budget=None,
    ):
        super().__init__(parent)

        self.jalali_year = int(
            jalali_year
        )

        self.jalali_month = int(
            jalali_month
        )

        self.budget = budget

        self.setWindowTitle(
            "بودجه جدید"
            if budget is None
            else "ویرایش بودجه"
        )

        self.setMinimumWidth(
            450
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "بودجه ماهانه"
        )

        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        month_label = QLabel(
            format_jalali_month_title(
                self.jalali_year,
                self.jalali_month,
            )
        )

        month_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            month_label
        )

        form = QFormLayout()

        self.category_input = (
            QComboBox()
        )

        categories = (
            get_finance_categories(
                "expense"
            )
        )

        for category in categories:
            self.category_input.addItem(
                category["name"],
                category["id"],
            )

        self.amount_input = QLineEdit()

        self.amount_input.setPlaceholderText(
            "مثلاً 5000000"
        )

        form.addRow(
            "دسته‌بندی:",
            self.category_input,
        )

        form.addRow(
            "بودجه (تومان):",
            self.amount_input,
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

        if budget is not None:
            category_index = (
                self.category_input
                .findData(
                    budget[
                        "category_id"
                    ]
                )
            )

            if category_index >= 0:
                self.category_input.setCurrentIndex(
                    category_index
                )

            self.amount_input.setText(
                str(
                    budget["amount"]
                )
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
                "بودجه باید یک عدد صحیح مثبت باشد."
            )

        amount = int(
            text
        )

        if amount <= 0:
            raise ValueError(
                "بودجه باید بیشتر از صفر باشد."
            )

        return amount

    def validate_and_accept(
        self,
    ):
        if (
            self.category_input
            .currentData()
            is None
        ):
            QMessageBox.warning(
                self,
                "دسته‌بندی",
                (
                    "ابتدا یک دسته‌بندی "
                    "هزینه ایجاد کنید."
                ),
            )

            return

        try:
            self.parse_amount()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "بودجه نامعتبر",
                str(error),
            )

            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        return {
            "category_id": int(
                self.category_input
                .currentData()
            ),
            "jalali_year": (
                self.jalali_year
            ),
            "jalali_month": (
                self.jalali_month
            ),
            "amount": (
                self.parse_amount()
            ),
        }