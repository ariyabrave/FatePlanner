from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from fateplanner.ui.theme import theme_hex
from fateplanner.services.finance_service import (
    format_money,
)
from fateplanner.services.savings_service import (
    add_savings_entry,
    create_savings_goal,
    delete_savings_goal,
    get_savings_goal,
    get_savings_goals,
    get_savings_overview,
    update_savings_goal,
)
from fateplanner.ui.savings_entry_dialog import (
    SavingsEntryDialog,
)
from fateplanner.ui.savings_goal_dialog import (
    SavingsGoalDialog,
)
from fateplanner.ui.savings_history_dialog import (
    SavingsHistoryDialog,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
    to_persian_digits,
)


class SavingsGoalsWidget(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout(
            self
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

        self.target_label = (
            self.create_summary_label()
        )

        self.saved_label = (
            self.create_summary_label()
        )

        self.remaining_label = (
            self.create_summary_label()
        )

        self.completed_label = (
            self.create_summary_label()
        )

        overview_layout.addWidget(
            self.target_label
        )

        overview_layout.addWidget(
            self.saved_label
        )

        overview_layout.addWidget(
            self.remaining_label
        )

        overview_layout.addWidget(
            self.completed_label
        )

        layout.addWidget(
            overview_frame
        )

        add_button = QPushButton(
            "＋ هدف پس‌انداز جدید"
        )

        add_button.setMinimumHeight(
            42
        )

        add_button.clicked.connect(
            self.open_add_goal
        )

        layout.addWidget(
            add_button
        )

        self.container = QWidget()

        self.goals_layout = QVBoxLayout(
            self.container
        )

        self.goals_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setWidget(
            self.container
        )

        layout.addWidget(
            scroll,
            1,
        )

        self.refresh()

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

    def refresh(
        self,
    ):
        self.clear_layout(
            self.goals_layout
        )

        overview = (
            get_savings_overview()
        )

        self.target_label.setText(
            "مجموع اهداف\n"
            + to_persian_digits(
                format_money(
                    overview[
                        "total_target"
                    ]
                )
            )
            + " تومان"
        )

        self.saved_label.setText(
            "مجموع پس‌انداز\n"
            + to_persian_digits(
                format_money(
                    overview[
                        "total_saved"
                    ]
                )
            )
            + " تومان"
        )

        self.remaining_label.setText(
            "باقی‌مانده اهداف\n"
            + to_persian_digits(
                format_money(
                    overview[
                        "total_remaining"
                    ]
                )
            )
            + " تومان"
        )

        self.completed_label.setText(
            "اهداف تکمیل‌شده\n"
            + to_persian_digits(
                overview[
                    "completed_goals"
                ]
            )
            + " از "
            + to_persian_digits(
                overview[
                    "goal_count"
                ]
            )
        )

        goals = get_savings_goals()

        if not goals:
            label = QLabel(
                (
                    "هنوز هدف پس‌اندازی "
                    "ایجاد نشده است."
                )
            )

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setStyleSheet(
                """
                padding: 30px;
                color: palette(window-text);
                """
            )

            self.goals_layout.addWidget(
                label
            )

            return

        for goal in goals:
            self.goals_layout.addWidget(
                self.create_goal_card(
                    goal
                )
            )

    def create_goal_card(
        self,
        goal,
    ):
        frame = QFrame()

        border = (
            theme_hex("success")
            if goal["completed"]
            else theme_hex("border")
        )

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
            goal["title"]
        )

        title.setStyleSheet(
            """
            font-size: 18px;
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
            goal_id=goal["id"]:
            self.open_edit_goal(
                goal_id
            )
        )

        delete_button.clicked.connect(
            lambda _,
            goal_id=goal["id"]:
            self.confirm_delete_goal(
                goal_id
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

        if goal["description"]:
            description = QLabel(
                goal["description"]
            )

            description.setWordWrap(
                True
            )

            layout.addWidget(
                description
            )

        target = to_persian_digits(
            format_money(
                goal["target_amount"]
            )
        )

        saved = to_persian_digits(
            format_money(
                goal["current_amount"]
            )
        )

        remaining = to_persian_digits(
            format_money(
                goal[
                    "remaining_amount"
                ]
            )
        )

        amounts = QLabel(
            f"هدف: {target} تومان"
            "  |  "
            f"پس‌انداز شده: {saved} تومان"
            "  |  "
            f"باقی‌مانده: {remaining} تومان"
        )

        amounts.setWordWrap(
            True
        )

        layout.addWidget(
            amounts
        )

        if goal["target_date"]:
            target_date = (
                date.fromisoformat(
                    goal["target_date"]
                )
            )

            deadline = QLabel(
                "تاریخ هدف: "
                + format_jalali_date(
                    target_date
                )
            )

            layout.addWidget(
                deadline
            )

        percentage = int(
            goal["percentage"]
        )

        progress_label = QLabel(
            "پیشرفت: "
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

        if goal["completed"]:
            complete_label = QLabel(
                "✓ هدف تکمیل شده است"
            )

            complete_label.setStyleSheet(
                """
                font-weight: bold;
                color: #347342;
                """
            )

            layout.addWidget(
                complete_label
            )

        actions = QHBoxLayout()

        deposit_button = QPushButton(
            "＋ واریز"
        )

        withdrawal_button = QPushButton(
            "− برداشت"
        )

        history_button = QPushButton(
            "تاریخچه"
        )

        deposit_button.clicked.connect(
            lambda _,
            goal_id=goal["id"]:
            self.open_entry(
                goal_id,
                "deposit",
            )
        )

        withdrawal_button.clicked.connect(
            lambda _,
            goal_id=goal["id"]:
            self.open_entry(
                goal_id,
                "withdrawal",
            )
        )

        history_button.clicked.connect(
            lambda _,
            goal_id=goal["id"]:
            self.open_history(
                goal_id
            )
        )

        actions.addWidget(
            deposit_button
        )

        actions.addWidget(
            withdrawal_button
        )

        actions.addWidget(
            history_button
        )

        layout.addLayout(
            actions
        )

        return frame

    def open_add_goal(
        self,
    ):
        dialog = SavingsGoalDialog(
            self
        )

        if not dialog.exec():
            return

        try:
            create_savings_goal(
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

    def open_edit_goal(
        self,
        goal_id: int,
    ):
        goal = get_savings_goal(
            goal_id
        )

        if goal is None:
            return

        dialog = SavingsGoalDialog(
            self,
            goal=goal,
        )

        if not dialog.exec():
            return

        try:
            update_savings_goal(
                goal_id=goal_id,
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

    def confirm_delete_goal(
        self,
        goal_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف هدف پس‌انداز",
            (
                "با حذف این هدف، تمام "
                "تاریخچه واریز و برداشت آن "
                "هم حذف می‌شود. ادامه می‌دهید؟"
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

        delete_savings_goal(
            goal_id
        )

        self.refresh()

    def open_entry(
        self,
        goal_id: int,
        entry_type: str,
    ):
        goal = get_savings_goal(
            goal_id
        )

        if goal is None:
            return

        dialog = SavingsEntryDialog(
            goal,
            self,
            default_type=entry_type,
        )

        if not dialog.exec():
            return

        try:
            add_savings_entry(
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

    def open_history(
        self,
        goal_id: int,
    ):
        dialog = SavingsHistoryDialog(
            goal_id,
            self,
            on_data_changed=self.refresh,
        )

        dialog.exec()

        self.refresh()

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