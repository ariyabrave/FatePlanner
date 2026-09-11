from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.task_center_service import (
    get_task_center_summary,
    get_task_center_tasks,
    set_task_center_completed,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
    format_jalali_short,
    to_persian_digits,
)


PRIORITY_LABELS = {
    "low": "کم",
    "normal": "معمولی",
    "medium": "متوسط",
    "high": "زیاد",
}


class TaskCenterPage(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "کارها"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        self.date_label = QLabel()

        layout.addWidget(
            title
        )

        layout.addWidget(
            self.date_label
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

        self.today_label = (
            self.create_summary_label()
        )

        self.overdue_label = (
            self.create_summary_label()
        )

        self.upcoming_label = (
            self.create_summary_label()
        )

        self.unscheduled_label = (
            self.create_summary_label()
        )

        self.completed_label = (
            self.create_summary_label()
        )

        summary_layout.addWidget(
            self.today_label
        )

        summary_layout.addWidget(
            self.overdue_label
        )

        summary_layout.addWidget(
            self.upcoming_label
        )

        summary_layout.addWidget(
            self.unscheduled_label
        )

        summary_layout.addWidget(
            self.completed_label
        )

        layout.addWidget(
            summary_frame
        )

        filters = QHBoxLayout()

        self.filter_input = QComboBox()

        self.filter_input.addItem(
            "کارهای باز",
            "open",
        )

        self.filter_input.addItem(
            "امروز",
            "today",
        )

        self.filter_input.addItem(
            "عقب‌افتاده",
            "overdue",
        )

        self.filter_input.addItem(
            "آینده",
            "upcoming",
        )

        self.filter_input.addItem(
            "بدون تاریخ",
            "unscheduled",
        )

        self.filter_input.addItem(
            "انجام‌شده",
            "completed",
        )

        self.filter_input.addItem(
            "همه",
            "all",
        )

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "جستجو در کارها..."
        )

        self.filter_input.currentIndexChanged.connect(
            self.refresh_tasks
        )

        self.search_input.textChanged.connect(
            self.refresh_tasks
        )

        filters.addWidget(
            QLabel(
                "نمایش:"
            )
        )

        filters.addWidget(
            self.filter_input
        )

        filters.addWidget(
            self.search_input,
            1,
        )

        layout.addLayout(
            filters
        )

        info = QLabel(
            "مدیریت جزئیات و زمان‌بندی دقیق از "
            "برنامه روزانه و برنامه هفتگی انجام می‌شود؛ "
            "این صفحه نمای مرکزی همه کارهاست."
        )

        info.setWordWrap(
            True
        )

        info.setStyleSheet(
            """
            color: palette(window-text);
            padding: 4px;
            """
        )

        layout.addWidget(
            info
        )

        self.table = QTableWidget()

        self.table.setColumnCount(
            7
        )

        self.table.setHorizontalHeaderLabels(
            [
                "انجام",
                "عنوان",
                "تاریخ",
                "زمان",
                "اولویت",
                "نوع",
                "توضیحات",
            ]
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(
            self.table,
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

        label.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            padding: 8px;
            """
        )

        return label

    def refresh(
        self,
    ):
        today = date.today()

        self.date_label.setText(
            format_jalali_date(
                today
            )
        )

        summary = (
            get_task_center_summary(
                today.isoformat()
            )
        )

        self.today_label.setText(
            "امروز\n"
            + to_persian_digits(
                summary["today"]
            )
        )

        self.overdue_label.setText(
            "عقب‌افتاده\n"
            + to_persian_digits(
                summary["overdue"]
            )
        )

        self.upcoming_label.setText(
            "آینده\n"
            + to_persian_digits(
                summary["upcoming"]
            )
        )

        self.unscheduled_label.setText(
            "بدون تاریخ\n"
            + to_persian_digits(
                summary[
                    "unscheduled"
                ]
            )
        )

        self.completed_label.setText(
            "انجام‌شده\n"
            + to_persian_digits(
                summary[
                    "completed"
                ]
            )
        )

        self.refresh_tasks()

    def refresh_tasks(
        self,
        *args,
    ):
        rows = get_task_center_tasks(
            filter_mode=(
                self.filter_input
                .currentData()
            ),
            search=(
                self.search_input
                .text()
            ),
        )

        self.table.setRowCount(
            len(rows)
        )

        for row_index, task in enumerate(
            rows
        ):
            checkbox = QCheckBox()

            checkbox.setChecked(
                bool(
                    task["completed"]
                )
            )

            checkbox.setStyleSheet(
                """
                margin-left: auto;
                margin-right: auto;
                """
            )

            checkbox.toggled.connect(
                lambda checked,
                task_id=task["id"]:
                self.toggle_task(
                    task_id,
                    checked,
                )
            )

            self.table.setCellWidget(
                row_index,
                0,
                checkbox,
            )

            if task["due_date"]:
                task_date = (
                    date.fromisoformat(
                        task["due_date"]
                    )
                )

                date_text = (
                    format_jalali_short(
                        task_date
                    )
                )

            else:
                date_text = (
                    "بدون تاریخ"
                )

            if task["all_day"]:
                time_text = "تمام روز"

            elif task["start_time"]:
                time_text = (
                    task["start_time"]
                )

                if task["end_time"]:
                    time_text += (
                        " تا "
                        + task[
                            "end_time"
                        ]
                    )

            else:
                time_text = "—"

            recurring_text = (
                "تکرارشونده"
                if task[
                    "recurring_template_id"
                ]
                is not None
                else "عادی"
            )

            values = [
                task["title"],
                date_text,
                time_text,
                PRIORITY_LABELS.get(
                    task["priority"],
                    task["priority"],
                ),
                recurring_text,
                (
                    task["description"]
                    or "—"
                ),
            ]

            for column, value in enumerate(
                values,
                start=1,
            ):
                item = QTableWidgetItem(
                    str(value)
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.table.setItem(
                    row_index,
                    column,
                    item,
                )

    def toggle_task(
        self,
        task_id,
        checked,
    ):
        set_task_center_completed(
            task_id,
            checked,
        )

        self.refresh()

    def showEvent(
        self,
        event,
    ):
        super().showEvent(
            event
        )

        self.refresh()