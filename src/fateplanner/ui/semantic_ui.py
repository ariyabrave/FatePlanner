from PySide6.QtCore import (
    QEvent,
    QObject,
)
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
)


VALID_BUTTON_ROLES = {
    "primary",
    "secondary",
    "success",
    "warning",
    "danger",
}


DANGER_KEYWORDS = (
    "حذف",
    "پاک",
)

SUCCESS_KEYWORDS = (
    "واریز",
    "تکمیل",
)

WARNING_KEYWORDS = (
    "برداشت",
    "بازیابی",
    "بازنشانی",
)

PRIMARY_KEYWORDS = (
    "افزودن",
    "اضافه",
    "ذخیره",
    "ثبت",
    "ساخت",
    "شروع",
)


def normalize_button_text(
    text: str,
) -> str:
    return " ".join(
        text.replace(
            "&",
            "",
        ).split()
    )


def classify_button_text(
    text: str,
) -> str:
    text = normalize_button_text(
        text
    )

    if not text:
        return "secondary"

    if text in {
        "×",
        "✕",
        "✖",
    }:
        return "danger"

    for keyword in DANGER_KEYWORDS:
        if keyword in text:
            return "danger"

    for keyword in SUCCESS_KEYWORDS:
        if keyword in text:
            return "success"

    for keyword in WARNING_KEYWORDS:
        if keyword in text:
            return "warning"

    for keyword in PRIMARY_KEYWORDS:
        if keyword in text:
            return "primary"

    return "secondary"


def set_button_role(
    button: QPushButton,
    role: str,
) -> None:
    if role not in VALID_BUTTON_ROLES:
        role = "secondary"

    button.setProperty(
        "semanticRole",
        role,
    )

    style = button.style()

    style.unpolish(
        button
    )

    style.polish(
        button
    )

    button.update()


class SemanticUiPolisher(
    QObject
):
    def eventFilter(
        self,
        watched,
        event,
    ):
        if (
            isinstance(
                watched,
                QPushButton,
            )
            and event.type()
            == QEvent.Type.Show
        ):
            existing_role = (
                watched.property(
                    "semanticRole"
                )
            )

            if not existing_role:
                role = (
                    classify_button_text(
                        watched.text()
                    )
                )

                set_button_role(
                    watched,
                    role,
                )

        return super().eventFilter(
            watched,
            event,
        )


def install_semantic_ui(
    app: QApplication,
) -> SemanticUiPolisher:
    polisher = (
        SemanticUiPolisher(
            app
        )
    )

    app.installEventFilter(
        polisher
    )

    return polisher