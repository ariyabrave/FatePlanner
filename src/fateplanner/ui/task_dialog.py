from PySide6.QtCore import (
    QDate,
    QTime,
    Qt,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
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


class TaskDialog(QDialog):
    def __init__(
        self,
        parent=None,
        default_date: QDate | None = None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "افزودن کار جدید"
        )

        self.setMinimumWidth(
            450
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        main_layout = QVBoxLayout(
            self
        )

        title_label = QLabel(
            "کار جدید"
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

        form_layout = (
            QFormLayout()
        )

        # Title
        self.title_input = (
            QLineEdit()
        )

        self.title_input.setPlaceholderText(
            "مثلاً مطالعه زبان انگلیسی"
        )

        # Description
        self.description_input = (
            QTextEdit()
        )

        self.description_input.setPlaceholderText(
            "توضیحات بیشتر..."
        )

        self.description_input.setMaximumHeight(
            100
        )

        # Priority
        self.priority_input = (
            QComboBox()
        )

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

        self.due_date_input = (
            QDateEdit()
        )

        self.due_date_input.setCalendarPopup(
            True
        )

        if default_date is not None:
            self.due_date_input.setDate(
                default_date
            )

            self.has_due_date.setChecked(
                True
            )

        else:
            self.due_date_input.setDate(
                QDate.currentDate()
            )

        # All day
        self.all_day_input = QCheckBox(
            "تمام روز"
        )

        # Start time
        self.start_time_input = (
            QTimeEdit()
        )

        self.start_time_input.setDisplayFormat(
            "HH:mm"
        )

        self.start_time_input.setTime(
            QTime(9, 0)
        )

        # End time
        self.end_time_input = (
            QTimeEdit()
        )

        self.end_time_input.setDisplayFormat(
            "HH:mm"
        )

        self.end_time_input.setTime(
            QTime(10, 0)
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

        button_layout = (
            QHBoxLayout()
        )

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

        button_layout.addWidget(
            save_button
        )

        button_layout.addWidget(
            cancel_button
        )

        main_layout.addLayout(
            button_layout
        )

        self.update_schedule_state()

        self.title_input.setFocus()

    def update_schedule_state(
        self,
    ):
        has_date = (
            self.has_due_date
            .isChecked()
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
            and not self.all_day_input
            .isChecked()
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
            and not self.all_day_input
            .isChecked()
        ):
            start = (
                self.start_time_input
                .time()
            )

            end = (
                self.end_time_input
                .time()
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

        if (
            self.has_due_date
            .isChecked()
        ):
            due_date = (
                self.due_date_input
                .date()
                .toString(
                    "yyyy-MM-dd"
                )
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