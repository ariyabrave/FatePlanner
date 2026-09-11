

def test_stylesheets_build_without_runtime_errors():
    from fateplanner.ui.theme import (
        THEME_DARK,
        THEME_LIGHT,
        build_stylesheet,
    )

    light = build_stylesheet(
        THEME_LIGHT
    )

    dark = build_stylesheet(
        THEME_DARK
    )

    assert "QPushButton" in light
    assert "QPushButton" in dark

    assert "QAbstractItemView" in light
    assert "QAbstractItemView" in dark
