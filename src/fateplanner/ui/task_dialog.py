from datetime import date

from PySide6.QtCore import (
    QDate,
    QTime,
    Qt,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
)

from fateplanner.ui.jalali_date_input import (
    JalaliDateInput,
)


class TaskDialog(QDialog):
    def __init__(
        self,
        parent=None,
        default_date: QDate | date | None = None,
        task=None,
    ):
        super().__init__(parent)

        self.task = task

        if task is None:
            self.setWindowTitle(
                "افزودن کار جدید"
            )
        else:
            self.setWindowTitle(
                "ویرایش کار"
            )

        self.setMinimumWidth(
            500
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        # Determine initial date.
        initial_date = default_date

        if (
            task is not None
            and task["due_date"]
        ):
            initial_date = date.fromisoformat(
                task["due_date"]
            )

        main_layout = QVBoxLayout(
            self
        )

        title_label = QLabel(
            "کار جدید"
            if task is None
            else "ویرایش کار"
        )

        title_label.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            title_label
        )

        form_layout = QFormLayout()

        # Title
        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "مثلاً مطالعه زبان انگلیسی"
        )

        # Description
        self.description_input = QTextEdit()

        self.description_input.setPlaceholderText(
            "توضیحات بیشتر..."
        )

        self.description_input.setMaximumHeight(
            100
        )

        # Priority
        self.priority_input = QComboBox()

        self.priority_input.addItem(
            "کم",
            "low",
        )

        self.priority_input.addItem(
            "معمولی",
            "normal",
        )

        self.priority_input.addItem(
            "زیاد",
            "high",
        )

        self.priority_input.setCurrentIndex(
            1
        )

        # Date
        self.has_due_date = QCheckBox(
            "برای این کار تاریخ تعیین شود"
        )

        if initial_date is not None:
            self.has_due_date.setChecked(
                True
            )

        self.due_date_input = JalaliDateInput(
            default_date=initial_date
        )

        # All day
        self.all_day_input = QCheckBox(
            "تمام روز"
        )

        # Start time
        self.start_time_input = QTimeEdit()

        self.start_time_input.setDisplayFormat(
            "HH:mm"
        )

        self.start_time_input.setTime(
            QTime(
                9,
                0,
            )
        )

        # End time
        self.end_time_input = QTimeEdit()

        self.end_time_input.setDisplayFormat(
            "HH:mm"
        )

        self.end_time_input.setTime(
            QTime(
                10,
                0,
            )
        )

        self.has_due_date.toggled.connect(
            self.update_schedule_state
        )

        self.all_day_input.toggled.connect(
            self.update_schedule_state
        )

        form_layout.addRow(
            "عنوان:",
            self.title_input,
        )

        form_layout.addRow(
            "توضیحات:",
            self.description_input,
        )

        form_layout.addRow(
            "اولویت:",
            self.priority_input,
        )

        form_layout.addRow(
            "",
            self.has_due_date,
        )

        form_layout.addRow(
            "تاریخ:",
            self.due_date_input,
        )

        form_layout.addRow(
            "",
            self.all_day_input,
        )

        form_layout.addRow(
            "زمان شروع:",
            self.start_time_input,
        )

        form_layout.addRow(
            "زمان پایان:",
            self.end_time_input,
        )

        main_layout.addLayout(
            form_layout
        )

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "ذخیره"
        )

        cancel_button = QPushButton(
            "انصراف"
        )

        save_button.setDefault(
            True
        )

        save_button.clicked.connect(
            self.validate_and_accept
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            save_button
        )

        buttons.addWidget(
            cancel_button
        )

        main_layout.addLayout(
            buttons
        )

        if task is not None:
            self.load_task(
                task
            )

        self.update_schedule_state()

        self.title_input.setFocus()

    def load_task(
        self,
        task,
    ):
        self.title_input.setText(
            task["title"]
        )

        self.description_input.setPlainText(
            task["description"] or ""
        )

        priority_index = (
            self.priority_input.findData(
                task["priority"]
            )
        )

        if priority_index >= 0:
            self.priority_input.setCurrentIndex(
                priority_index
            )

        if task["due_date"]:
            self.has_due_date.setChecked(
                True
            )

            self.due_date_input.set_gregorian_date(
                date.fromisoformat(
                    task["due_date"]
                )
            )
        else:
            self.has_due_date.setChecked(
                False
            )

        self.all_day_input.setChecked(
            bool(task["all_day"])
        )

        if task["start_time"]:
            parsed_start = QTime.fromString(
                task["start_time"],
                "HH:mm",
            )

            if parsed_start.isValid():
                self.start_time_input.setTime(
                    parsed_start
                )

        if task["end_time"]:
            parsed_end = QTime.fromString(
                task["end_time"],
                "HH:mm",
            )

            if parsed_end.isValid():
                self.end_time_input.setTime(
                    parsed_end
                )

    def update_schedule_state(
        self,
    ):
        has_date = (
            self.has_due_date.isChecked()
        )

        self.due_date_input.setEnabled(
            has_date
        )

        self.all_day_input.setEnabled(
            has_date
        )

        if not has_date:
            self.all_day_input.setChecked(
                False
            )

        time_enabled = (
            has_date
            and not self.all_day_input.isChecked()
        )

        self.start_time_input.setEnabled(
            time_enabled
        )

        self.end_time_input.setEnabled(
            time_enabled
        )

    def validate_and_accept(
        self,
    ):
        if not (
            self.title_input
            .text()
            .strip()
        ):
            QMessageBox.warning(
                self,
                "عنوان خالی",
                "لطفاً برای کار یک عنوان وارد کنید.",
            )

            return

        if (
            self.has_due_date.isChecked()
            and not self.all_day_input.isChecked()
        ):
            start = (
                self.start_time_input.time()
            )

            end = (
                self.end_time_input.time()
            )

            if end <= start:
                QMessageBox.warning(
                    self,
                    "زمان نامعتبر",
                    "زمان پایان باید بعد از زمان شروع باشد.",
                )

                return

        self.accept()

    def get_task_data(
        self,
    ) -> dict:
        due_date = None
        start_time = None
        end_time = None
        all_day = False

        if self.has_due_date.isChecked():
            due_date = (
                self.due_date_input
                .to_iso_date()
            )

            all_day = (
                self.all_day_input
                .isChecked()
            )

            if not all_day:
                start_time = (
                    self.start_time_input
                    .time()
                    .toString("HH:mm")
                )

                end_time = (
                    self.end_time_input
                    .time()
                    .toString("HH:mm")
                )

        return {
            "title": (
                self.title_input
                .text()
                .strip()
            ),
            "description": (
                self.description_input
                .toPlainText()
                .strip()
            ),
            "priority": (
                self.priority_input
                .currentData()
            ),
            "due_date": due_date,
            "start_time": start_time,
            "end_time": end_time,
            "all_day": all_day,
        }