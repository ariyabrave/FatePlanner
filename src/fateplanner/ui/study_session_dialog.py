from datetime import date

from PySide6.QtCore import Qt
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
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from fateplanner.services.study_service import (
    get_subjects,
)
from fateplanner.ui.jalali_date_input import (
    JalaliDateInput,
)


class StudySessionDialog(QDialog):
    def __init__(
        self,
        parent=None,
        session=None,
        default_date: date | None = None,
    ):
        super().__init__(parent)

        self.session = session

        self.setWindowTitle(
            "جلسه مطالعه جدید"
            if session is None
            else "ویرایش جلسه مطالعه"
        )

        self.setMinimumWidth(
            500
        )

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        if default_date is None:
            default_date = date.today()

        if session is not None:
            default_date = date.fromisoformat(
                session["session_date"]
            )

        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "جلسه مطالعه جدید"
            if session is None
            else "ویرایش جلسه مطالعه"
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

        # Subject
        self.subject_input = QComboBox()

        subjects = get_subjects()

        for subject in subjects:
            self.subject_input.addItem(
                subject["name"],
                subject["id"],
            )

        # Optional session title
        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "مثلاً مرور فصل سوم"
        )

        # Date
        self.date_input = JalaliDateInput(
            default_date=default_date
        )

        # Planned duration
        self.planned_minutes_input = (
            QSpinBox()
        )

        self.planned_minutes_input.setRange(
            1,
            1440,
        )

        self.planned_minutes_input.setValue(
            50
        )

        self.planned_minutes_input.setSuffix(
            " دقیقه"
        )

        # Completed
        self.completed_input = QCheckBox(
            "جلسه انجام شده است"
        )

        # Notes
        self.notes_input = QTextEdit()

        self.notes_input.setPlaceholderText(
            "یادداشت جلسه..."
        )

        self.notes_input.setMaximumHeight(
            100
        )

        form.addRow(
            "موضوع:",
            self.subject_input,
        )

        form.addRow(
            "عنوان جلسه:",
            self.title_input,
        )

        form.addRow(
            "تاریخ:",
            self.date_input,
        )

        form.addRow(
            "زمان برنامه‌ریزی:",
            self.planned_minutes_input,
        )

        form.addRow(
            "",
            self.completed_input,
        )

        form.addRow(
            "یادداشت:",
            self.notes_input,
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

        if session is not None:
            self.load_session(
                session
            )

    def load_session(
        self,
        session,
    ):
        index = self.subject_input.findData(
            session["subject_id"]
        )

        if index >= 0:
            self.subject_input.setCurrentIndex(
                index
            )

        self.title_input.setText(
            session["title"] or ""
        )

        self.date_input.set_gregorian_date(
            date.fromisoformat(
                session["session_date"]
            )
        )

        self.planned_minutes_input.setValue(
            int(
                session["planned_minutes"]
            )
        )

        self.completed_input.setChecked(
            bool(
                session["completed"]
            )
        )

        self.notes_input.setPlainText(
            session["notes"] or ""
        )

    def validate_and_accept(
        self,
    ):
        if (
            self.subject_input.currentData()
            is None
        ):
            QMessageBox.warning(
                self,
                "موضوع مطالعه",
                "ابتدا یک موضوع مطالعه ایجاد کنید.",
            )

            return

        self.accept()

    def get_data(
        self,
    ) -> dict:
        return {
            "subject_id": int(
                self.subject_input
                .currentData()
            ),
            "title": (
                self.title_input
                .text()
                .strip()
            ),
            "session_date": (
                self.date_input
                .to_iso_date()
            ),
            "planned_minutes": (
                self.planned_minutes_input
                .value()
            ),
            "completed": (
                self.completed_input
                .isChecked()
            ),
            "notes": (
                self.notes_input
                .toPlainText()
                .strip()
            ),
        }