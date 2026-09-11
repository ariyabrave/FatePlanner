from datetime import date

from fateplanner.utils.date_utils import (
    format_jalali_date,
    get_persian_week,
    to_persian_digits,
)


def test_persian_digits():
    assert (
        to_persian_digits(
            "1405"
        )
        == "۱۴۰۵"
    )

    assert (
        to_persian_digits(
            1234567890
        )
        == "۱۲۳۴۵۶۷۸۹۰"
    )


def test_nowruz_1405():
    result = (
        format_jalali_date(
            date(
                2026,
                3,
                21,
            )
        )
    )

    assert (
        result
        == "شنبه ۱ فروردین ۱۴۰۵"
    )


def test_persian_week_starts_saturday():
    week = get_persian_week(
        date(
            2026,
            3,
            25,
        )
    )

    assert len(week) == 7

    assert (
        week[0]
        == date(
            2026,
            3,
            21,
        )
    )

    assert (
        week[-1]
        == date(
            2026,
            3,
            27,
        )
    )

    assert (
        week[0].weekday()
        == 5
    )

    assert (
        week[-1].weekday()
        == 4
    )