import math

from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import QWidget

from fateplanner.ui.theme import theme_color
from fateplanner.utils.date_utils import (
    format_jalali_short,
    to_persian_digits,
)


class GaugeWidget(QWidget):
    def __init__(
        self,
        title="",
        parent=None,
    ):
        super().__init__(parent)

        self.title = title
        self.value = 0
        self.detail = ""

        self.setMinimumSize(
            180,
            150,
        )

    def set_data(
        self,
        value: int,
        detail: str = "",
    ):
        self.value = max(
            0,
            int(value),
        )

        self.detail = detail

        self.update()

    def paintEvent(
        self,
        event,
    ):
        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        arc_rect = QRectF(
            25,
            35,
            width - 50,
            max(
                80,
                height - 65,
            ),
        )

        pen = QPen(
            theme_color("grid")
        )

        pen.setWidth(13)

        pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )

        painter.setPen(pen)

        painter.drawArc(
            arc_rect,
            180 * 16,
            -180 * 16,
        )

        ratio = min(
            1.0,
            self.value / 100,
        )

        progress_pen = QPen(
            theme_color("accent")
        )

        progress_pen.setWidth(13)

        progress_pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )

        painter.setPen(
            progress_pen
        )

        painter.drawArc(
            arc_rect,
            180 * 16,
            int(
                -180
                * ratio
                * 16
            ),
        )

        title_font = QFont(
            painter.font()
        )

        title_font.setBold(True)
        title_font.setPointSize(10)

        painter.setFont(
            title_font
        )

        painter.setPen(
            theme_color("text")
        )

        painter.drawText(
            QRectF(
                0,
                5,
                width,
                25,
            ),
            Qt.AlignmentFlag.AlignCenter,
            self.title,
        )

        value_font = QFont(
            painter.font()
        )

        value_font.setBold(True)
        value_font.setPointSize(20)

        painter.setFont(
            value_font
        )

        painter.setPen(
            theme_color("text")
        )

        painter.drawText(
            QRectF(
                0,
                height / 2 - 5,
                width,
                40,
            ),
            Qt.AlignmentFlag.AlignCenter,
            (
                to_persian_digits(
                    self.value
                )
                + "٪"
            ),
        )

        if self.detail:
            detail_font = QFont(
                painter.font()
            )

            detail_font.setBold(False)
            detail_font.setPointSize(8)

            painter.setFont(
                detail_font
            )

            painter.setPen(
                theme_color("muted")
            )

            painter.drawText(
                QRectF(
                    8,
                    height - 28,
                    width - 16,
                    22,
                ),
                Qt.AlignmentFlag.AlignCenter,
                self.detail,
            )


class RadarChartWidget(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.metrics = []

        self.setMinimumHeight(
            330
        )

    def set_metrics(
        self,
        metrics: list[tuple[str, int]],
    ):
        self.metrics = [
            (
                label,
                max(
                    0,
                    min(
                        100,
                        int(value),
                    ),
                ),
            )
            for label, value
            in metrics
        ]

        self.update()

    def paintEvent(
        self,
        event,
    ):
        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        if len(self.metrics) < 3:
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "داده کافی برای نمودار وجود ندارد.",
            )

            return

        width = self.width()
        height = self.height()

        center = QPointF(
            width / 2,
            height / 2 + 10,
        )

        radius = min(
            width,
            height,
        ) * 0.31

        count = len(
            self.metrics
        )

        def point_for(
            index,
            ratio,
        ):
            angle = (
                -math.pi / 2
                + 2
                * math.pi
                * index
                / count
            )

            return QPointF(
                center.x()
                + math.cos(angle)
                * radius
                * ratio,
                center.y()
                + math.sin(angle)
                * radius
                * ratio,
            )

        grid_pen = QPen(
            theme_color("grid")
        )

        grid_pen.setWidth(1)

        painter.setPen(
            grid_pen
        )

        for level in range(
            1,
            6,
        ):
            ratio = level / 5

            polygon = QPolygonF(
                [
                    point_for(
                        index,
                        ratio,
                    )
                    for index
                    in range(count)
                ]
            )

            painter.drawPolygon(
                polygon
            )

        for index in range(count):
            painter.drawLine(
                center,
                point_for(
                    index,
                    1,
                ),
            )

        value_polygon = QPolygonF(
            [
                point_for(
                    index,
                    value / 100,
                )
                for index, (
                    _,
                    value,
                )
                in enumerate(
                    self.metrics
                )
            ]
        )

        fill = theme_color("accent")

        fill.setAlpha(80)

        painter.setBrush(
            fill
        )

        value_pen = QPen(
            theme_color("accent")
        )

        value_pen.setWidth(2)

        painter.setPen(
            value_pen
        )

        painter.drawPolygon(
            value_polygon
        )

        painter.setBrush(
            theme_color("accent")
        )

        for point in value_polygon:
            painter.drawEllipse(
                point,
                4,
                4,
            )

        label_font = QFont(
            painter.font()
        )

        label_font.setPointSize(9)
        label_font.setBold(True)

        painter.setFont(
            label_font
        )

        painter.setPen(
            theme_color("text")
        )

        for index, (
            label,
            value,
        ) in enumerate(
            self.metrics
        ):
            point = point_for(
                index,
                1.22,
            )

            painter.drawText(
                QRectF(
                    point.x() - 55,
                    point.y() - 18,
                    110,
                    36,
                ),
                Qt.AlignmentFlag.AlignCenter,
                (
                    f"{label}\n"
                    f"{to_persian_digits(value)}٪"
                ),
            )


class DonutChartWidget(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.data = []

        self.setMinimumSize(
            360,
            300,
        )

    def set_data(
        self,
        rows: list[dict],
    ):
        normalized = [
            {
                "label": row["label"],
                "value": max(
                    0,
                    int(
                        row["value"]
                    ),
                ),
            }
            for row in rows
            if int(
                row["value"]
            ) > 0
        ]

        normalized.sort(
            key=lambda row:
                row["value"],
            reverse=True,
        )

        if len(normalized) > 6:
            top = normalized[:5]

            other_value = sum(
                row["value"]
                for row
                in normalized[5:]
            )

            top.append(
                {
                    "label": "سایر",
                    "value": (
                        other_value
                    ),
                }
            )

            normalized = top

        self.data = normalized

        self.update()

    def paintEvent(
        self,
        event,
    ):
        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        total = sum(
            row["value"]
            for row
            in self.data
        )

        if total <= 0:
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "هنوز هزینه‌ای برای نمایش وجود ندارد.",
            )

            return

        colors = [
            theme_color("accent"),
            theme_color("success"),
            theme_color("warning"),
            theme_color("purple"),
            theme_color("danger"),
            theme_color("teal"),
        ]

        size = min(
            self.height() - 50,
            self.width() * 0.54,
        )

        pie_rect = QRectF(
            20,
            (
                self.height()
                - size
            )
            / 2,
            size,
            size,
        )

        start_angle = 90 * 16

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        for index, row in enumerate(
            self.data
        ):
            ratio = (
                row["value"]
                / total
            )

            span = int(
                -360
                * ratio
                * 16
            )

            painter.setBrush(
                colors[
                    index
                    % len(colors)
                ]
            )

            painter.drawPie(
                pie_rect,
                start_angle,
                span,
            )

            start_angle += span

        hole_size = (
            size * 0.50
        )

        hole_rect = QRectF(
            pie_rect.center().x()
            - hole_size / 2,
            pie_rect.center().y()
            - hole_size / 2,
            hole_size,
            hole_size,
        )

        painter.setBrush(
            self.palette().window()
        )

        painter.drawEllipse(
            hole_rect
        )

        painter.setPen(
            theme_color("text")
        )

        total_font = QFont(
            painter.font()
        )

        total_font.setBold(True)
        total_font.setPointSize(11)

        painter.setFont(
            total_font
        )

        painter.drawText(
            hole_rect,
            Qt.AlignmentFlag.AlignCenter,
            (
                "کل هزینه\n"
                + to_persian_digits(
                    f"{total:,}"
                )
            ),
        )

        legend_x = (
            pie_rect.right()
            + 28
        )

        legend_y = 35

        legend_font = QFont(
            painter.font()
        )

        legend_font.setBold(False)
        legend_font.setPointSize(9)

        painter.setFont(
            legend_font
        )

        for index, row in enumerate(
            self.data
        ):
            color = colors[
                index
                % len(colors)
            ]

            painter.fillRect(
                QRectF(
                    legend_x,
                    legend_y,
                    12,
                    12,
                ),
                color,
            )

            percentage = round(
                row["value"]
                / total
                * 100
            )

            painter.setPen(
                theme_color("text")
            )

            painter.drawText(
                QRectF(
                    legend_x + 20,
                    legend_y - 6,
                    max(
                        100,
                        self.width()
                        - legend_x
                        - 25,
                    ),
                    26,
                ),
                (
                    Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignVCenter
                ),
                (
                    f"{row['label']} "
                    f"({to_persian_digits(percentage)}٪)"
                ),
            )

            legend_y += 35


class ProductivityChartWidget(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self.mode = "tasks"
        self.data = []

        self.setMinimumHeight(
            320
        )

    def set_data(
        self,
        data: list[dict],
        mode: str,
    ):
        self.data = data
        self.mode = mode

        self.update()

    def _row_date(
        self,
        row,
    ):
        key = (
            "date"
            if "date" in row
            else "session_date"
        )

        from datetime import date

        return date.fromisoformat(
            row[key]
        )

    def paintEvent(
        self,
        event,
    ):
        super().paintEvent(event)

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        if not self.data:
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "داده‌ای برای نمایش وجود ندارد.",
            )

            return

        width = self.width()
        height = self.height()

        left = 60
        right = 20
        top = 35
        bottom = 60

        chart_width = max(
            1,
            width - left - right,
        )

        chart_height = max(
            1,
            height - top - bottom,
        )

        titles = {
            "tasks": (
                "کارهای انجام‌شده و باقی‌مانده"
            ),
            "habits": (
                "روند انجام عادت‌ها"
            ),
            "study": (
                "مطالعه برنامه‌ریزی‌شده و واقعی"
            ),
        }

        title_font = QFont(
            painter.font()
        )

        title_font.setBold(True)
        title_font.setPointSize(11)

        painter.setFont(
            title_font
        )

        painter.setPen(
            theme_color("text")
        )

        painter.drawText(
            QRectF(
                left,
                0,
                chart_width,
                28,
            ),
            Qt.AlignmentFlag.AlignCenter,
            titles[
                self.mode
            ],
        )

        if self.mode == "tasks":
            values = [
                row["total"]
                for row
                in self.data
            ]

            maximum = max(
                values
                + [1]
            )

        elif self.mode == "habits":
            maximum = 100

        else:
            maximum = max(
                [
                    row[
                        "planned_minutes"
                    ]
                    for row
                    in self.data
                ]
                + [
                    row[
                        "actual_seconds"
                    ]
                    / 60
                    for row
                    in self.data
                ]
                + [1]
            )

        painter.setPen(
            QPen(
                theme_color("grid"),
                1,
            )
        )

        for step in range(
            5
        ):
            ratio = step / 4

            y = (
                top
                + chart_height
                - chart_height
                * ratio
            )

            painter.drawLine(
                left,
                int(y),
                left + chart_width,
                int(y),
            )

            painter.setPen(
                theme_color("muted")
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
                    round(
                        maximum
                        * ratio
                    )
                ),
            )

            painter.setPen(
                QPen(
                    theme_color("grid"),
                    1,
                )
            )

        group_width = (
            chart_width
            / len(
                self.data
            )
        )

        if self.mode == "habits":
            points = []

            for index, row in enumerate(
                self.data
            ):
                x = (
                    left
                    + group_width
                    * (
                        index
                        + 0.5
                    )
                )

                y = (
                    top
                    + chart_height
                    - (
                        row[
                            "percentage"
                        ]
                        / 100
                        * chart_height
                    )
                )

                points.append(
                    QPointF(
                        x,
                        y,
                    )
                )

            area = QPainterPath()

            area.moveTo(
                points[0].x(),
                top + chart_height,
            )

            for point in points:
                area.lineTo(
                    point
                )

            area.lineTo(
                points[-1].x(),
                top + chart_height,
            )

            area.closeSubpath()

            area_fill = theme_color("success")

            area_fill.setAlpha(
                70
            )

            painter.fillPath(
                area,
                area_fill,
            )

            line_path = QPainterPath()

            line_path.moveTo(
                points[0]
            )

            for point in points[1:]:
                line_path.lineTo(
                    point
                )

            painter.setPen(
                QPen(
                    theme_color("success"),
                    3,
                )
            )

            painter.drawPath(
                line_path
            )

            painter.setBrush(
                theme_color("success")
            )

            for point in points:
                painter.drawEllipse(
                    point,
                    4,
                    4,
                )

        elif self.mode == "tasks":
            bar_width = min(
                38,
                group_width * 0.46,
            )

            for index, row in enumerate(
                self.data
            ):
                x = (
                    left
                    + group_width
                    * (
                        index
                        + 0.5
                    )
                    - bar_width / 2
                )

                completed = (
                    row["completed"]
                )

                remaining = max(
                    0,
                    row["total"]
                    - completed,
                )

                completed_height = (
                    completed
                    / maximum
                    * chart_height
                )

                remaining_height = (
                    remaining
                    / maximum
                    * chart_height
                )

                bottom = (
                    top
                    + chart_height
                )

                painter.fillRect(
                    QRectF(
                        x,
                        bottom
                        - completed_height,
                        bar_width,
                        completed_height,
                    ),
                    theme_color("success"),
                )

                painter.fillRect(
                    QRectF(
                        x,
                        bottom
                        - completed_height
                        - remaining_height,
                        bar_width,
                        remaining_height,
                    ),
                    theme_color("grid"),
                )

        else:
            bar_width = min(
                25,
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

                planned = (
                    row[
                        "planned_minutes"
                    ]
                )

                actual = (
                    row[
                        "actual_seconds"
                    ]
                    / 60
                )

                planned_height = (
                    planned
                    / maximum
                    * chart_height
                )

                actual_height = (
                    actual
                    / maximum
                    * chart_height
                )

                bottom = (
                    top
                    + chart_height
                )

                painter.fillRect(
                    QRectF(
                        center_x
                        - bar_width
                        - 2,
                        bottom
                        - planned_height,
                        bar_width,
                        planned_height,
                    ),
                    theme_color("accent"),
                )

                painter.fillRect(
                    QRectF(
                        center_x
                        + 2,
                        bottom
                        - actual_height,
                        bar_width,
                        actual_height,
                    ),
                    theme_color("success"),
                )

        label_font = QFont(
            painter.font()
        )

        label_font.setPointSize(8)

        painter.setFont(
            label_font
        )

        painter.setPen(
            theme_color("text")
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

            painter.drawText(
                QRectF(
                    center_x
                    - group_width / 2,
                    top
                    + chart_height
                    + 8,
                    group_width,
                    38,
                ),
                (
                    Qt.AlignmentFlag.AlignCenter
                    | Qt.AlignmentFlag.AlignTop
                ),
                format_jalali_short(
                    self._row_date(
                        row
                    )
                ),
            )