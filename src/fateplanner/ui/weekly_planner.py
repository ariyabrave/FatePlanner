from datetime import (
    date,
    timedelta,
)

from PySide6.QtCore import (
    QDate,
    Qt,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.recurrence_service import (
    create_recurring_series,
    ensure_recurring_instances_through,
    generate_recurring_instances,
)
from fateplanner.services.task_service import (
    create_task,
    get_tasks_for_date,
    set_task_completed,
)
from fateplanner.ui.task_dialog import (
    TaskDialog,
)
from fateplanner.utils.date_utils import (
    PERSIAN_WEEKDAY_NAMES,
    format_jalali_short,
    format_jalali_week_range,
    get_persian_week,
)


class WeeklyPlanner(QWidget):
    def __init__(
        self,
        parent=None,
        on_data_changed=None,
        on_edit_task=None,
        on_delete_task=None,
    ):
        super().__init__(parent)

        self.anchor_date = (
            date.today()
        )

        self.on_data_changed = (
            on_data_changed
        )

        self.on_edit_task = (
            on_edit_task
        )

        self.on_delete_task = (
            on_delete_task
        )

        self.main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "تقویم و برنامه‌ریزی"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        self.main_layout.addWidget(
            title
        )

        navigation_layout = (
            QHBoxLayout()
        )

        self.previous_button = QPushButton(
            "هفته قبل"
        )

        self.today_button = QPushButton(
            "امروز"
        )

        self.next_button = QPushButton(
            "هفته بعد"
        )

        self.week_label = QLabel()

        self.week_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.week_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        self.previous_button.clicked.connect(
            self.previous_week
        )

        self.today_button.clicked.connect(
            self.go_to_today
        )

        self.next_button.clicked.connect(
            self.next_week
        )

        navigation_layout.addWidget(
            self.previous_button
        )

        navigation_layout.addWidget(
            self.today_button
        )

        navigation_layout.addWidget(
            self.week_label,
            1,
        )

        navigation_layout.addWidget(
            self.next_button
        )

        self.main_layout.addLayout(
            navigation_layout
        )

        self.days_container = QWidget()

        self.days_layout = QHBoxLayout(
            self.days_container
        )

        self.days_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(
            True
        )

        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        scroll_area.setWidget(
            self.days_container
        )

        self.main_layout.addWidget(
            scroll_area,
            1,
        )

        self.refresh()

    def refresh(
        self,
    ):
        self.clear_days()

        week = get_persian_week(
            self.anchor_date
        )

        ensure_recurring_instances_through(
            week[-1].isoformat()
        )

        self.week_label.setText(
            format_jalali_week_range(
                week[0],
                week[-1],
            )
        )

        for day in week:
            self.days_layout.addWidget(
                self.create_day_card(
                    day
                )
            )

    def create_day_card(
        self,
        day: date,
    ) -> QFrame:

        frame = QFrame()

        frame.setMinimumWidth(
            145
        )

        frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 8px;
            }
            """
        )

        layout = QVBoxLayout(
            frame
        )

        weekday_label = QLabel(
            PERSIAN_WEEKDAY_NAMES[
                day.weekday()
            ]
        )

        weekday_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        weekday_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        date_label = QLabel(
            format_jalali_short(
                day
            )
        )

        date_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            weekday_label
        )

        layout.addWidget(
            date_label
        )

        if day == date.today():
            today_label = QLabel(
                "امروز"
            )

            today_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            today_label.setStyleSheet(
                """
                font-weight: bold;
                """
            )

            layout.addWidget(
                today_label
            )

        tasks = get_tasks_for_date(
            day.isoformat()
        )

        if not tasks:
            empty_label = QLabel(
                "برنامه‌ای ثبت نشده"
            )

            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty_label.setWordWrap(
                True
            )

            layout.addWidget(
                empty_label
            )

        else:
            for task in tasks:
                layout.addWidget(
                    self.create_task_widget(
                        task
                    )
                )

        layout.addStretch()

        add_button = QPushButton(
            "＋ افزودن"
        )

        add_button.clicked.connect(
            lambda _,
            selected_day=day:
            self.open_task_dialog(
                selected_day
            )
        )

        layout.addWidget(
            add_button
        )

        return frame

    def create_task_widget(
        self,
        task,
    ) -> QWidget:

        widget = QWidget()

        layout = QVBoxLayout(
            widget
        )

        layout.setContentsMargins(
            2,
            2,
            2,
            2,
        )

        title = task["title"]

        if task["recurring_template_id"]:
            title = (
                "↻ "
                + title
            )

        checkbox = QCheckBox(
            title
        )

        checkbox.setChecked(
            bool(
                task["completed"]
            )
        )

        checkbox.toggled.connect(
            lambda checked,
            task_id=task["id"]:
            self.toggle_task(
                task_id,
                checked,
            )
        )

        layout.addWidget(
            checkbox
        )

        if task["all_day"]:
            schedule_text = (
                "تمام روز"
            )

        elif (
            task["start_time"]
            and task["end_time"]
        ):
            schedule_text = (
                f"{task['start_time']} "
                f"تا "
                f"{task['end_time']}"
            )

        else:
            schedule_text = (
                "بدون ساعت"
            )

        schedule_label = QLabel(
            schedule_text
        )

        schedule_label.setStyleSheet(
            """
            font-size: 11px;
            color: palette(window-text);
            """
        )

        layout.addWidget(
            schedule_label
        )

        action_layout = QHBoxLayout()

        if self.on_edit_task:
            edit_button = QPushButton(
                "ویرایش"
            )

            edit_button.clicked.connect(
                lambda _,
                task_id=task["id"]:
                self.on_edit_task(
                    task_id
                )
            )

            action_layout.addWidget(
                edit_button
            )

        if self.on_delete_task:
            delete_button = QPushButton(
                "حذف"
            )

            delete_button.clicked.connect(
                lambda _,
                task_id=task["id"]:
                self.on_delete_task(
                    task_id
                )
            )

            action_layout.addWidget(
                delete_button
            )

        if action_layout.count():
            layout.addLayout(
                action_layout
            )

        return widget

    def open_task_dialog(
        self,
        selected_day: date,
    ):
        qt_date = QDate(
            selected_day.year,
            selected_day.month,
            selected_day.day,
        )

        dialog = TaskDialog(
            self,
            default_date=qt_date,
        )

        if not dialog.exec():
            return

        task_data = (
            dialog.get_task_data()
        )

        recurrence_data = (
            dialog.get_recurrence_data()
        )

        try:
            if (
                recurrence_data[
                    "recurrence_type"
                ]
                == "none"
            ):
                create_task(
                    **task_data
                )

            else:
                template_id = (
                    create_recurring_series(
                        title=task_data[
                            "title"
                        ],
                        description=task_data[
                            "description"
                        ],
                        start_time=task_data[
                            "start_time"
                        ],
                        end_time=task_data[
                            "end_time"
                        ],
                        all_day=task_data[
                            "all_day"
                        ],
                        priority=task_data[
                            "priority"
                        ],
                        recurrence_type=(
                            recurrence_data[
                                "recurrence_type"
                            ]
                        ),
                        recurrence_start_date=(
                            task_data[
                                "due_date"
                            ]
                        ),
                        recurrence_weekdays=(
                            recurrence_data[
                                "recurrence_weekdays"
                            ]
                        ),
                        recurrence_end_date=(
                            recurrence_data[
                                "recurrence_end_date"
                            ]
                        ),
                    )
                )

                generate_recurring_instances(
                    template_id,
                    selected_day.isoformat(),
                )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

        if self.on_data_changed:
            self.on_data_changed()

    def toggle_task(
        self,
        task_id: int,
        completed: bool,
    ):
        set_task_completed(
            task_id,
            completed,
        )

        self.refresh()

        if self.on_data_changed:
            self.on_data_changed()

    def previous_week(
        self,
    ):
        self.anchor_date -= timedelta(
            days=7
        )

        self.refresh()

    def next_week(
        self,
    ):
        self.anchor_date += timedelta(
            days=7
        )

        self.refresh()

    def go_to_today(
        self,
    ):
        self.anchor_date = date.today()

        self.refresh()

    def clear_days(
        self,
    ):
        while self.days_layout.count():
            item = (
                self.days_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()