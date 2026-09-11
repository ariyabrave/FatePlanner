from datetime import date

from PySide6.QtCore import Qt
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


class HabitDialog(QDialog):
    def __init__(
        self,
        parent=None,
        habit=None,
    ):
        super().__init__(parent)

        self.habit = habit

        self.setWindowTitle(
            "عادت جدید"
            if habit is None
            else "ویرایش عادت"
        )

        self.setMinimumWidth(
            500
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "عادت جدید"
            if habit is None
            else "ویرایش عادت"
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

        form = QFormLayout()

        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "مثلاً مطالعه ۳۰ دقیقه"
        )

        self.description_input = QTextEdit()

        self.description_input.setPlaceholderText(
            "توضیحات اختیاری..."
        )

        self.description_input.setMaximumHeight(
            90
        )

        self.schedule_input = QComboBox()

        self.schedule_input.addItem(
            "هر روز",
            "daily",
        )

        self.schedule_input.addItem(
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
            weekday,
        ) in enumerate(
            WEEKDAY_OPTIONS
        ):
            checkbox = QCheckBox(
                label
            )

            self.weekday_checkboxes[
                weekday
            ] = checkbox

            weekday_layout.addWidget(
                checkbox,
                index // 4,
                index % 4,
            )

        self.start_date_input = (
            JalaliDateInput(
                default_date=date.today()
            )
        )

        form.addRow(
            "عنوان:",
            self.title_input,
        )

        form.addRow(
            "توضیحات:",
            self.description_input,
        )

        form.addRow(
            "برنامه:",
            self.schedule_input,
        )

        form.addRow(
            "روزها:",
            self.weekday_widget,
        )

        form.addRow(
            "شروع:",
            self.start_date_input,
        )

        main_layout.addLayout(
            form
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

        self.schedule_input.currentIndexChanged.connect(
            self.update_ui_state
        )

        if habit is not None:
            self.load_habit(
                habit
            )

        self.update_ui_state()

        self.title_input.setFocus()

    def load_habit(
        self,
        habit,
    ):
        self.title_input.setText(
            habit["title"]
        )

        self.description_input.setPlainText(
            habit["description"] or ""
        )

        index = self.schedule_input.findData(
            habit["schedule_type"]
        )

        if index >= 0:
            self.schedule_input.setCurrentIndex(
                index
            )

        if habit["weekdays"]:
            selected = {
                int(day)
                for day
                in habit["weekdays"].split(",")
                if day.strip()
            }

            for weekday, checkbox in (
                self.weekday_checkboxes.items()
            ):
                checkbox.setChecked(
                    weekday in selected
                )

        self.start_date_input.set_gregorian_date(
            date.fromisoformat(
                habit["start_date"]
            )
        )

    def update_ui_state(
        self,
    ):
        self.weekday_widget.setVisible(
            self.schedule_input.currentData()
            == "weekdays"
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
                "لطفاً عنوان عادت را وارد کنید.",
            )

            return

        if (
            self.schedule_input.currentData()
            == "weekdays"
            and not self.selected_weekdays()
        ):
            QMessageBox.warning(
                self,
                "روزهای عادت",
                "حداقل یک روز هفته را انتخاب کنید.",
            )

            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        schedule_type = (
            self.schedule_input.currentData()
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
            "schedule_type": (
                schedule_type
            ),
            "weekdays": (
                self.selected_weekdays()
                if schedule_type
                == "weekdays"
                else []
            ),
            "start_date": (
                self.start_date_input
                .to_iso_date()
            ),
        }