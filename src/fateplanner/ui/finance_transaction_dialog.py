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

from fateplanner.services.finance_service import (
    get_finance_categories,
)
from fateplanner.ui.jalali_date_input import (
    JalaliDateInput,
)


DIGIT_TRANSLATION = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


class FinanceTransactionDialog(QDialog):
    def __init__(
        self,
        parent=None,
        transaction=None,
        default_type: str = "expense",
    ):
        super().__init__(parent)

        self.transaction = transaction

        self.setWindowTitle(
            "تراکنش جدید"
            if transaction is None
            else "ویرایش تراکنش"
        )

        self.setMinimumWidth(
            500
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        if transaction is not None:
            default_type = (
                transaction[
                    "transaction_type"
                ]
            )

            default_date = (
                date.fromisoformat(
                    transaction[
                        "transaction_date"
                    ]
                )
            )

        else:
            default_date = date.today()

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "تراکنش مالی"
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

        self.category_input = QComboBox()

        self.amount_input = QLineEdit()

        self.amount_input.setPlaceholderText(
            "مثلاً 250000"
        )

        self.date_input = JalaliDateInput(
            default_date=default_date
        )

        self.description_input = QTextEdit()

        self.description_input.setPlaceholderText(
            "توضیحات اختیاری..."
        )

        self.description_input.setMaximumHeight(
            100
        )

        form.addRow(
            "نوع:",
            self.type_input,
        )

        form.addRow(
            "دسته‌بندی:",
            self.category_input,
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
            "توضیحات:",
            self.description_input,
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

        self.type_input.currentIndexChanged.connect(
            self.refresh_categories
        )

        self.refresh_categories()

        if transaction is not None:
            self.load_transaction(
                transaction
            )

    def refresh_categories(
        self,
    ):
        previous = (
            self.category_input
            .currentData()
        )

        transaction_type = (
            self.type_input
            .currentData()
        )

        categories = (
            get_finance_categories(
                transaction_type
            )
        )

        self.category_input.clear()

        for category in categories:
            self.category_input.addItem(
                category["name"],
                category["id"],
            )

        if previous is not None:
            index = (
                self.category_input.findData(
                    previous
                )
            )

            if index >= 0:
                self.category_input.setCurrentIndex(
                    index
                )

    def load_transaction(
        self,
        transaction,
    ):
        type_index = (
            self.type_input.findData(
                transaction[
                    "transaction_type"
                ]
            )
        )

        if type_index >= 0:
            self.type_input.setCurrentIndex(
                type_index
            )

        self.refresh_categories()

        category_index = (
            self.category_input.findData(
                transaction["category_id"]
            )
        )

        if category_index >= 0:
            self.category_input.setCurrentIndex(
                category_index
            )

        self.amount_input.setText(
            str(
                transaction["amount"]
            )
        )

        self.date_input.set_gregorian_date(
            date.fromisoformat(
                transaction[
                    "transaction_date"
                ]
            )
        )

        self.description_input.setPlainText(
            transaction["description"]
            or ""
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
        )

        text = (
            text
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
        if (
            self.category_input.currentData()
            is None
        ):
            QMessageBox.warning(
                self,
                "دسته‌بندی",
                (
                    "برای این نوع تراکنش هنوز "
                    "دسته‌بندی ساخته نشده است."
                ),
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
        return {
            "transaction_type": (
                self.type_input
                .currentData()
            ),
            "category_id": int(
                self.category_input
                .currentData()
            ),
            "amount": (
                self.parse_amount()
            ),
            "transaction_date": (
                self.date_input
                .to_iso_date()
            ),
            "description": (
                self.description_input
                .toPlainText()
                .strip()
            ),
        }