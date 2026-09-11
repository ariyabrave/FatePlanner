from datetime import date
from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
)


VALID_FILTERS = {
    "open",
    "today",
    "overdue",
    "upcoming",
    "unscheduled",
    "completed",
    "all",
}


def _supports_skipped(
    connection,
) -> bool:
    columns = {
        row["name"]
        for row in connection.execute(
            """
            PRAGMA table_info(tasks)
            """
        ).fetchall()
    }

    return (
        "is_skipped"
        in columns
    )


def get_task_center_summary(
    reference_date: str | None = None,
    database_path: str | Path | None = None,
):
    reference_date = (
        reference_date
        or date.today().isoformat()
    )

    with get_connection(
        database_path
    ) as connection:

        skip_clause = (
            "AND is_skipped = 0"
            if _supports_skipped(
                connection
            )
            else ""
        )

        def count(
            condition,
            params=(),
        ):
            row = connection.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM tasks
                WHERE
                    is_recurring_template = 0
                    AND parent_id IS NULL
                    {skip_clause}
                    AND {condition}
                """,
                params,
            ).fetchone()

            return int(
                row["total"] or 0
            )

        return {
            "today": count(
                "due_date = ?",
                (
                    reference_date,
                ),
            ),
            "overdue": count(
                """
                completed = 0
                AND due_date IS NOT NULL
                AND due_date < ?
                """,
                (
                    reference_date,
                ),
            ),
            "upcoming": count(
                """
                completed = 0
                AND due_date > ?
                """,
                (
                    reference_date,
                ),
            ),
            "unscheduled": count(
                """
                completed = 0
                AND due_date IS NULL
                """
            ),
            "completed": count(
                "completed = 1"
            ),
        }


def get_task_center_tasks(
    *,
    filter_mode: str = "open",
    search: str = "",
    reference_date: str | None = None,
    database_path: str | Path | None = None,
):
    if filter_mode not in VALID_FILTERS:
        raise ValueError(
            "Invalid task filter."
        )

    reference_date = (
        reference_date
        or date.today().isoformat()
    )

    search = search.strip()

    conditions = [
        "is_recurring_template = 0",
        "parent_id IS NULL",
    ]

    parameters = []

    if filter_mode == "open":
        conditions.append(
            "completed = 0"
        )

    elif filter_mode == "today":
        conditions.append(
            "due_date = ?"
        )

        parameters.append(
            reference_date
        )

    elif filter_mode == "overdue":
        conditions.extend(
            [
                "completed = 0",
                "due_date IS NOT NULL",
                "due_date < ?",
            ]
        )

        parameters.append(
            reference_date
        )

    elif filter_mode == "upcoming":
        conditions.extend(
            [
                "completed = 0",
                "due_date > ?",
            ]
        )

        parameters.append(
            reference_date
        )

    elif filter_mode == "unscheduled":
        conditions.extend(
            [
                "completed = 0",
                "due_date IS NULL",
            ]
        )

    elif filter_mode == "completed":
        conditions.append(
            "completed = 1"
        )

    if search:
        conditions.append(
            """
            (
                title LIKE ?
                OR COALESCE(
                    description,
                    ''
                ) LIKE ?
            )
            """
        )

        like = (
            f"%{search}%"
        )

        parameters.extend(
            [
                like,
                like,
            ]
        )

    with get_connection(
        database_path
    ) as connection:

        if _supports_skipped(
            connection
        ):
            conditions.append(
                "is_skipped = 0"
            )

        where_sql = (
            " AND ".join(
                conditions
            )
        )

        return connection.execute(
            f"""
            SELECT
                id,
                title,
                description,
                due_date,
                start_time,
                end_time,
                all_day,
                priority,
                completed,
                recurring_template_id
            FROM tasks
            WHERE {where_sql}
            ORDER BY
                completed ASC,

                CASE
                    WHEN due_date IS NULL
                    THEN 1
                    ELSE 0
                END ASC,

                due_date ASC,

                CASE
                    WHEN start_time IS NULL
                    THEN 1
                    ELSE 0
                END ASC,

                start_time ASC,
                id ASC
            """,
            parameters,
        ).fetchall()


def set_task_center_completed(
    task_id: int,
    completed: bool,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        result = connection.execute(
            """
            UPDATE tasks
            SET completed = ?
            WHERE
                id = ?
                AND is_recurring_template = 0
            """,
            (
                int(
                    bool(
                        completed
                    )
                ),
                task_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Task does not exist."
            )

        connection.commit()