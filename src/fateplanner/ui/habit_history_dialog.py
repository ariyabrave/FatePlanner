from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.habit_service import (
    get_habit,
    get_habit_logs_between,
    get_habit_month_stats,
    get_habit_stats,
    is_habit_scheduled_on_date,
    set_habit_completed,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
    format_jalali_month_title,
    get_jalali_month_dates,
    get_persian_weekday_column,
    gregorian_to_jalali,
    to_persian_digits,
)


WEEKDAY_HEADERS = [
    "شنبه",
    "یکشنبه",
    "دوشنبه",
    "سه‌شنبه",
    "چهارشنبه",
    "پنجشنبه",
    "جمعه",
]


class HabitHistoryDialog(QDialog):
    def __init__(
        self,
        habit_id: int,
        parent=None,
    ):
        super().__init__(parent)

        self.habit_id = habit_id

        today_jalali = (
            gregorian_to_jalali(
                date.today()
            )
        )

        self.year = (
            today_jalali.year
        )

        self.month = (
            today_jalali.month
        )

        self.setWindowTitle(
            "تاریخچه عادت"
        )

        self.resize(
            820,
            680,
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        main_layout = QVBoxLayout(
            self
        )

        self.habit_title = QLabel()

        self.habit_title.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            self.habit_title
        )

        # Month navigation
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
            font-size: 19px;
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

        # Monthly stats
        stats_frame = QFrame()

        stats_layout = QVBoxLayout(
            stats_frame
        )

        self.month_progress_label = QLabel()

        self.month_progress_label.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            """
        )

        self.month_details_label = QLabel()

        self.streak_label = QLabel()

        self.streak_label.setStyleSheet(
            """
            font-weight: bold;
            """
        )

        stats_layout.addWidget(
            self.month_progress_label
        )

        stats_layout.addWidget(
            self.month_details_label
        )

        stats_layout.addWidget(
            self.streak_label
        )

        main_layout.addWidget(
            stats_frame
        )

        # Legend
        legend = QLabel(
            "✓ انجام شده   "
            "× انجام نشده   "
            "— بدون برنامه   "
            "… آینده"
        )

        legend.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addWidget(
            legend
        )

        # Calendar
        self.calendar_widget = QWidget()

        self.calendar_layout = QGridLayout(
            self.calendar_widget
        )

        self.calendar_layout.setSpacing(
            6
        )

        main_layout.addWidget(
            self.calendar_widget,
            1,
        )

        close_button = QPushButton(
            "بستن"
        )

        close_button.clicked.connect(
            self.accept
        )

        main_layout.addWidget(
            close_button
        )

        self.refresh()

    def refresh(
        self,
    ):
        habit = get_habit(
            self.habit_id
        )

        if habit is None:
            QMessageBox.warning(
                self,
                "خطا",
                "عادت پیدا نشد.",
            )

            self.reject()
            return

        self.habit_title.setText(
            habit["title"]
        )

        self.month_label.setText(
            format_jalali_month_title(
                self.year,
                self.month,
            )
        )

        today = date.today()

        monthly_stats = (
            get_habit_month_stats(
                self.habit_id,
                self.year,
                self.month,
                through_date=(
                    today.isoformat()
                ),
            )
        )

        overall_stats = (
            get_habit_stats(
                self.habit_id,
                through_date=(
                    today.isoformat()
                ),
            )
        )

        self.month_progress_label.setText(
            "عملکرد این ماه: "
            f"{to_persian_digits(monthly_stats['percentage'])}٪"
        )

        self.month_details_label.setText(
            "انجام شده: "
            f"{to_persian_digits(monthly_stats['completed'])}"
            "   |   "
            "از دست رفته: "
            f"{to_persian_digits(monthly_stats['missed'])}"
            "   |   "
            "روزهای برنامه‌ریزی‌شده: "
            f"{to_persian_digits(monthly_stats['scheduled'])}"
        )

        self.streak_label.setText(
            "🔥 تداوم فعلی: "
            f"{to_persian_digits(overall_stats['current_streak'])} روز"
            "   |   "
            "🏆 بهترین تداوم: "
            f"{to_persian_digits(overall_stats['best_streak'])} روز"
        )

        self.clear_calendar()

        for column, label in enumerate(
            WEEKDAY_HEADERS
        ):
            header = QLabel(
                label
            )

            header.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            header.setStyleSheet(
                """
                font-weight: bold;
                padding: 6px;
                """
            )

            self.calendar_layout.addWidget(
                header,
                0,
                column,
            )

        month_dates = (
            get_jalali_month_dates(
                self.year,
                self.month,
            )
        )

        logs = get_habit_logs_between(
            self.habit_id,
            month_dates[0].isoformat(),
            month_dates[-1].isoformat(),
        )

        completed_dates = {
            row["log_date"]
            for row in logs
            if row["completed"]
        }

        first_column = (
            get_persian_weekday_column(
                month_dates[0]
            )
        )

        for index, gregorian_date in enumerate(
            month_dates
        ):
            position = (
                first_column
                + index
            )

            row = (
                position // 7
                + 1
            )

            column = (
                position % 7
            )

            button = self.create_day_button(
                habit,
                gregorian_date,
                completed_dates,
            )

            self.calendar_layout.addWidget(
                button,
                row,
                column,
            )

    def create_day_button(
        self,
        habit,
        gregorian_date: date,
        completed_dates: set[str],
    ) -> QPushButton:
        jalali_date = (
            gregorian_to_jalali(
                gregorian_date
            )
        )

        day_text = to_persian_digits(
            jalali_date.day
        )

        iso_date = (
            gregorian_date.isoformat()
        )

        scheduled = (
            is_habit_scheduled_on_date(
                habit,
                gregorian_date,
            )
        )

        completed = (
            iso_date
            in completed_dates
        )

        is_future = (
            gregorian_date
            > date.today()
        )

        is_today = (
            gregorian_date
            == date.today()
        )

        button = QPushButton()

        button.setMinimumSize(
            82,
            64,
        )

        button.setToolTip(
            format_jalali_date(
                gregorian_date
            )
        )

        if not scheduled:
            symbol = "—"

            button.setEnabled(
                False
            )

            background = "#f2f2f2"
            border = "#dddddd"
            text_color = "#999999"

        elif is_future:
            symbol = "…"

            button.setEnabled(
                False
            )

            background = "#f5f5f5"
            border = "#dddddd"
            text_color = "#888888"

        elif completed:
            symbol = "✓"

            background = "#dff3e3"
            border = "#75b882"
            text_color = "#245d32"

            button.clicked.connect(
                lambda _,
                selected_date=gregorian_date:
                self.toggle_date(
                    selected_date
                )
            )

        else:
            symbol = "×"

            background = "#f8e2e2"
            border = "#cf8b8b"
            text_color = "#7d3030"

            button.clicked.connect(
                lambda _,
                selected_date=gregorian_date:
                self.toggle_date(
                    selected_date
                )
            )

        if is_today:
            border_rule = (
                "2px solid #6666cc"
            )
        else:
            border_rule = (
                f"1px solid {border}"
            )

        button.setText(
            f"{day_text}\n{symbol}"
        )

        button.setStyleSheet(
            f"""
            QPushButton {{
                background: {background};
                color: {text_color};
                border: {border_rule};
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 5px;
            }}
            """
        )

        return button

    def toggle_date(
        self,
        selected_date: date,
    ):
        habit = get_habit(
            self.habit_id
        )

        if habit is None:
            return

        if not is_habit_scheduled_on_date(
            habit,
            selected_date,
        ):
            return

        if selected_date > date.today():
            return

        selected_iso = (
            selected_date.isoformat()
        )

        logs = get_habit_logs_between(
            self.habit_id,
            selected_iso,
            selected_iso,
        )

        currently_completed = any(
            row["completed"]
            for row in logs
        )

        try:
            set_habit_completed(
                self.habit_id,
                selected_iso,
                not currently_completed,
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

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
        current = (
            gregorian_to_jalali(
                date.today()
            )
        )

        self.year = (
            current.year
        )

        self.month = (
            current.month
        )

        self.refresh()

    def clear_calendar(
        self,
    ):
        while (
            self.calendar_layout.count()
        ):
            item = (
                self.calendar_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()