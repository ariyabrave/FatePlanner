from pathlib import Path

from fateplanner.database.connection import get_connection


VALID_PRIORITIES = {
    "low",
    "normal",
    "high",
}


def create_task(
    title: str,
    description: str = "",
    due_date: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    all_day: bool = False,
    priority: str = "normal",
    database_path: str | Path | None = None,
) -> int:
    title = title.strip()
    description = description.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    if priority not in VALID_PRIORITIES:
        raise ValueError("Invalid task priority.")

    if start_time and end_time:
        if end_time <= start_time:
            raise ValueError(
                "End time must be later than start time."
            )

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                due_date,
                start_time,
                end_time,
                all_day,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                due_date,
                start_time,
                end_time,
                int(all_day),
                priority,
            ),
        )

        connection.commit()

        return int(cursor.lastrowid)


def get_tasks(
    database_path: str | Path | None = None,
):
    with get_connection(database_path) as connection:
        return connection.execute(
            """
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
                created_at
            FROM tasks
            ORDER BY
                completed ASC,
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'normal' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END ASC,
                id DESC
            """
        ).fetchall()


def get_tasks_for_date(
    date: str,
    database_path: str | Path | None = None,
):
    with get_connection(database_path) as connection:
        return connection.execute(
            """
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
                created_at
            FROM tasks
            WHERE due_date = ?
            ORDER BY
                completed ASC,
                all_day DESC,
                start_time ASC,
                id ASC
            """,
            (date,),
        ).fetchall()


def set_task_completed(
    task_id: int,
    completed: bool,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(database_path) as connection:
        connection.execute(
            """
            UPDATE tasks
            SET completed = ?
            WHERE id = ?
            """,
            (
                int(completed),
                task_id,
            ),
        )

        connection.commit()


def delete_task(
    task_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(database_path) as connection:
        connection.execute(
            """
            DELETE FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        connection.commit()


def get_task_progress(
    database_path: str | Path | None = None,
) -> tuple[int, int, int]:
    with get_connection(database_path) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN completed = 1 THEN 1
                        ELSE 0
                    END
                ) AS completed
            FROM tasks
            """
        ).fetchone()

    total = int(row["total"])
    completed = int(row["completed"] or 0)

    percentage = (
        round((completed / total) * 100)
        if total > 0
        else 0
    )

    return total, completed, percentage


def get_task_progress_for_date(
    date: str,
    database_path: str | Path | None = None,
) -> tuple[int, int, int]:
    with get_connection(database_path) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN completed = 1 THEN 1
                        ELSE 0
                    END
                ) AS completed
            FROM tasks
            WHERE due_date = ?
            """,
            (date,),
        ).fetchone()

    total = int(row["total"])
    completed = int(row["completed"] or 0)

    percentage = (
        round((completed / total) * 100)
        if total > 0
        else 0
    )

    return total, completed, percentage