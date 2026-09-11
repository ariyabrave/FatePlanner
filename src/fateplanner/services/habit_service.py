from datetime import (
    date,
    timedelta,
)
from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
)
from fateplanner.utils.date_utils import (
    get_jalali_month_dates,
)


VALID_SCHEDULE_TYPES = {
    "daily",
    "weekdays",
}


def _parse_date(
    value: str,
) -> date:
    try:
        return date.fromisoformat(
            value
        )

    except ValueError as error:
        raise ValueError(
            "Invalid date."
        ) from error


def _normalize_weekdays(
    weekdays: list[int] | None,
) -> list[int]:
    if not weekdays:
        return []

    result = sorted(
        set(
            int(day)
            for day in weekdays
        )
    )

    if any(
        day < 0 or day > 6
        for day in result
    ):
        raise ValueError(
            "Invalid weekday."
        )

    return result


def _serialize_weekdays(
    weekdays: list[int],
) -> str | None:
    if not weekdays:
        return None

    return ",".join(
        str(day)
        for day in weekdays
    )


def _deserialize_weekdays(
    value: str | None,
) -> set[int]:
    if not value:
        return set()

    return {
        int(day)
        for day in value.split(",")
        if day.strip()
    }


def _validate_habit(
    *,
    title: str,
    schedule_type: str,
    weekdays: list[int],
    start_date: str,
) -> None:
    if not title.strip():
        raise ValueError(
            "Habit title cannot be empty."
        )

    if (
        schedule_type
        not in VALID_SCHEDULE_TYPES
    ):
        raise ValueError(
            "Invalid habit schedule."
        )

    _parse_date(
        start_date
    )

    if (
        schedule_type == "weekdays"
        and not weekdays
    ):
        raise ValueError(
            "At least one weekday "
            "must be selected."
        )


def create_habit(
    *,
    title: str,
    description: str = "",
    schedule_type: str = "daily",
    weekdays: list[int] | None = None,
    start_date: str | None = None,
    database_path: str | Path | None = None,
) -> int:
    title = title.strip()
    description = description.strip()

    if start_date is None:
        start_date = (
            date.today().isoformat()
        )

    normalized_weekdays = (
        _normalize_weekdays(
            weekdays
        )
    )

    _validate_habit(
        title=title,
        schedule_type=schedule_type,
        weekdays=normalized_weekdays,
        start_date=start_date,
    )

    with get_connection(
        database_path
    ) as connection:

        cursor = connection.execute(
            """
            INSERT INTO habits (
                title,
                description,
                schedule_type,
                weekdays,
                start_date,
                archived
            )
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (
                title,
                description,
                schedule_type,
                _serialize_weekdays(
                    normalized_weekdays
                ),
                start_date,
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


def get_habit(
    habit_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                title,
                description,
                schedule_type,
                weekdays,
                start_date,
                archived,
                created_at
            FROM habits
            WHERE id = ?
            """,
            (habit_id,),
        ).fetchone()


def get_habits(
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                title,
                description,
                schedule_type,
                weekdays,
                start_date,
                archived,
                created_at
            FROM habits
            WHERE archived = 0
            ORDER BY id DESC
            """
        ).fetchall()


def update_habit(
    *,
    habit_id: int,
    title: str,
    description: str = "",
    schedule_type: str = "daily",
    weekdays: list[int] | None = None,
    start_date: str,
    database_path: str | Path | None = None,
) -> None:
    title = title.strip()
    description = description.strip()

    normalized_weekdays = (
        _normalize_weekdays(
            weekdays
        )
    )

    _validate_habit(
        title=title,
        schedule_type=schedule_type,
        weekdays=normalized_weekdays,
        start_date=start_date,
    )

    with get_connection(
        database_path
    ) as connection:

        result = connection.execute(
            """
            UPDATE habits
            SET
                title = ?,
                description = ?,
                schedule_type = ?,
                weekdays = ?,
                start_date = ?
            WHERE id = ?
            """,
            (
                title,
                description,
                schedule_type,
                _serialize_weekdays(
                    normalized_weekdays
                ),
                start_date,
                habit_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Habit does not exist."
            )

        connection.commit()


def delete_habit(
    habit_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        connection.execute(
            """
            DELETE FROM habits
            WHERE id = ?
            """,
            (habit_id,),
        )

        connection.commit()


def is_habit_scheduled_on_date(
    habit,
    target_date: str | date,
) -> bool:
    if isinstance(
        target_date,
        str,
    ):
        target = _parse_date(
            target_date
        )
    else:
        target = target_date

    start = _parse_date(
        habit["start_date"]
    )

    if target < start:
        return False

    if (
        habit["schedule_type"]
        == "daily"
    ):
        return True

    if (
        habit["schedule_type"]
        == "weekdays"
    ):
        weekdays = _deserialize_weekdays(
            habit["weekdays"]
        )

        return (
            target.weekday()
            in weekdays
        )

    return False


def get_habits_for_date(
    target_date: str,
    database_path: str | Path | None = None,
):
    target = _parse_date(
        target_date
    )

    habits = get_habits(
        database_path=database_path
    )

    return [
        habit
        for habit in habits
        if is_habit_scheduled_on_date(
            habit,
            target,
        )
    ]


def is_habit_completed(
    habit_id: int,
    log_date: str,
    database_path: str | Path | None = None,
) -> bool:
    _parse_date(
        log_date
    )

    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT completed
            FROM habit_logs
            WHERE
                habit_id = ?
                AND log_date = ?
            """,
            (
                habit_id,
                log_date,
            ),
        ).fetchone()

    return bool(
        row
        and row["completed"]
    )


def set_habit_completed(
    habit_id: int,
    log_date: str,
    completed: bool,
    database_path: str | Path | None = None,
) -> None:
    target = _parse_date(
        log_date
    )

    habit = get_habit(
        habit_id,
        database_path=database_path,
    )

    if habit is None:
        raise ValueError(
            "Habit does not exist."
        )

    if not is_habit_scheduled_on_date(
        habit,
        target,
    ):
        raise ValueError(
            "Habit is not scheduled "
            "for this date."
        )

    with get_connection(
        database_path
    ) as connection:

        if completed:
            connection.execute(
                """
                INSERT INTO habit_logs (
                    habit_id,
                    log_date,
                    completed
                )
                VALUES (?, ?, 1)

                ON CONFLICT(
                    habit_id,
                    log_date
                )
                DO UPDATE SET
                    completed = 1
                """,
                (
                    habit_id,
                    log_date,
                ),
            )

        else:
            connection.execute(
                """
                DELETE FROM habit_logs
                WHERE
                    habit_id = ?
                    AND log_date = ?
                """,
                (
                    habit_id,
                    log_date,
                ),
            )

        connection.commit()


def get_habit_logs_between(
    habit_id: int,
    start_date: str,
    end_date: str,
    database_path: str | Path | None = None,
):
    start = _parse_date(
        start_date
    )

    end = _parse_date(
        end_date
    )

    if end < start:
        raise ValueError(
            "End date cannot be "
            "before start date."
        )

    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                habit_id,
                log_date,
                completed,
                created_at
            FROM habit_logs
            WHERE
                habit_id = ?
                AND log_date >= ?
                AND log_date <= ?
            ORDER BY log_date ASC
            """,
            (
                habit_id,
                start.isoformat(),
                end.isoformat(),
            ),
        ).fetchall()


def get_habit_progress_for_date(
    target_date: str,
    database_path: str | Path | None = None,
) -> tuple[int, int, int]:
    habits = get_habits_for_date(
        target_date,
        database_path=database_path,
    )

    total = len(
        habits
    )

    completed = sum(
        1
        for habit in habits
        if is_habit_completed(
            habit["id"],
            target_date,
            database_path=database_path,
        )
    )

    percentage = (
        round(
            completed / total * 100
        )
        if total
        else 0
    )

    return (
        total,
        completed,
        percentage,
    )


def get_habit_stats(
    habit_id: int,
    through_date: str | None = None,
    database_path: str | Path | None = None,
) -> dict:
    habit = get_habit(
        habit_id,
        database_path=database_path,
    )

    if habit is None:
        raise ValueError(
            "Habit does not exist."
        )

    if through_date is None:
        target = date.today()
    else:
        target = _parse_date(
            through_date
        )

    start = _parse_date(
        habit["start_date"]
    )

    if target < start:
        return {
            "current_streak": 0,
            "best_streak": 0,
            "completed": 0,
            "scheduled": 0,
            "percentage": 0,
        }

    with get_connection(
        database_path
    ) as connection:

        rows = connection.execute(
            """
            SELECT log_date
            FROM habit_logs
            WHERE
                habit_id = ?
                AND completed = 1
                AND log_date <= ?
            """,
            (
                habit_id,
                target.isoformat(),
            ),
        ).fetchall()

    completed_dates = {
        row["log_date"]
        for row in rows
    }

    scheduled_dates = []

    current = start

    while current <= target:
        if is_habit_scheduled_on_date(
            habit,
            current,
        ):
            scheduled_dates.append(
                current
            )

        current += timedelta(
            days=1
        )

    best_streak = 0
    running_streak = 0

    for scheduled_date in (
        scheduled_dates
    ):
        if (
            scheduled_date.isoformat()
            in completed_dates
        ):
            running_streak += 1

            best_streak = max(
                best_streak,
                running_streak,
            )

        else:
            running_streak = 0

    current_streak = 0

    for scheduled_date in reversed(
        scheduled_dates
    ):
        if (
            scheduled_date.isoformat()
            in completed_dates
        ):
            current_streak += 1

        else:
            break

    scheduled_count = len(
        scheduled_dates
    )

    completed_count = sum(
        1
        for scheduled_date
        in scheduled_dates
        if (
            scheduled_date.isoformat()
            in completed_dates
        )
    )

    percentage = (
        round(
            completed_count
            / scheduled_count
            * 100
        )
        if scheduled_count
        else 0
    )

    return {
        "current_streak": (
            current_streak
        ),
        "best_streak": (
            best_streak
        ),
        "completed": (
            completed_count
        ),
        "scheduled": (
            scheduled_count
        ),
        "percentage": (
            percentage
        ),
    }


def get_habit_month_stats(
    habit_id: int,
    jalali_year: int,
    jalali_month: int,
    through_date: str | None = None,
    database_path: str | Path | None = None,
) -> dict:
    habit = get_habit(
        habit_id,
        database_path=database_path,
    )

    if habit is None:
        raise ValueError(
            "Habit does not exist."
        )

    month_dates = (
        get_jalali_month_dates(
            jalali_year,
            jalali_month,
        )
    )

    if through_date is None:
        target = date.today()
    else:
        target = _parse_date(
            through_date
        )

    relevant_dates = [
        month_date
        for month_date in month_dates
        if (
            month_date <= target
            and is_habit_scheduled_on_date(
                habit,
                month_date,
            )
        )
    ]

    if not relevant_dates:
        return {
            "scheduled": 0,
            "completed": 0,
            "missed": 0,
            "percentage": 0,
        }

    logs = get_habit_logs_between(
        habit_id,
        month_dates[0].isoformat(),
        month_dates[-1].isoformat(),
        database_path=database_path,
    )

    completed_dates = {
        row["log_date"]
        for row in logs
        if row["completed"]
    }

    scheduled = len(
        relevant_dates
    )

    completed = sum(
        1
        for relevant_date
        in relevant_dates
        if (
            relevant_date.isoformat()
            in completed_dates
        )
    )

    missed = (
        scheduled
        - completed
    )

    percentage = (
        round(
            completed
            / scheduled
            * 100
        )
        if scheduled
        else 0
    )

    return {
        "scheduled": scheduled,
        "completed": completed,
        "missed": missed,
        "percentage": percentage,
    }