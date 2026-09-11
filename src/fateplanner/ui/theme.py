from PySide6.QtCore import (
    QSettings,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
)
from PySide6.QtWidgets import (
    QApplication,
)


THEME_SYSTEM = "system"
THEME_LIGHT = "light"
THEME_DARK = "dark"

VALID_THEMES = {
    THEME_SYSTEM,
    THEME_LIGHT,
    THEME_DARK,
}


def normalize_theme(
    value: str | None,
) -> str:
    if value in VALID_THEMES:
        return value

    return THEME_SYSTEM


def get_theme_preference() -> str:
    settings = QSettings()

    value = settings.value(
        "appearance/theme",
        THEME_SYSTEM,
        type=str,
    )

    return normalize_theme(
        value
    )


def set_theme_preference(
    theme: str,
) -> None:
    theme = normalize_theme(
        theme
    )

    settings = QSettings()

    settings.setValue(
        "appearance/theme",
        theme,
    )

    settings.sync()


def detect_system_theme(
    app: QApplication,
) -> str:
    try:
        scheme = (
            app.styleHints()
            .colorScheme()
        )

        if (
            scheme
            == Qt.ColorScheme.Dark
        ):
            return THEME_DARK

        if (
            scheme
            == Qt.ColorScheme.Light
        ):
            return THEME_LIGHT

    except Exception:
        pass

    palette = app.palette()

    window_color = palette.window().color()

    if window_color.lightness() < 128:
        return THEME_DARK

    return THEME_LIGHT


def resolve_theme(
    app: QApplication,
    preference: str | None = None,
) -> str:
    preference = normalize_theme(
        preference
        or get_theme_preference()
    )

    if preference == THEME_SYSTEM:
        return detect_system_theme(
            app
        )

    return preference


def get_best_font_family() -> str:
    available = set(
        QFontDatabase.families()
    )

    preferred = [
        "Vazirmatn",
        "Vazir",
        "IRANSans",
        "Segoe UI",
        "Tahoma",
        "Arial",
    ]

    for family in preferred:
        if family in available:
            return family

    return (
        QApplication
        .font()
        .family()
    )


def apply_ui_font(
    app: QApplication,
) -> None:
    font = QFont(
        get_best_font_family()
    )

    font.setPointSize(
        10
    )

    app.setFont(
        font
    )


def build_stylesheet(
    theme: str,
) -> str:
    theme = normalize_theme(
        theme
    )

    if theme == THEME_DARK:
        colors = {
            "window": "#181a1f",
            "surface": "#202329",
            "surface_alt": "#292d35",
            "surface_hover": "#323741",
            "border": "#3b404b",
            "border_soft": "#30343c",
            "text": "#f1f3f5",
            "text_secondary": "#aeb4bf",
            "accent": "#7398ff",
            "accent_hover": "#88a8ff",
            "accent_pressed": "#5f82df",
            "accent_text": "#ffffff",
            "success": "#68b97a",
            "warning": "#d9a74c",
            "danger": "#d66b72",
            "input": "#252930",
            "selection": "#405a9b",
            "progress_background": "#30343c",
            "disabled": "#737985",
        }

    else:
        colors = {
            "window": "#f5f6f8",
            "surface": "#ffffff",
            "surface_alt": "#f0f2f5",
            "surface_hover": "#e8ecf2",
            "border": "#d9dde5",
            "border_soft": "#e7e9ee",
            "text": "#252830",
            "text_secondary": "#6d7480",
            "accent": "#5478d4",
            "accent_hover": "#6788dc",
            "accent_pressed": "#4668bc",
            "accent_text": "#ffffff",
            "success": "#4e9d64",
            "warning": "#bf8736",
            "danger": "#c6535c",
            "input": "#ffffff",
            "selection": "#cbd8ff",
            "progress_background": "#e5e8ee",
            "disabled": "#9da3ad",
        }

    return f"""
    QWidget {{
        background-color: {colors["window"]};
        color: {colors["text"]};
        selection-background-color: {colors["selection"]};
    }}

    QMainWindow {{
        background-color: {colors["window"]};
    }}

    QLabel {{
        background-color: transparent;
        color: {colors["text"]};
    }}

    QFrame {{
        background-color: transparent;
    }}

    QScrollArea {{
        background-color: transparent;
        border: none;
    }}

    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}


    /* ================================
       Sidebar
       ================================ */

    QListWidget {{
        background-color: {colors["surface"]};
        border: none;
        border-left: 1px solid {colors["border"]};
        padding: 10px 7px;
        outline: none;
    }}

    QListWidget::item {{
        color: {colors["text_secondary"]};
        padding: 12px 14px;
        margin: 3px 2px;
        border-radius: 8px;
    }}

    QListWidget::item:hover {{
        background-color: {colors["surface_hover"]};
        color: {colors["text"]};
    }}

    QListWidget::item:selected {{
        background-color: {colors["accent"]};
        color: {colors["accent_text"]};
    }}


    /* ================================
       Buttons
       ================================ */

    QPushButton {{
        background-color: {colors["surface"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 8px;
        padding: 7px 12px;
        min-height: 22px;
    }}

    QPushButton:hover {{
        background-color: {colors["surface_hover"]};
        border-color: {colors["accent"]};
    }}

    QPushButton:pressed {{
        background-color: {colors["surface_alt"]};
    }}

    QPushButton:default {{
        background-color: {colors["accent"]};
        color: {colors["accent_text"]};
        border-color: {colors["accent"]};
        font-weight: 600;
    }}

    QPushButton:default:hover {{
        background-color: {colors["accent_hover"]};
    }}

    QPushButton:default:pressed {{
        background-color: {colors["accent_pressed"]};
    }}

    QPushButton:disabled {{
        color: {colors["disabled"]};
        background-color: {colors["surface_alt"]};
        border-color: {colors["border_soft"]};
    }}


    /* ================================
       Semantic actions
       ================================ */

    QPushButton[semanticRole="primary"] {{
        background-color: {colors["accent"]};
        color: {colors["accent_text"]};
        border-color: {colors["accent"]};
        font-weight: 600;
    }}

    QPushButton[semanticRole="primary"]:hover {{
        background-color: {colors["accent_hover"]};
        border-color: {colors["accent_hover"]};
    }}

    QPushButton[semanticRole="primary"]:pressed {{
        background-color: {colors["accent_pressed"]};
        border-color: {colors["accent_pressed"]};
    }}


    QPushButton[semanticRole="success"] {{
        background-color: {colors["success"]};
        color: #ffffff;
        border-color: {colors["success"]};
        font-weight: 600;
    }}


    QPushButton[semanticRole="warning"] {{
        background-color: {colors["warning"]};
        color: #ffffff;
        border-color: {colors["warning"]};
        font-weight: 600;
    }}


    QPushButton[semanticRole="danger"] {{
        background-color: transparent;
        color: {colors["danger"]};
        border-color: {colors["danger"]};
        font-weight: 600;
    }}

    QPushButton[semanticRole="danger"]:hover {{
        background-color: {colors["danger"]};
        color: #ffffff;
    }}

    QPushButton[semanticRole="danger"]:pressed {{
        background-color: {colors["danger"]};
        color: #ffffff;
    }}


    QPushButton[semanticRole="secondary"] {{
        color: {colors["text"]};
    }}


    QDialogButtonBox QPushButton {{
        min-width: 90px;
        padding-left: 16px;
        padding-right: 16px;
    }}



    /* ================================
       Inputs
       ================================ */

    QLineEdit,
    QTextEdit,
    QPlainTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QDateEdit,
    QTimeEdit,
    QDateTimeEdit,
    QComboBox {{
        background-color: {colors["input"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 7px;
        padding: 7px 9px;
    }}

    QLineEdit:focus,
    QTextEdit:focus,
    QPlainTextEdit:focus,
    QSpinBox:focus,
    QDoubleSpinBox:focus,
    QDateEdit:focus,
    QTimeEdit:focus,
    QDateTimeEdit:focus,
    QComboBox:focus {{
        border: 1px solid {colors["accent"]};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 26px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {colors["surface"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        selection-background-color: {colors["accent"]};
        selection-color: {colors["accent_text"]};
    }}


    /* ================================
       Checkboxes
       ================================ */

    QCheckBox {{
        spacing: 8px;
        background-color: transparent;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {colors["border"]};
        border-radius: 5px;
        background-color: {colors["surface"]};
    }}

    QCheckBox::indicator:hover {{
        border-color: {colors["accent"]};
    }}

    QCheckBox::indicator:checked {{
        background-color: {colors["accent"]};
        border-color: {colors["accent"]};
    }}


    /* ================================
       Tabs
       ================================ */

    QTabWidget::pane {{
        background-color: {colors["surface"]};
        border: 1px solid {colors["border"]};
        border-radius: 10px;
        top: -1px;
    }}

    QTabBar::tab {{
        background-color: {colors["surface_alt"]};
        color: {colors["text_secondary"]};
        border: 1px solid {colors["border"]};
        padding: 9px 16px;
        margin-left: 3px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
    }}

    QTabBar::tab:hover {{
        background-color: {colors["surface_hover"]};
        color: {colors["text"]};
    }}

    QTabBar::tab:selected {{
        background-color: {colors["surface"]};
        color: {colors["accent"]};
        border-bottom-color: {colors["surface"]};
        font-weight: 600;
    }}


    /* ================================
       Tables
       ================================ */

    QTableWidget,
    QTableView {{
        background-color: {colors["surface"]};
        alternate-background-color: {colors["surface_alt"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 8px;
        gridline-color: {colors["border_soft"]};
        selection-background-color: {colors["selection"]};
    }}

    QTableWidget::item,
    QTableView::item {{
        padding: 7px;
    }}

    QHeaderView::section {{
        background-color: {colors["surface_alt"]};
        color: {colors["text"]};
        border: none;
        border-bottom: 1px solid {colors["border"]};
        padding: 8px;
        font-weight: 600;
    }}


    /* ================================
       Progress
       ================================ */

    QProgressBar {{
        background-color: {colors["progress_background"]};
        color: {colors["text"]};
        border: none;
        border-radius: 7px;
        min-height: 14px;
        text-align: center;
    }}

    QProgressBar::chunk {{
        background-color: {colors["accent"]};
        border-radius: 7px;
    }}


    /* Additional polish */

    QGroupBox {{
        background-color: {colors["surface"]};
        border: 1px solid {colors["border"]};
        border-radius: 9px;
        margin-top: 12px;
        padding: 12px;
        font-weight: 600;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top right;
        padding: 0 8px;
        color: {colors["text"]};
    }}


    QRadioButton {{
        background-color: transparent;
        spacing: 8px;
    }}

    QRadioButton::indicator {{
        width: 17px;
        height: 17px;
    }}


    QLineEdit:disabled,
    QTextEdit:disabled,
    QPlainTextEdit:disabled,
    QComboBox:disabled {{
        background-color: {colors["surface_alt"]};
        color: {colors["disabled"]};
    }}


    QSplitter::handle {{
        background-color: {colors["border_soft"]};
    }}

    QSplitter::handle:hover {{
        background-color: {colors["accent"]};
    }}


    QTableWidget::item:hover,
    QTableView::item:hover {{
        background-color: {colors["surface_hover"]};
    }}



    /* ================================
       Menus / tooltips
       ================================ */

    QMenu {{
        background-color: {colors["surface"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        padding: 5px;
    }}

    QMenu::item {{
        padding: 7px 20px;
        border-radius: 5px;
    }}

    QMenu::item:selected {{
        background-color: {colors["accent"]};
        color: {colors["accent_text"]};
    }}

    QToolTip {{
        background-color: {colors["surface_alt"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        padding: 5px;
    }}


    /* ================================
       Dialogs
       ================================ */

    QDialog {{
        background-color: {colors["window"]};
    }}

    QMessageBox {{
        background-color: {colors["window"]};
    }}


    /* ================================
       Scrollbars
       ================================ */

    QScrollBar:vertical {{
        background: transparent;
        width: 11px;
        margin: 2px;
    }}

    QScrollBar::handle:vertical {{
        background: {colors["border"]};
        min-height: 30px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {colors["text_secondary"]};
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 11px;
        margin: 2px;
    }}

    QScrollBar::handle:horizontal {{
        background: {colors["border"]};
        min-width: 30px;
        border-radius: 5px;
    }}

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    """



def _active_theme_name() -> str:
    app = QApplication.instance()

    if app is None:
        return THEME_LIGHT

    theme = app.property(
        "fateplannerTheme"
    )

    if theme == THEME_DARK:
        return THEME_DARK

    return THEME_LIGHT


def theme_hex(
    role: str,
) -> str:
    palettes = {
        THEME_DARK: {
            "text": "#f1f3f5",
            "muted": "#aeb4bf",
            "grid": "#3b404b",
            "border": "#3b404b",
            "accent": "#7398ff",
            "success": "#68b97a",
            "warning": "#d9a74c",
            "danger": "#d66b72",
            "purple": "#c087d6",
            "teal": "#66bebb",
            "surface": "#202329",
            "surface_alt": "#292d35",
            "success_bg": "#20382a",
            "danger_bg": "#3a2427",
            "warning_bg": "#3b3120",
        },

        THEME_LIGHT: {
            "text": "#252830",
            "muted": "#6d7480",
            "grid": "#d9dde5",
            "border": "#d9dde5",
            "accent": "#5478d4",
            "success": "#4e9d64",
            "warning": "#bf8736",
            "danger": "#c6535c",
            "purple": "#9a5bab",
            "teal": "#3e9996",
            "surface": "#ffffff",
            "surface_alt": "#f0f2f5",
            "success_bg": "#e3f4e7",
            "danger_bg": "#f7e4e5",
            "warning_bg": "#f7eddc",
        },
    }

    theme = _active_theme_name()

    palette = palettes[
        theme
    ]

    return palette.get(
        role,
        palette["text"],
    )


def theme_color(
    role: str,
) -> QColor:
    return QColor(
        theme_hex(
            role
        )
    )


def apply_appearance(
    app: QApplication,
    preference: str | None = None,
) -> str:
    apply_ui_font(
        app
    )

    resolved = resolve_theme(
        app,
        preference,
    )

    app.setStyleSheet(
        build_stylesheet(
            resolved
        )
    )

    app.setProperty(
        "fateplannerTheme",
        resolved,
    )

    return resolved