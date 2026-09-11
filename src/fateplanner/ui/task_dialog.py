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
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from fateplanner.ui.jalali_date_input import (
    JalaliDateInput,
)


WEEKDAY_OPTIONS = [
    ("شنبه", 5),
    ("یکشنبه", 6),
    ("دوشنبه", 0),
    ("سه‌شنبه", 1),
    ("چهارشنبه", 2),
    ("پنجشنبه", 3),
    ("جمعه", 4),
]


class TaskDialog(QDialog):
    def __init__(
        self,
        parent=None,
        default_date: QDate | date | None = None,
        task=None,
    ):
        super().__init__(parent)

        self.task = task

        self.setWindowTitle(
            "افزودن کار جدید"
            if task is None
            else "ویرایش کار"
        )

        self.setMinimumWidth(
            540
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

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

        # -------------------------
        # Basic task fields
        # -------------------------

        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "مثلاً مطالعه زبان انگلیسی"
        )

        self.description_input = QTextEdit()

        self.description_input.setPlaceholderText(
            "توضیحات بیشتر..."
        )

        self.description_input.setMaximumHeight(
            90
        )

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

        # -------------------------
        # Date
        # -------------------------

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

        # -------------------------
        # Schedule
        # -------------------------

        self.all_day_input = QCheckBox(
            "تمام روز"
        )

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

        # -------------------------
        # Recurrence
        # -------------------------

        self.recurrence_input = QComboBox()

        self.recurrence_input.addItem(
            "بدون تکرار",
            "none",
        )

        self.recurrence_input.addItem(
            "هر روز",
            "daily",
        )

        self.recurrence_input.addItem(
            "هر هفته",
            "weekly",
        )

        self.recurrence_input.addItem(
            "روزهای انتخابی",
            "weekdays",
        )

        self.weekday_widget = QWidget()

        weekday_layout = QGridLayout(
            self.weekday_widget
        )

        weekday_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.weekday_checkboxes = {}

        for index, (
            label,
            python_weekday,
        ) in enumerate(
            WEEKDAY_OPTIONS
        ):
            checkbox = QCheckBox(
                label
            )

            self.weekday_checkboxes[
                python_weekday
            ] = checkbox

            weekday_layout.addWidget(
                checkbox,
                index // 4,
                index % 4,
            )

        self.has_recurrence_end = QCheckBox(
            "تاریخ پایان تکرار"
        )

        self.recurrence_end_input = JalaliDateInput(
            default_date=initial_date
        )

        # Editing a single existing task
        # does not transform it into a
        # recurring series.
        self.recurrence_input.setEnabled(
            task is None
        )

        self.has_recurrence_end.setEnabled(
            task is None
        )

        # -------------------------
        # Form
        # -------------------------

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

        if task is None:
            form_layout.addRow(
                "تکرار:",
                self.recurrence_input,
            )

            form_layout.addRow(
                "روزها:",
                self.weekday_widget,
            )

            form_layout.addRow(
                "",
                self.has_recurrence_end,
            )

            form_layout.addRow(
                "پایان تکرار:",
                self.recurrence_end_input,
            )

        main_layout.addLayout(
            form_layout
        )

        # -------------------------
        # Buttons
        # -------------------------

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

        # Signals
        self.has_due_date.toggled.connect(
            self.update_ui_state
        )

        self.all_day_input.toggled.connect(
            self.update_ui_state
        )

        self.recurrence_input.currentIndexChanged.connect(
            self.update_ui_state
        )

        self.has_recurrence_end.toggled.connect(
            self.update_ui_state
        )

        if task is not None:
            self.load_task(
                task
            )

        self.update_ui_state()

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
            bool(
                task["all_day"]
            )
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

    def update_ui_state(
        self,
    ):
        recurrence_type = (
            self.recurrence_input.currentData()
            if self.task is None
            else "none"
        )

        # A recurring task must have
        # a starting date.
        if (
            recurrence_type != "none"
            and not self.has_due_date.isChecked()
        ):
            self.has_due_date.setChecked(
                True
            )

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

        custom_weekdays = (
            recurrence_type
            == "weekdays"
        )

        self.weekday_widget.setVisible(
            custom_weekdays
        )

        recurrence_enabled = (
            recurrence_type != "none"
        )

        self.has_recurrence_end.setVisible(
            recurrence_enabled
        )

        self.recurrence_end_input.setVisible(
            recurrence_enabled
        )

        self.recurrence_end_input.setEnabled(
            recurrence_enabled
            and self.has_recurrence_end
            .isChecked()
        )

    def selected_weekdays(
        self,
    ) -> list[int]:
        return [
            weekday
            for weekday, checkbox
            in self.weekday_checkboxes.items()
            if checkbox.isChecked()
        ]

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

        recurrence_type = (
            self.get_recurrence_type()
        )

        if recurrence_type != "none":
            if not self.has_due_date.isChecked():
                QMessageBox.warning(
                    self,
                    "تاریخ شروع",
                    "برای کار تکرارشونده باید تاریخ شروع تعیین شود.",
                )

                return

            if (
                recurrence_type == "weekdays"
                and not self.selected_weekdays()
            ):
                QMessageBox.warning(
                    self,
                    "روزهای تکرار",
                    "حداقل یک روز هفته را انتخاب کنید.",
                )

                return

            if self.has_recurrence_end.isChecked():
                start_date = (
                    self.due_date_input
                    .get_gregorian_date()
                )

                end_date = (
                    self.recurrence_end_input
                    .get_gregorian_date()
                )

                if end_date < start_date:
                    QMessageBox.warning(
                        self,
                        "تاریخ پایان",
                        "تاریخ پایان تکرار نمی‌تواند قبل از تاریخ شروع باشد.",
                    )

                    return

        self.accept()

    def get_recurrence_type(
        self,
    ) -> str:
        if self.task is not None:
            return "none"

        return str(
            self.recurrence_input
            .currentData()
        )

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

    def get_recurrence_data(
        self,
    ) -> dict:
        recurrence_type = (
            self.get_recurrence_type()
        )

        recurrence_end_date = None

        if (
            recurrence_type != "none"
            and self.has_recurrence_end
            .isChecked()
        ):
            recurrence_end_date = (
                self.recurrence_end_input
                .to_iso_date()
            )

        return {
            "recurrence_type": (
                recurrence_type
            ),
            "recurrence_weekdays": (
                self.selected_weekdays()
                if recurrence_type
                == "weekdays"
                else []
            ),
            "recurrence_end_date": (
                recurrence_end_date
            ),
        }