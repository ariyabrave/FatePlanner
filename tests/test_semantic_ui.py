from fateplanner.ui.semantic_ui import (
    classify_button_text,
    normalize_button_text,
)


def test_normalize_button_text():
    assert (
        normalize_button_text(
            "  ＋   افزودن   کار  "
        )
        == "＋ افزودن کار"
    )


def test_delete_is_danger():
    assert (
        classify_button_text(
            "حذف"
        )
        == "danger"
    )

    assert (
        classify_button_text(
            "×"
        )
        == "danger"
    )


def test_deposit_is_success():
    assert (
        classify_button_text(
            "＋ واریز"
        )
        == "success"
    )


def test_complete_is_success():
    assert (
        classify_button_text(
            "تکمیل جلسه"
        )
        == "success"
    )


def test_withdraw_is_warning():
    assert (
        classify_button_text(
            "− برداشت"
        )
        == "warning"
    )


def test_restore_is_warning():
    assert (
        classify_button_text(
            "بازیابی نسخه پشتیبان"
        )
        == "warning"
    )


def test_add_is_primary():
    assert (
        classify_button_text(
            "＋ افزودن کار جدید"
        )
        == "primary"
    )


def test_save_is_primary():
    assert (
        classify_button_text(
            "ذخیره"
        )
        == "primary"
    )


def test_edit_is_secondary():
    assert (
        classify_button_text(
            "ویرایش"
        )
        == "secondary"
    )


def test_cancel_is_secondary():
    assert (
        classify_button_text(
            "انصراف"
        )
        == "secondary"
    )