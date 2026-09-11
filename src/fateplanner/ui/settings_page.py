from datetime import datetime
from pathlib import Path

from PySide6.QtCore import (
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QDesktopServices,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from fateplanner.database.connection import (
    get_database_path,
)
from fateplanner.services.backup_service import (
    create_backup,
    export_csv_bundle,
    export_json,
    get_backup_directory,
    get_backup_files,
    restore_database,
    validate_database,
)


class SettingsPage(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "تنظیمات"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        description = QLabel(
            "مدیریت داده‌ها، نسخه پشتیبان، "
            "بازیابی و خروجی گرفتن از FatePlanner"
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            description
        )

        # ==================================
        # Database information
        # ==================================

        info_frame = QFrame()

        info_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d8d8d8;
                border-radius: 10px;
                padding: 10px;
            }
            """
        )

        info_layout = QVBoxLayout(
            info_frame
        )

        info_title = QLabel(
            "محل ذخیره داده‌ها"
        )

        info_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        self.database_label = QLabel()

        self.database_label.setWordWrap(
            True
        )

        self.backup_status_label = QLabel()

        self.backup_status_label.setWordWrap(
            True
        )

        open_backup_folder = QPushButton(
            "باز کردن پوشه پشتیبان‌ها"
        )

        open_backup_folder.clicked.connect(
            self.open_backup_directory
        )

        info_layout.addWidget(
            info_title
        )

        info_layout.addWidget(
            self.database_label
        )

        info_layout.addWidget(
            self.backup_status_label
        )

        info_layout.addWidget(
            open_backup_folder
        )

        layout.addWidget(
            info_frame
        )

        # ==================================
        # Backup / Restore
        # ==================================

        backup_frame = QFrame()

        backup_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d8d8d8;
                border-radius: 10px;
                padding: 10px;
            }
            """
        )

        backup_layout = QVBoxLayout(
            backup_frame
        )

        backup_title = QLabel(
            "پشتیبان‌گیری و بازیابی"
        )

        backup_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        automatic_label = QLabel(
            "FatePlanner هنگام اولین اجرای هر روز "
            "به‌صورت خودکار یک نسخه پشتیبان ایجاد می‌کند "
            "و ۱۰ نسخه خودکار اخیر را نگه می‌دارد."
        )

        automatic_label.setWordWrap(
            True
        )

        backup_buttons = QHBoxLayout()

        manual_backup_button = QPushButton(
            "ساخت نسخه پشتیبان"
        )

        restore_button = QPushButton(
            "بازیابی نسخه پشتیبان"
        )

        manual_backup_button.clicked.connect(
            self.create_manual_backup
        )

        restore_button.clicked.connect(
            self.restore_backup
        )

        backup_buttons.addWidget(
            manual_backup_button
        )

        backup_buttons.addWidget(
            restore_button
        )

        backup_layout.addWidget(
            backup_title
        )

        backup_layout.addWidget(
            automatic_label
        )

        backup_layout.addLayout(
            backup_buttons
        )

        layout.addWidget(
            backup_frame
        )

        # ==================================
        # Export
        # ==================================

        export_frame = QFrame()

        export_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d8d8d8;
                border-radius: 10px;
                padding: 10px;
            }
            """
        )

        export_layout = QVBoxLayout(
            export_frame
        )

        export_title = QLabel(
            "خروجی داده‌ها"
        )

        export_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        export_description = QLabel(
            "JSON برای یک خروجی کامل و قابل پردازش، "
            "و CSV برای مشاهده داده‌های هر بخش در "
            "Excel یا نرم‌افزارهای مشابه."
        )

        export_description.setWordWrap(
            True
        )

        export_buttons = QHBoxLayout()

        json_button = QPushButton(
            "خروجی JSON"
        )

        csv_button = QPushButton(
            "خروجی CSV"
        )

        json_button.clicked.connect(
            self.export_json_data
        )

        csv_button.clicked.connect(
            self.export_csv_data
        )

        export_buttons.addWidget(
            json_button
        )

        export_buttons.addWidget(
            csv_button
        )

        export_layout.addWidget(
            export_title
        )

        export_layout.addWidget(
            export_description
        )

        export_layout.addLayout(
            export_buttons
        )

        layout.addWidget(
            export_frame
        )

        layout.addStretch()

        self.refresh()

    def refresh(
        self,
    ):
        database_path = Path(
            get_database_path()
        )

        self.database_label.setText(
            "پایگاه داده:\n"
            f"{database_path}"
        )

        backups = get_backup_files()

        if backups:
            latest = backups[0]

            modified = datetime.fromtimestamp(
                latest.stat().st_mtime
            )

            self.backup_status_label.setText(
                "آخرین پشتیبان: "
                f"{latest.name}\n"
                "زمان: "
                f"{modified:%Y-%m-%d %H:%M:%S}\n"
                "تعداد نسخه‌ها: "
                f"{len(backups)}"
            )

        else:
            self.backup_status_label.setText(
                "هنوز نسخه پشتیبانی موجود نیست."
            )

    def open_backup_directory(
        self,
    ):
        directory = (
            get_backup_directory()
        )

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(
                    directory
                )
            )
        )

    def create_manual_backup(
        self,
    ):
        timestamp = (
            datetime.now()
            .strftime(
                "%Y%m%d-%H%M%S"
            )
        )

        default_path = (
            Path.home()
            / (
                "FatePlanner-Backup-"
                f"{timestamp}.db"
            )
        )

        path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "ذخیره نسخه پشتیبان",
                str(
                    default_path
                ),
                "SQLite Database (*.db)",
            )
        )

        if not path:
            return

        try:
            backup = create_backup(
                path
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "خطا در پشتیبان‌گیری",
                str(
                    error
                ),
            )

            return

        QMessageBox.information(
            self,
            "پشتیبان ساخته شد",
            (
                "نسخه پشتیبان با موفقیت ساخته شد:\n\n"
                f"{backup}"
            ),
        )

        self.refresh()

    def restore_backup(
        self,
    ):
        path, _ = (
            QFileDialog.getOpenFileName(
                self,
                "انتخاب نسخه پشتیبان",
                str(
                    get_backup_directory()
                ),
                "SQLite Database (*.db)",
            )
        )

        if not path:
            return

        validation = (
            validate_database(
                path
            )
        )

        if not validation["valid"]:
            missing = ", ".join(
                validation[
                    "missing_tables"
                ]
            )

            message = (
                "این فایل یک نسخه معتبر "
                "از FatePlanner نیست.\n\n"
                "Integrity: "
                f"{validation['integrity']}"
            )

            if missing:
                message += (
                    "\n\nجدول‌های مفقود:\n"
                    f"{missing}"
                )

            QMessageBox.critical(
                self,
                "نسخه پشتیبان نامعتبر",
                message,
            )

            return

        answer = QMessageBox.warning(
            self,
            "بازیابی نسخه پشتیبان",
            (
                "اطلاعات فعلی FatePlanner با اطلاعات "
                "نسخه انتخاب‌شده جایگزین می‌شود.\n\n"
                "قبل از بازیابی، FatePlanner به‌صورت "
                "خودکار از وضعیت فعلی یک نسخه ایمنی "
                "می‌سازد.\n\n"
                "ادامه می‌دهید؟"
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

        try:
            safety_backup = (
                restore_database(
                    path
                )
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "خطا در بازیابی",
                str(
                    error
                ),
            )

            return

        message = (
            "نسخه پشتیبان با موفقیت بازیابی شد.\n\n"
            "برای اطمینان از تازه شدن تمام صفحات، "
            "یک بار FatePlanner را ببندید و دوباره اجرا کنید."
        )

        if safety_backup:
            message += (
                "\n\nنسخه ایمنی قبل از بازیابی:\n"
                f"{safety_backup}"
            )

        QMessageBox.information(
            self,
            "بازیابی انجام شد",
            message,
        )

        self.refresh()

    def export_json_data(
        self,
    ):
        timestamp = (
            datetime.now()
            .strftime(
                "%Y%m%d-%H%M%S"
            )
        )

        default_path = (
            Path.home()
            / (
                "FatePlanner-Export-"
                f"{timestamp}.json"
            )
        )

        path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "خروجی JSON",
                str(
                    default_path
                ),
                "JSON (*.json)",
            )
        )

        if not path:
            return

        try:
            exported = export_json(
                path
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "خطا در خروجی",
                str(
                    error
                ),
            )

            return

        QMessageBox.information(
            self,
            "خروجی آماده شد",
            (
                "فایل JSON ساخته شد:\n\n"
                f"{exported}"
            ),
        )

    def export_csv_data(
        self,
    ):
        directory = (
            QFileDialog.getExistingDirectory(
                self,
                "انتخاب پوشه خروجی CSV",
                str(
                    Path.home()
                ),
            )
        )

        if not directory:
            return

        try:
            exported = (
                export_csv_bundle(
                    directory
                )
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "خطا در خروجی",
                str(
                    error
                ),
            )

            return

        QMessageBox.information(
            self,
            "خروجی آماده شد",
            (
                "فایل‌های CSV ساخته شدند:\n\n"
                f"{exported}"
            ),
        )