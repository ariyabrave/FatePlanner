from datetime import date

from PySide6.QtCore import (
    QDate,
    Qt,
)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.recurrence_service import (
    create_recurring_series,
    delete_recurring_series,
    ensure_recurring_instances_through,
    generate_recurring_instances,
    get_recurring_template,
    update_recurring_series,
)
from fateplanner.services.task_service import (
    create_subtask,
    create_task,
    delete_task,
    get_subtask_progress,
    get_subtasks,
    get_task,
    get_task_progress,
    get_task_progress_for_date,
    get_tasks,
    get_tasks_for_date,
    set_task_completed,
    update_task,
)
from fateplanner.ui.analytics_page import (
    AnalyticsPage,
)
from fateplanner.ui.settings_page import (
    SettingsPage,
)
from fateplanner.ui.finance_page import (
    FinancePage,
)
from fateplanner.ui.habit_page import (
    HabitPage,
)
from fateplanner.ui.recurring_series_dialog import (
    RecurringSeriesDialog,
)
from fateplanner.ui.study_page import (
    StudyPage,
)
from fateplanner.ui.subtask_dialog import (
    SubtaskDialog,
)
from fateplanner.ui.task_dialog import (
    TaskDialog,
)
from fateplanner.ui.weekly_planner import (
    WeeklyPlanner,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
    format_jalali_short,
)


PRIORITY_LABELS = {
    "low": "کم",
    "normal": "معمولی",
    "high": "زیاد",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "FatePlanner"
        )

        self.resize(
            1180,
            780,
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QHBoxLayout(
            central_widget
        )

        self.sidebar = QListWidget()

        self.sidebar.setFixedWidth(
            230
        )

        self.sidebar.addItems(
            [
                "خانه",
                "برنامه امروز",
                "تقویم و برنامه‌ریزی",
                "کارها",
                "عادت‌ها",
                "مطالعه",
                "امور مالی",
                "گزارش‌ها و پیشرفت",
                "تنظیمات",
            ]
        )

        self.pages = QStackedWidget()

        self.home_page = (
            self.create_home_page()
        )

        self.today_page = (
            self.create_today_page()
        )

        self.weekly_page = WeeklyPlanner(
            on_data_changed=(
                self.refresh_all
            ),
            on_edit_task=(
                self.edit_task
            ),
            on_delete_task=(
                self.confirm_delete_task
            ),
        )

        self.tasks_page = (
            self.create_placeholder_page(
                "کارها"
            )
        )

        self.habits_page = HabitPage()

        self.study_page = StudyPage()

        self.finance_page = FinancePage()

        self.analytics_page = AnalyticsPage()

        self.settings_page = SettingsPage()

        self.pages.addWidget(
            self.home_page
        )

        self.pages.addWidget(
            self.today_page
        )

        self.pages.addWidget(
            self.weekly_page
        )

        self.pages.addWidget(
            self.tasks_page
        )

        self.pages.addWidget(
            self.habits_page
        )

        self.pages.addWidget(
            self.study_page
        )

        self.pages.addWidget(
            self.finance_page
        )

        self.pages.addWidget(
            self.analytics_page
        )

        self.pages.addWidget(
            self.settings_page
        )

        remaining_pages = []

        for page_name in remaining_pages:
            self.pages.addWidget(
                self.create_placeholder_page(
                    page_name
                )
            )

        self.sidebar.currentRowChanged.connect(
            self.change_page
        )

        main_layout.addWidget(
            self.sidebar
        )

        main_layout.addWidget(
            self.pages,
            1,
        )

        self.sidebar.setCurrentRow(
            0
        )

        self.refresh_all()

    # ==================================
    # Navigation
    # ==================================

    def change_page(
        self,
        index: int,
    ):
        self.pages.setCurrentIndex(
            index
        )

        if index == 0:
            self.refresh_home()

        elif index == 1:
            self.refresh_today()

        elif index == 2:
            self.weekly_page.refresh()

        elif index == 4:
            self.habits_page.refresh()

        elif index == 5:
            self.study_page.refresh()

        elif index == 6:
            self.finance_page.refresh()

        elif index == 7:
            self.analytics_page.refresh()

        elif index == 8:
            self.settings_page.refresh()

    # ==================================
    # Home
    # ==================================

    def create_home_page(
        self,
    ):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        title = QLabel(
            "سلام 🌷"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        subtitle = QLabel(
            "خوش آمدی به FatePlanner"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        progress_frame = QFrame()

        progress_layout = QVBoxLayout(
            progress_frame
        )

        self.home_progress_label = QLabel(
            "پیشرفت کلی: ۰٪"
        )

        self.home_progress_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        self.home_progress_bar = QProgressBar()

        self.home_progress_bar.setRange(
            0,
            100,
        )

        self.home_progress_details = QLabel(
            ""
        )

        progress_layout.addWidget(
            self.home_progress_label
        )

        progress_layout.addWidget(
            self.home_progress_bar
        )

        progress_layout.addWidget(
            self.home_progress_details
        )

        layout.addWidget(
            progress_frame
        )

        add_button = QPushButton(
            "＋ افزودن کار جدید"
        )

        add_button.setMinimumHeight(
            45
        )

        add_button.clicked.connect(
            self.open_general_task_dialog
        )

        layout.addWidget(
            add_button
        )

        tasks_title = QLabel(
            "همه کارها"
        )

        tasks_title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            margin-top: 15px;
            """
        )

        layout.addWidget(
            tasks_title
        )

        self.home_tasks_container = QWidget()

        self.home_tasks_layout = QVBoxLayout(
            self.home_tasks_container
        )

        self.home_tasks_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setWidget(
            self.home_tasks_container
        )

        layout.addWidget(
            scroll,
            1,
        )

        return page

    # ==================================
    # Today
    # ==================================

    def create_today_page(
        self,
    ):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        title = QLabel(
            "برنامه امروز"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        self.today_date_label = QLabel()

        layout.addWidget(
            title
        )

        layout.addWidget(
            self.today_date_label
        )

        progress_frame = QFrame()

        progress_layout = QVBoxLayout(
            progress_frame
        )

        self.today_progress_label = QLabel(
            "پیشرفت امروز: ۰٪"
        )

        self.today_progress_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        self.today_progress_bar = QProgressBar()

        self.today_progress_bar.setRange(
            0,
            100,
        )

        self.today_progress_details = QLabel(
            ""
        )

        progress_layout.addWidget(
            self.today_progress_label
        )

        progress_layout.addWidget(
            self.today_progress_bar
        )

        progress_layout.addWidget(
            self.today_progress_details
        )

        layout.addWidget(
            progress_frame
        )

        add_today_button = QPushButton(
            "＋ افزودن کار برای امروز"
        )

        add_today_button.setMinimumHeight(
            45
        )

        add_today_button.clicked.connect(
            self.open_today_task_dialog
        )

        layout.addWidget(
            add_today_button
        )

        schedule_title = QLabel(
            "برنامه روز"
        )

        schedule_title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            margin-top: 15px;
            """
        )

        layout.addWidget(
            schedule_title
        )

        self.today_tasks_container = QWidget()

        self.today_tasks_layout = QVBoxLayout(
            self.today_tasks_container
        )

        self.today_tasks_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setWidget(
            self.today_tasks_container
        )

        layout.addWidget(
            scroll,
            1,
        )

        return page

    # ==================================
    # Placeholder
    # ==================================

    def create_placeholder_page(
        self,
        page_name: str,
    ):
        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        title = QLabel(
            page_name
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        message = QLabel(
            "این بخش در مراحل بعدی FatePlanner ساخته می‌شود."
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            message
        )

        layout.addStretch()

        return page

    # ==================================
    # New tasks
    # ==================================

    def open_general_task_dialog(
        self,
    ):
        dialog = TaskDialog(
            self
        )

        if dialog.exec():
            self.save_new_task(
                dialog
            )

    def open_today_task_dialog(
        self,
    ):
        dialog = TaskDialog(
            self,
            default_date=QDate.currentDate(),
        )

        if dialog.exec():
            self.save_new_task(
                dialog
            )

    def save_new_task(
        self,
        dialog: TaskDialog,
    ):
        task_data = dialog.get_task_data()

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
                    task_data[
                        "due_date"
                    ],
                )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh_all()

    # ==================================
    # Edit task
    # ==================================

    def edit_task(
        self,
        task_id: int,
    ):
        task = get_task(
            task_id
        )

        if task is None:
            return

        template_id = (
            task[
                "recurring_template_id"
            ]
        )

        if template_id:
            scope = self.ask_recurring_scope(
                "ویرایش"
            )

            if scope is None:
                return

            if scope == "series":
                self.edit_recurring_series(
                    template_id
                )

                return

        self.edit_single_task(
            task
        )

    def edit_single_task(
        self,
        task,
    ):
        dialog = TaskDialog(
            self,
            task=task,
        )

        if not dialog.exec():
            return

        try:
            update_task(
                task_id=task["id"],
                **dialog.get_task_data(),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh_all()

    def edit_recurring_series(
        self,
        template_id: int,
    ):
        template = get_recurring_template(
            template_id
        )

        if template is None:
            QMessageBox.warning(
                self,
                "خطا",
                "مجموعه تکرارشونده پیدا نشد.",
            )

            return

        dialog = RecurringSeriesDialog(
            template,
            self,
        )

        if not dialog.exec():
            return

        try:
            update_recurring_series(
                template_id=template_id,
                replace_instances_from=(
                    date.today().isoformat()
                ),
                **dialog.get_data(),
            )

            ensure_recurring_instances_through(
                date.today().isoformat()
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh_all()

    # ==================================
    # Subtasks
    # ==================================

    def add_subtask(
        self,
        parent_id: int,
    ):
        dialog = SubtaskDialog(
            self
        )

        if not dialog.exec():
            return

        try:
            create_subtask(
                parent_id=parent_id,
                **dialog.get_data(),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh_all()

    # ==================================
    # Refresh
    # ==================================

    def refresh_all(
        self,
    ):
        ensure_recurring_instances_through(
            date.today().isoformat()
        )

        self.refresh_home()
        self.refresh_today()

        if hasattr(
            self,
            "weekly_page",
        ):
            self.weekly_page.refresh()

        if hasattr(
            self,
            "habits_page",
        ):
            self.habits_page.refresh()

        if hasattr(
            self,
            "study_page",
        ):
            self.study_page.refresh()

    def refresh_home(
        self,
    ):
        self.clear_layout(
            self.home_tasks_layout
        )

        tasks = get_tasks()

        if not tasks:
            self.add_empty_message(
                self.home_tasks_layout,
                "هنوز کاری اضافه نشده است 🌱",
            )

        else:
            for task in tasks:
                self.home_tasks_layout.addWidget(
                    self.create_task_widget(
                        task
                    )
                )

        (
            total,
            completed,
            percentage,
        ) = get_task_progress()

        self.home_progress_label.setText(
            f"پیشرفت کلی: {percentage}٪"
        )

        self.home_progress_bar.setValue(
            percentage
        )

        if total == 0:
            self.home_progress_details.setText(
                "هنوز کاری وجود ندارد."
            )

        else:
            self.home_progress_details.setText(
                f"{completed} از "
                f"{total} کار انجام شده"
            )

    def refresh_today(
        self,
    ):
        today_date = date.today()

        today = today_date.isoformat()

        ensure_recurring_instances_through(
            today
        )

        self.today_date_label.setText(
            format_jalali_date(
                today_date
            )
        )

        self.clear_layout(
            self.today_tasks_layout
        )

        tasks = get_tasks_for_date(
            today
        )

        if not tasks:
            self.add_empty_message(
                self.today_tasks_layout,
                "برای امروز هنوز برنامه‌ای ثبت نشده است 🌱",
            )

        else:
            for task in tasks:
                self.today_tasks_layout.addWidget(
                    self.create_task_widget(
                        task,
                        show_schedule=True,
                    )
                )

        (
            total,
            completed,
            percentage,
        ) = get_task_progress_for_date(
            today
        )

        self.today_progress_label.setText(
            f"پیشرفت امروز: "
            f"{percentage}٪"
        )

        self.today_progress_bar.setValue(
            percentage
        )

        if total == 0:
            self.today_progress_details.setText(
                "امروز هنوز کاری برنامه‌ریزی نشده است."
            )

        else:
            self.today_progress_details.setText(
                f"{completed} از "
                f"{total} کار امروز انجام شده"
            )

    # ==================================
    # Task card
    # ==================================

    def create_task_widget(
        self,
        task,
        show_schedule: bool = False,
    ):
        frame = QFrame()

        frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d8d8d8;
                border-radius: 8px;
                padding: 8px;
            }
            """
        )

        outer_layout = QVBoxLayout(
            frame
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

        font = QFont()

        font.setPointSize(
            11
        )

        if task["completed"]:
            font.setStrikeOut(
                True
            )

        checkbox.setFont(
            font
        )

        checkbox.toggled.connect(
            lambda checked,
            task_id=task["id"]:
            self.toggle_task(
                task_id,
                checked,
            )
        )

        outer_layout.addWidget(
            checkbox
        )

        details = []

        priority = PRIORITY_LABELS.get(
            task["priority"],
            "معمولی",
        )

        details.append(
            f"اولویت: {priority}"
        )

        if task["recurring_template_id"]:
            details.append(
                "تکرارشونده"
            )

        if show_schedule:
            if task["all_day"]:
                details.append(
                    "تمام روز"
                )

            elif (
                task["start_time"]
                and task["end_time"]
            ):
                details.append(
                    f"{task['start_time']} "
                    f"تا "
                    f"{task['end_time']}"
                )

            else:
                details.append(
                    "بدون ساعت"
                )

        elif task["due_date"]:
            try:
                task_date = date.fromisoformat(
                    task["due_date"]
                )

                details.append(
                    "تاریخ: "
                    + format_jalali_short(
                        task_date
                    )
                )

            except ValueError:
                pass

        detail_label = QLabel(
            " | ".join(
                details
            )
        )

        detail_label.setStyleSheet(
            """
            font-size: 12px;
            color: #777;
            """
        )

        outer_layout.addWidget(
            detail_label
        )

        if task["description"]:
            description = QLabel(
                task["description"]
            )

            description.setWordWrap(
                True
            )

            outer_layout.addWidget(
                description
            )

        subtasks = get_subtasks(
            task["id"]
        )

        if subtasks:
            (
                subtask_total,
                subtask_completed,
                subtask_percentage,
            ) = get_subtask_progress(
                task["id"]
            )

            progress_label = QLabel(
                f"زیرکارها: "
                f"{subtask_completed} از "
                f"{subtask_total}"
            )

            outer_layout.addWidget(
                progress_label
            )

            progress_bar = QProgressBar()

            progress_bar.setRange(
                0,
                100,
            )

            progress_bar.setValue(
                subtask_percentage
            )

            outer_layout.addWidget(
                progress_bar
            )

            for subtask in subtasks:
                outer_layout.addWidget(
                    self.create_subtask_widget(
                        subtask
                    )
                )

        buttons = QHBoxLayout()

        edit_button = QPushButton(
            "ویرایش"
        )

        add_subtask_button = QPushButton(
            "＋ زیرکار"
        )

        delete_button = QPushButton(
            "حذف"
        )

        edit_button.clicked.connect(
            lambda _,
            task_id=task["id"]:
            self.edit_task(
                task_id
            )
        )

        add_subtask_button.clicked.connect(
            lambda _,
            task_id=task["id"]:
            self.add_subtask(
                task_id
            )
        )

        delete_button.clicked.connect(
            lambda _,
            task_id=task["id"]:
            self.confirm_delete_task(
                task_id
            )
        )

        buttons.addWidget(
            edit_button
        )

        buttons.addWidget(
            add_subtask_button
        )

        buttons.addWidget(
            delete_button
        )

        outer_layout.addLayout(
            buttons
        )

        return frame

    def create_subtask_widget(
        self,
        subtask,
    ):
        widget = QWidget()

        layout = QHBoxLayout(
            widget
        )

        layout.setContentsMargins(
            20,
            2,
            2,
            2,
        )

        checkbox = QCheckBox(
            subtask["title"]
        )

        checkbox.setChecked(
            bool(
                subtask["completed"]
            )
        )

        checkbox.toggled.connect(
            lambda checked,
            task_id=subtask["id"]:
            self.toggle_task(
                task_id,
                checked,
            )
        )

        delete_button = QPushButton(
            "×"
        )

        delete_button.setMaximumWidth(
            40
        )

        delete_button.clicked.connect(
            lambda _,
            task_id=subtask["id"]:
            self.confirm_delete_task(
                task_id
            )
        )

        layout.addWidget(
            checkbox,
            1,
        )

        layout.addWidget(
            delete_button
        )

        return widget

    # ==================================
    # Recurring task scope
    # ==================================

    def ask_recurring_scope(
        self,
        action: str,
    ) -> str | None:
        box = QMessageBox(
            self
        )

        box.setIcon(
            QMessageBox.Icon.Question
        )

        box.setWindowTitle(
            f"{action} کار تکرارشونده"
        )

        box.setText(
            "این کار بخشی از یک مجموعه تکرارشونده است."
        )

        box.setInformativeText(
            f"{action} فقط برای همین مورد انجام شود "
            "یا برای کل مجموعه؟"
        )

        single_button = box.addButton(
            "فقط این مورد",
            QMessageBox.ButtonRole.AcceptRole,
        )

        series_button = box.addButton(
            "کل مجموعه",
            QMessageBox.ButtonRole.ActionRole,
        )

        cancel_button = box.addButton(
            "انصراف",
            QMessageBox.ButtonRole.RejectRole,
        )

        box.exec()

        clicked = box.clickedButton()

        if clicked == single_button:
            return "single"

        if clicked == series_button:
            return "series"

        if clicked == cancel_button:
            return None

        return None

    # ==================================
    # Actions
    # ==================================

    def toggle_task(
        self,
        task_id: int,
        completed: bool,
    ):
        set_task_completed(
            task_id,
            completed,
        )

        self.refresh_all()

    def confirm_delete_task(
        self,
        task_id: int,
    ):
        task = get_task(
            task_id
        )

        if task is None:
            return

        template_id = (
            task[
                "recurring_template_id"
            ]
        )

        if template_id:
            scope = self.ask_recurring_scope(
                "حذف"
            )

            if scope is None:
                return

            if scope == "series":
                answer = QMessageBox.question(
                    self,
                    "حذف کل مجموعه",
                    (
                        "همه موارد این مجموعه "
                        "تکرارشونده حذف شوند؟"
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

                delete_recurring_series(
                    template_id
                )

                self.refresh_all()

                return

        answer = QMessageBox.question(
            self,
            "حذف کار",
            "آیا از حذف این مورد مطمئن هستی؟",
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

        delete_task(
            task_id
        )

        self.refresh_all()

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

    def add_empty_message(
        self,
        layout,
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

        layout.addWidget(
            label
        )