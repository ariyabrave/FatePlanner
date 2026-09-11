from datetime import date

from fateplanner.utils.date_utils import (
    format_jalali_date,
    get_jalali_month_length,
    get_persian_week,
    gregorian_to_jalali,
    jalali_to_gregorian,
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
    result = format_jalali_date(
        date(
            2026,
            3,
            21,
        )
    )

    assert (
        result
        == "شنبه ۱ فروردین ۱۴۰۵"
    )


def test_gregorian_to_jalali():
    result = gregorian_to_jalali(
        date(
            2026,
            3,
            21,
        )
    )

    assert result.year == 1405
    assert result.month == 1
    assert result.day == 1


def test_jalali_to_gregorian():
    result = jalali_to_gregorian(
        1405,
        1,
        1,
    )

    assert result == date(
        2026,
        3,
        21,
    )


def test_first_six_months_have_31_days():
    assert (
        get_jalali_month_length(
            1405,
            1,
        )
        == 31
    )

    assert (
        get_jalali_month_length(
            1405,
            6,
        )
        == 31
    )


def test_second_half_months_have_30_days():
    assert (
        get_jalali_month_length(
            1405,
            7,
        )
        == 30
    )

    assert (
        get_jalali_month_length(
            1405,
            11,
        )
        == 30
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

    assert week[0] == date(
        2026,
        3,
        21,
    )

    assert week[-1] == date(
        2026,
        3,
        27,
    )

    assert (
        week[0].weekday()
        == 5
    )

    assert (
        week[-1].weekday()
        == 4
    )


def test_farvardin_1405_has_31_dates():
    from fateplanner.utils.date_utils import (
        get_jalali_month_dates,
    )

    dates = get_jalali_month_dates(
        1405,
        1,
    )

    assert len(dates) == 31

    assert (
        dates[0]
        == date(
            2026,
            3,
            21,
        )
    )


def test_saturday_is_first_calendar_column():
    from fateplanner.utils.date_utils import (
        get_persian_weekday_column,
    )

    assert (
        get_persian_weekday_column(
            date(
                2026,
                3,
                21,
            )
        )
        == 0
    )    