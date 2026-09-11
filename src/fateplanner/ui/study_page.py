from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.study_service import (
    create_study_session,
    create_subject,
    delete_study_session,
    delete_subject,
    format_study_duration,
    get_study_session,
    get_study_sessions_for_date,
    get_study_stats_for_date,
    get_subject,
    get_subjects,
    set_study_session_completed,
    update_study_session,
    update_subject,
)
from fateplanner.ui.focus_timer_widget import (
    FocusTimerWidget,
)
from fateplanner.ui.study_analytics_widget import (
    StudyAnalyticsWidget,
)
from fateplanner.ui.study_session_dialog import (
    StudySessionDialog,
)
from fateplanner.ui.study_subject_dialog import (
    StudySubjectDialog,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
    to_persian_digits,
)


class StudyPage(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(
            self
        )

        # ==================================
        # Header
        # ==================================

        title = QLabel(
            "مطالعه"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        self.date_label = QLabel()

        self.date_label.setStyleSheet(
            """
            font-size: 15px;
            color: palette(window-text);
            """
        )

        self.main_layout.addWidget(
            title
        )

        self.main_layout.addWidget(
            self.date_label
        )

        # ==================================
        # Tabs
        # ==================================

        self.tabs = QTabWidget()

        self.tabs.setDocumentMode(
            True
        )

        self.tabs.setStyleSheet(
            """
            QTabBar::tab {
                min-width: 150px;
                min-height: 36px;
                padding: 6px 14px;
                font-size: 14px;
            }
            """
        )

        self.planner_tab = (
            self.create_planner_tab()
        )

        self.timer_tab = (
            self.create_timer_tab()
        )

        self.analytics_tab = (
            self.create_analytics_tab()
        )

        self.tabs.addTab(
            self.planner_tab,
            "برنامه مطالعه",
        )

        self.tabs.addTab(
            self.timer_tab,
            "تایمر تمرکز",
        )

        self.tabs.addTab(
            self.analytics_tab,
            "تاریخچه و آمار",
        )

        self.tabs.currentChanged.connect(
            self.on_tab_changed
        )

        self.main_layout.addWidget(
            self.tabs,
            1,
        )

        self.refresh()

    # ==================================
    # Planner tab
    # ==================================

    def create_planner_tab(
        self,
    ) -> QWidget:
        tab = QWidget()

        outer_layout = QVBoxLayout(
            tab
        )

        stats_frame = QFrame()

        stats_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 8px;
            }
            """
        )

        stats_layout = QVBoxLayout(
            stats_frame
        )

        self.progress_label = QLabel(
            "پیشرفت مطالعه امروز: ۰٪"
        )

        self.progress_label.setStyleSheet(
            """
            font-size: 19px;
            font-weight: bold;
            """
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100,
        )

        self.session_details = QLabel()

        self.time_details = QLabel()

        stats_layout.addWidget(
            self.progress_label
        )

        stats_layout.addWidget(
            self.progress_bar
        )

        stats_layout.addWidget(
            self.session_details
        )

        stats_layout.addWidget(
            self.time_details
        )

        outer_layout.addWidget(
            stats_frame
        )

        button_layout = QHBoxLayout()

        add_subject_button = QPushButton(
            "＋ موضوع جدید"
        )

        add_session_button = QPushButton(
            "＋ برنامه مطالعه"
        )

        add_subject_button.setMinimumHeight(
            42
        )

        add_session_button.setMinimumHeight(
            42
        )

        add_subject_button.clicked.connect(
            self.open_add_subject
        )

        add_session_button.clicked.connect(
            self.open_add_session
        )

        button_layout.addWidget(
            add_subject_button
        )

        button_layout.addWidget(
            add_session_button
        )

        outer_layout.addLayout(
            button_layout
        )

        content_layout = QHBoxLayout()

        # ----------------------------------
        # Subjects
        # ----------------------------------

        subjects_frame = QFrame()

        subjects_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
            """
        )

        subjects_frame_layout = QVBoxLayout(
            subjects_frame
        )

        subjects_title = QLabel(
            "موضوع‌های مطالعه"
        )

        subjects_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        subjects_frame_layout.addWidget(
            subjects_title
        )

        self.subjects_container = QWidget()

        self.subjects_layout = QVBoxLayout(
            self.subjects_container
        )

        self.subjects_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        subjects_scroll = QScrollArea()

        subjects_scroll.setWidgetResizable(
            True
        )

        subjects_scroll.setWidget(
            self.subjects_container
        )

        subjects_frame_layout.addWidget(
            subjects_scroll,
            1,
        )

        # ----------------------------------
        # Sessions
        # ----------------------------------

        sessions_frame = QFrame()

        sessions_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
            """
        )

        sessions_frame_layout = QVBoxLayout(
            sessions_frame
        )

        sessions_title = QLabel(
            "برنامه مطالعه امروز"
        )

        sessions_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        sessions_frame_layout.addWidget(
            sessions_title
        )

        self.sessions_container = QWidget()

        self.sessions_layout = QVBoxLayout(
            self.sessions_container
        )

        self.sessions_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        sessions_scroll = QScrollArea()

        sessions_scroll.setWidgetResizable(
            True
        )

        sessions_scroll.setWidget(
            self.sessions_container
        )

        sessions_frame_layout.addWidget(
            sessions_scroll,
            1,
        )

        content_layout.addWidget(
            subjects_frame,
            1,
        )

        content_layout.addWidget(
            sessions_frame,
            2,
        )

        outer_layout.addLayout(
            content_layout,
            1,
        )

        return tab

    # ==================================
    # Timer tab
    # ==================================

    def create_timer_tab(
        self,
    ) -> QWidget:
        tab = QWidget()

        layout = QVBoxLayout(
            tab
        )

        self.focus_timer = FocusTimerWidget(
            self,
            on_data_changed=(
                self.refresh_after_timer_change
            ),
        )

        layout.addWidget(
            self.focus_timer
        )

        layout.addStretch()

        return tab

    # ==================================
    # Analytics tab
    # ==================================

    def create_analytics_tab(
        self,
    ) -> QWidget:
        self.analytics_widget = (
            StudyAnalyticsWidget(
                self
            )
        )

        return self.analytics_widget

    def on_tab_changed(
        self,
        index: int,
    ):
        if (
            hasattr(
                self,
                "analytics_widget",
            )
            and self.tabs.widget(index)
            is self.analytics_widget
        ):
            self.analytics_widget.refresh()

    # ==================================
    # Refresh
    # ==================================

    def refresh(
        self,
    ):
        today = date.today()

        today_iso = (
            today.isoformat()
        )

        self.date_label.setText(
            format_jalali_date(
                today
            )
        )

        self.refresh_subjects()

        self.refresh_sessions(
            today_iso
        )

        self.refresh_stats(
            today_iso
        )

        if hasattr(
            self,
            "focus_timer",
        ):
            self.focus_timer.refresh_sessions()

        if hasattr(
            self,
            "analytics_widget",
        ):
            self.analytics_widget.refresh()

    def refresh_after_timer_change(
        self,
    ):
        today_iso = (
            date.today().isoformat()
        )

        self.refresh_sessions(
            today_iso
        )

        self.refresh_stats(
            today_iso
        )

        if hasattr(
            self,
            "analytics_widget",
        ):
            self.analytics_widget.refresh()

    # ==================================
    # Subjects
    # ==================================

    def refresh_subjects(
        self,
    ):
        self.clear_layout(
            self.subjects_layout
        )

        subjects = get_subjects()

        if not subjects:
            self.add_empty_message(
                self.subjects_layout,
                (
                    "هنوز موضوع مطالعه‌ای "
                    "اضافه نشده است."
                ),
            )

            return

        for subject in subjects:
            self.subjects_layout.addWidget(
                self.create_subject_card(
                    subject
                )
            )

    def create_subject_card(
        self,
        subject,
    ):
        frame = QFrame()

        frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 6px;
            }
            """
        )

        layout = QVBoxLayout(
            frame
        )

        name = QLabel(
            subject["name"]
        )

        name.setStyleSheet(
            """
            font-weight: bold;
            font-size: 15px;
            """
        )

        layout.addWidget(
            name
        )

        if subject["description"]:
            description = QLabel(
                subject["description"]
            )

            description.setWordWrap(
                True
            )

            description.setStyleSheet(
                """
                color: palette(window-text);
                """
            )

            layout.addWidget(
                description
            )

        actions = QHBoxLayout()

        edit_button = QPushButton(
            "ویرایش"
        )

        delete_button = QPushButton(
            "حذف"
        )

        edit_button.clicked.connect(
            lambda _,
            subject_id=subject["id"]:
            self.open_edit_subject(
                subject_id
            )
        )

        delete_button.clicked.connect(
            lambda _,
            subject_id=subject["id"]:
            self.confirm_delete_subject(
                subject_id
            )
        )

        actions.addWidget(
            edit_button
        )

        actions.addWidget(
            delete_button
        )

        layout.addLayout(
            actions
        )

        return frame

    def open_add_subject(
        self,
    ):
        dialog = StudySubjectDialog(
            self
        )

        if not dialog.exec():
            return

        try:
            create_subject(
                **dialog.get_data()
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def open_edit_subject(
        self,
        subject_id: int,
    ):
        subject = get_subject(
            subject_id
        )

        if subject is None:
            return

        dialog = StudySubjectDialog(
            self,
            subject=subject,
        )

        if not dialog.exec():
            return

        try:
            update_subject(
                subject_id=subject_id,
                **dialog.get_data(),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def confirm_delete_subject(
        self,
        subject_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف موضوع",
            (
                "با حذف این موضوع، تمام "
                "جلسات مطالعه مربوط به آن "
                "هم حذف می‌شوند. ادامه می‌دهید؟"
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

        self.focus_timer.pause_timer(
            notify=False
        )

        delete_subject(
            subject_id
        )

        self.refresh()

    # ==================================
    # Sessions
    # ==================================

    def refresh_sessions(
        self,
        today_iso: str,
    ):
        self.clear_layout(
            self.sessions_layout
        )

        sessions = (
            get_study_sessions_for_date(
                today_iso
            )
        )

        if not sessions:
            self.add_empty_message(
                self.sessions_layout,
                (
                    "برای امروز هنوز جلسه "
                    "مطالعه‌ای برنامه‌ریزی نشده است."
                ),
            )

            return

        for session in sessions:
            self.sessions_layout.addWidget(
                self.create_session_card(
                    session
                )
            )

    def create_session_card(
        self,
        session,
    ):
        frame = QFrame()

        frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 9px;
                padding: 8px;
            }
            """
        )

        layout = QVBoxLayout(
            frame
        )

        title_text = (
            session["title"]
            or session["subject_name"]
        )

        checkbox = QCheckBox(
            title_text
        )

        checkbox.setChecked(
            bool(
                session["completed"]
            )
        )

        checkbox.toggled.connect(
            lambda checked,
            session_id=session["id"]:
            self.toggle_session(
                session_id,
                checked,
            )
        )

        layout.addWidget(
            checkbox
        )

        subject = QLabel(
            "موضوع: "
            + session["subject_name"]
        )

        subject.setStyleSheet(
            """
            color: palette(window-text);
            """
        )

        layout.addWidget(
            subject
        )

        planned = (
            session["planned_minutes"]
        )

        actual = to_persian_digits(
            format_study_duration(
                session["actual_seconds"]
            )
        )

        time_label = QLabel(
            "زمان برنامه‌ریزی‌شده: "
            f"{to_persian_digits(planned)} دقیقه"
            "  |  "
            "زمان ثبت‌شده: "
            f"{actual}"
        )

        layout.addWidget(
            time_label
        )

        if session["notes"]:
            notes = QLabel(
                session["notes"]
            )

            notes.setWordWrap(
                True
            )

            layout.addWidget(
                notes
            )

        actions = QHBoxLayout()

        edit_button = QPushButton(
            "ویرایش"
        )

        delete_button = QPushButton(
            "حذف"
        )

        edit_button.clicked.connect(
            lambda _,
            session_id=session["id"]:
            self.open_edit_session(
                session_id
            )
        )

        delete_button.clicked.connect(
            lambda _,
            session_id=session["id"]:
            self.confirm_delete_session(
                session_id
            )
        )

        actions.addWidget(
            edit_button
        )

        actions.addWidget(
            delete_button
        )

        layout.addLayout(
            actions
        )

        return frame

    def open_add_session(
        self,
    ):
        if not get_subjects():
            QMessageBox.information(
                self,
                "موضوع مطالعه",
                (
                    "ابتدا حداقل یک موضوع "
                    "مطالعه ایجاد کنید."
                ),
            )

            return

        dialog = StudySessionDialog(
            self,
            default_date=date.today(),
        )

        if not dialog.exec():
            return

        try:
            create_study_session(
                **dialog.get_data()
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def open_edit_session(
        self,
        session_id: int,
    ):
        session = get_study_session(
            session_id
        )

        if session is None:
            return

        if (
            self.focus_timer.session_id
            == session_id
            and self.focus_timer.running
        ):
            self.focus_timer.pause_timer()

        dialog = StudySessionDialog(
            self,
            session=session,
        )

        if not dialog.exec():
            return

        try:
            update_study_session(
                session_id=session_id,
                **dialog.get_data(),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "خطا",
                str(error),
            )

            return

        self.refresh()

    def toggle_session(
        self,
        session_id: int,
        completed: bool,
    ):
        set_study_session_completed(
            session_id,
            completed,
        )

        self.refresh_after_timer_change()

    def confirm_delete_session(
        self,
        session_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "حذف جلسه مطالعه",
            (
                "آیا از حذف این جلسه "
                "مطالعه مطمئن هستید؟"
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

        if (
            self.focus_timer.session_id
            == session_id
        ):
            self.focus_timer.pause_timer(
                notify=False
            )

        delete_study_session(
            session_id
        )

        self.refresh()

    # ==================================
    # Daily stats
    # ==================================

    def refresh_stats(
        self,
        today_iso: str,
    ):
        stats = get_study_stats_for_date(
            today_iso
        )

        percentage = (
            stats["session_percentage"]
        )

        self.progress_label.setText(
            "پیشرفت جلسات امروز: "
            f"{to_persian_digits(percentage)}٪"
        )

        self.progress_bar.setValue(
            percentage
        )

        self.session_details.setText(
            "جلسات انجام‌شده: "
            f"{to_persian_digits(stats['completed_sessions'])}"
            " از "
            f"{to_persian_digits(stats['total_sessions'])}"
        )

        planned = (
            stats["planned_minutes"]
        )

        actual = to_persian_digits(
            format_study_duration(
                stats["actual_seconds"]
            )
        )

        self.time_details.setText(
            "زمان برنامه‌ریزی‌شده: "
            f"{to_persian_digits(planned)} دقیقه"
            "   |   "
            "زمان واقعی ثبت‌شده: "
            f"{actual}"
        )

    # ==================================
    # Helpers
    # ==================================

    def clear_layout(
        self,
        layout,
    ):
        while layout.count():
            item = layout.takeAt(
                0
            )

            widget = item.widget()

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
            padding: 20px;
            color: palette(window-text);
            """
        )

        layout.addWidget(
            label
        )