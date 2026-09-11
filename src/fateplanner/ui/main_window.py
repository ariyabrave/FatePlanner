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

from fateplanner.services.task_service import (
    create_task,
    delete_task,
    get_task_progress,
    get_task_progress_for_date,
    get_tasks,
    get_tasks_for_date,
    set_task_completed,
)
from fateplanner.ui.task_dialog import (
    TaskDialog,
)
from fateplanner.ui.weekly_planner import (
    WeeklyPlanner,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
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
            1150,
            750,
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

        # =========================
        # Sidebar
        # =========================

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

        # =========================
        # Pages
        # =========================

        self.pages = (
            QStackedWidget()
        )

        self.home_page = (
            self.create_home_page()
        )

        self.today_page = (
            self.create_today_page()
        )

        self.weekly_page = (
            WeeklyPlanner(
                on_data_changed=(
                    self.refresh_all
                )
            )
        )

        self.pages.addWidget(
            self.home_page
        )

        self.pages.addWidget(
            self.today_page
        )

        self.pages.addWidget(
            self.weekly_page
        )

        remaining_pages = [
            "کارها",
            "عادت‌ها",
            "مطالعه",
            "امور مالی",
            "گزارش‌ها و پیشرفت",
            "تنظیمات",
        ]

        for page_name in (
            remaining_pages
        ):
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

    # =========================
    # Navigation
    # =========================

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

    # =========================
    # Home
    # =========================

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

        subtitle.setStyleSheet(
            """
            font-size: 16px;
            """
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        progress_frame = QFrame()

        progress_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d0d0d0;
                border-radius: 10px;
                padding: 10px;
            }
            """
        )

        progress_layout = (
            QVBoxLayout(
                progress_frame
            )
        )

        self.home_progress_label = (
            QLabel(
                "پیشرفت کلی: ۰٪"
            )
        )

        self.home_progress_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        self.home_progress_bar = (
            QProgressBar()
        )

        self.home_progress_bar.setRange(
            0,
            100,
        )

        self.home_progress_details = (
            QLabel("")
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

        self.home_tasks_container = (
            QWidget()
        )

        self.home_tasks_layout = (
            QVBoxLayout(
                self.home_tasks_container
            )
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

    # =========================
    # Today
    # =========================

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

        self.today_date_label = (
            QLabel()
        )

        self.today_date_label.setStyleSheet(
            """
            font-size: 16px;
            """
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            self.today_date_label
        )

        progress_frame = QFrame()

        progress_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d0d0d0;
                border-radius: 10px;
                padding: 10px;
            }
            """
        )

        progress_layout = (
            QVBoxLayout(
                progress_frame
            )
        )

        self.today_progress_label = (
            QLabel(
                "پیشرفت امروز: ۰٪"
            )
        )

        self.today_progress_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        self.today_progress_bar = (
            QProgressBar()
        )

        self.today_progress_bar.setRange(
            0,
            100,
        )

        self.today_progress_details = (
            QLabel("")
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

        add_today_button = (
            QPushButton(
                "＋ افزودن کار برای امروز"
            )
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

        self.today_tasks_container = (
            QWidget()
        )

        self.today_tasks_layout = (
            QVBoxLayout(
                self.today_tasks_container
            )
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

    # =========================
    # Placeholder pages
    # =========================

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

        message.setStyleSheet(
            """
            font-size: 16px;
            """
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            message
        )

        layout.addStretch()

        return page

    # =========================
    # Dialogs
    # =========================

    def open_general_task_dialog(
        self,
    ):
        dialog = TaskDialog(
            self
        )

        if dialog.exec():
            self.save_task_from_dialog(
                dialog
            )

    def open_today_task_dialog(
        self,
    ):
        dialog = TaskDialog(
            self,
            default_date=(
                QDate.currentDate()
            ),
        )

        if dialog.exec():
            self.save_task_from_dialog(
                dialog
            )

    def save_task_from_dialog(
        self,
        dialog: TaskDialog,
    ):
        task_data = (
            dialog.get_task_data()
        )

        try:
            create_task(
                **task_data
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )
            return

        self.refresh_all()

    # =========================
    # Refresh
    # =========================

    def refresh_all(
        self,
    ):
        self.refresh_home()
        self.refresh_today()

        if hasattr(
            self,
            "weekly_page",
        ):
            self.weekly_page.refresh()

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
        today_date = (
            date.today()
        )

        today = (
            today_date.isoformat()
        )

        visible_date = (
            format_jalali_date(
                today_date
            )
        )

        self.today_date_label.setText(
            visible_date
        )

        self.clear_layout(
            self.today_tasks_layout
        )

        tasks = (
            get_tasks_for_date(
                today
            )
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
        ) = (
            get_task_progress_for_date(
                today
            )
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

    # =========================
    # Task widget
    # =========================

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

        layout = QHBoxLayout(
            frame
        )

        text_layout = (
            QVBoxLayout()
        )

        checkbox = QCheckBox(
            task["title"]
        )

        checkbox.setChecked(
            bool(task["completed"])
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

        text_layout.addWidget(
            checkbox
        )

        details = []

        priority = (
            PRIORITY_LABELS.get(
                task["priority"],
                "معمولی",
            )
        )

        details.append(
            f"اولویت: {priority}"
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

            elif task["start_time"]:
                details.append(
                    f"شروع: "
                    f"{task['start_time']}"
                )

            else:
                details.append(
                    "بدون ساعت"
                )

        elif task["due_date"]:
            details.append(
                f"تاریخ: "
                f"{task['due_date']}"
            )

        details_label = QLabel(
            " | ".join(
                details
            )
        )

        details_label.setStyleSheet(
            """
            font-size: 12px;
            color: #777;
            """
        )

        text_layout.addWidget(
            details_label
        )

        if task["description"]:
            description = QLabel(
                task["description"]
            )

            description.setWordWrap(
                True
            )

            description.setStyleSheet(
                """
                font-size: 13px;
                color: #555;
                """
            )

            text_layout.addWidget(
                description
            )

        delete_button = QPushButton(
            "حذف"
        )

        delete_button.setMaximumWidth(
            80
        )

        delete_button.clicked.connect(
            lambda _,
            task_id=task["id"]:
            self.confirm_delete_task(
                task_id
            )
        )

        layout.addLayout(
            text_layout,
            1,
        )

        layout.addWidget(
            delete_button
        )

        return frame

    # =========================
    # Task actions
    # =========================

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
        answer = QMessageBox.question(
            self,
            "حذف کار",
            "آیا از حذف این کار مطمئن هستی؟",
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            == QMessageBox.StandardButton.Yes
        ):
            delete_task(
                task_id
            )

            self.refresh_all()

    # =========================
    # Helpers
    # =========================

    def clear_layout(
        self,
        layout,
    ):
        while layout.count():
            item = (
                layout.takeAt(0)
            )

            widget = (
                item.widget()
            )

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