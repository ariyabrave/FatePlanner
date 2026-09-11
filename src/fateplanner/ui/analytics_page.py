from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from fateplanner.services.analytics_service import (
    get_finance_snapshot,
    get_productivity_snapshot,
)
from fateplanner.services.finance_service import (
    format_money,
)
from fateplanner.services.study_service import (
    format_study_duration,
)
from fateplanner.ui.analytics_charts import (
    DonutChartWidget,
    GaugeWidget,
    ProductivityChartWidget,
    RadarChartWidget,
)
from fateplanner.utils.date_utils import (
    format_jalali_date,
    format_jalali_month_title,
    format_jalali_short,
    format_jalali_week_range,
    get_persian_week,
    gregorian_to_jalali,
    jalali_to_gregorian,
    to_persian_digits,
)


class AnalyticsPage(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.productivity_anchor = (
            date.today()
        )

        self.finance_anchor = (
            date.today()
        )

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "گزارش‌ها و پیشرفت"
        )

        title.setStyleSheet(
            """
            font-size: 30px;
            font-weight: bold;
            """
        )

        self.date_label = QLabel()

        layout.addWidget(
            title
        )

        layout.addWidget(
            self.date_label
        )

        self.tabs = QTabWidget()

        self.overview_tab = (
            self.create_overview_tab()
        )

        self.productivity_tab = (
            self.create_productivity_tab()
        )

        self.finance_tab = (
            self.create_finance_tab()
        )

        self.tabs.addTab(
            self.overview_tab,
            "نمای کلی",
        )

        self.tabs.addTab(
            self.productivity_tab,
            "بهره‌وری",
        )

        self.tabs.addTab(
            self.finance_tab,
            "امور مالی",
        )

        self.tabs.currentChanged.connect(
            self.on_tab_changed
        )

        layout.addWidget(
            self.tabs,
            1,
        )

        self.refresh()

    def create_overview_tab(
        self,
    ):
        tab = QWidget()

        layout = QVBoxLayout(
            tab
        )

        top_layout = QHBoxLayout()

        self.radar = RadarChartWidget()

        top_layout.addWidget(
            self.radar,
            2,
        )

        gauges_widget = QWidget()

        gauges = QGridLayout(
            gauges_widget
        )

        self.task_gauge = GaugeWidget(
            "کارها"
        )

        self.habit_gauge = GaugeWidget(
            "عادت‌ها"
        )

        self.study_gauge = GaugeWidget(
            "مطالعه"
        )

        self.savings_gauge = GaugeWidget(
            "پس‌انداز"
        )

        gauges.addWidget(
            self.task_gauge,
            0,
            0,
        )

        gauges.addWidget(
            self.habit_gauge,
            0,
            1,
        )

        gauges.addWidget(
            self.study_gauge,
            1,
            0,
        )

        gauges.addWidget(
            self.savings_gauge,
            1,
            1,
        )

        top_layout.addWidget(
            gauges_widget,
            2,
        )

        layout.addLayout(
            top_layout
        )

        finance_frame = QFrame()

        finance_frame.setStyleSheet(
            """
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 8px;
            }
            """
        )

        finance_layout = QHBoxLayout(
            finance_frame
        )

        self.overview_finance = (
            self.create_card()
        )

        self.overview_budget = (
            self.create_card()
        )

        self.overview_savings = (
            self.create_card()
        )

        finance_layout.addWidget(
            self.overview_finance
        )

        finance_layout.addWidget(
            self.overview_budget
        )

        finance_layout.addWidget(
            self.overview_savings
        )

        layout.addWidget(
            finance_frame
        )

        self.overview_warning = QLabel()

        self.overview_warning.setWordWrap(
            True
        )

        self.overview_warning.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.overview_warning.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            padding: 12px;
            """
        )

        layout.addWidget(
            self.overview_warning
        )

        return tab

    def create_productivity_tab(
        self,
    ):
        tab = QWidget()

        layout = QVBoxLayout(
            tab
        )

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

        self.productivity_week_label = (
            QLabel()
        )

        self.productivity_week_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        previous_button.clicked.connect(
            self.previous_productivity_week
        )

        current_button.clicked.connect(
            self.current_productivity_week
        )

        next_button.clicked.connect(
            self.next_productivity_week
        )

        navigation.addWidget(
            previous_button
        )

        navigation.addWidget(
            current_button
        )

        navigation.addWidget(
            self.productivity_week_label,
            1,
        )

        navigation.addWidget(
            next_button
        )

        layout.addLayout(
            navigation
        )

        summary = QHBoxLayout()

        self.task_summary_label = (
            self.create_card()
        )

        self.habit_summary_label = (
            self.create_card()
        )

        self.study_summary_label = (
            self.create_card()
        )

        summary.addWidget(
            self.task_summary_label
        )

        summary.addWidget(
            self.habit_summary_label
        )

        summary.addWidget(
            self.study_summary_label
        )

        layout.addLayout(
            summary
        )

        metric_layout = QHBoxLayout()

        metric_layout.addWidget(
            QLabel(
                "نمودار:"
            )
        )

        self.metric_input = QComboBox()

        self.metric_input.addItem(
            "کارها",
            "tasks",
        )

        self.metric_input.addItem(
            "عادت‌ها",
            "habits",
        )

        self.metric_input.addItem(
            "مطالعه",
            "study",
        )

        self.metric_input.currentIndexChanged.connect(
            self.refresh_productivity_chart
        )

        metric_layout.addWidget(
            self.metric_input,
            1,
        )

        layout.addLayout(
            metric_layout
        )

        self.productivity_chart = (
            ProductivityChartWidget()
        )

        layout.addWidget(
            self.productivity_chart
        )

        self.daily_table = QTableWidget()

        self.daily_table.setColumnCount(
            6
        )

        self.daily_table.setHorizontalHeaderLabels(
            [
                "تاریخ",
                "کارها",
                "عادت‌ها",
                "مطالعه برنامه",
                "مطالعه واقعی",
                "وضعیت",
            ]
        )

        self.configure_table(
            self.daily_table
        )

        layout.addWidget(
            self.daily_table,
            1,
        )

        return tab

    def create_finance_tab(
        self,
    ):
        tab = QWidget()

        layout = QVBoxLayout(
            tab
        )

        navigation = QHBoxLayout()

        previous_button = QPushButton(
            "ماه قبل"
        )

        current_button = QPushButton(
            "ماه جاری"
        )

        next_button = QPushButton(
            "ماه بعد"
        )

        self.finance_month_label = QLabel()

        self.finance_month_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        previous_button.clicked.connect(
            self.previous_finance_month
        )

        current_button.clicked.connect(
            self.current_finance_month
        )

        next_button.clicked.connect(
            self.next_finance_month
        )

        navigation.addWidget(
            previous_button
        )

        navigation.addWidget(
            current_button
        )

        navigation.addWidget(
            self.finance_month_label,
            1,
        )

        navigation.addWidget(
            next_button
        )

        layout.addLayout(
            navigation
        )

        summary = QHBoxLayout()

        self.finance_summary_label = (
            self.create_card()
        )

        self.budget_summary_label = (
            self.create_card()
        )

        self.savings_summary_label = (
            self.create_card()
        )

        summary.addWidget(
            self.finance_summary_label
        )

        summary.addWidget(
            self.budget_summary_label
        )

        summary.addWidget(
            self.savings_summary_label
        )

        layout.addLayout(
            summary
        )

        finance_visuals = QHBoxLayout()

        self.expense_donut = (
            DonutChartWidget()
        )

        finance_visuals.addWidget(
            self.expense_donut,
            1,
        )

        self.category_table = QTableWidget()

        self.category_table.setColumnCount(
            4
        )

        self.category_table.setHorizontalHeaderLabels(
            [
                "دسته‌بندی",
                "هزینه",
                "تراکنش‌ها",
                "سهم از هزینه",
            ]
        )

        self.configure_table(
            self.category_table
        )

        finance_visuals.addWidget(
            self.category_table,
            2,
        )

        layout.addLayout(
            finance_visuals,
            1,
        )

        return tab

    def create_card(
        self,
    ):
        label = QLabel()

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        label.setWordWrap(
            True
        )

        label.setMinimumHeight(
            100
        )

        label.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            padding: 10px;
            """
        )

        return label

    def configure_table(
        self,
        table,
    ):
        table.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        table.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        table.setAlternatingRowColors(
            True
        )

        table.verticalHeader().setVisible(
            False
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

    def refresh(
        self,
    ):
        self.date_label.setText(
            format_jalali_date(
                date.today()
            )
        )

        self.refresh_overview()
        self.refresh_productivity()
        self.refresh_finance()

    def refresh_overview(
        self,
    ):
        productivity = (
            get_productivity_snapshot(
                date.today()
            )
        )

        finance = (
            get_finance_snapshot(
                date.today()
            )
        )

        tasks = productivity["tasks"]
        habits = productivity["habits"]
        study = productivity["study"]

        finance_data = finance["finance"]
        budgets = finance["budgets"]
        savings = finance["savings"]

        task_score = min(
            100,
            tasks["percentage"],
        )

        habit_score = min(
            100,
            habits["percentage"],
        )

        study_score = min(
            100,
            study["time_percentage"],
        )

        if savings["total_target"]:
            savings_score = min(
                100,
                round(
                    savings["total_saved"]
                    / savings["total_target"]
                    * 100
                ),
            )

        else:
            savings_score = 0

        if budgets["total_budget"]:
            if (
                budgets["budgeted_spending"]
                <= budgets["total_budget"]
            ):
                budget_score = 100

            else:
                budget_score = max(
                    0,
                    round(
                        budgets["total_budget"]
                        / budgets[
                            "budgeted_spending"
                        ]
                        * 100
                    ),
                )

        else:
            budget_score = 0

        self.task_gauge.set_data(
            task_score,
            "تکمیل هفتگی",
        )

        self.habit_gauge.set_data(
            habit_score,
            "پایبندی هفتگی",
        )

        self.study_gauge.set_data(
            study_score,
            "تحقق زمان مطالعه",
        )

        self.savings_gauge.set_data(
            savings_score,
            "پیشرفت اهداف",
        )

        self.radar.set_metrics(
            [
                (
                    "کارها",
                    task_score,
                ),
                (
                    "عادت‌ها",
                    habit_score,
                ),
                (
                    "مطالعه",
                    study_score,
                ),
                (
                    "بودجه",
                    budget_score,
                ),
                (
                    "پس‌انداز",
                    savings_score,
                ),
            ]
        )

        self.overview_finance.setText(
            "مالی ماه\n\n"
            "درآمد: "
            + to_persian_digits(
                format_money(
                    finance_data[
                        "income"
                    ]
                )
            )
            + "\nهزینه: "
            + to_persian_digits(
                format_money(
                    finance_data[
                        "expense"
                    ]
                )
            )
            + "\nمانده: "
            + to_persian_digits(
                format_money(
                    finance_data[
                        "balance"
                    ]
                )
            )
        )

        self.overview_budget.setText(
            "بودجه\n\n"
            "کل: "
            + to_persian_digits(
                format_money(
                    budgets[
                        "total_budget"
                    ]
                )
            )
            + "\nمصرف: "
            + to_persian_digits(
                format_money(
                    budgets[
                        "budgeted_spending"
                    ]
                )
            )
            + "\nردشده: "
            + to_persian_digits(
                budgets[
                    "overspent_count"
                ]
            )
        )

        self.overview_savings.setText(
            "پس‌انداز\n\n"
            "ذخیره‌شده: "
            + to_persian_digits(
                format_money(
                    savings[
                        "total_saved"
                    ]
                )
            )
            + "\nباقی‌مانده: "
            + to_persian_digits(
                format_money(
                    savings[
                        "total_remaining"
                    ]
                )
            )
            + "\nاهداف کامل: "
            + to_persian_digits(
                savings[
                    "completed_goals"
                ]
            )
        )

        warnings = []

        if productivity["overdue_tasks"]:
            warnings.append(
                "کار عقب‌افتاده: "
                + to_persian_digits(
                    productivity[
                        "overdue_tasks"
                    ]
                )
            )

        if budgets["overspent_count"]:
            warnings.append(
                "بودجه ردشده: "
                + to_persian_digits(
                    budgets[
                        "overspent_count"
                    ]
                )
            )

        self.overview_warning.setText(
            (
                "⚠️ "
                + "   |   ".join(
                    warnings
                )
            )
            if warnings
            else (
                "وضعیت کلی خوب است؛ "
                "مورد هشدار فعالی وجود ندارد."
            )
        )

    def refresh_productivity(
        self,
    ):
        snapshot = (
            get_productivity_snapshot(
                self.productivity_anchor
            )
        )

        self.productivity_snapshot = (
            snapshot
        )

        self.productivity_week_label.setText(
            format_jalali_week_range(
                snapshot["start_date"],
                snapshot["end_date"],
            )
        )

        tasks = snapshot["tasks"]
        habits = snapshot["habits"]
        study = snapshot["study"]

        self.task_summary_label.setText(
            "کارها\n"
            f"{to_persian_digits(tasks['completed'])}"
            " از "
            f"{to_persian_digits(tasks['total'])}"
            "\n"
            f"{to_persian_digits(tasks['percentage'])}٪"
            "\nعقب‌افتاده: "
            f"{to_persian_digits(snapshot['overdue_tasks'])}"
        )

        self.habit_summary_label.setText(
            "عادت‌ها\n"
            f"{to_persian_digits(habits['completed'])}"
            " از "
            f"{to_persian_digits(habits['scheduled'])}"
            "\n"
            f"{to_persian_digits(habits['percentage'])}٪"
        )

        actual = format_study_duration(
            study["actual_seconds"]
        )

        self.study_summary_label.setText(
            "مطالعه\n"
            f"{to_persian_digits(actual)}"
            "\nبرنامه: "
            f"{to_persian_digits(study['planned_minutes'])} دقیقه"
            "\nتحقق: "
            f"{to_persian_digits(study['time_percentage'])}٪"
        )

        self.refresh_productivity_chart()
        self.refresh_daily_table()

    def refresh_productivity_chart(
        self,
    ):
        if not hasattr(
            self,
            "productivity_snapshot",
        ):
            return

        mode = (
            self.metric_input
            .currentData()
        )

        if mode == "tasks":
            data = (
                self.productivity_snapshot[
                    "task_daily"
                ]
            )

        elif mode == "habits":
            data = (
                self.productivity_snapshot[
                    "habit_daily"
                ]
            )

        else:
            data = (
                self.productivity_snapshot[
                    "study_daily"
                ]
            )

        self.productivity_chart.set_data(
            data,
            mode,
        )

    def refresh_daily_table(
        self,
    ):
        snapshot = (
            self.productivity_snapshot
        )

        tasks = snapshot[
            "task_daily"
        ]

        habits = snapshot[
            "habit_daily"
        ]

        study = snapshot[
            "study_daily"
        ]

        self.daily_table.setRowCount(
            7
        )

        for index in range(
            7
        ):
            target_date = date.fromisoformat(
                tasks[index]["date"]
            )

            task_text = (
                f"{to_persian_digits(tasks[index]['completed'])}"
                " / "
                f"{to_persian_digits(tasks[index]['total'])}"
            )

            habit_text = (
                f"{to_persian_digits(habits[index]['completed'])}"
                " / "
                f"{to_persian_digits(habits[index]['scheduled'])}"
                "  "
                f"({to_persian_digits(habits[index]['percentage'])}٪)"
            )

            study_actual = (
                format_study_duration(
                    study[index][
                        "actual_seconds"
                    ]
                )
            )

            status_parts = []

            if (
                tasks[index]["total"]
                and tasks[index]["completed"]
                == tasks[index]["total"]
            ):
                status_parts.append(
                    "کارها کامل"
                )

            if (
                habits[index]["scheduled"]
                and habits[index]["percentage"]
                == 100
            ):
                status_parts.append(
                    "عادت‌ها کامل"
                )

            status = (
                "، ".join(
                    status_parts
                )
                if status_parts
                else "—"
            )

            values = [
                format_jalali_short(
                    target_date
                ),
                task_text,
                habit_text,
                (
                    to_persian_digits(
                        study[index][
                            "planned_minutes"
                        ]
                    )
                    + " دقیقه"
                ),
                to_persian_digits(
                    study_actual
                ),
                status,
            ]

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    str(value)
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.daily_table.setItem(
                    index,
                    column,
                    item,
                )

    def refresh_finance(
        self,
    ):
        snapshot = (
            get_finance_snapshot(
                self.finance_anchor
            )
        )

        self.finance_snapshot = (
            snapshot
        )

        self.finance_month_label.setText(
            format_jalali_month_title(
                snapshot["jalali_year"],
                snapshot["jalali_month"],
            )
        )

        finance = snapshot["finance"]
        budgets = snapshot["budgets"]
        savings = snapshot["savings"]

        self.finance_summary_label.setText(
            "ماه مالی\n"
            "درآمد: "
            + to_persian_digits(
                format_money(
                    finance["income"]
                )
            )
            + "\nهزینه: "
            + to_persian_digits(
                format_money(
                    finance["expense"]
                )
            )
            + "\nمانده: "
            + to_persian_digits(
                format_money(
                    finance["balance"]
                )
            )
        )

        self.budget_summary_label.setText(
            "بودجه‌ها\n"
            "کل: "
            + to_persian_digits(
                format_money(
                    budgets["total_budget"]
                )
            )
            + "\nمصرف: "
            + to_persian_digits(
                format_money(
                    budgets[
                        "budgeted_spending"
                    ]
                )
            )
            + "\nبدون بودجه: "
            + to_persian_digits(
                format_money(
                    budgets[
                        "unbudgeted_expense"
                    ]
                )
            )
        )

        self.savings_summary_label.setText(
            "پس‌انداز\n"
            "هدف: "
            + to_persian_digits(
                format_money(
                    savings["total_target"]
                )
            )
            + "\nذخیره‌شده: "
            + to_persian_digits(
                format_money(
                    savings["total_saved"]
                )
            )
            + "\nباقی‌مانده: "
            + to_persian_digits(
                format_money(
                    savings[
                        "total_remaining"
                    ]
                )
            )
        )

        donut_data = [
            {
                "label": row[
                    "category_name"
                ],
                "value": row[
                    "total_amount"
                ],
            }
            for row in (
                snapshot[
                    "category_spending"
                ]
            )
        ]

        self.expense_donut.set_data(
            donut_data
        )

        self.refresh_category_table()

    def refresh_category_table(
        self,
    ):
        rows = (
            self.finance_snapshot[
                "category_spending"
            ]
        )

        total_expense = (
            self.finance_snapshot[
                "finance"
            ]["expense"]
        )

        self.category_table.setRowCount(
            len(rows)
        )

        for row_index, row in enumerate(
            rows
        ):
            share = (
                round(
                    row["total_amount"]
                    / total_expense
                    * 100
                )
                if total_expense
                else 0
            )

            values = [
                row["category_name"],
                (
                    to_persian_digits(
                        format_money(
                            row[
                                "total_amount"
                            ]
                        )
                    )
                    + " تومان"
                ),
                to_persian_digits(
                    row[
                        "transaction_count"
                    ]
                ),
                (
                    to_persian_digits(
                        share
                    )
                    + "٪"
                ),
            ]

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    str(value)
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.category_table.setItem(
                    row_index,
                    column,
                    item,
                )

    def previous_productivity_week(
        self,
    ):
        week = get_persian_week(
            self.productivity_anchor
        )

        self.productivity_anchor = (
            week[0]
            - date.resolution
        )

        self.refresh_productivity()

    def next_productivity_week(
        self,
    ):
        week = get_persian_week(
            self.productivity_anchor
        )

        self.productivity_anchor = (
            week[-1]
            + date.resolution
        )

        self.refresh_productivity()

    def current_productivity_week(
        self,
    ):
        self.productivity_anchor = (
            date.today()
        )

        self.refresh_productivity()

    def previous_finance_month(
        self,
    ):
        jalali = gregorian_to_jalali(
            self.finance_anchor
        )

        year = jalali.year
        month = jalali.month

        if month == 1:
            year -= 1
            month = 12

        else:
            month -= 1

        self.finance_anchor = (
            jalali_to_gregorian(
                year,
                month,
                1,
            )
        )

        self.refresh_finance()

    def next_finance_month(
        self,
    ):
        jalali = gregorian_to_jalali(
            self.finance_anchor
        )

        year = jalali.year
        month = jalali.month

        if month == 12:
            year += 1
            month = 1

        else:
            month += 1

        self.finance_anchor = (
            jalali_to_gregorian(
                year,
                month,
                1,
            )
        )

        self.refresh_finance()

    def current_finance_month(
        self,
    ):
        self.finance_anchor = (
            date.today()
        )

        self.refresh_finance()

    def on_tab_changed(
        self,
        index,
    ):
        widget = self.tabs.widget(
            index
        )

        if widget is self.overview_tab:
            self.refresh_overview()

        elif widget is self.productivity_tab:
            self.refresh_productivity()

        elif widget is self.finance_tab:
            self.refresh_finance()