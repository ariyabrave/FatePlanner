from PySide6.QtCore import Qt
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
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.task_service import (
    create_task,
    delete_task,
    get_task_progress,
    get_tasks,
    set_task_completed,
)
from fateplanner.ui.task_dialog import TaskDialog


PRIORITY_LABELS = {
    "low": "کم",
    "normal": "معمولی",
    "high": "زیاد",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FatePlanner")
        self.resize(1100, 700)

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)

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

        self.sidebar.setCurrentRow(0)

        # Dashboard
        dashboard = QWidget()
        dashboard_layout = QVBoxLayout(dashboard)

        title = QLabel("سلام 🌷")
        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        subtitle = QLabel(
            "امروز چه کارهایی می‌خواهی انجام بدهی؟"
        )
        subtitle.setStyleSheet(
            """
            font-size: 16px;
            """
        )

        dashboard_layout.addWidget(title)
        dashboard_layout.addWidget(subtitle)

        # Progress area
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

        progress_layout = QVBoxLayout(progress_frame)

        self.progress_label = QLabel(
            "پیشرفت امروز: ۰٪"
        )

        self.progress_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.progress_details = QLabel(
            "هنوز کاری اضافه نشده است."
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

        dashboard_layout.addWidget(
            progress_frame
        )

        # Add task button
        self.add_task_button = QPushButton(
            "＋ افزودن کار جدید"
        )

        self.add_task_button.setMinimumHeight(45)

        self.add_task_button.clicked.connect(
            self.open_task_dialog
        )

        dashboard_layout.addWidget(
            self.add_task_button
        )

        tasks_title = QLabel("کارها")

        tasks_title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            margin-top: 15px;
            """
        )

        dashboard_layout.addWidget(tasks_title)

        # Scrollable task list
        self.tasks_container = QWidget()

        self.tasks_layout = QVBoxLayout(
            self.tasks_container
        )

        self.tasks_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(
            self.tasks_container
        )

        dashboard_layout.addWidget(
            scroll_area,
            1,
        )

        main_layout.addWidget(
            self.sidebar
        )

        main_layout.addWidget(
            dashboard,
            1,
        )

        self.refresh_tasks()

    def open_task_dialog(self):
        dialog = TaskDialog(self)

        if dialog.exec():
            task_data = dialog.get_task_data()

            try:
                create_task(**task_data)

            except ValueError as error:
                QMessageBox.warning(
                    self,
                    "خطا",
                    str(error),
                )
                return

            self.refresh_tasks()

    def refresh_tasks(self):
        self.clear_task_widgets()

        tasks = get_tasks()

        if not tasks:
            empty_label = QLabel(
                "هنوز کاری اضافه نشده است 🌱"
            )

            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty_label.setStyleSheet(
                """
                font-size: 16px;
                padding: 30px;
                """
            )

            self.tasks_layout.addWidget(
                empty_label
            )

        else:
            for task in tasks:
                self.tasks_layout.addWidget(
                    self.create_task_widget(task)
                )

        self.update_progress()

    def create_task_widget(self, task):
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

        layout = QHBoxLayout(frame)

        checkbox = QCheckBox(task["title"])
        checkbox.setChecked(
            bool(task["completed"])
        )

        checkbox_font = QFont()
        checkbox_font.setPointSize(11)

        if task["completed"]:
            checkbox_font.setStrikeOut(True)

        checkbox.setFont(checkbox_font)

        checkbox.toggled.connect(
            lambda checked, task_id=task["id"]:
            self.toggle_task(
                task_id,
                checked,
            )
        )

        details = []

        priority = PRIORITY_LABELS.get(
            task["priority"],
            "معمولی",
        )

        details.append(
            f"اولویت: {priority}"
        )

        if task["due_date"]:
            details.append(
                f"تاریخ: {task['due_date']}"
            )

        detail_label = QLabel(
            " | ".join(details)
        )

        detail_label.setStyleSheet(
            """
            font-size: 12px;
            color: #777;
            """
        )

        text_layout = QVBoxLayout()

        text_layout.addWidget(
            checkbox
        )

        text_layout.addWidget(
            detail_label
        )

        if task["description"]:
            description_label = QLabel(
                task["description"]
            )

            description_label.setWordWrap(True)

            description_label.setStyleSheet(
                """
                font-size: 13px;
                color: #555;
                """
            )

            text_layout.addWidget(
                description_label
            )

        delete_button = QPushButton(
            "حذف"
        )

        delete_button.setMaximumWidth(80)

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

    def toggle_task(
        self,
        task_id: int,
        completed: bool,
    ):
        set_task_completed(
            task_id,
            completed,
        )

        self.refresh_tasks()

    def confirm_delete_task(
        self,
        task_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف کار",
            "آیا از حذف این کار مطمئن هستی؟",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            == QMessageBox.StandardButton.Yes
        ):
            delete_task(task_id)

            self.refresh_tasks()

    def update_progress(self):
        total, completed, percentage = (
            get_task_progress()
        )

        self.progress_label.setText(
            f"پیشرفت امروز: {percentage}٪"
        )

        self.progress_bar.setValue(
            percentage
        )

        if total == 0:
            self.progress_details.setText(
                "هنوز کاری اضافه نشده است."
            )

        else:
            self.progress_details.setText(
                f"{completed} از {total} کار انجام شده"
            )

    def clear_task_widgets(self):
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()