from datetime import date

from PySide6.QtCore import (
    QDate,
    Qt,
)
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QWidget,
)

from fateplanner.utils.date_utils import (
    PERSIAN_MONTH_NAMES,
    get_jalali_month_length,
    gregorian_to_jalali,
    jalali_to_gregorian,
    to_persian_digits,
)


class JalaliDateInput(QWidget):
    def __init__(
        self,
        parent=None,
        default_date: QDate | date | None = None,
    ):
        super().__init__(parent)

        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.day_input = QComboBox()
        self.month_input = QComboBox()
        self.year_input = QComboBox()

        today_jalali = gregorian_to_jalali(
            date.today()
        )

        start_year = (
            today_jalali.year - 10
        )

        end_year = (
            today_jalali.year + 20
        )

        for year in range(
            start_year,
            end_year + 1,
        ):
            self.year_input.addItem(
                to_persian_digits(year),
                year,
            )

        for month in range(
            1,
            13,
        ):
            self.month_input.addItem(
                PERSIAN_MONTH_NAMES[
                    month
                ],
                month,
            )

        layout.addWidget(
            self.day_input
        )

        layout.addWidget(
            self.month_input
        )

        layout.addWidget(
            self.year_input
        )

        self.year_input.currentIndexChanged.connect(
            self.update_days
        )

        self.month_input.currentIndexChanged.connect(
            self.update_days
        )

        if default_date is None:
            gregorian_date = date.today()

        elif isinstance(
            default_date,
            QDate,
        ):
            gregorian_date = date(
                default_date.year(),
                default_date.month(),
                default_date.day(),
            )

        else:
            gregorian_date = default_date

        self.set_gregorian_date(
            gregorian_date
        )

    def set_combo_value(
        self,
        combo: QComboBox,
        value: int,
    ):
        index = combo.findData(
            value
        )

        if index >= 0:
            combo.setCurrentIndex(
                index
            )

    def set_gregorian_date(
        self,
        gregorian_date: date,
    ):
        jalali_date = (
            gregorian_to_jalali(
                gregorian_date
            )
        )

        self.set_combo_value(
            self.year_input,
            jalali_date.year,
        )

        self.set_combo_value(
            self.month_input,
            jalali_date.month,
        )

        self.update_days()

        self.set_combo_value(
            self.day_input,
            jalali_date.day,
        )

    def update_days(
        self,
    ):
        year = self.year_input.currentData()
        month = self.month_input.currentData()

        if year is None or month is None:
            return

        current_day = (
            self.day_input.currentData()
        )

        month_length = (
            get_jalali_month_length(
                year,
                month,
            )
        )

        self.day_input.blockSignals(
            True
        )

        self.day_input.clear()

        for day in range(
            1,
            month_length + 1,
        ):
            self.day_input.addItem(
                to_persian_digits(day),
                day,
            )

        if current_day is not None:
            day_to_restore = min(
                current_day,
                month_length,
            )

            self.set_combo_value(
                self.day_input,
                day_to_restore,
            )

        self.day_input.blockSignals(
            False
        )

    def get_jalali_date(
        self,
    ) -> tuple[int, int, int]:
        return (
            int(
                self.year_input.currentData()
            ),
            int(
                self.month_input.currentData()
            ),
            int(
                self.day_input.currentData()
            ),
        )

    def get_gregorian_date(
        self,
    ) -> date:
        year, month, day = (
            self.get_jalali_date()
        )

        return jalali_to_gregorian(
            year,
            month,
            day,
        )

    def to_iso_date(
        self,
    ) -> str:
        return (
            self.get_gregorian_date()
            .isoformat()
        )