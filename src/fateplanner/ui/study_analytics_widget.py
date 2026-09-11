from datetime import date

from PySide6.QtCore import (
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.study_analytics_service import (
    get_study_daily_totals_between,
    get_study_sessions_between,
    get_study_subject_totals_between,
    get_study_summary_between,
)
from fateplanner.services.study_service import (
    format_study_duration,
)
from fateplanner.utils.date_utils import (
    PERSIAN_WEEKDAY_NAMES,
    format_jalali_date,
    format_jalali_short,
    format_jalali_week_range,
    get_persian_week,
    to_persian_digits,
)


class StudyBarChart(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.data = []

        self.setMinimumHeight(
            270
        )

    def set_data(
        self,
        data: list[dict],
    ):
        self.data = data

        self.update()

    def paintEvent(
        self,
        event,
    ):
        super().paintEvent(
            event
        )

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        left = 55
        right = 20
        top = 40
        bottom = 55

        chart_width = max(
            1,
            width - left - right,
        )

        chart_height = max(
            1,
            height - top - bottom,
        )

        # Background
        painter.fillRect(
            self.rect(),
            self.palette().base(),
        )

        # Title
        title_font = QFont(
            painter.font()
        )

        title_font.setBold(
            True
        )

        title_font.setPointSize(
            11
        )

        painter.setFont(
            title_font
        )

        painter.drawText(
            QRectF(
                left,
                5,
                chart_width,
                30,
            ),
            (
                Qt.AlignmentFlag.AlignCenter
                | Qt.AlignmentFlag.AlignVCenter
            ),
            "زمان برنامه‌ریزی‌شده و واقعی",
        )

        if not self.data:
            painter.drawText(
                QRectF(
                    left,
                    top,
                    chart_width,
                    chart_height,
                ),
                (
                    Qt.AlignmentFlag.AlignCenter
                    | Qt.AlignmentFlag.AlignVCenter
                ),
                "داده‌ای برای این بازه وجود ندارد.",
            )

            return

        planned_values = [
            float(
                row["planned_minutes"]
            )
            for row in self.data
        ]

        actual_values = [
            float(
                row["actual_seconds"]
            )
            / 60
            for row in self.data
        ]

        maximum = max(
            planned_values
            + actual_values
            + [1]
        )

        # Axes
        axis_pen = QPen(
            QColor(
                "#888888"
            )
        )

        painter.setPen(
            axis_pen
        )

        painter.drawLine(
            left,
            top,
            left,
            top + chart_height,
        )

        painter.drawLine(
            left,
            top + chart_height,
            left + chart_width,
            top + chart_height,
        )

        # Simple horizontal guides
        guide_font = QFont(
            painter.font()
        )

        guide_font.setPointSize(
            8
        )

        guide_font.setBold(
            False
        )

        painter.setFont(
            guide_font
        )

        for step in range(
            5
        ):
            ratio = (
                step / 4
            )

            y = (
                top
                + chart_height
                - chart_height
                * ratio
            )

            value = round(
                maximum
                * ratio
            )

            guide_pen = QPen(
                QColor(
                    "#dddddd"
                )
            )

            painter.setPen(
                guide_pen
            )

            painter.drawLine(
                left,
                int(y),
                left + chart_width,
                int(y),
            )

            painter.setPen(
                QColor(
                    "#666666"
                )
            )

            painter.drawText(
                QRectF(
                    0,
                    y - 10,
                    left - 8,
                    20,
                ),
                (
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                ),
                to_persian_digits(
                    value
                ),
            )

        group_width = (
            chart_width
            / len(
                self.data
            )
        )

        bar_width = min(
            24,
            group_width * 0.28,
        )

        for index, row in enumerate(
            self.data
        ):
            center_x = (
                left
                + group_width
                * (
                    index
                    + 0.5
                )
            )

            planned_minutes = float(
                row["planned_minutes"]
            )

            actual_minutes = (
                float(
                    row["actual_seconds"]
                )
                / 60
            )

            planned_height = (
                planned_minutes
                / maximum
                * chart_height
            )

            actual_height = (
                actual_minutes
                / maximum
                * chart_height
            )

            planned_rect = QRectF(
                center_x
                - bar_width
                - 2,
                top
                + chart_height
                - planned_height,
                bar_width,
                planned_height,
            )

            actual_rect = QRectF(
                center_x
                + 2,
                top
                + chart_height
                - actual_height,
                bar_width,
                actual_height,
            )

            painter.fillRect(
                planned_rect,
                QColor(
                    "#8fa8ff"
                ),
            )

            painter.fillRect(
                actual_rect,
                QColor(
                    "#67b77a"
                ),
            )

            row_date = (
                date.fromisoformat(
                    row[
                        "session_date"
                    ]
                )
            )

            weekday = (
                PERSIAN_WEEKDAY_NAMES[
                    row_date.weekday()
                ]
            )

            painter.setPen(
                QColor(
                    "#555555"
                )
            )

            painter.drawText(
                QRectF(
                    center_x
                    - group_width / 2,
                    top
                    + chart_height
                    + 7,
                    group_width,
                    38,
                ),
                (
                    Qt.AlignmentFlag.AlignCenter
                    | Qt.AlignmentFlag.AlignTop
                ),
                weekday,
            )

        # Legend
        legend_y = (
            height - 20
        )

        painter.fillRect(
            QRectF(
                left,
                legend_y,
                12,
                12,
            ),
            QColor(
                "#8fa8ff"
            ),
        )

        painter.drawText(
            QRectF(
                left + 18,
                legend_y - 4,
                130,
                20,
            ),
            Qt.AlignmentFlag.AlignLeft,
            "برنامه‌ریزی‌شده",
        )

        painter.fillRect(
            QRectF(
                left + 150,
                legend_y,
                12,
                12,
            ),
            QColor(
                "#67b77a"
            ),
        )

        painter.drawText(
            QRectF(
                left + 168,
                legend_y - 4,
                100,
                20,
            ),
            Qt.AlignmentFlag.AlignLeft,
            "زمان واقعی",
        )


class StudyAnalyticsWidget(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.anchor_date = (
            date.today()
        )

        main_layout = QVBoxLayout(
            self
        )

        # ==================================
        # Navigation
        # ==================================

        navigation = QHBoxLayout()

        previous_button = QPushButton(
            "هفته قبل"
        )

        current_button = QPushButton(
            "این هفته"
        )

        next_button = QPushButton(
            "هفته بعد"
        )

        self.week_label = QLabel()

        self.week_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.week_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        previous_button.clicked.connect(
            self.previous_week
        )

        current_button.clicked.connect(
            self.current_week
        )

        next_button.clicked.connect(
            self.next_week
        )

        navigation.addWidget(
            previous_button
        )

        navigation.addWidget(
            current_button
        )

        navigation.addWidget(
            self.week_label,
            1,
        )

        navigation.addWidget(
            next_button
        )

        main_layout.addLayout(
            navigation
        )

        # ==================================
        # Summary
        # ==================================

        summary_frame = QFrame()

        summary_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid #d8d8d8;
                border-radius: 10px;
                padding: 8px;
            }
            """
        )

        summary_layout = QHBoxLayout(
            summary_frame
        )

        self.planned_label = (
            self.create_summary_label()
        )

        self.actual_label = (
            self.create_summary_label()
        )

        self.sessions_label = (
            self.create_summary_label()
        )

        self.time_rate_label = (
            self.create_summary_label()
        )

        summary_layout.addWidget(
            self.planned_label
        )

        summary_layout.addWidget(
            self.actual_label
        )

        summary_layout.addWidget(
            self.sessions_label
        )

        summary_layout.addWidget(
            self.time_rate_label
        )

        main_layout.addWidget(
            summary_frame
        )

        # ==================================
        # Weekly chart
        # ==================================

        self.chart = StudyBarChart()

        main_layout.addWidget(
            self.chart
        )

        # ==================================
        # Subject table
        # ==================================

        subject_title = QLabel(
            "آمار موضوع‌ها"
        )

        subject_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            subject_title
        )

        self.subject_table = QTableWidget()

        self.subject_table.setColumnCount(
            6
        )

        self.subject_table.setHorizontalHeaderLabels(
            [
                "موضوع",
                "جلسات",
                "انجام‌شده",
                "برنامه",
                "زمان واقعی",
                "تحقق زمان",
            ]
        )

        self.configure_table(
            self.subject_table
        )

        self.subject_table.setMaximumHeight(
            230
        )

        main_layout.addWidget(
            self.subject_table
        )

        # ==================================
        # History
        # ==================================

        history_title = QLabel(
            "تاریخچه جلسات این هفته"
        )

        history_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        main_layout.addWidget(
            history_title
        )

        self.history_table = QTableWidget()

        self.history_table.setColumnCount(
            7
        )

        self.history_table.setHorizontalHeaderLabels(
            [
                "تاریخ",
                "موضوع",
                "جلسه",
                "برنامه",
                "زمان واقعی",
                "وضعیت",
                "یادداشت",
            ]
        )

        self.configure_table(
            self.history_table
        )

        main_layout.addWidget(
            self.history_table,
            1,
        )

        self.refresh()

    def create_summary_label(
        self,
    ) -> QLabel:
        label = QLabel()

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        label.setWordWrap(
            True
        )

        label.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            padding: 8px;
            """
        )

        return label

    def configure_table(
        self,
        table: QTableWidget,
    ):
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        table.setAlternatingRowColors(
            True
        )

        table.verticalHeader().setVisible(
            False
        )

        header = (
            table.horizontalHeader()
        )

        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    # ==================================
    # Refresh
    # ==================================

    def refresh(
        self,
    ):
        week = get_persian_week(
            self.anchor_date
        )

        start_date = (
            week[0]
        )

        end_date = (
            week[-1]
        )

        start_iso = (
            start_date.isoformat()
        )

        end_iso = (
            end_date.isoformat()
        )

        self.week_label.setText(
            format_jalali_week_range(
                start_date,
                end_date,
            )
        )

        summary = (
            get_study_summary_between(
                start_iso,
                end_iso,
            )
        )

        daily = (
            get_study_daily_totals_between(
                start_iso,
                end_iso,
            )
        )

        subjects = (
            get_study_subject_totals_between(
                start_iso,
                end_iso,
            )
        )

        sessions = (
            get_study_sessions_between(
                start_iso,
                end_iso,
            )
        )

        self.refresh_summary(
            summary
        )

        self.chart.set_data(
            daily
        )

        self.refresh_subject_table(
            subjects
        )

        self.refresh_history_table(
            sessions
        )

    def refresh_summary(
        self,
        summary: dict,
    ):
        planned = (
            summary[
                "planned_minutes"
            ]
        )

        actual = (
            format_study_duration(
                summary[
                    "actual_seconds"
                ]
            )
        )

        completed = (
            summary[
                "completed_sessions"
            ]
        )

        total = (
            summary[
                "total_sessions"
            ]
        )

        time_rate = (
            summary[
                "time_percentage"
            ]
        )

        self.planned_label.setText(
            "زمان برنامه‌ریزی‌شده\n"
            f"{to_persian_digits(planned)} دقیقه"
        )

        self.actual_label.setText(
            "زمان واقعی\n"
            f"{to_persian_digits(actual)}"
        )

        self.sessions_label.setText(
            "جلسات تکمیل‌شده\n"
            f"{to_persian_digits(completed)}"
            " از "
            f"{to_persian_digits(total)}"
        )

        self.time_rate_label.setText(
            "تحقق زمان\n"
            f"{to_persian_digits(time_rate)}٪"
        )

    def refresh_subject_table(
        self,
        subjects: list[dict],
    ):
        self.subject_table.setRowCount(
            len(
                subjects
            )
        )

        for row_index, subject in enumerate(
            subjects
        ):
            actual = (
                format_study_duration(
                    subject[
                        "actual_seconds"
                    ]
                )
            )

            values = [
                subject[
                    "subject_name"
                ],
                to_persian_digits(
                    subject[
                        "total_sessions"
                    ]
                ),
                to_persian_digits(
                    subject[
                        "completed_sessions"
                    ]
                ),
                (
                    to_persian_digits(
                        subject[
                            "planned_minutes"
                        ]
                    )
                    + " دقیقه"
                ),
                to_persian_digits(
                    actual
                ),
                (
                    to_persian_digits(
                        subject[
                            "time_percentage"
                        ]
                    )
                    + "٪"
                ),
            ]

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    str(
                        value
                    )
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.subject_table.setItem(
                    row_index,
                    column,
                    item,
                )

    def refresh_history_table(
        self,
        sessions,
    ):
        sessions = list(
            reversed(
                sessions
            )
        )

        self.history_table.setRowCount(
            len(
                sessions
            )
        )

        for row_index, session in enumerate(
            sessions
        ):
            session_date = (
                date.fromisoformat(
                    session[
                        "session_date"
                    ]
                )
            )

            title = (
                session["title"]
                or "—"
            )

            actual = (
                format_study_duration(
                    session[
                        "actual_seconds"
                    ]
                )
            )

            status = (
                "انجام شده"
                if session["completed"]
                else "انجام نشده"
            )

            notes = (
                session["notes"]
                or "—"
            )

            values = [
                format_jalali_short(
                    session_date
                ),
                session[
                    "subject_name"
                ],
                title,
                (
                    to_persian_digits(
                        session[
                            "planned_minutes"
                        ]
                    )
                    + " دقیقه"
                ),
                to_persian_digits(
                    actual
                ),
                status,
                notes,
            ]

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    str(
                        value
                    )
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.history_table.setItem(
                    row_index,
                    column,
                    item,
                )

    # ==================================
    # Navigation
    # ==================================

    def previous_week(
        self,
    ):
        week = get_persian_week(
            self.anchor_date
        )

        self.anchor_date = (
            week[0]
            - date.resolution
        )

        self.refresh()

    def next_week(
        self,
    ):
        week = get_persian_week(
            self.anchor_date
        )

        self.anchor_date = (
            week[-1]
            + date.resolution
        )

        self.refresh()

    def current_week(
        self,
    ):
        self.anchor_date = (
            date.today()
        )

        self.refresh()