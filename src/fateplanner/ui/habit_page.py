from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
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

from fateplanner.services.habit_service import (
    create_habit,
    delete_habit,
    get_habit,
    get_habit_progress_for_date,
    get_habit_stats,
    get_habits,
    is_habit_completed,
    is_habit_scheduled_on_date,
    set_habit_completed,
    update_habit,
)
from fateplanner.ui.habit_dialog import (
    HabitDialog,
)
from fateplanner.ui.habit_history_dialog import (
    HabitHistoryDialog,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
    to_persian_digits,
)


WEEKDAYS = [
    (5, "شنبه"),
    (6, "یکشنبه"),
    (0, "دوشنبه"),
    (1, "سه‌شنبه"),
    (2, "چهارشنبه"),
    (3, "پنجشنبه"),
    (4, "جمعه"),
]


class HabitPage(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "عادت‌ها"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        self.date_label = QLabel()

        self.main_layout.addWidget(
            title
        )

        self.main_layout.addWidget(
            self.date_label
        )

        progress_frame = QFrame()

        progress_layout = QVBoxLayout(
            progress_frame
        )

        self.progress_label = QLabel(
            "پیشرفت عادت‌های امروز: ۰٪"
        )

        self.progress_label.setStyleSheet(
            """
            font-size: 19px;
            font-weight: bold;
            """
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100,
        )

        self.progress_details = QLabel(
            ""
        )

        progress_layout.addWidget(
            self.progress_label
        )

        progress_layout.addWidget(
            self.progress_bar
        )

        progress_layout.addWidget(
            self.progress_details
        )

        self.main_layout.addWidget(
            progress_frame
        )

        add_button = QPushButton(
            "＋ افزودن عادت"
        )

        add_button.setMinimumHeight(
            45
        )

        add_button.clicked.connect(
            self.open_add_dialog
        )

        self.main_layout.addWidget(
            add_button
        )

        habits_title = QLabel(
            "عادت‌های من"
        )

        habits_title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            margin-top: 10px;
            """
        )

        self.main_layout.addWidget(
            habits_title
        )

        self.container = QWidget()

        self.habits_layout = QVBoxLayout(
            self.container
        )

        self.habits_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setWidget(
            self.container
        )

        self.main_layout.addWidget(
            scroll,
            1,
        )

        self.refresh()

    def refresh(
        self,
    ):
        today = date.today()

        today_iso = (
            today.isoformat()
        )

        self.date_label.setText(
            format_jalali_date(
                today
            )
        )

        self.clear_layout(
            self.habits_layout
        )

        habits = get_habits()

        if not habits:
            self.add_empty_message(
                "هنوز عادتی ساخته نشده است 🌱"
            )

        else:
            for habit in habits:
                self.habits_layout.addWidget(
                    self.create_habit_card(
                        habit,
                        today_iso,
                    )
                )

        (
            total,
            completed,
            percentage,
        ) = get_habit_progress_for_date(
            today_iso
        )

        self.progress_label.setText(
            "پیشرفت عادت‌های امروز: "
            f"{to_persian_digits(percentage)}٪"
        )

        self.progress_bar.setValue(
            percentage
        )

        if total == 0:
            self.progress_details.setText(
                "برای امروز عادتی برنامه‌ریزی نشده است."
            )

        else:
            self.progress_details.setText(
                f"{to_persian_digits(completed)} "
                f"از {to_persian_digits(total)} "
                "عادت انجام شده"
            )

    def create_habit_card(
        self,
        habit,
        today_iso: str,
    ):
        frame = QFrame()

        frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d8d8d8;
                border-radius: 10px;
                padding: 8px;
            }
            """
        )

        layout = QVBoxLayout(
            frame
        )

        title = QLabel(
            habit["title"]
        )

        title.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            title
        )

        if habit["description"]:
            description = QLabel(
                habit["description"]
            )

            description.setWordWrap(
                True
            )

            layout.addWidget(
                description
            )

        schedule = QLabel(
            self.schedule_text(
                habit
            )
        )

        schedule.setStyleSheet(
            """
            font-size: 12px;
            color: #777;
            """
        )

        layout.addWidget(
            schedule
        )

        scheduled_today = (
            is_habit_scheduled_on_date(
                habit,
                today_iso,
            )
        )

        if scheduled_today:
            completed = (
                is_habit_completed(
                    habit["id"],
                    today_iso,
                )
            )

            checkbox = QCheckBox(
                "انجام شد امروز"
            )

            checkbox.setChecked(
                completed
            )

            checkbox.toggled.connect(
                lambda checked,
                habit_id=habit["id"]:
                self.toggle_habit(
                    habit_id,
                    checked,
                )
            )

            layout.addWidget(
                checkbox
            )

        else:
            not_today = QLabel(
                "امروز در برنامه این عادت نیست."
            )

            not_today.setStyleSheet(
                """
                color: #777;
                font-size: 12px;
                """
            )

            layout.addWidget(
                not_today
            )

        stats = get_habit_stats(
            habit["id"],
            through_date=today_iso,
        )

        streak_text = QLabel(
            "🔥 تداوم فعلی: "
            f"{to_persian_digits(stats['current_streak'])} روز"
            "  |  "
            "🏆 بهترین تداوم: "
            f"{to_persian_digits(stats['best_streak'])} روز"
        )

        streak_text.setStyleSheet(
            """
            font-weight: bold;
            """
        )

        layout.addWidget(
            streak_text
        )

        percentage = (
            stats["percentage"]
        )

        history_label = QLabel(
            "عملکرد کلی: "
            f"{to_persian_digits(percentage)}٪"
        )

        layout.addWidget(
            history_label
        )

        progress = QProgressBar()

        progress.setRange(
            0,
            100,
        )

        progress.setValue(
            percentage
        )

        progress.setMaximumHeight(
            18
        )

        layout.addWidget(
            progress
        )

        buttons = QHBoxLayout()

        history_button = QPushButton(
            "تاریخچه"
        )

        edit_button = QPushButton(
            "ویرایش"
        )

        delete_button = QPushButton(
            "حذف"
        )

        history_button.clicked.connect(
            lambda _,
            habit_id=habit["id"]:
            self.open_history(
                habit_id
            )
        )

        edit_button.clicked.connect(
            lambda _,
            habit_id=habit["id"]:
            self.open_edit_dialog(
                habit_id
            )
        )

        delete_button.clicked.connect(
            lambda _,
            habit_id=habit["id"]:
            self.confirm_delete(
                habit_id
            )
        )

        buttons.addWidget(
            history_button
        )

        buttons.addWidget(
            edit_button
        )

        buttons.addWidget(
            delete_button
        )

        layout.addLayout(
            buttons
        )

        return frame

    def schedule_text(
        self,
        habit,
    ) -> str:
        if (
            habit["schedule_type"]
            == "daily"
        ):
            return "برنامه: هر روز"

        selected = set()

        if habit["weekdays"]:
            selected = {
                int(day)
                for day
                in habit["weekdays"].split(",")
                if day.strip()
            }

        labels = [
            label
            for weekday, label
            in WEEKDAYS
            if weekday in selected
        ]

        return (
            "برنامه: "
            + "، ".join(
                labels
            )
        )

    def open_add_dialog(
        self,
    ):
        dialog = HabitDialog(
            self
        )

        if not dialog.exec():
            return

        try:
            create_habit(
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

    def open_edit_dialog(
        self,
        habit_id: int,
    ):
        habit = get_habit(
            habit_id
        )

        if habit is None:
            return

        dialog = HabitDialog(
            self,
            habit=habit,
        )

        if not dialog.exec():
            return

        try:
            update_habit(
                habit_id=habit_id,
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

    def open_history(
        self,
        habit_id: int,
    ):
        dialog = HabitHistoryDialog(
            habit_id,
            self,
        )

        dialog.exec()

        self.refresh()

    def toggle_habit(
        self,
        habit_id: int,
        completed: bool,
    ):
        try:
            set_habit_completed(
                habit_id,
                date.today().isoformat(),
                completed,
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def confirm_delete(
        self,
        habit_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف عادت",
            (
                "آیا از حذف این عادت و "
                "تمام سابقه آن مطمئن هستی؟"
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

        delete_habit(
            habit_id
        )

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

    def add_empty_message(
        self,
        text: str,
    ):
        label = QLabel(
            text
        )

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        label.setStyleSheet(
            """
            font-size: 16px;
            padding: 30px;
            """
        )

        self.habits_layout.addWidget(
            label
        )