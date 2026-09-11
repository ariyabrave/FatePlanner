from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from fateplanner.ui.theme import theme_hex
from fateplanner.services.finance_service import (
    create_finance_budget,
    create_finance_category,
    create_finance_transaction,
    delete_finance_budget,
    delete_finance_category,
    delete_finance_transaction,
    format_money,
    get_finance_budget,
    get_finance_budget_overview,
    get_finance_budget_statuses,
    get_finance_categories,
    get_finance_category,
    get_finance_summary_between,
    get_finance_transaction,
    get_finance_transactions_between,
    update_finance_budget,
    update_finance_category,
    update_finance_transaction,
)
from fateplanner.ui.finance_budget_dialog import (
    FinanceBudgetDialog,
)
from fateplanner.ui.finance_category_dialog import (
    FinanceCategoryDialog,
)
from fateplanner.ui.finance_transaction_dialog import (
    FinanceTransactionDialog,
)
from fateplanner.ui.savings_goals_widget import (
    SavingsGoalsWidget,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
    format_jalali_month_title,
    format_jalali_short,
    get_jalali_month_dates,
    gregorian_to_jalali,
    to_persian_digits,
)


TYPE_LABELS = {
    "income": "درآمد",
    "expense": "هزینه",
}


class FinancePage(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        current = gregorian_to_jalali(
            date.today()
        )

        self.year = current.year
        self.month = current.month

        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "امور مالی"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        self.date_label = QLabel(
            format_jalali_date(
                date.today()
            )
        )

        main_layout.addWidget(
            title
        )

        main_layout.addWidget(
            self.date_label
        )

        # ==================================
        # Shared month navigation
        # ==================================

        navigation = QHBoxLayout()

        previous_button = QPushButton(
            "ماه قبل"
        )

        current_button = QPushButton(
            "ماه جاری"
        )

        next_button = QPushButton(
            "ماه بعد"
        )

        self.month_label = QLabel()

        self.month_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.month_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        previous_button.clicked.connect(
            self.previous_month
        )

        current_button.clicked.connect(
            self.current_month
        )

        next_button.clicked.connect(
            self.next_month
        )

        navigation.addWidget(
            previous_button
        )

        navigation.addWidget(
            current_button
        )

        navigation.addWidget(
            self.month_label,
            1,
        )

        navigation.addWidget(
            next_button
        )

        main_layout.addLayout(
            navigation
        )

        # ==================================
        # Tabs
        # ==================================

        self.tabs = QTabWidget()

        self.ledger_tab = (
            self.create_ledger_tab()
        )

        self.categories_tab = (
            self.create_categories_tab()
        )

        self.budgets_tab = (
            self.create_budgets_tab()
        )

        self.savings_tab = (
            SavingsGoalsWidget(
                self
            )
        )

        self.tabs.addTab(
            self.ledger_tab,
            "تراکنش‌ها",
        )

        self.tabs.addTab(
            self.categories_tab,
            "دسته‌بندی‌ها",
        )

        self.tabs.addTab(
            self.budgets_tab,
            "بودجه‌ها",
        )

        self.tabs.addTab(
            self.savings_tab,
            "اهداف پس‌انداز",
        )

        self.tabs.currentChanged.connect(
            self.on_tab_changed
        )

        main_layout.addWidget(
            self.tabs,
            1,
        )

        self.refresh()

    # ==================================
    # Ledger
    # ==================================

    def create_ledger_tab(
        self,
    ):
        tab = QWidget()

        layout = QVBoxLayout(
            tab
        )

        summary_frame = QFrame()

        summary_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 8px;
            }
            """
        )

        summary_layout = QHBoxLayout(
            summary_frame
        )

        self.income_label = (
            self.create_summary_label()
        )

        self.expense_label = (
            self.create_summary_label()
        )

        self.balance_label = (
            self.create_summary_label()
        )

        self.count_label = (
            self.create_summary_label()
        )

        summary_layout.addWidget(
            self.income_label
        )

        summary_layout.addWidget(
            self.expense_label
        )

        summary_layout.addWidget(
            self.balance_label
        )

        summary_layout.addWidget(
            self.count_label
        )

        layout.addWidget(
            summary_frame
        )

        actions = QHBoxLayout()

        income_button = QPushButton(
            "＋ ثبت درآمد"
        )

        expense_button = QPushButton(
            "＋ ثبت هزینه"
        )

        income_button.setMinimumHeight(
            42
        )

        expense_button.setMinimumHeight(
            42
        )

        income_button.clicked.connect(
            lambda:
            self.open_add_transaction(
                "income"
            )
        )

        expense_button.clicked.connect(
            lambda:
            self.open_add_transaction(
                "expense"
            )
        )

        actions.addWidget(
            income_button
        )

        actions.addWidget(
            expense_button
        )

        layout.addLayout(
            actions
        )

        self.transaction_table = (
            QTableWidget()
        )

        self.transaction_table.setColumnCount(
            6
        )

        self.transaction_table.setHorizontalHeaderLabels(
            [
                "تاریخ",
                "نوع",
                "دسته‌بندی",
                "مبلغ",
                "توضیحات",
                "عملیات",
            ]
        )

        # FatePlanner finance action sizing
        self.transaction_table.verticalHeader().setMinimumSectionSize(
            48
        )

        self.transaction_table.verticalHeader().setDefaultSectionSize(
            50
        )

        action_header = self.transaction_table.horizontalHeader()

        action_header.setSectionResizeMode(
            5,
            action_header.ResizeMode.Fixed,
        )

        self.transaction_table.setColumnWidth(
            5,
            190,
        )

        self.transaction_table.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        self.transaction_table.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        self.transaction_table.setAlternatingRowColors(
            True
        )

        self.transaction_table.verticalHeader().setVisible(
            False
        )

        self.transaction_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(
            self.transaction_table,
            1,
        )

        return tab

    # ==================================
    # Categories
    # ==================================

    def create_categories_tab(
        self,
    ):
        tab = QWidget()

        layout = QVBoxLayout(
            tab
        )

        buttons = QHBoxLayout()

        expense_button = QPushButton(
            "＋ دسته‌بندی هزینه"
        )

        income_button = QPushButton(
            "＋ دسته‌بندی درآمد"
        )

        expense_button.clicked.connect(
            lambda:
            self.open_add_category(
                "expense"
            )
        )

        income_button.clicked.connect(
            lambda:
            self.open_add_category(
                "income"
            )
        )

        buttons.addWidget(
            expense_button
        )

        buttons.addWidget(
            income_button
        )

        layout.addLayout(
            buttons
        )

        self.categories_container = QWidget()

        self.categories_layout = QVBoxLayout(
            self.categories_container
        )

        self.categories_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setWidget(
            self.categories_container
        )

        layout.addWidget(
            scroll,
            1,
        )

        return tab

    # ==================================
    # Budgets
    # ==================================

    def create_budgets_tab(
        self,
    ):
        tab = QWidget()

        layout = QVBoxLayout(
            tab
        )

        overview_frame = QFrame()

        overview_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 8px;
            }
            """
        )

        overview_layout = QHBoxLayout(
            overview_frame
        )

        self.total_budget_label = (
            self.create_summary_label()
        )

        self.budget_spent_label = (
            self.create_summary_label()
        )

        self.budget_remaining_label = (
            self.create_summary_label()
        )

        self.overspent_label = (
            self.create_summary_label()
        )

        overview_layout.addWidget(
            self.total_budget_label
        )

        overview_layout.addWidget(
            self.budget_spent_label
        )

        overview_layout.addWidget(
            self.budget_remaining_label
        )

        overview_layout.addWidget(
            self.overspent_label
        )

        layout.addWidget(
            overview_frame
        )

        self.unbudgeted_label = QLabel()

        self.unbudgeted_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.unbudgeted_label.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            padding: 6px;
            """
        )

        layout.addWidget(
            self.unbudgeted_label
        )

        add_button = QPushButton(
            "＋ افزودن بودجه"
        )

        add_button.setMinimumHeight(
            42
        )

        add_button.clicked.connect(
            self.open_add_budget
        )

        layout.addWidget(
            add_button
        )

        self.budgets_container = QWidget()

        self.budgets_layout = QVBoxLayout(
            self.budgets_container
        )

        self.budgets_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setWidget(
            self.budgets_container
        )

        layout.addWidget(
            scroll,
            1,
        )

        return tab

    def create_summary_label(
        self,
    ):
        label = QLabel()

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        label.setWordWrap(
            True
        )

        label.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            padding: 8px;
            """
        )

        return label

    # ==================================
    # Refresh
    # ==================================

    def get_month_range(
        self,
    ):
        dates = get_jalali_month_dates(
            self.year,
            self.month,
        )

        return (
            dates[0],
            dates[-1],
        )

    def refresh(
        self,
    ):
        self.month_label.setText(
            format_jalali_month_title(
                self.year,
                self.month,
            )
        )

        start, end = (
            self.get_month_range()
        )

        self.refresh_summary(
            start,
            end,
        )

        self.refresh_transactions(
            start,
            end,
        )

        self.refresh_categories()

        self.refresh_budgets()

        if hasattr(
            self,
            "savings_tab",
        ):
            self.savings_tab.refresh()

    def refresh_summary(
        self,
        start: date,
        end: date,
    ):
        summary = (
            get_finance_summary_between(
                start.isoformat(),
                end.isoformat(),
            )
        )

        income = to_persian_digits(
            format_money(
                summary["income"]
            )
        )

        expense = to_persian_digits(
            format_money(
                summary["expense"]
            )
        )

        balance = to_persian_digits(
            format_money(
                summary["balance"]
            )
        )

        count = to_persian_digits(
            summary[
                "total_transactions"
            ]
        )

        self.income_label.setText(
            "درآمد ماه\n"
            f"{income} تومان"
        )

        self.expense_label.setText(
            "هزینه ماه\n"
            f"{expense} تومان"
        )

        self.balance_label.setText(
            "مانده ماه\n"
            f"{balance} تومان"
        )

        self.count_label.setText(
            "تعداد تراکنش‌ها\n"
            f"{count}"
        )

    def refresh_transactions(
        self,
        start: date,
        end: date,
    ):
        transactions = (
            get_finance_transactions_between(
                start.isoformat(),
                end.isoformat(),
            )
        )

        self.transaction_table.setRowCount(
            len(
                transactions
            )
        )

        for row_index, transaction in enumerate(
            transactions
        ):
            transaction_date = (
                date.fromisoformat(
                    transaction[
                        "transaction_date"
                    ]
                )
            )

            values = [
                format_jalali_short(
                    transaction_date
                ),
                TYPE_LABELS[
                    transaction[
                        "transaction_type"
                    ]
                ],
                transaction[
                    "category_name"
                ],
                (
                    to_persian_digits(
                        format_money(
                            transaction[
                                "amount"
                            ]
                        )
                    )
                    + " تومان"
                ),
                (
                    transaction[
                        "description"
                    ]
                    or "—"
                ),
            ]

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    str(
                        value
                    )
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.transaction_table.setItem(
                    row_index,
                    column,
                    item,
                )

            action_widget = QWidget()

            action_layout = QHBoxLayout(
                action_widget
            )

            action_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            edit_button = QPushButton(
                "ویرایش"
            )

            delete_button = QPushButton(
                "حذف"
            )

            edit_button.clicked.connect(
                lambda _,
                transaction_id=transaction["id"]:
                self.open_edit_transaction(
                    transaction_id
                )
            )

            delete_button.clicked.connect(
                lambda _,
                transaction_id=transaction["id"]:
                self.confirm_delete_transaction(
                    transaction_id
                )
            )

            action_layout.addWidget(
                edit_button
            )

            action_layout.addWidget(
                delete_button
            )

            self.transaction_table.setCellWidget(
                row_index,
                5,
                action_widget,
            )

    def refresh_categories(
        self,
    ):
        self.clear_layout(
            self.categories_layout
        )

        categories = (
            get_finance_categories()
        )

        if not categories:
            label = QLabel(
                "هنوز دسته‌بندی مالی ساخته نشده است."
            )

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.categories_layout.addWidget(
                label
            )

            return

        for category in categories:
            self.categories_layout.addWidget(
                self.create_category_card(
                    category
                )
            )

    def refresh_budgets(
        self,
    ):
        self.clear_layout(
            self.budgets_layout
        )

        overview = (
            get_finance_budget_overview(
                self.year,
                self.month,
            )
        )

        statuses = (
            get_finance_budget_statuses(
                self.year,
                self.month,
            )
        )

        self.total_budget_label.setText(
            "کل بودجه\n"
            + to_persian_digits(
                format_money(
                    overview[
                        "total_budget"
                    ]
                )
            )
            + " تومان"
        )

        self.budget_spent_label.setText(
            "هزینه از بودجه‌ها\n"
            + to_persian_digits(
                format_money(
                    overview[
                        "budgeted_spending"
                    ]
                )
            )
            + " تومان"
        )

        self.budget_remaining_label.setText(
            "باقی‌مانده بودجه\n"
            + to_persian_digits(
                format_money(
                    overview[
                        "remaining"
                    ]
                )
            )
            + " تومان"
        )

        self.overspent_label.setText(
            "بودجه‌های ردشده\n"
            + to_persian_digits(
                overview[
                    "overspent_count"
                ]
            )
        )

        self.unbudgeted_label.setText(
            "هزینه بدون بودجه: "
            + to_persian_digits(
                format_money(
                    overview[
                        "unbudgeted_expense"
                    ]
                )
            )
            + " تومان"
        )

        if not statuses:
            label = QLabel(
                (
                    "برای این ماه هنوز "
                    "بودجه‌ای تعیین نشده است."
                )
            )

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setStyleSheet(
                """
                padding: 25px;
                color: palette(window-text);
                """
            )

            self.budgets_layout.addWidget(
                label
            )

            return

        for status in statuses:
            self.budgets_layout.addWidget(
                self.create_budget_card(
                    status
                )
            )

    # ==================================
    # Budget cards
    # ==================================

    def create_budget_card(
        self,
        status: dict,
    ):
        frame = QFrame()

        if status["overspent"]:
            border = theme_hex("danger")
        elif status["percentage"] >= 80:
            border = theme_hex("warning")
        else:
            border = "palette(mid)"

        frame.setStyleSheet(
            f"""
            QFrame {{
                border: 1px solid {border};
                border-radius: 10px;
                padding: 8px;
            }}
            """
        )

        layout = QVBoxLayout(
            frame
        )

        header = QHBoxLayout()

        title = QLabel(
            status["category_name"]
        )

        title.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            """
        )

        edit_button = QPushButton(
            "ویرایش"
        )

        delete_button = QPushButton(
            "حذف"
        )

        edit_button.clicked.connect(
            lambda _,
            budget_id=status["id"]:
            self.open_edit_budget(
                budget_id
            )
        )

        delete_button.clicked.connect(
            lambda _,
            budget_id=status["id"]:
            self.confirm_delete_budget(
                budget_id
            )
        )

        header.addWidget(
            title,
            1,
        )

        header.addWidget(
            edit_button
        )

        header.addWidget(
            delete_button
        )

        layout.addLayout(
            header
        )

        amount_text = (
            to_persian_digits(
                format_money(
                    status["amount"]
                )
            )
        )

        spent_text = (
            to_persian_digits(
                format_money(
                    status["spent"]
                )
            )
        )

        remaining_text = (
            to_persian_digits(
                format_money(
                    status["remaining"]
                )
            )
        )

        details = QLabel(
            "بودجه: "
            f"{amount_text} تومان"
            "  |  "
            "هزینه‌شده: "
            f"{spent_text} تومان"
            "  |  "
            "باقی‌مانده: "
            f"{remaining_text} تومان"
        )

        details.setWordWrap(
            True
        )

        layout.addWidget(
            details
        )

        percentage = int(
            status["percentage"]
        )

        progress_label = QLabel(
            "مصرف بودجه: "
            f"{to_persian_digits(percentage)}٪"
        )

        layout.addWidget(
            progress_label
        )

        progress = QProgressBar()

        progress.setRange(
            0,
            100,
        )

        progress.setValue(
            min(
                100,
                percentage,
            )
        )

        layout.addWidget(
            progress
        )

        if status["overspent"]:
            warning = QLabel(
                "⚠️ این بودجه رد شده است."
            )

            warning.setStyleSheet(
                """
                font-weight: bold;
                color: #b33a3a;
                """
            )

            layout.addWidget(
                warning
            )

        elif percentage >= 80:
            warning = QLabel(
                "⚠️ به سقف بودجه نزدیک شده‌اید."
            )

            warning.setStyleSheet(
                """
                font-weight: bold;
                """
            )

            layout.addWidget(
                warning
            )

        return frame

    # ==================================
    # Transactions
    # ==================================

    def open_add_transaction(
        self,
        transaction_type: str,
    ):
        if not get_finance_categories(
            transaction_type
        ):
            QMessageBox.information(
                self,
                "دسته‌بندی",
                (
                    "ابتدا حداقل یک دسته‌بندی "
                    "برای این نوع تراکنش بسازید."
                ),
            )

            self.tabs.setCurrentWidget(
                self.categories_tab
            )

            return

        dialog = FinanceTransactionDialog(
            self,
            default_type=transaction_type,
        )

        if not dialog.exec():
            return

        try:
            create_finance_transaction(
                **dialog.get_data()
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def open_edit_transaction(
        self,
        transaction_id: int,
    ):
        transaction = (
            get_finance_transaction(
                transaction_id
            )
        )

        if transaction is None:
            return

        dialog = FinanceTransactionDialog(
            self,
            transaction=transaction,
        )

        if not dialog.exec():
            return

        try:
            update_finance_transaction(
                transaction_id=transaction_id,
                **dialog.get_data(),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def confirm_delete_transaction(
        self,
        transaction_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف تراکنش",
            "آیا از حذف این تراکنش مطمئن هستید؟",
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        delete_finance_transaction(
            transaction_id
        )

        self.refresh()

    # ==================================
    # Categories
    # ==================================

    def create_category_card(
        self,
        category,
    ):
        frame = QFrame()

        frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 6px;
            }
            """
        )

        layout = QHBoxLayout(
            frame
        )

        name = QLabel(
            category["name"]
        )

        name.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            """
        )

        type_label = QLabel(
            TYPE_LABELS[
                category[
                    "transaction_type"
                ]
            ]
        )

        edit_button = QPushButton(
            "ویرایش"
        )

        delete_button = QPushButton(
            "حذف"
        )

        edit_button.clicked.connect(
            lambda _,
            category_id=category["id"]:
            self.open_edit_category(
                category_id
            )
        )

        delete_button.clicked.connect(
            lambda _,
            category_id=category["id"]:
            self.confirm_delete_category(
                category_id
            )
        )

        layout.addWidget(
            name,
            1,
        )

        layout.addWidget(
            type_label
        )

        layout.addWidget(
            edit_button
        )

        layout.addWidget(
            delete_button
        )

        return frame

    def open_add_category(
        self,
        transaction_type: str,
    ):
        dialog = FinanceCategoryDialog(
            self,
            default_type=transaction_type,
        )

        if not dialog.exec():
            return

        try:
            create_finance_category(
                **dialog.get_data()
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def open_edit_category(
        self,
        category_id: int,
    ):
        category = get_finance_category(
            category_id
        )

        if category is None:
            return

        dialog = FinanceCategoryDialog(
            self,
            category=category,
        )

        if not dialog.exec():
            return

        try:
            update_finance_category(
                category_id=category_id,
                **dialog.get_data(),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def confirm_delete_category(
        self,
        category_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف دسته‌بندی",
            "آیا از حذف این دسته‌بندی مطمئن هستید؟",
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            delete_finance_category(
                category_id
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "امکان حذف وجود ندارد",
                str(error),
            )

            return

        self.refresh()

    # ==================================
    # Budgets
    # ==================================

    def open_add_budget(
        self,
    ):
        if not get_finance_categories(
            "expense"
        ):
            QMessageBox.information(
                self,
                "دسته‌بندی هزینه",
                (
                    "ابتدا حداقل یک "
                    "دسته‌بندی هزینه ایجاد کنید."
                ),
            )

            self.tabs.setCurrentWidget(
                self.categories_tab
            )

            return

        dialog = FinanceBudgetDialog(
            jalali_year=self.year,
            jalali_month=self.month,
            parent=self,
        )

        if not dialog.exec():
            return

        try:
            create_finance_budget(
                **dialog.get_data()
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def open_edit_budget(
        self,
        budget_id: int,
    ):
        budget = get_finance_budget(
            budget_id
        )

        if budget is None:
            return

        dialog = FinanceBudgetDialog(
            jalali_year=self.year,
            jalali_month=self.month,
            parent=self,
            budget=budget,
        )

        if not dialog.exec():
            return

        try:
            update_finance_budget(
                budget_id=budget_id,
                **dialog.get_data(),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def confirm_delete_budget(
        self,
        budget_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف بودجه",
            "آیا از حذف این بودجه مطمئن هستید؟",
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        delete_finance_budget(
            budget_id
        )

        self.refresh()

    # ==================================
    # Month navigation
    # ==================================

    def previous_month(
        self,
    ):
        if self.month == 1:
            self.month = 12
            self.year -= 1

        else:
            self.month -= 1

        self.refresh()

    def next_month(
        self,
    ):
        if self.month == 12:
            self.month = 1
            self.year += 1

        else:
            self.month += 1

        self.refresh()

    def current_month(
        self,
    ):
        current = gregorian_to_jalali(
            date.today()
        )

        self.year = current.year
        self.month = current.month

        self.refresh()

    def on_tab_changed(
        self,
        index: int,
    ):
        if (
            self.tabs.widget(index)
            is self.categories_tab
        ):
            self.refresh_categories()

        elif (
            self.tabs.widget(index)
            is self.budgets_tab
        ):
            self.refresh_budgets()

        elif (
            self.tabs.widget(index)
            is self.savings_tab
        ):
            self.savings_tab.refresh()

    # ==================================
    # Helpers
    # ==================================

    def clear_layout(
        self,
        layout,
    ):
        while layout.count():
            item = layout.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()