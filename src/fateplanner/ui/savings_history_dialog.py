from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.finance_service import (
    format_money,
)
from fateplanner.services.savings_service import (
    delete_savings_entry,
    get_savings_entries,
    get_savings_goal,
)
from fateplanner.utils.date_utils import (
    format_jalali_short,
    to_persian_digits,
)


ENTRY_LABELS = {
    "deposit": "واریز",
    "withdrawal": "برداشت",
}


class SavingsHistoryDialog(QDialog):
    def __init__(
        self,
        goal_id: int,
        parent=None,
        on_data_changed=None,
    ):
        super().__init__(parent)

        self.goal_id = goal_id

        self.on_data_changed = (
            on_data_changed
        )

        self.setWindowTitle(
            "تاریخچه پس‌انداز"
        )

        self.resize(
            760,
            520,
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        layout = QVBoxLayout(
            self
        )

        self.title_label = QLabel()

        self.title_label.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        self.summary_label = QLabel()

        self.summary_label.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            self.title_label
        )

        layout.addWidget(
            self.summary_label
        )

        self.table = QTableWidget()

        self.table.setColumnCount(
            5
        )

        self.table.setHorizontalHeaderLabels(
            [
                "تاریخ",
                "نوع",
                "مبلغ",
                "یادداشت",
                "عملیات",
            ]
        )

        self.table.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(
            self.table,
            1,
        )

        close_button = QPushButton(
            "بستن"
        )

        close_button.clicked.connect(
            self.accept
        )

        layout.addWidget(
            close_button
        )

        self.refresh()

    def refresh(
        self,
    ):
        goal = get_savings_goal(
            self.goal_id
        )

        if goal is None:
            self.reject()
            return

        self.title_label.setText(
            goal["title"]
        )

        saved = to_persian_digits(
            format_money(
                goal["current_amount"]
            )
        )

        target = to_persian_digits(
            format_money(
                goal["target_amount"]
            )
        )

        self.summary_label.setText(
            f"پس‌انداز شده: {saved} تومان"
            "  |  "
            f"هدف: {target} تومان"
        )

        entries = get_savings_entries(
            self.goal_id
        )

        self.table.setRowCount(
            len(
                entries
            )
        )

        for row_index, entry in enumerate(
            entries
        ):
            entry_date = date.fromisoformat(
                entry["entry_date"]
            )

            values = [
                format_jalali_short(
                    entry_date
                ),
                ENTRY_LABELS[
                    entry["entry_type"]
                ],
                (
                    to_persian_digits(
                        format_money(
                            entry["amount"]
                        )
                    )
                    + " تومان"
                ),
                entry["note"] or "—",
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

                self.table.setItem(
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

            delete_button = QPushButton(
                "حذف"
            )

            delete_button.clicked.connect(
                lambda _,
                entry_id=entry["id"]:
                self.confirm_delete(
                    entry_id
                )
            )

            action_layout.addWidget(
                delete_button
            )

            self.table.setCellWidget(
                row_index,
                4,
                action_widget,
            )

    def confirm_delete(
        self,
        entry_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف رکورد",
            (
                "آیا از حذف این رکورد "
                "پس‌انداز مطمئن هستید؟"
            ),
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
            delete_savings_entry(
                entry_id
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "امکان حذف وجود ندارد",
                str(error),
            )

            return

        self.refresh()

        if self.on_data_changed:
            self.on_data_changed()