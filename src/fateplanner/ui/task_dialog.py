from PySide6.QtCore import QDate, Qt
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
    QVBoxLayout,
)


class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("افزودن کار جدید")
        self.setMinimumWidth(450)

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        main_layout = QVBoxLayout(self)

        title_label = QLabel("کار جدید")
        title_label.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(title_label)

        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "مثلاً مطالعه زبان انگلیسی"
        )

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "توضیحات بیشتر..."
        )
        self.description_input.setMaximumHeight(100)

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

        self.priority_input.setCurrentIndex(1)

        self.has_due_date = QCheckBox(
            "برای این کار تاریخ تعیین شود"
        )

        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate())
        self.due_date_input.setEnabled(False)

        self.has_due_date.toggled.connect(
            self.due_date_input.setEnabled
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

        main_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()

        save_button = QPushButton("ذخیره")
        cancel_button = QPushButton("انصراف")

        save_button.setDefault(True)

        save_button.clicked.connect(
            self.validate_and_accept
        )

        cancel_button.clicked.connect(
            self.reject
        )

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        self.title_input.setFocus()

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(
                self,
                "عنوان خالی",
                "لطفاً برای کار یک عنوان وارد کنید.",
            )
            return

        self.accept()

    def get_task_data(self) -> dict:
        due_date = None

        if self.has_due_date.isChecked():
            due_date = (
                self.due_date_input
                .date()
                .toString("yyyy-MM-dd")
            )

        return {
            "title": self.title_input.text().strip(),
            "description": (
                self.description_input
                .toPlainText()
                .strip()
            ),
            "priority": (
                self.priority_input.currentData()
            ),
            "due_date": due_date,
        }