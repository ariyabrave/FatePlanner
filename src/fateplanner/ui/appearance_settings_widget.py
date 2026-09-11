from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from fateplanner.ui.theme import (
    THEME_DARK,
    THEME_LIGHT,
    THEME_SYSTEM,
    apply_appearance,
    get_theme_preference,
    set_theme_preference,
)


THEME_LABELS = {
    THEME_SYSTEM: "مطابق سیستم",
    THEME_LIGHT: "روشن",
    THEME_DARK: "تیره",
}


class AppearanceSettingsWidget(
    QFrame
):
    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.setObjectName(
            "appearanceSettingsCard"
        )

        self.setStyleSheet(
            """
            QFrame#appearanceSettingsCard {
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 10px;
            }
            """
        )

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "ظاهر برنامه"
        )

        title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        description = QLabel(
            "حالت نمایش FatePlanner را انتخاب کنید. "
            "انتخاب شما به‌صورت خودکار ذخیره می‌شود."
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

        row = QHBoxLayout()

        label = QLabel(
            "پوسته:"
        )

        self.theme_input = (
            QComboBox()
        )

        self.theme_input.addItem(
            THEME_LABELS[
                THEME_SYSTEM
            ],
            THEME_SYSTEM,
        )

        self.theme_input.addItem(
            THEME_LABELS[
                THEME_LIGHT
            ],
            THEME_LIGHT,
        )

        self.theme_input.addItem(
            THEME_LABELS[
                THEME_DARK
            ],
            THEME_DARK,
        )

        row.addWidget(
            label
        )

        row.addWidget(
            self.theme_input,
            1,
        )

        layout.addLayout(
            row
        )

        self.status_label = QLabel()

        self.status_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.status_label
        )

        self.load_current_theme()

        self.theme_input.currentIndexChanged.connect(
            self.on_theme_changed
        )

    def load_current_theme(
        self,
    ):
        preference = (
            get_theme_preference()
        )

        index = (
            self.theme_input.findData(
                preference
            )
        )

        if index >= 0:
            self.theme_input.blockSignals(
                True
            )

            self.theme_input.setCurrentIndex(
                index
            )

            self.theme_input.blockSignals(
                False
            )

        self.update_status()

    def update_status(
        self,
    ):
        app = (
            QApplication.instance()
        )

        if app is None:
            return

        preference = (
            get_theme_preference()
        )

        resolved = (
            app.property(
                "fateplannerTheme"
            )
            or preference
        )

        preference_label = (
            THEME_LABELS.get(
                preference,
                preference,
            )
        )

        resolved_label = (
            THEME_LABELS.get(
                resolved,
                resolved,
            )
        )

        if preference == THEME_SYSTEM:
            self.status_label.setText(
                "انتخاب فعلی: "
                f"{preference_label}"
                " — "
                "حالت فعال: "
                f"{resolved_label}"
            )

        else:
            self.status_label.setText(
                "حالت فعال: "
                f"{resolved_label}"
            )

    def on_theme_changed(
        self,
        index: int,
    ):
        theme = (
            self.theme_input
            .itemData(
                index
            )
        )

        if theme is None:
            return

        set_theme_preference(
            theme
        )

        app = (
            QApplication.instance()
        )

        if app is None:
            return

        apply_appearance(
            app,
            theme,
        )

        self.update_status()