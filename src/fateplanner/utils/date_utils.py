from datetime import date, timedelta

import jdatetime


PERSIAN_MONTH_NAMES = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند",
}


PERSIAN_WEEKDAY_NAMES = {
    0: "دوشنبه",
    1: "سه‌شنبه",
    2: "چهارشنبه",
    3: "پنجشنبه",
    4: "جمعه",
    5: "شنبه",
    6: "یکشنبه",
}


PERSIAN_DIGIT_TRANSLATION = (
    str.maketrans(
        "0123456789",
        "۰۱۲۳۴۵۶۷۸۹",
    )
)


def to_persian_digits(
    value: str | int,
) -> str:
    return str(value).translate(
        PERSIAN_DIGIT_TRANSLATION
    )


def gregorian_to_jalali(
    gregorian_date: date,
) -> jdatetime.date:
    return jdatetime.date.fromgregorian(
        date=gregorian_date
    )


def jalali_to_gregorian(
    year: int,
    month: int,
    day: int,
) -> date:
    jalali_date = jdatetime.date(
        year,
        month,
        day,
    )

    return jalali_date.togregorian()


def get_jalali_month_length(
    year: int,
    month: int,
) -> int:
    if 1 <= month <= 6:
        return 31

    if 7 <= month <= 11:
        return 30

    if month != 12:
        raise ValueError(
            "Invalid Jalali month."
        )

    try:
        jdatetime.date(
            year,
            12,
            30,
        )

        return 30

    except ValueError:
        return 29


def get_jalali_month_dates(
    year: int,
    month: int,
) -> list[date]:
    month_length = (
        get_jalali_month_length(
            year,
            month,
        )
    )

    return [
        jalali_to_gregorian(
            year,
            month,
            day,
        )
        for day in range(
            1,
            month_length + 1,
        )
    ]


def get_persian_weekday_column(
    gregorian_date: date,
) -> int:
    """
    Saturday = 0
    Sunday   = 1
    ...
    Friday   = 6
    """

    return (
        gregorian_date.weekday() - 5
    ) % 7


def format_jalali_month_title(
    year: int,
    month: int,
) -> str:
    if month not in PERSIAN_MONTH_NAMES:
        raise ValueError(
            "Invalid Jalali month."
        )

    return (
        f"{PERSIAN_MONTH_NAMES[month]} "
        f"{to_persian_digits(year)}"
    )


def format_jalali_date(
    gregorian_date: date,
) -> str:
    jalali_date = (
        gregorian_to_jalali(
            gregorian_date
        )
    )

    weekday = (
        PERSIAN_WEEKDAY_NAMES[
            gregorian_date.weekday()
        ]
    )

    day = to_persian_digits(
        jalali_date.day
    )

    month = (
        PERSIAN_MONTH_NAMES[
            jalali_date.month
        ]
    )

    year = to_persian_digits(
        jalali_date.year
    )

    return (
        f"{weekday} "
        f"{day} "
        f"{month} "
        f"{year}"
    )


def format_jalali_short(
    gregorian_date: date,
) -> str:
    jalali_date = (
        gregorian_to_jalali(
            gregorian_date
        )
    )

    day = to_persian_digits(
        jalali_date.day
    )

    month = (
        PERSIAN_MONTH_NAMES[
            jalali_date.month
        ]
    )

    return (
        f"{day} {month}"
    )


def format_jalali_week_range(
    start_date: date,
    end_date: date,
) -> str:
    start_text = (
        format_jalali_short(
            start_date
        )
    )

    end_text = (
        format_jalali_short(
            end_date
        )
    )

    end_jalali = (
        gregorian_to_jalali(
            end_date
        )
    )

    year = to_persian_digits(
        end_jalali.year
    )

    return (
        f"{start_text} تا "
        f"{end_text} "
        f"{year}"
    )


def get_persian_week(
    anchor_date: date | None = None,
) -> list[date]:
    if anchor_date is None:
        anchor_date = date.today()

    days_since_saturday = (
        anchor_date.weekday() - 5
    ) % 7

    saturday = (
        anchor_date
        - timedelta(
            days=days_since_saturday
        )
    )

    return [
        saturday
        + timedelta(days=index)
        for index in range(7)
    ]