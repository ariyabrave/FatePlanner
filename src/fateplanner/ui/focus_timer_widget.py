from datetime import date

from PySide6.QtCore import (
    Qt,
    QTimer,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.study_service import (
    add_study_time,
    format_study_duration,
    get_study_session,
    get_study_sessions_for_date,
    get_study_timer_state,
    save_study_timer_state,
    set_study_session_completed,
    sync_study_session_completion_from_time,
)
from fateplanner.utils.date_utils import (
    to_persian_digits,
)


class FocusTimerWidget(QFrame):
    def __init__(
        self,
        parent=None,
        on_data_changed=None,
    ):
        super().__init__(parent)

        self.on_data_changed = (
            on_data_changed
        )

        self.session_id = None

        self.phase = "focus"

        self.focus_minutes = 25

        self.break_minutes = 5

        self.remaining_seconds = (
            25 * 60
        )

        self.pomodoro_count = 0

        self.running = False

        self.unflushed_focus_seconds = 0

        self.base_actual_seconds = 0

        self.persistence_counter = 0

        self.timer = QTimer(
            self
        )

        self.timer.setInterval(
            1000
        )

        self.timer.timeout.connect(
            self.tick
        )

        self.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d0d0d0;
                border-radius: 12px;
                padding: 10px;
            }
            """
        )

        main_layout = QVBoxLayout(
            self
        )

        # ==================================
        # Heading
        # ==================================

        heading = QLabel(
            "⏱ تمرکز و پومودورو"
        )

        heading.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            heading
        )

        # ==================================
        # Study session
        # ==================================

        session_layout = QHBoxLayout()

        session_label = QLabel(
            "جلسه مطالعه:"
        )

        self.session_input = QComboBox()

        self.session_input.currentIndexChanged.connect(
            self.on_session_changed
        )

        session_layout.addWidget(
            session_label
        )

        session_layout.addWidget(
            self.session_input,
            1,
        )

        main_layout.addLayout(
            session_layout
        )

        # ==================================
        # Preset
        # ==================================

        preset_layout = QHBoxLayout()

        preset_label = QLabel(
            "حالت تمرکز:"
        )

        self.preset_input = QComboBox()

        self.preset_input.addItem(
            "پومودورو ۲۵ / ۵",
            "pomodoro",
        )

        self.preset_input.addItem(
            "تمرکز عمیق ۵۰ / ۱۰",
            "deep",
        )

        self.preset_input.addItem(
            "سفارشی",
            "custom",
        )

        self.preset_input.currentIndexChanged.connect(
            self.on_preset_changed
        )

        preset_layout.addWidget(
            preset_label
        )

        preset_layout.addWidget(
            self.preset_input,
            1,
        )

        main_layout.addLayout(
            preset_layout
        )

        # ==================================
        # Custom durations
        # ==================================

        self.custom_widget = QWidget()

        custom_layout = QHBoxLayout(
            self.custom_widget
        )

        custom_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.custom_focus_input = (
            QSpinBox()
        )

        self.custom_focus_input.setRange(
            1,
            180,
        )

        self.custom_focus_input.setValue(
            25
        )

        self.custom_focus_input.setSuffix(
            " دقیقه تمرکز"
        )

        self.custom_break_input = (
            QSpinBox()
        )

        self.custom_break_input.setRange(
            1,
            60,
        )

        self.custom_break_input.setValue(
            5
        )

        self.custom_break_input.setSuffix(
            " دقیقه استراحت"
        )

        self.custom_focus_input.valueChanged.connect(
            self.on_custom_duration_changed
        )

        self.custom_break_input.valueChanged.connect(
            self.on_custom_duration_changed
        )

        custom_layout.addWidget(
            self.custom_focus_input
        )

        custom_layout.addWidget(
            self.custom_break_input
        )

        main_layout.addWidget(
            self.custom_widget
        )

        # ==================================
        # Phase
        # ==================================

        self.phase_label = QLabel()

        self.phase_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.phase_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            self.phase_label
        )

        # ==================================
        # Timer
        # ==================================

        self.timer_label = QLabel(
            "۲۵:۰۰"
        )

        self.timer_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.timer_label.setStyleSheet(
            """
            font-size: 48px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            self.timer_label
        )

        self.phase_progress = QProgressBar()

        main_layout.addWidget(
            self.phase_progress
        )

        # ==================================
        # Pomodoro count
        # ==================================

        self.pomodoro_label = QLabel()

        self.pomodoro_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addWidget(
            self.pomodoro_label
        )

        # ==================================
        # Actual study progress
        # ==================================

        self.session_time_label = QLabel()

        self.session_time_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addWidget(
            self.session_time_label
        )

        self.session_progress = QProgressBar()

        self.session_progress.setRange(
            0,
            100,
        )

        main_layout.addWidget(
            self.session_progress
        )

        # ==================================
        # Main controls
        # ==================================

        controls = QHBoxLayout()

        self.start_button = QPushButton(
            "شروع"
        )

        self.pause_button = QPushButton(
            "توقف موقت"
        )

        self.reset_button = QPushButton(
            "بازنشانی"
        )

        self.next_phase_button = QPushButton(
            "مرحله بعد"
        )

        self.start_button.clicked.connect(
            self.start_timer
        )

        self.pause_button.clicked.connect(
            self.pause_timer
        )

        self.reset_button.clicked.connect(
            self.reset_timer
        )

        self.next_phase_button.clicked.connect(
            self.skip_phase
        )

        controls.addWidget(
            self.start_button
        )

        controls.addWidget(
            self.pause_button
        )

        controls.addWidget(
            self.reset_button
        )

        controls.addWidget(
            self.next_phase_button
        )

        main_layout.addLayout(
            controls
        )

        # ==================================
        # Session completion
        # ==================================

        self.finish_session_button = QPushButton(
            "✓ پایان جلسه مطالعه"
        )

        self.finish_session_button.clicked.connect(
            self.finish_session
        )

        main_layout.addWidget(
            self.finish_session_button
        )

        # ==================================
        # Restore saved timer
        # ==================================

        self.load_saved_state()

        self.refresh_sessions()

        self.update_custom_visibility()

        self.update_display()

        self.update_button_state()

        app = QApplication.instance()

        if app is not None:
            app.aboutToQuit.connect(
                self.prepare_for_shutdown
            )

    # ==================================
    # Persistence
    # ==================================

    def load_saved_state(
        self,
    ):
        state = get_study_timer_state()

        if state is None:
            return

        self.session_id = (
            state["session_id"]
        )

        self.phase = (
            state["phase"]
        )

        self.focus_minutes = int(
            state["focus_minutes"]
        )

        self.break_minutes = int(
            state["break_minutes"]
        )

        self.remaining_seconds = max(
            0,
            int(
                state["remaining_seconds"]
            ),
        )

        self.pomodoro_count = int(
            state["pomodoro_count"]
        )

        # A previously running timer is
        # deliberately restored PAUSED.
        self.running = False

        self.custom_focus_input.blockSignals(
            True
        )

        self.custom_break_input.blockSignals(
            True
        )

        self.custom_focus_input.setValue(
            self.focus_minutes
        )

        self.custom_break_input.setValue(
            self.break_minutes
        )

        self.custom_focus_input.blockSignals(
            False
        )

        self.custom_break_input.blockSignals(
            False
        )

        self.preset_input.blockSignals(
            True
        )

        if (
            self.focus_minutes == 25
            and self.break_minutes == 5
        ):
            index = (
                self.preset_input.findData(
                    "pomodoro"
                )
            )

        elif (
            self.focus_minutes == 50
            and self.break_minutes == 10
        ):
            index = (
                self.preset_input.findData(
                    "deep"
                )
            )

        else:
            index = (
                self.preset_input.findData(
                    "custom"
                )
            )

        if index >= 0:
            self.preset_input.setCurrentIndex(
                index
            )

        self.preset_input.blockSignals(
            False
        )

        self.save_state(
            is_running=False
        )

    def save_state(
        self,
        is_running: bool | None = None,
    ):
        if is_running is None:
            is_running = self.running

        save_study_timer_state(
            session_id=self.session_id,
            phase=self.phase,
            focus_minutes=self.focus_minutes,
            break_minutes=self.break_minutes,
            remaining_seconds=(
                self.remaining_seconds
            ),
            pomodoro_count=(
                self.pomodoro_count
            ),
            is_running=is_running,
        )

    def prepare_for_shutdown(
        self,
    ):
        if self.timer.isActive():
            self.timer.stop()

        self.running = False

        self.flush_focus_time()

        self.save_state(
            is_running=False
        )

    # ==================================
    # Session selection
    # ==================================

    def refresh_sessions(
        self,
    ):
        previous_session_id = (
            self.session_id
        )

        sessions = (
            get_study_sessions_for_date(
                date.today().isoformat()
            )
        )

        self.session_input.blockSignals(
            True
        )

        self.session_input.clear()

        for session in sessions:
            title = (
                session["title"]
                or session["subject_name"]
            )

            label = (
                f"{session['subject_name']} — "
                f"{title}"
                " — "
                f"{to_persian_digits(session['planned_minutes'])} دقیقه"
            )

            self.session_input.addItem(
                label,
                session["id"],
            )

        selected_index = -1

        if previous_session_id is not None:
            selected_index = (
                self.session_input.findData(
                    previous_session_id
                )
            )

        if (
            selected_index < 0
            and self.session_input.count()
        ):
            selected_index = 0

        if selected_index >= 0:
            self.session_input.setCurrentIndex(
                selected_index
            )

            new_session_id = (
                self.session_input.currentData()
            )

        else:
            new_session_id = None

        self.session_input.blockSignals(
            False
        )

        if (
            new_session_id
            != previous_session_id
        ):
            if self.running:
                self.pause_timer(
                    notify=False
                )

            self.session_id = (
                new_session_id
            )

            self.phase = "focus"

            self.remaining_seconds = (
                self.focus_minutes
                * 60
            )

            self.pomodoro_count = 0

            self.unflushed_focus_seconds = 0

        else:
            self.session_id = (
                new_session_id
            )

        self.load_session_time()

        self.save_state(
            is_running=False
        )

        self.update_display()

        self.update_button_state()

    def on_session_changed(
        self,
    ):
        new_session_id = (
            self.session_input.currentData()
        )

        if (
            new_session_id
            == self.session_id
        ):
            return

        if self.running:
            self.pause_timer(
                notify=True
            )

        self.session_id = (
            new_session_id
        )

        self.phase = "focus"

        self.remaining_seconds = (
            self.focus_minutes * 60
        )

        self.pomodoro_count = 0

        self.unflushed_focus_seconds = 0

        self.load_session_time()

        self.save_state(
            is_running=False
        )

        self.update_display()

        self.update_button_state()

    def load_session_time(
        self,
    ):
        self.base_actual_seconds = 0

        if self.session_id is None:
            return

        session = get_study_session(
            self.session_id
        )

        if session is None:
            self.session_id = None
            return

        self.base_actual_seconds = int(
            session["actual_seconds"]
        )

    # ==================================
    # Presets
    # ==================================

    def on_preset_changed(
        self,
    ):
        if self.running:
            self.pause_timer(
                notify=True
            )

        preset = (
            self.preset_input.currentData()
        )

        if preset == "pomodoro":
            self.focus_minutes = 25
            self.break_minutes = 5

        elif preset == "deep":
            self.focus_minutes = 50
            self.break_minutes = 10

        else:
            self.focus_minutes = (
                self.custom_focus_input
                .value()
            )

            self.break_minutes = (
                self.custom_break_input
                .value()
            )

        self.phase = "focus"

        self.remaining_seconds = (
            self.focus_minutes * 60
        )

        self.pomodoro_count = 0

        self.update_custom_visibility()

        self.save_state(
            is_running=False
        )

        self.update_display()

    def on_custom_duration_changed(
        self,
    ):
        if (
            self.preset_input.currentData()
            != "custom"
        ):
            return

        if self.running:
            return

        self.focus_minutes = (
            self.custom_focus_input.value()
        )

        self.break_minutes = (
            self.custom_break_input.value()
        )

        self.phase = "focus"

        self.remaining_seconds = (
            self.focus_minutes * 60
        )

        self.pomodoro_count = 0

        self.save_state(
            is_running=False
        )

        self.update_display()

    def update_custom_visibility(
        self,
    ):
        self.custom_widget.setVisible(
            self.preset_input.currentData()
            == "custom"
        )

    # ==================================
    # Timer
    # ==================================

    def start_timer(
        self,
    ):
        if self.session_id is None:
            QMessageBox.information(
                self,
                "جلسه مطالعه",
                (
                    "برای شروع تایمر ابتدا "
                    "یک جلسه مطالعه برای امروز "
                    "ایجاد کنید."
                ),
            )

            return

        if self.running:
            return

        if self.remaining_seconds <= 0:
            self.reset_current_phase()

        self.running = True

        self.persistence_counter = 0

        self.timer.start()

        self.save_state(
            is_running=True
        )

        self.update_button_state()

    def pause_timer(
        self,
        *,
        notify: bool = True,
    ):
        if self.timer.isActive():
            self.timer.stop()

        was_running = self.running

        self.running = False

        flushed = self.flush_focus_time()

        self.save_state(
            is_running=False
        )

        self.update_display()

        self.update_button_state()

        if (
            notify
            and (
                was_running
                or flushed
            )
            and self.on_data_changed
        ):
            self.on_data_changed()

    def reset_timer(
        self,
    ):
        self.pause_timer(
            notify=True
        )

        self.phase = "focus"

        self.remaining_seconds = (
            self.focus_minutes
            * 60
        )

        self.pomodoro_count = 0

        self.persistence_counter = 0

        self.save_state(
            is_running=False
        )

        self.update_display()

        self.update_button_state()

    def reset_current_phase(
        self,
    ):
        if self.phase == "focus":
            self.remaining_seconds = (
                self.focus_minutes
                * 60
            )

        else:
            self.remaining_seconds = (
                self.break_minutes
                * 60
            )

    def tick(
        self,
    ):
        if not self.running:
            return

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1

            if self.phase == "focus":
                self.unflushed_focus_seconds += 1

        self.persistence_counter += 1

        if (
            self.persistence_counter
            >= 5
        ):
            self.persistence_counter = 0

            self.flush_focus_time()

            self.save_state(
                is_running=True
            )

        self.update_display()

        if self.remaining_seconds <= 0:
            self.complete_phase()

    def complete_phase(
        self,
    ):
        if self.phase == "focus":
            self.flush_focus_time()

            self.pomodoro_count += 1

            if self.session_id is not None:
                sync_study_session_completion_from_time(
                    self.session_id
                )

            self.phase = "break"

            self.remaining_seconds = (
                self.break_minutes
                * 60
            )

            if self.on_data_changed:
                self.on_data_changed()

        else:
            self.phase = "focus"

            self.remaining_seconds = (
                self.focus_minutes
                * 60
            )

        self.save_state(
            is_running=self.running
        )

        self.update_display()

    def skip_phase(
        self,
    ):
        if self.session_id is None:
            return

        if self.phase == "focus":
            flushed = (
                self.flush_focus_time()
            )

            self.phase = "break"

            self.remaining_seconds = (
                self.break_minutes
                * 60
            )

            if (
                flushed
                and self.on_data_changed
            ):
                self.on_data_changed()

        else:
            self.phase = "focus"

            self.remaining_seconds = (
                self.focus_minutes
                * 60
            )

        self.save_state()

        self.update_display()

    # ==================================
    # Actual study time
    # ==================================

    def flush_focus_time(
        self,
    ) -> bool:
        if (
            self.session_id is None
            or self.unflushed_focus_seconds <= 0
        ):
            return False

        seconds = (
            self.unflushed_focus_seconds
        )

        add_study_time(
            self.session_id,
            seconds,
        )

        self.base_actual_seconds += (
            seconds
        )

        self.unflushed_focus_seconds = 0

        sync_study_session_completion_from_time(
            self.session_id
        )

        return True

    def finish_session(
        self,
    ):
        if self.session_id is None:
            return

        self.pause_timer(
            notify=False
        )

        set_study_session_completed(
            self.session_id,
            True,
        )

        self.phase = "focus"

        self.remaining_seconds = (
            self.focus_minutes
            * 60
        )

        self.pomodoro_count = 0

        self.save_state(
            is_running=False
        )

        self.update_display()

        if self.on_data_changed:
            self.on_data_changed()

    # ==================================
    # Display
    # ==================================

    def update_display(
        self,
    ):
        minutes = (
            self.remaining_seconds
            // 60
        )

        seconds = (
            self.remaining_seconds
            % 60
        )

        timer_text = (
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

        self.timer_label.setText(
            to_persian_digits(
                timer_text
            )
        )

        if self.phase == "focus":
            self.phase_label.setText(
                "🎯 زمان تمرکز"
            )

            total_seconds = (
                self.focus_minutes
                * 60
            )

        else:
            self.phase_label.setText(
                "☕ زمان استراحت"
            )

            total_seconds = (
                self.break_minutes
                * 60
            )

        elapsed = max(
            0,
            total_seconds
            - self.remaining_seconds,
        )

        self.phase_progress.setRange(
            0,
            max(
                1,
                total_seconds,
            ),
        )

        self.phase_progress.setValue(
            min(
                total_seconds,
                elapsed,
            )
        )

        self.pomodoro_label.setText(
            "پومودوروهای کامل: "
            f"{to_persian_digits(self.pomodoro_count)}"
        )

        self.update_session_progress()

    def update_session_progress(
        self,
    ):
        if self.session_id is None:
            self.session_time_label.setText(
                "جلسه‌ای انتخاب نشده است."
            )

            self.session_progress.setValue(
                0
            )

            return

        session = get_study_session(
            self.session_id
        )

        if session is None:
            self.session_time_label.setText(
                "جلسه پیدا نشد."
            )

            self.session_progress.setValue(
                0
            )

            return

        actual_seconds = (
            self.base_actual_seconds
            + self.unflushed_focus_seconds
        )

        planned_seconds = (
            int(
                session["planned_minutes"]
            )
            * 60
        )

        percentage = (
            round(
                actual_seconds
                / planned_seconds
                * 100
            )
            if planned_seconds
            else 0
        )

        visible_percentage = min(
            100,
            percentage,
        )

        actual_text = (
            to_persian_digits(
                format_study_duration(
                    actual_seconds
                )
            )
        )

        planned_text = (
            to_persian_digits(
                session[
                    "planned_minutes"
                ]
            )
        )

        self.session_time_label.setText(
            "زمان ثبت‌شده: "
            f"{actual_text}"
            " از "
            f"{planned_text} دقیقه"
        )

        self.session_progress.setValue(
            visible_percentage
        )

    def update_button_state(
        self,
    ):
        has_session = (
            self.session_id is not None
        )

        self.start_button.setEnabled(
            has_session
            and not self.running
        )

        self.pause_button.setEnabled(
            self.running
        )

        self.reset_button.setEnabled(
            has_session
        )

        self.next_phase_button.setEnabled(
            has_session
        )

        self.finish_session_button.setEnabled(
            has_session
        )

        self.session_input.setEnabled(
            not self.running
        )

        self.preset_input.setEnabled(
            not self.running
        )

        custom_enabled = (
            not self.running
            and self.preset_input.currentData()
            == "custom"
        )

        self.custom_focus_input.setEnabled(
            custom_enabled
        )

        self.custom_break_input.setEnabled(
            custom_enabled
        )

        if self.running:
            self.start_button.setText(
                "در حال اجرا"
            )

        elif (
            self.phase == "focus"
            and self.remaining_seconds
            < self.focus_minutes * 60
        ):
            self.start_button.setText(
                "ادامه"
            )

        elif (
            self.phase == "break"
            and self.remaining_seconds
            < self.break_minutes * 60
        ):
            self.start_button.setText(
                "ادامه"
            )

        else:
            self.start_button.setText(
                "شروع"
            )