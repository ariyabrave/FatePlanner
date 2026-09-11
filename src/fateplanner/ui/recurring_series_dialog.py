from datetime import date

from PySide6.QtCore import (
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


class RecurringSeriesDialog(QDialog):
    def __init__(
        self,
        template,
        parent=None,
    ):
        super().__init__(parent)

        self.template = template

        self.setWindowTitle(
            "ویرایش مجموعه تکرارشونده"
        )

        self.setMinimumWidth(
            550
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        start_date = date.fromisoformat(
            template["recurrence_start_date"]
        )

        if template["recurrence_end_date"]:
            end_date = date.fromisoformat(
                template["recurrence_end_date"]
            )
        else:
            end_date = start_date

        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "ویرایش مجموعه تکرارشونده"
        )

        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            title
        )

        help_text = QLabel(
            "تغییرات روی موارد آینده این مجموعه اعمال می‌شود."
        )

        help_text.setWordWrap(
            True
        )

        main_layout.addWidget(
            help_text
        )

        form = QFormLayout()

        # -------------------------
        # Title
        # -------------------------

        self.title_input = QLineEdit()

        self.title_input.setText(
            template["title"]
        )

        # -------------------------
        # Description
        # -------------------------

        self.description_input = QTextEdit()

        self.description_input.setPlainText(
            template["description"] or ""
        )

        self.description_input.setMaximumHeight(
            90
        )

        # -------------------------
        # Priority
        # -------------------------

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

        priority_index = (
            self.priority_input.findData(
                template["priority"]
            )
        )

        if priority_index >= 0:
            self.priority_input.setCurrentIndex(
                priority_index
            )

        # -------------------------
        # Start date
        # -------------------------

        self.start_date_input = (
            JalaliDateInput(
                default_date=start_date
            )
        )

        # -------------------------
        # Schedule
        # -------------------------

        self.all_day_input = QCheckBox(
            "تمام روز"
        )

        self.all_day_input.setChecked(
            bool(
                template["all_day"]
            )
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

        if template["start_time"]:
            value = QTime.fromString(
                template["start_time"],
                "HH:mm",
            )

            if value.isValid():
                self.start_time_input.setTime(
                    value
                )

        if template["end_time"]:
            value = QTime.fromString(
                template["end_time"],
                "HH:mm",
            )

            if value.isValid():
                self.end_time_input.setTime(
                    value
                )

        # -------------------------
        # Recurrence
        # -------------------------

        self.recurrence_input = QComboBox()

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

        recurrence_index = (
            self.recurrence_input.findData(
                template[
                    "recurrence_type"
                ]
            )
        )

        if recurrence_index >= 0:
            self.recurrence_input.setCurrentIndex(
                recurrence_index
            )

        # -------------------------
        # Weekdays
        # -------------------------

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

        selected_weekdays = set()

        if template[
            "recurrence_weekdays"
        ]:
            selected_weekdays = {
                int(value)
                for value
                in template[
                    "recurrence_weekdays"
                ].split(",")
                if value.strip()
            }

        for index, (
            label,
            python_weekday,
        ) in enumerate(
            WEEKDAY_OPTIONS
        ):
            checkbox = QCheckBox(
                label
            )

            checkbox.setChecked(
                python_weekday
                in selected_weekdays
            )

            self.weekday_checkboxes[
                python_weekday
            ] = checkbox

            weekday_layout.addWidget(
                checkbox,
                index // 4,
                index % 4,
            )

        # -------------------------
        # End date
        # -------------------------

        self.has_end_date = QCheckBox(
            "تاریخ پایان تکرار"
        )

        self.has_end_date.setChecked(
            bool(
                template[
                    "recurrence_end_date"
                ]
            )
        )

        self.end_date_input = JalaliDateInput(
            default_date=end_date
        )

        # -------------------------
        # Form rows
        # -------------------------

        form.addRow(
            "عنوان:",
            self.title_input,
        )

        form.addRow(
            "توضیحات:",
            self.description_input,
        )

        form.addRow(
            "اولویت:",
            self.priority_input,
        )

        form.addRow(
            "شروع تکرار:",
            self.start_date_input,
        )

        form.addRow(
            "",
            self.all_day_input,
        )

        form.addRow(
            "زمان شروع:",
            self.start_time_input,
        )

        form.addRow(
            "زمان پایان:",
            self.end_time_input,
        )

        form.addRow(
            "تکرار:",
            self.recurrence_input,
        )

        form.addRow(
            "روزها:",
            self.weekday_widget,
        )

        form.addRow(
            "",
            self.has_end_date,
        )

        form.addRow(
            "پایان تکرار:",
            self.end_date_input,
        )

        main_layout.addLayout(
            form
        )

        # -------------------------
        # Buttons
        # -------------------------

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "ذخیره تغییرات"
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
        self.all_day_input.toggled.connect(
            self.update_ui_state
        )

        self.recurrence_input.currentIndexChanged.connect(
            self.update_ui_state
        )

        self.has_end_date.toggled.connect(
            self.update_ui_state
        )

        self.update_ui_state()

    def update_ui_state(
        self,
    ):
        recurrence_type = (
            self.recurrence_input.currentData()
        )

        self.weekday_widget.setVisible(
            recurrence_type
            == "weekdays"
        )

        self.end_date_input.setEnabled(
            self.has_end_date.isChecked()
        )

        time_enabled = (
            not self.all_day_input.isChecked()
        )

        self.start_time_input.setEnabled(
            time_enabled
        )

        self.end_time_input.setEnabled(
            time_enabled
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
                "لطفاً عنوان کار را وارد کنید.",
            )

            return

        if not self.all_day_input.isChecked():
            if (
                self.end_time_input.time()
                <= self.start_time_input.time()
            ):
                QMessageBox.warning(
                    self,
                    "زمان نامعتبر",
                    "زمان پایان باید بعد از زمان شروع باشد.",
                )

                return

        if (
            self.recurrence_input.currentData()
            == "weekdays"
            and not self.selected_weekdays()
        ):
            QMessageBox.warning(
                self,
                "روزهای تکرار",
                "حداقل یک روز هفته را انتخاب کنید.",
            )

            return

        if self.has_end_date.isChecked():
            if (
                self.end_date_input
                .get_gregorian_date()
                <
                self.start_date_input
                .get_gregorian_date()
            ):
                QMessageBox.warning(
                    self,
                    "تاریخ پایان",
                    "تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد.",
                )

                return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        all_day = (
            self.all_day_input.isChecked()
        )

        start_time = None
        end_time = None

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

        recurrence_end_date = None

        if self.has_end_date.isChecked():
            recurrence_end_date = (
                self.end_date_input
                .to_iso_date()
            )

        recurrence_type = (
            self.recurrence_input
            .currentData()
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
            "all_day": all_day,
            "start_time": start_time,
            "end_time": end_time,
            "recurrence_type": (
                recurrence_type
            ),
            "recurrence_start_date": (
                self.start_date_input
                .to_iso_date()
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