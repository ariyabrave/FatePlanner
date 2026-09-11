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
    priority: str = "normal",
    database_path: str | Path | None = None,
) -> int:
    title = title.strip()
    description = description.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    if priority not in VALID_PRIORITIES:
        raise ValueError("Invalid task priority.")

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                due_date,
                priority
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                description,
                due_date,
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
                END,
                id DESC
            """
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

    if total == 0:
        percentage = 0
    else:
        percentage = round((completed / total) * 100)

    return total, completed, percentage