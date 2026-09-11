from datetime import date, timedelta
from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
)


VALID_RECURRENCE_TYPES = {
    "daily",
    "weekly",
    "weekdays",
}


VALID_PRIORITIES = {
    "low",
    "normal",
    "high",
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


def _validate_time_range(
    start_time: str | None,
    end_time: str | None,
) -> None:
    if (
        start_time
        and end_time
        and end_time <= start_time
    ):
        raise ValueError(
            "End time must be later "
            "than start time."
        )


def _normalize_weekdays(
    weekdays: list[int] | tuple[int, ...] | None,
) -> list[int]:
    if not weekdays:
        return []

    normalized = sorted(
        set(
            int(day)
            for day in weekdays
        )
    )

    if any(
        day < 0 or day > 6
        for day in normalized
    ):
        raise ValueError(
            "Invalid recurrence weekday."
        )

    return normalized


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


def _validate_series(
    *,
    title: str,
    priority: str,
    recurrence_type: str,
    recurrence_start_date: str,
    recurrence_end_date: str | None,
    recurrence_weekdays: list[int],
    start_time: str | None,
    end_time: str | None,
) -> tuple[date, date | None]:

    if not title.strip():
        raise ValueError(
            "Task title cannot be empty."
        )

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            "Invalid task priority."
        )

    if recurrence_type not in (
        VALID_RECURRENCE_TYPES
    ):
        raise ValueError(
            "Invalid recurrence type."
        )

    start_date = _parse_date(
        recurrence_start_date
    )

    end_date = None

    if recurrence_end_date:
        end_date = _parse_date(
            recurrence_end_date
        )

        if end_date < start_date:
            raise ValueError(
                "Recurrence end date cannot "
                "be before start date."
            )

    if (
        recurrence_type == "weekdays"
        and not recurrence_weekdays
    ):
        raise ValueError(
            "At least one weekday "
            "must be selected."
        )

    _validate_time_range(
        start_time,
        end_time,
    )

    return (
        start_date,
        end_date,
    )


def create_recurring_series(
    *,
    title: str,
    recurrence_type: str,
    recurrence_start_date: str,
    description: str = "",
    start_time: str | None = None,
    end_time: str | None = None,
    all_day: bool = False,
    priority: str = "normal",
    recurrence_weekdays: list[int] | None = None,
    recurrence_end_date: str | None = None,
    database_path: str | Path | None = None,
) -> int:

    title = title.strip()
    description = description.strip()

    weekdays = _normalize_weekdays(
        recurrence_weekdays
    )

    _validate_series(
        title=title,
        priority=priority,
        recurrence_type=recurrence_type,
        recurrence_start_date=(
            recurrence_start_date
        ),
        recurrence_end_date=(
            recurrence_end_date
        ),
        recurrence_weekdays=weekdays,
        start_time=start_time,
        end_time=end_time,
    )

    if all_day:
        start_time = None
        end_time = None

    with get_connection(
        database_path
    ) as connection:

        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                due_date,
                start_time,
                end_time,
                all_day,
                priority,
                completed,
                parent_id,

                is_recurring_template,
                recurrence_type,
                recurrence_weekdays,
                recurrence_start_date,
                recurrence_end_date,
                recurring_template_id
            )
            VALUES (
                ?, ?, NULL, ?, ?, ?, ?, 0, NULL,
                1, ?, ?, ?, ?, NULL
            )
            """,
            (
                title,
                description,
                start_time,
                end_time,
                int(all_day),
                priority,
                recurrence_type,
                _serialize_weekdays(
                    weekdays
                ),
                recurrence_start_date,
                recurrence_end_date,
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


def get_recurring_template(
    template_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE
                id = ?
                AND is_recurring_template = 1
            """,
            (template_id,),
        ).fetchone()


def get_series_instances(
    template_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE recurring_template_id = ?
            ORDER BY due_date ASC
            """,
            (template_id,),
        ).fetchall()


def _matches_recurrence(
    *,
    current_date: date,
    start_date: date,
    recurrence_type: str,
    selected_weekdays: set[int],
) -> bool:

    if recurrence_type == "daily":
        return True

    if recurrence_type == "weekly":
        return (
            current_date.weekday()
            == start_date.weekday()
        )

    if recurrence_type == "weekdays":
        return (
            current_date.weekday()
            in selected_weekdays
        )

    return False


def generate_recurring_instances(
    template_id: int,
    through_date: str,
    database_path: str | Path | None = None,
) -> int:

    template = get_recurring_template(
        template_id,
        database_path=database_path,
    )

    if template is None:
        raise ValueError(
            "Recurring task series "
            "does not exist."
        )

    start_date = _parse_date(
        template[
            "recurrence_start_date"
        ]
    )

    requested_end = _parse_date(
        through_date
    )

    series_end = None

    if template[
        "recurrence_end_date"
    ]:
        series_end = _parse_date(
            template[
                "recurrence_end_date"
            ]
        )

    end_date = requested_end

    if (
        series_end is not None
        and series_end < end_date
    ):
        end_date = series_end

    if end_date < start_date:
        return 0

    selected_weekdays = (
        _deserialize_weekdays(
            template[
                "recurrence_weekdays"
            ]
        )
    )

    created = 0

    current_date = start_date

    with get_connection(
        database_path
    ) as connection:

        while current_date <= end_date:

            if _matches_recurrence(
                current_date=current_date,
                start_date=start_date,
                recurrence_type=(
                    template[
                        "recurrence_type"
                    ]
                ),
                selected_weekdays=(
                    selected_weekdays
                ),
            ):
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE
                    INTO tasks (
                        title,
                        description,
                        due_date,
                        start_time,
                        end_time,
                        all_day,
                        priority,
                        completed,
                        parent_id,

                        is_recurring_template,
                        recurrence_type,
                        recurrence_weekdays,
                        recurrence_start_date,
                        recurrence_end_date,
                        recurring_template_id
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, 0, NULL,
                        0, 'none', NULL, NULL, NULL, ?
                    )
                    """,
                    (
                        template["title"],
                        template["description"],
                        current_date.isoformat(),
                        template["start_time"],
                        template["end_time"],
                        template["all_day"],
                        template["priority"],
                        template_id,
                    ),
                )

                if cursor.rowcount > 0:
                    created += 1

            current_date += timedelta(
                days=1
            )

        connection.commit()

    return created


def ensure_recurring_instances_through(
    through_date: str,
    database_path: str | Path | None = None,
) -> int:

    target_date = _parse_date(
        through_date
    )

    with get_connection(
        database_path
    ) as connection:

        templates = connection.execute(
            """
            SELECT id
            FROM tasks
            WHERE
                is_recurring_template = 1
                AND recurrence_start_date <= ?
                AND (
                    recurrence_end_date IS NULL
                    OR recurrence_end_date >= ?
                )
            """,
            (
                target_date.isoformat(),
                target_date.isoformat(),
            ),
        ).fetchall()

    created = 0

    for template in templates:
        created += generate_recurring_instances(
            template["id"],
            target_date.isoformat(),
            database_path=database_path,
        )

    return created


def update_recurring_series(
    *,
    template_id: int,
    title: str,
    recurrence_type: str,
    recurrence_start_date: str,
    description: str = "",
    start_time: str | None = None,
    end_time: str | None = None,
    all_day: bool = False,
    priority: str = "normal",
    recurrence_weekdays: list[int] | None = None,
    recurrence_end_date: str | None = None,
    replace_instances_from: str | None = None,
    database_path: str | Path | None = None,
) -> None:

    title = title.strip()
    description = description.strip()

    weekdays = _normalize_weekdays(
        recurrence_weekdays
    )

    _validate_series(
        title=title,
        priority=priority,
        recurrence_type=recurrence_type,
        recurrence_start_date=(
            recurrence_start_date
        ),
        recurrence_end_date=(
            recurrence_end_date
        ),
        recurrence_weekdays=weekdays,
        start_time=start_time,
        end_time=end_time,
    )

    if all_day:
        start_time = None
        end_time = None

    if replace_instances_from is None:
        replace_instances_from = (
            date.today().isoformat()
        )

    _parse_date(
        replace_instances_from
    )

    with get_connection(
        database_path
    ) as connection:

        result = connection.execute(
            """
            UPDATE tasks
            SET
                title = ?,
                description = ?,
                start_time = ?,
                end_time = ?,
                all_day = ?,
                priority = ?,

                recurrence_type = ?,
                recurrence_weekdays = ?,
                recurrence_start_date = ?,
                recurrence_end_date = ?
            WHERE
                id = ?
                AND is_recurring_template = 1
            """,
            (
                title,
                description,
                start_time,
                end_time,
                int(all_day),
                priority,

                recurrence_type,
                _serialize_weekdays(
                    weekdays
                ),
                recurrence_start_date,
                recurrence_end_date,

                template_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Recurring task series "
                "does not exist."
            )

        # Preserve past history and already-
        # completed occurrences. Rebuild future
        # incomplete occurrences.
        connection.execute(
            """
            DELETE FROM tasks
            WHERE
                recurring_template_id = ?
                AND due_date >= ?
                AND completed = 0
            """,
            (
                template_id,
                replace_instances_from,
            ),
        )

        connection.commit()


def delete_recurring_series(
    template_id: int,
    database_path: str | Path | None = None,
) -> None:

    with get_connection(
        database_path
    ) as connection:

        connection.execute(
            """
            DELETE FROM tasks
            WHERE
                id = ?
                AND is_recurring_template = 1
            """,
            (template_id,),
        )

        connection.commit()